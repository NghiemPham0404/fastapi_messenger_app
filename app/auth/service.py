from sqlalchemy.orm import Session

from .models import AuthProviderInDB

from ..user.models import UserInDB
from ..entities.user import User
from ..entities.auth_provider import AuthProvider

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

	
	def sign_up_user(self, db : Session, user_in_db : UserInDB):
		'''
		Sign up user
		'''
		user =  User(**user_in_db.model_dump(exclude_unset=True, exclude_none=True))
		db.add(user)
		db.commit()
		db.refresh(user)
		return user
	
	def find_user_by_provider_id(self, db:Session, provider_id : str):
		return (db.query(User)
		  .join(AuthProvider)
		  .where(User.id == AuthProvider.user_id)
		  .first()
		  )
	

	def create_auth_provider(self, db:Session, auth_in_db : AuthProviderInDB):
		'''
		Create Auth Provider for 3rd party authentication
		'''
		auth_entity = AuthProvider(**auth_in_db.model_dump(exclude_unset=True, exclude_none=True))
		db.add(auth_entity)
		db.commit()
		db.refresh(auth_entity)
		return auth_entity

	
        
service = AuthService()