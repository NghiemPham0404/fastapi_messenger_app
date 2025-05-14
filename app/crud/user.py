from typing import List
from sqlalchemy.orm import Session
from .base import CRUDRepository
from ..models.users import User
from ..models.conversations import Conversation
from ..models.conversation_people import ConversationPeople

class UserRepository(CRUDRepository):
    def find_user_by_email(self, db: Session, email: str) -> User:
        """
        Find a user by email
        """
        return self.get_one(db, self._model.email == email)
    
    def get_user_conversations(self, db:Session, user_id : int):
        return (db.query(Conversation)
                .join(ConversationPeople, ConversationPeople.conversation_id == Conversation.id)
                .join(User, User.id == ConversationPeople.user_id)
                .filter(User.id == user_id)
                .all()
                )
        


crud = UserRepository(model=User)