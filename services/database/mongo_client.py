from pymongo import MongoClient
from urllib.parse import quote_plus
import os
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

def get_database():
    """
    Retorna uma conexão segura com o banco de dados MongoDB
    com tratamento para caracteres especiais nas credenciais
    """
    # Recupera e codifica as credenciais
    username = quote_plus(os.getenv("MONGO_APP_USER", "app_user"))
    password = quote_plus(os.getenv("MONGO_APP_PASSWORD", "senh@Complexa_321!"))
    db_name = os.getenv("MONGO_DB", "gateway_db")

    # Constrói a URI de conexão com parâmetros de segurança
    mongo_uri = (
        f"mongodb://{username}:{password}@mongodb:27017/{db_name}"
        f"?authSource={db_name}"
        f"&authMechanism=SCRAM-SHA-256"
        f"&retryWrites=true"
        f"&w=majority"
        f"&connectTimeoutMS=5000"
        f"&socketTimeoutMS=30000"
    )

    # Configuração do cliente com parâmetros otimizados
    client = MongoClient(
        mongo_uri,
        appname="gateway_app",  # Identificação da aplicação
        maxPoolSize=50,         # Pool de conexões
        minPoolSize=10,
        maxIdleTimeMS=30000,
        serverSelectionTimeoutMS=5000
    )

    # Testa a conexão imediatamente
    try:
        client.admin.command('ping')
        return client[db_name]
    except Exception as e:
        raise ConnectionError(f"Falha na conexão com MongoDB: {str(e)}")
