from dotenv import load_dotenv
from cryptography.fernet import Fernet
import os



load_dotenv()
#key = Fernet.generate_key()
key = os.getenv("SECRET_KEY_FERNET")
# print(key)
fernet = Fernet(key)

# Decrypt
def decrypt_message(encrypted_str : str) -> str:
    # print(encrypted_str)
    encrypted_bytes = encrypted_str.encode()
    decrypted_str = fernet.decrypt(encrypted_bytes).decode()
    return decrypted_str

print(decrypt_message("gAAAAABoG3lV8RsSPxqPrHjYPCQoD69cKY6Sy0PoL3PyTuFqiimO1fGf9R_zuL6ysPEJupSYgDWyIhU2VOr8COOrzMeKTmz8Aw=="))