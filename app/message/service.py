import datetime
from bson import ObjectId
from sqlalchemy.orm import Session
from .models import MessageOut, MessageUpdate, MessageSender
from ..database import mongodb
from ..entities import *
from ..encrypt_message import encrypt_message, decrypt_message

message_collection = mongodb['messages']

async def create(message_create : dict):
    if message_create.content:
        message_create.content =  encrypt_message(message_create.content)
    message = message_create.model_dump(exclude_none=True, exclude_unset=True)
    message["timestamp"] = message.get("timestamp") or datetime.datetime.utcnow()
    result = await message_collection.insert_one(message)
    return {**message, "id": str(result.inserted_id)}

async def read_many_direct(user_id_1: int, user_id_2: int, page: int = 0, limit: int = 25):
    conditions = {
        "$or": [
            {"user_id": user_id_1, "receiver_id": user_id_2},
            {"user_id": user_id_2, "receiver_id": user_id_1}
        ]
    }
    skip = page * limit
    cursor = message_collection.find(conditions).sort("timestamp", -1).skip(skip).limit(limit)
    results = []
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        doc['content'] = decrypt_message(str(doc["content"]))
        results.append(doc)
    return results


async def read_many_group(group_id: int, page: int = 0, limit: int = 25):
    conditions = {"group_id": group_id}
    skip = page * limit
    cursor = message_collection.find(conditions).sort("timestamp", -1).skip(skip).limit(limit)
    results = []
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        doc['content'] = decrypt_message(str(doc["content"]))
        results.append(doc)
    return results

async def read_one(id: str):
    message = await message_collection.find_one({'_id': ObjectId(id)})
    if message:
        message["id"] = str(message["_id"])
    return message


async def update(id: str, message_update: MessageUpdate):
    message_update.content =  encrypt_message(message_update.content)
    update_data = message_update.model_dump(exclude_none=True, exclude_defaults=True)
    if not update_data:
        return None
    message = await message_collection.find_one_and_update(
        {'_id': ObjectId(id)},
        {'$set': update_data},
        return_document=True
    )
    if message:
        message["id"] = str(message["_id"])
    return message


async def delete(id: str):
    result = await message_collection.delete_one({"_id": ObjectId(id)})
    return result.deleted_count == 1

async def convert_to_message_extend(message: dict, db: Session):
    if message.get("content"):
        message["content"] = decrypt_message(message["content"])

    message_extended_data = (
        db.query(User.id, User.name, User.avatar)
        .where(User.id == message["user_id"])
        .first()
    )

    if message_extended_data:
        message["sender"] = MessageSender.model_validate(message_extended_data)

    return MessageOut(**message)