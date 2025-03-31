from flask import Blueprint, request, jsonify
from flask.views import MethodView
from enums.http_status_enum import HttpStatusEnum
from services.database.mongo_client import get_database
import secrets

database_bp = Blueprint('database_service', __name__)

class DatabaseAPI(MethodView):
    def post(self):
        """
        Manages POST requests for creating collections, inserting data, deleting collections, or deleting data.
        """
        data = request.get_json()

        if not data or "method" not in data:
            return jsonify({"error": "'method' field is required"}), HttpStatusEnum.BAD_REQUEST.value

        method = data["method"]

        if method == "create_collection":
            return self.create_collection(data)
        elif method == "insert_data":
            return self.insert_data(data)
        elif method == "delete_collection":
            return self.delete_collection(data)
        elif method == "delete_data":
            return self.delete_data(data)
        else:
            return jsonify({"error": "Invalid method"}), HttpStatusEnum.BAD_REQUEST.value

    def create_collection(self, data):
        """
        Creates a new collection and generates a Bearer Token for access, storing it in MongoDB.
        """
        collection_name = data.get("collection_name")

        if not collection_name:
            return jsonify({"error": "'collection_name' is required"}), HttpStatusEnum.BAD_REQUEST.value

        db = get_database()
        if collection_name in db.list_collection_names():
            return jsonify({"error": "Collection already exists"}), HttpStatusEnum.BAD_REQUEST.value

        db.create_collection(collection_name)

        # Generate token and store it in MongoDB
        token = secrets.token_hex(32)
        db["_tokens"].insert_one({"collection": collection_name, "token": token})

        return jsonify({
            "message": "Collection created successfully | Auth - Bearer Token",
            "collection_name": collection_name,
            "token": f"{token}"
        }), HttpStatusEnum.CREATED.value

    def insert_data(self, data):
        """
        Inserts a new document into the collection, validates the Bearer Token, and generates a sequential ID.
        """
        collection_name = data.get("collection_name")
        document = data.get("data")
        token = self.extract_bearer_token()

        if not collection_name or not document:
            return jsonify({"error": "'collection_name' and 'data' fields are required"}), HttpStatusEnum.BAD_REQUEST.value

        if not self.is_valid_token(collection_name, token):
            return jsonify({"error": "Access denied. Invalid or missing token"}), HttpStatusEnum.UNAUTHORIZED.value

        db = get_database()
        collection = db[collection_name]

        # Get the next sequential ID
        last_doc = collection.find_one(sort=[("id", -1)])
        next_id = (last_doc["id"] + 1) if last_doc else 1  # Start with 1 if empty

        document["id"] = next_id  # Assign ID to document
        last_doc = collection.find_one(sort=[("id", -1)])
        next_id = (last_doc["id"] + 1) if last_doc else 1

        document["id"] = next_id
        collection.insert_one(document)

        return jsonify({
            "message": "Document inserted successfully",
            "id": next_id
        }), HttpStatusEnum.CREATED.value

    def delete_collection(self, data):
        """
        Deletes an entire collection and removes the associated token.
        """
        collection_name = data.get("collection_name")
        token = self.extract_bearer_token()

        if not collection_name:
            return jsonify({"error": "'collection_name' is required"}), HttpStatusEnum.BAD_REQUEST.value

        if not self.is_valid_token(collection_name, token):
            return jsonify({"error": "Access denied. Invalid or missing token"}), HttpStatusEnum.UNAUTHORIZED.value

        db = get_database()

        if collection_name not in db.list_collection_names():
            return jsonify({"error": "Collection not found"}), HttpStatusEnum.NOT_FOUND.value

        db.drop_collection(collection_name)  # Remove the collection
        db["_tokens"].delete_one({"collection": collection_name})  # Remove token
        db.drop_collection(collection_name)
        db["_tokens"].delete_one({"collection": collection_name})

        return jsonify({
            "message": f"Collection '{collection_name}' successfully deleted"
        }), HttpStatusEnum.OK.value

    def delete_data(self, data):
        """
        Deletes specific documents from a collection or all documents if no ID is provided.
        """
        collection_name = data.get("collection_name")
        document_id = data.get("id")  # Optional
        token = self.extract_bearer_token()

        if not collection_name:
            return jsonify({"error": "'collection_name' is required"}), HttpStatusEnum.BAD_REQUEST.value

        if not self.is_valid_token(collection_name, token):
            return jsonify({"error": "Access denied. Invalid or missing token"}), HttpStatusEnum.UNAUTHORIZED.value

        db = get_database()
        collection = db[collection_name]

        if document_id:
            result = collection.delete_one({"id": document_id})
            if result.deleted_count == 0:
                return jsonify({"error": f"No document found with id {document_id}"}), HttpStatusEnum.NOT_FOUND.value
            return jsonify({"message": f"Document with id {document_id} deleted successfully"}), HttpStatusEnum.OK.value
        else:
            collection.delete_many({})  # Deletes all documents in the collection
            return jsonify({"message": f"All documents in collection '{collection_name}' deleted successfully"}), HttpStatusEnum.OK.value

    def get(self, collection_name):
        """
        Retrieves all documents from a collection, validating the Bearer Token.
        """
        token = self.extract_bearer_token()

        if not self.is_valid_token(collection_name, token):
            return jsonify({"error": "Access denied. Invalid or missing token"}), HttpStatusEnum.UNAUTHORIZED.value

        db = get_database()
        collection = db[collection_name]
        documents = list(collection.find({}, {"_id": 0}))

        return jsonify({"documents": documents}), HttpStatusEnum.OK.value

    def extract_bearer_token(self):
        """
        Extracts the Bearer Token from the Authorization header.
        """
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header.split(" ")[1]  # Extract the token without 'Bearer' prefix
        return None

    def is_valid_token(self, collection_name, token):
        """
        Validates if the token matches the correct collection stored in MongoDB.
        """
        db = get_database()
        stored_token = db["_tokens"].find_one({"collection": collection_name}, {"_id": 0, "token": 1})

        return stored_token and stored_token["token"] == token

# Define routes
database_bp.add_url_rule('/api', view_func=DatabaseAPI.as_view('database_api'), methods=['POST'])
database_bp.add_url_rule('/api/<collection_name>', view_func=DatabaseAPI.as_view('database_collection_api'), methods=['GET'])
