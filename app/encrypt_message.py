from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os


load_dotenv()
#key = Fernet.generate_key()
key = os.getenv("SECRET_KEY_FERNET")
# print(key)
fernet = Fernet(key)

# Encrypt
def encrypt_message(original_str : str) -> str:
    encrypted_bytes:str = fernet.encrypt(original_str.encode())
    return encrypted_bytes.decode()

# Decrypt
def decrypt_message(encrypted_str : str) -> str:
    # print(encrypted_str)
    encrypted_bytes = encrypted_str.encode()
    decrypted_str = fernet.decrypt(encrypted_bytes).decode()
    return decrypted_str