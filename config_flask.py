from flask import Flask
from dotenv import load_dotenv
import os
import json

load_dotenv()
FLASK_SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")

class CustomJSONEncoder(json.JSONEncoder):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('ensure_ascii', False)
        super().__init__(*args, **kwargs)

def create_app():
    app = Flask(__name__, template_folder="templates")
    app.secret_key = FLASK_SECRET_KEY

    app.config['JSON_AS_ASCII'] = False
    app.json_encoder = CustomJSONEncoder

    # Registra os blueprints das rotas (com templates e sem templates)

    # Exemplo de blueprint com templates
    # Importa o blueprint definido no inicio do arquivo routes.py -> template_bp = Blueprint('template_service', __name__, template_folder='templates')
    from services.template_example.routes import template_bp

    # Exemplo de blueprint sem templates
    # Importa o blueprint definido no inicio do arquivo routes.py -> webhook_bp = Blueprint('webhook_service', __name__)
    from services.webhook_example.routes import webhook_bp

    # Registrar blueprint das rotas a partir daqui:
    from services.database.routes import database_bp

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
    app.register_blueprint(webhook_bp, url_prefix='/webhook')

    #Registrar rotas novas a partir daqui:
    app.register_blueprint(database_bp, url_prefix='/database')
    return app
