from typing import List
from crud.base import CRUDRepository
from models.users import User
from sqlalchemy.orm import Session

class UserRepository(CRUDRepository):
    def find_user_by_email(self, db: Session, email: str) -> User:
        """
        Find a user by email
        """
        return self.get_one(db, self._model.email == email)


crud = UserRepository(model=User)