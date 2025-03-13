from typing import List
from schemas.conversation_base import *
from models.conversations import Conversations
from sqlalchemy.orm import Session
from crud.base import CRUDRepository
from models.users import User
from models.messages import Message
from models.conversations import Conversations
from models.conversation_people import ConversationPeople

class ConversationRepository(CRUDRepository):
    def get_conversation_messages(self,
                                    conversation_id: int,
                                    skip: int, 
                                    limit: int, 
                                    start : str, 
                                    end : str, 
                                    db:Session) -> List[MessageBaseExtended]:

        return (
        db.query(Message.cp_id, 
        Message.message, 
        Message.timestamp, 
        User.name, 
        User.avatar)
        .join(ConversationPeople, Message.cp_id == ConversationPeople.id)
        .join(User, User.id == ConversationPeople.user_id)
        .filter(
            ConversationPeople.conversation_id == conversation_id,
            Message.timestamp >= start,
            Message.timestamp <= end
        )
        .order_by(Message.timestamp.desc())
        .offset(skip)
        .limit(limit)
        .all()
        )

crud = ConversationRepository(model=Conversations)