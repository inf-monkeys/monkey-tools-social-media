from src.server.app import api
from flask_restx import Resource
from flask import request, jsonify
from src.database import ToolsCredentialEntity
from src.utils.credentials import encrypt, decrypt
import json

credentials_ns = api.namespace("credentials", description="Credentials")


def get_credential_data(credential_id):
    entity = ToolsCredentialEntity.get(
        ToolsCredentialEntity.credential_id == credential_id
    )
    encrypted_data = entity.data
    decrypted_data = decrypt(encrypted_data)
    return json.loads(decrypted_data)


@credentials_ns.route("/")
class CredentialsResource(Resource):
    @credentials_ns.doc("create_credential")
    def post(self):
        input_data = request.json
        context = input_data.get("context", {})
        credential_id = context.get("credentialId")
        creator_user_id = context.get("creatorUserId")
        team_id = context.get("teamId")

        display_name = input_data.get("displayName")
        data = input_data.get("data")
        encrypted_data = encrypt(json.dumps(data))
        type = input_data.get("type")

        ToolsCredentialEntity.create(
            credential_id=credential_id,
            team_id=team_id,
            creator_user_id=creator_user_id,
            display_name=display_name,
            data=encrypted_data,
            type=type,
        )
        return jsonify({"success": True})
