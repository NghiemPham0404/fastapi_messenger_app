import os
from motor.motor_asyncio import AsyncIOMotorClient  # ✅ async client
from dotenv import load_dotenv
import asyncio
from cryptography.fernet import Fernet



load_dotenv()
#key = Fernet.generate_key()
key = os.getenv("SECRET_KEY_FERNET")
# print(key)
fernet = Fernet(key)

# Encrypt
def encrypt_message(original_str : str) -> str:
    encrypted_bytes:str = fernet.encrypt(original_str.encode())
    return encrypted_bytes.decode()


async def test_connection():
    mongo_url = os.getenv("MONGO_DB_URL")
    client = AsyncIOMotorClient(mongo_url)
    db = client["chatting_app"]
    collection = db["messages"]
    # print(collection.find_one())

    cursor = collection.find({})  # Motor's async cursor

    async for doc in cursor:
        original = doc["content"]
        encrypted = encrypt_message(original)

        await collection.update_one(
            {"_id": doc["_id"]},
            {"$set": {"content": encrypted}}
        )

    print("All messages encrypted.")


asyncio.run(test_connection())

