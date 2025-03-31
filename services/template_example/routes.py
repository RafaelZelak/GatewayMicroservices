# Importação dos módulos necessários para usar templates
from flask import Blueprint
import os
from services.config import create_blueprint_env, secured_route

# Cria o blueprint e define o diretório relativo de templates
# template_bp <- nome da variável do blueprint (será importado no config_flask.py)
# template_service <- nome do blueprint (deve ser único)
# template_folder='templates' <- diretório relativo de templates (manter como 'templates')
template_bp = Blueprint('template_service', __name__, template_folder='templates')

# configuração para a utilização de uma rota com auth LDAP
template_bp.secured_config_path = os.path.join(os.path.dirname(__file__), "secured_route.yml")

# Rota padrão do blueprint, usa rota definida em config_flask.py (url_prefix='/template')
# http://gateway.localhost/template
@template_bp.route('/')
def index():
    # Sempre que for criar uma rota que renderiza um template, criar um "env" -> env = create_blueprint_env(__file__)
    env = create_blueprint_env(__file__)
    # Carrega o template 'index.html' do diretório 'templates' do blueprint
    template = env.get_template('index.html')
    # Renderiza o template
    return template.render()

# Sub-rota do blueprint, usa rota definida em config_flask.py (url_prefix='/template')
# http://gateway.localhost/template/home
# secured_route é usado para adicionar uma senha na rota (senha serve apenas para a rota que ela foi habilitada)
# senha do secure_route é definida pelo LDAP, as configs ficam no arquivo "secured_route.yml"
@secured_route(template_bp, '/home/', login=True)
def home():
    # Sempre que for criar uma rota que renderiza um template, criar um "env" -> env = create_blueprint_env(__file__)
    env = create_blueprint_env(__file__)
    # Carrega o template 'home.html' do diretório 'templates' do blueprint - sub-rota do blueprint
    template = env.get_template('home.html')
    # Renderiza o template
    return template.render()