from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os


load_dotenv()
#key = Fernet.generate_key()
key = os.getenv("SECRET_KEY_FERNET")
print(key)
fernet = Fernet(key)

# Encrypt
def encrypt_message(original_str : str):
    encrypted_str = fernet.encrypt(original_str.encode())
    return encrypted_str

# Decrypt
def decrypt_message(encrypted_str : str):
    decrypted_str = fernet.decrypt(encrypted_str).decode()
    return decrypt_str
