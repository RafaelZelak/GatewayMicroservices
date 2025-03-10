import os
import yaml
from functools import wraps
from flask import session, redirect, url_for, request, render_template

# Suponha que seu código de autenticação LDAP esteja disponível em um módulo,
# por exemplo, auth_service.py. Se estiver no mesmo arquivo, você pode copiar as classes.
# Aqui vamos importar AuthService e load_access_config:
from services.auth_service import AuthService  # seu módulo com AuthService e load_access_config

def create_blueprint_env(module_file, templates_folder="templates"):
    """
    Cria um ambiente Jinja2 exclusivo para o blueprint,
    carregando os templates do diretório especificado.
    """
    template_dir = os.path.join(os.path.dirname(module_file), templates_folder)
    from jinja2 import Environment, FileSystemLoader
    return Environment(loader=FileSystemLoader(template_dir))

def blueprint_login_required(bp):
    """
    Decorator que protege as rotas de um blueprint usando uma
    tela de login única (em /templates/login.html), mas valida as
    credenciais via LDAP.

    O arquivo YAML (por exemplo, secured_route.yml) deve estar localizado
    no diretório do blueprint (ex: /services/template_example/secured_route.yml)
    e conter a configuração:

    allowed_groups:
      - "Infra"
    allowed_users:
      - "rafael.zelak"
      - "teste"
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            session_key = f"{bp.name}_logged_in"
            # Se já estiver logado, segue para a rota protegida
            if session.get(session_key):
                return func(*args, **kwargs)
            # Se a requisição for POST, processa o formulário de login
            if request.method == "POST":
                username = request.form.get("username")
                password = request.form.get("password")
                # Autentica via LDAP
                user_info = AuthService.authenticate(username, password)
                if not user_info:
                    error = "Falha na autenticação LDAP."
                    return render_template("login.html", error=error, service=bp.name)
                # Tenta carregar o arquivo YAML de acesso (secured_route.yml) do blueprint
                try:
                    with open(bp.secured_config_path, "r") as f:
                        config = yaml.safe_load(f)
                except Exception as e:
                    return f"Erro ao ler arquivo YAML: {str(e)}", 500
                allowed_groups = config.get("allowed_groups", [])
                allowed_users = config.get("allowed_users", [])
                # Verifica autorização: primeiro por allowed_users (caso definido)
                authorized = False
                if allowed_users and username.lower() in [u.lower() for u in allowed_users]:
                    authorized = True
                # Se não estiver explicitamente na lista de usuários e grupos estiverem definidos,
                # verifica se algum grupo do usuário está entre os allowed_groups.
                elif allowed_groups:
                    user_groups = user_info.get("groups", [])
                    if any(group in allowed_groups for group in user_groups):
                        authorized = True
                if authorized:
                    session[session_key] = True
                    # Tenta obter 'next' do form; se não houver, usa request.args ou request.path
                    next_url = request.form.get("next") or request.args.get("next") or request.path
                    return redirect(next_url)
                else:
                    error = "Você não tem permissão para acessar este serviço."
                    return render_template("login.html", error=error, service=bp.name)
            # Se for GET, renderiza a tela de login (global, em /templates/login.html)
            return render_template("login.html", service=bp.name)
        return wrapper
    return decorator

def secured_route(bp, rule, login=False, **options):
    """
    Função auxiliar para registrar rotas em um blueprint.

    Se login=True, aplica o decorator que automaticamente:
      - Lê o arquivo YAML de credenciais (em bp.secured_config_path),
      - Exibe a tela de login única (em /templates/login.html),
      - Valida as credenciais via LDAP e verifica se o usuário (ou seus grupos)
        têm permissão de acesso.

    Basta decorar a rota e o sistema cuidará do resto.
    """
    def decorator(func):
        if login:
            # Se nenhum método for especificado, forçamos GET e POST
            if "methods" not in options:
                options["methods"] = ["GET", "POST"]
            func = blueprint_login_required(bp)(func)
        bp.route(rule, **options)(func)
        return func
    return decorator
