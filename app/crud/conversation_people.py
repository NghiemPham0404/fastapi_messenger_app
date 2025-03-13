from schemas.conversation_people_base import ConversationPeopleBase
from models.conversation_people import ConversationPeople
from models.users import User
from sqlalchemy.orm import Session
from crud.base import CRUDRepository

class ConversationPeopleRepo(CRUDRepository):
    pass

crud = ConversationPeopleRepo(ConversationPeople)
    
