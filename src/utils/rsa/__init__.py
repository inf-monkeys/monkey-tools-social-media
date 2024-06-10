import base64
from Crypto.Cipher import PKCS1_v1_5 as PKCS1_cipher
from src.config import private_key
import json
from Crypto.PublicKey import RSA


def decrypt_with_private_key(encrypted_message: str):
    chunks = encrypted_message.split("\n\n")
    str = ""
    for chunk in chunks:
        cipher = PKCS1_cipher.new(RSA.importKey(private_key))
        str += cipher.decrypt(base64.b64decode(chunk), "error").decode("utf-8")
    try:
        return json.loads(str)
    except:
        raise Exception("Invalid credential data, not a valid JSON string")
