from math import ceil
from sqlalchemy.orm import Session
from motor.motor_asyncio import AsyncIOMotorClient

from .models import ConversationOut, Sender

from ..entities.user import User
from ..entities.group import Group
from ..pagination import Page
from ..response import ListResponse
from ..entities.group_member import GroupMember
from ..encrypt_message import decrypt_message
from ..message.service import convert_to_message_extend

class ConversationRepo:

    async def get_latest_direct_messages(self, user_id: int, mongo_db : AsyncIOMotorClient):
        message_collection = mongo_db['messages']
        query = {
            "$and": [
                {
                    "$or": [
                        {"user_id": user_id},
                        {"receiver_id": user_id}
                    ]
                },
                {"receiver_id": {"$exists": True}}  # Ensure receiver_id exists
            ]
        }

        # Sort by latest
        cursor = message_collection.find(query).sort("timestamp", -1)
        results = {}
        async for doc in cursor:
            uid1 = doc["user_id"]
            uid2 = doc["receiver_id"]

            # Create a unique key for conversation
            pair_key = tuple(sorted([uid1, uid2]))

            if pair_key not in results:
                doc["_id"] = str(doc["_id"])
                results[pair_key] = doc

        return list(results.values())


    async def get_latest_group_messages(self, user_group_ids: list[int], mongo_db : AsyncIOMotorClient):
        message_collection = mongo_db['messages']
        if not user_group_ids:
            return []

        query = {"group_id": {"$in": user_group_ids}}
        cursor = message_collection.find(query).sort("timestamp", -1)

        results = {}
        async for doc in cursor:
            group_id = doc["group_id"]
            if group_id not in results:
                doc["_id"] = str(doc["_id"])
                results[group_id] = doc

        return list(results.values())
    
    async def convert_to_conversation_out(self, message: dict, user_id, db: Session):
        if message.get("content"):
            message["content"] = decrypt_message(message["content"])

        message_sender_data = (
            db.query(User.id, User.name, User.avatar)
            .where(User.id == message["user_id"])
            .first()
        )

        if message_sender_data:
            message["sender"] = Sender.model_validate(message_sender_data)

        # if message is a group messsage
        if message.get("group_id"):
            message_group_data = (
                db.query(Group.id, Group.subject, Group.avatar)
                .where(Group.id == message["group_id"])
                .first()
            )

            message['display_name'] = message_group_data.subject
            message['display_avatar'] = message_group_data.avatar

        # if message is a direct conversation message
        if message.get("receiver_id"):
            display_user_id =  message.get("user_id") if message.get("receiver_id") == user_id else message.get("receiver_id")
            message_receiver_data = (
                db.query(User.id, User.name, User.avatar)
                    .where(User.id == display_user_id)
                    .first()
            )

            message['display_name'] = message_receiver_data.name
            message['display_avatar'] = message_receiver_data.avatar

        return ConversationOut.model_validate(message)

        

    async def get_recent_conversations(self, user_id: int, mysql_db: Session, mongo_db :  AsyncIOMotorClient):
        """
        Example data response:
        {
            "_id": "...",
            "user_id": 5,
            "receiver_id": 9,
            "text": "Hey there!",
            "timestamp": "2025-05-24T10:00:00",
        }
        """

        user_group_ids_query = (
            mysql_db.query(GroupMember)
                .where(GroupMember.user_id == user_id)
        )
        user_group_ids = [x.group_id for x in user_group_ids_query]

        direct = await self.get_latest_direct_messages(user_id, mongo_db=mongo_db)
        groups = await self.get_latest_group_messages(user_group_ids, mongo_db=mongo_db)

        all_recent = direct + groups
        all_recent.sort(key=lambda x: x["timestamp"], reverse=True)
        for doc in all_recent:
            doc["id"] = str(doc.pop("_id"))
            doc = await self.convert_to_conversation_out(doc, user_id, mysql_db)
        return all_recent
    
    
    async def get_group_messages(self, 
                                mongo_db :  AsyncIOMotorClient, 
                                mysql_db : Session, 
                                group_id : int, 
                                page : int = 1, 
                                limit : int = 20):
        message_collection = mongo_db['messages']
        query = {
                    "group_id": group_id
                }
                
        total_results = await (message_collection.count_documents(query))
        cursor = (message_collection
                  .find(query)
                  .sort("timestamp", -1)
                  .skip((page-1)*limit)
                  .limit(limit)
                  )
        total_pages = ceil(total_results / limit) if limit else 1
        results = []
        
        async for doc in cursor:
            doc["id"] = str(doc.pop("_id"))
            doc = await convert_to_message_extend(doc, mysql_db)
            results.append(doc)
        
        return Page(page = page, 
                    items = results, 
                    total_pages=total_pages, 
                    total_results=total_results)
    
    async def get_direct_messages(self,
                                mysql_db : Session,
                                mongo_db :  AsyncIOMotorClient,  
                                user_id : int, 
                                other_user_id : int, 
                                page = 1,
                                limit = 20):
        message_collection = mongo_db['messages']
        query = {"$or" : [
                    {"user_id": user_id, "receiver_id": other_user_id},
                    {"user_id": other_user_id, "receiver_id": user_id},
                    ]
                }
        total_results = await (message_collection.count_documents(query))
        cursor = (message_collection
                  .find(query)
                  .sort("timestamp", -1)
                  .skip((page-1)*limit)
                  .limit(limit))
        
        results = []
        total_pages = ceil(total_results / limit) if limit else 1
        
        async for doc in cursor:
            doc["id"] = str(doc.pop("_id"))
            doc = await convert_to_message_extend(doc, mysql_db)
            results.append(doc)
        
        return Page(page=page, 
                    items=results, 
                    total_pages=total_pages, 
                    total_results=total_results)


conversation_repo = ConversationRepo()
