from sqlalchemy.orm import Session

from ..user.models import UserInDB
from ..entities.user import User

class AuthService:


	def find_user_by_email(self, db: Session, email: str) -> User:
		"""
		Find a user by email
		"""
		return db.query(User).filter(User.email == email).first()

	def find_user_by_id(self, db: Session, user_id : int) -> User:
		"""
		Find a user by email
		"""
		return db.query(User).filter(User.id == user_id).first()		

	def signUpUser(self, db : Session, user_in_db : UserInDB):
		user =  User(**user_in_db.model_dump(exclude_unset=True, exclude_none=True))
		db.add(user)
		db.commit()
		db.refresh(user)
		return user
	
        
service = AuthService()