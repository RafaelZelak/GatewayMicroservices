import os
import json
import time
import logging
import uuid
import hashlib
from urllib.parse import quote_plus
from pymongo import MongoClient, UpdateOne
from pymongo.errors import (
    ConnectionFailure,
    OperationFailure,
    BulkWriteError,
    PyMongoError
)

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Constantes
MAX_RETRIES = 8
RETRY_BACKOFF = 2
INITIAL_DELAY = 1

def get_encoded_uri():
    """Codifica credenciais para RFC 3986"""
    username = quote_plus(os.getenv("MONGO_APP_USER"))
    password = quote_plus(os.getenv("MONGO_APP_PASSWORD"))
    db_name = quote_plus(os.getenv("MONGO_DB"))

    return (
        f"mongodb://{username}:{password}@mongodb:27017/{db_name}"
        f"?authSource={db_name}&authMechanism=SCRAM-SHA-256"
    )

def get_mongo_client():
    """Cria conexão com retry exponencial"""
    mongo_uri = get_encoded_uri()
    attempt = 0

    while attempt < MAX_RETRIES:
        try:
            client = MongoClient(
                mongo_uri,
                appname="gateway_migration",
                connectTimeoutMS=5000,
                serverSelectionTimeoutMS=5000,
                retryWrites=True,
                w="majority"
            )
            client.admin.command("ping")
            return client
        except ConnectionFailure as e:
            delay = INITIAL_DELAY * (RETRY_BACKOFF ** attempt)
            logger.warning(
                f"Falha de conexão (tentativa {attempt+1}/{MAX_RETRIES}): {e}. "
                f"Retry em {delay}s..."
            )
            time.sleep(delay)
            attempt += 1
    raise RuntimeError("Falha permanente de conexão ao MongoDB")

def generate_deterministic_id(item: dict) -> str:
    """Gera um _id determinístico baseado no conteúdo do item."""
    # Certifica-se de não incluir um campo _id já existente no hash
    data_para_hash = {k: v for k, v in item.items() if k != "_id"}
    item_json = json.dumps(data_para_hash, sort_keys=True)
    return hashlib.sha256(item_json.encode('utf-8')).hexdigest()

def apply_migration(client):
    """Executa migrações de forma idempotente"""
    db = client[os.getenv("MONGO_DB")]

    SEED_FILES = [
        ("cnaes", "seed/data/cnaes.json"),
    ]

    for collection_name, file_path in SEED_FILES:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            collection = db[collection_name]
            operations = []

            for idx, item in enumerate(data, 1):
                try:
                    # Gera _id de forma determinística se não existir
                    if "_id" not in item:
                        item["_id"] = generate_deterministic_id(item)
                        logger.info(f"Item {idx}: _id gerado de forma determinística")

                    operations.append(
                        UpdateOne(
                            {"_id": item["_id"]},
                            {"$setOnInsert": item},
                            upsert=True
                        )
                    )

                except KeyError as e:
                    logger.error(f"Item {idx} inválido: Campo obrigatório faltando - {str(e)}")
                    continue

            if operations:
                result = collection.bulk_write(operations, ordered=False)
                logger.info(
                    f"Migração {collection_name}: "
                    f"{result.upserted_count} novos documentos, "
                    f"{result.matched_count} existentes"
                )

        except BulkWriteError as e:
            logger.warning(f"Conflitos em {collection_name}: {str(e.details['writeErrors'][:3])}...")
        except Exception as e:
            logger.error(f"Erro crítico: {str(e)}", exc_info=True)
            raise

def main():
    try:
        logger.info("Iniciando migração...")
        client = get_mongo_client()
        apply_migration(client)
        logger.info("Migração concluída com sucesso")
    except Exception as e:
        logger.error(f"Falha na migração: {str(e)}")
        exit(1)
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    main()
