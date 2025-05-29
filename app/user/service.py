from math import ceil
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.group.models import GroupOut
from app.response import ListResponse
from .models import UserOut
from ..base_crud import CRUDRepository
from ..entities.user import User
from ..entities.group import Group
from ..entities.group_member import GroupMember


class UserRepository(CRUDRepository):

    def get_users(self, db: Session, keyword, page : int = 1, limit : int = 20):
        users_page = crud.get_many(db, or_(
                                crud._model.name.like(f"%{keyword}%"),
                                crud._model.email.like(f"%{keyword}%"),
                                ),
                                page=page,
                                limit=limit
                            )
        return users_page

    def find_user_by_email(self, db: Session, email: str):
        """
        Find a user by email
        """
        return self.get_one(db, self._model.email == email)
    
    def get_user_groups(self, db:Session, user_id : int, page, limit : int = 20):
        query =  (db.query(Group)
                .join(GroupMember, Group.id == GroupMember.group_id)
                .join(User, GroupMember.user_id ==  User.id)
                .filter(User.id == user_id)
                )
        groups_page = crud.pagination_query(query, page, limit)
        return groups_page
            


crud = UserRepository(model=User)