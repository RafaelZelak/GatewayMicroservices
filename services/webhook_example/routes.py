# Importação dos módulos necessários para usar templates
from flask import Blueprint, request, jsonify
from flask.views import MethodView
from enums.http_status_enum import HttpStatusEnum

# Criação do blueprint para o serviço de webhook
# webhook_bp <- nome da variável do blueprint (será importado no config_flask.py)
# webhook_service <- nome do blueprint (deve ser único)
webhook_bp = Blueprint('webhook_service', __name__)

# Criação da classe WebhookAPI que herda de MethodView
# Essa classe será responsável por lidar com as requisições HTTP
class WebhookAPI(MethodView):
    # Método GET
    def get(self):
        return jsonify({"message": "Webhook GET recebido com sucesso"}), HttpStatusEnum.OK.value
    # Método POST
    def post(self):

        #Método POST: Processa um payload JSON.
        #URL final: /api/webhook
        data = request.get_json()
        if not data:
            return jsonify({"error": "Payload JSON não fornecido"}), HttpStatusEnum.BAD_REQUEST.value

        return jsonify({"message": "Webhook POST recebido com sucesso", "data": data}), HttpStatusEnum.OK.value

# Registra a view para a rota /webhook, associando os métodos GET e POST
# URL final: /api/webhook
# Quando lidamos com webhook, definimos sempre um url_rule para cada método HTTP
# sendo /webhook a subrota do blueprint e as_view('webhook_api') o nome da view (devem ser únicos)
webhook_bp.add_url_rule('/api', view_func=WebhookAPI.as_view('webhook_api'))
