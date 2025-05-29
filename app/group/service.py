from typing import List

from app.response import ListResponse
from .models import *
from sqlalchemy.orm import Session
from ..base_crud import CRUDRepository
from ..entities.group import Group
from .models import GroupOut


class ConversationRepository(CRUDRepository):
   
   def get_groups(self, db : Session, keyword : str, page : int = 1, limit : int = 20):
      groups_page = crud.get_many(db, crud._model.subject.like(f"%{keyword}%"), page=page, limit=limit)
      return groups_page


crud = ConversationRepository(model=Group)