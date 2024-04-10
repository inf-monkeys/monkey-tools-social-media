from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
from src.config import config_data

encrypt_config = config_data.get("encrypt")
iv = encrypt_config.get("iv")

if not iv:
    raise Exception("Startup Fail: encrypt.iv not configured.")

key = encrypt_config.get("key")

if not key:
    raise Exception("Startup Fail: encrypt.key not configured.")

iv = iv.encode()
key = key.encode()

def encrypt(message):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(message.encode(), AES.block_size))
    return base64.b64encode(ciphertext).decode()


def decrypt(ciphertext):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_message = cipher.decrypt(base64.b64decode(ciphertext))
    return unpad(decrypted_message, AES.block_size).decode()

test_message = 'Hello World'
try:
    encrypted = encrypt(test_message)
    decrypted = decrypt(encrypted)
except Exception as e:
    raise Exception("Startup Fail: unable to encrypt and decrypt using key and iv provided.")

if decrypted != test_message:
    raise Exception("Startup Fail: you may configured the wrong key and iv")
