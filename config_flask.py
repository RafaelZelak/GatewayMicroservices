from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()

FLASK_SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")

def create_app():
    app = Flask(__name__, template_folder="templates")
    app.secret_key = FLASK_SECRET_KEY

    # Registra os blueprints das rotas (com templates e sem templates)

    # Exemplo de blueprint com templates
    # Importa o blueprint definido no inicio do arquivo routes.py -> template_bp = Blueprint('template_service', __name__, template_folder='templates')
    from services.template_example.routes import template_bp

    # Exemplo de blueprint sem templates
    # Importa o blueprint definido no inicio do arquivo routes.py -> webhook_bp = Blueprint('webhook_service', __name__)
    from services.webhook_example.routes import webhook_bp

    # Registrar blueprint das rotas a partir daqui:

    # Registra as rotas dos blueprints

    # Exemplo rota com templates
    # Registra as rotas definidas no arquivo routes.py do blueprint template_bp
    # url_prefix define a rota base do blueprint (http://gateway.localhost/template)
    app.register_blueprint(template_bp, url_prefix='/template')

    # Exemplo rota sem templates
    # Registra as rotas definidas no arquivo routes.py do blueprint webhook_bp
    # url_prefix define a rota base do blueprint (http://gateway.localhost/api)
    # dentro do routes.py quando lidamos com webhook, definimos sempre um url_rule para cada método HTTP
    # exmplo -> add_url_rule('/webhook', view_func=WebhookAPI.as_view('webhook_api'))
    # logo para acessar a classe com os métodos GET e POST, a URL final será /api/webhook
    app.register_blueprint(webhook_bp, url_prefix='/api')

    #Registrar rotas novas a partir daqui:

    return app
