from ..schemas.conversation_people_base import ConversationPeopleBase
from sqlalchemy.orm import Session
from ..models.conversation_people import ConversationPeople
from ..models.users import User
from ..crud.base import CRUDRepository


class ConversationPeopleRepo(CRUDRepository):
    pass

crud = ConversationPeopleRepo(ConversationPeople)
    
