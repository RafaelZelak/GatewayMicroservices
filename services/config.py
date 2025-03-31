import os
import yaml
from functools import wraps
from flask import session, redirect, url_for, request, render_template
from services.auth_service import AuthService

def create_blueprint_env(module_file, templates_folder="templates"):
    """
    Cria um ambiente Jinja2 exclusivo para o blueprint,
    carregando os templates do diretório especificado.
    """
    template_dir = os.path.join(os.path.dirname(module_file), templates_folder)
    from jinja2 import Environment, FileSystemLoader
    return Environment(loader=FileSystemLoader(template_dir))

def blueprint_login_required(bp, jwt_enabled=False):
    """
    Decorator que protege as rotas de um blueprint usando a tela de login.
    Se jwt_enabled for True, gera um token JWT (ou o recupera na requisição GET)
    e injeta seus dados na view via parâmetro `user_data`.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            session_key = f"{bp.name}_logged_in"
            jwt_key = f"{bp.name}_jwt"
            if session.get(session_key):
                if jwt_enabled:
                    jwt_token = session.get(jwt_key)
                    if jwt_token:
                        try:
                            import jwt
                            JWT_SECRET = os.environ.get("JWT_SECRET", "minha_chave_secreta")
                            JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
                            payload = jwt.decode(jwt_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
                            kwargs['user_data'] = payload
                        except jwt.ExpiredSignatureError:
                            session.pop(session_key, None)
                            session.pop(jwt_key, None)
                            return redirect(url_for(f"{bp.name}.login", next=request.path))
                        except jwt.InvalidTokenError:
                            session.pop(session_key, None)
                            session.pop(jwt_key, None)
                            return redirect(url_for(f"{bp.name}.login", next=request.path))

                return func(*args, **kwargs)
            if request.method == "POST":
                username = request.form.get("username")
                password = request.form.get("password")
                user_info = AuthService.authenticate(username, password)
                if not user_info:
                    error = "Falha na autenticação LDAP."
                    return render_template("login.html", error=error, service=bp.name)
                try:
                    with open(bp.secured_config_path, "r") as f:
                        config = yaml.safe_load(f)
                except Exception as e:
                    return f"Erro ao ler arquivo YAML: {str(e)}", 500
                allowed_groups = config.get("allowed_groups", [])
                allowed_users = config.get("allowed_users", [])
                authorized = False
                if allowed_users and username.lower() in [u.lower() for u in allowed_users]:
                    authorized = True
                elif allowed_groups:
                    user_groups = user_info.get("groups", [])
                    if any(group in allowed_groups for group in user_groups):
                        authorized = True
                if authorized:
                    session[session_key] = True
                    if jwt_enabled:
                        import jwt, datetime
                        JWT_SECRET = os.environ.get("JWT_SECRET", "minha_chave_secreta")
                        JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
                        JWT_EXP_DELTA_SECONDS = 86400
                        payload = user_info.copy()
                        payload['exp'] = datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_EXP_DELTA_SECONDS)
                        jwt_token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
                        session[jwt_key] = jwt_token
                    next_url = request.form.get("next") or request.args.get("next") or request.path
                    return redirect(next_url)
                else:
                    error = "Você não tem permissão para acessar este serviço."
                    return render_template("login.html", error=error, service=bp.name)
            return render_template("login.html", service=bp.name)
        return wrapper
    return decorator

def secured_route(bp, rule, login=False, **options):
    def decorator(func):
        if login:
            jwt_enabled = options.pop("jwt", False)
            if "methods" not in options:
                options["methods"] = ["GET", "POST"]
            func = blueprint_login_required(bp, jwt_enabled=jwt_enabled)(func)
        bp.route(rule, **options)(func)
        return func
    return decorator
