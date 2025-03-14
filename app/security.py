from datetime import timedelta, datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from schemas.user_base import UserCreate, UserInDB, UserOut
from sqlalchemy.orm import Session
from starlette import status
from db.database import SessionLocal, get_db
from models import users
from passlib.context import CryptContext
from fastapi.security import HTTPAuthorizationCredentials, OAuth2PasswordRequestForm, OAuth2PasswordBearer, HTTPBearer
from jose import jwt, JWTError
from crud.user import crud
import os
from dotenv import load_dotenv

http_bearer = HTTPBearer()
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated = 'auto')

def create_access_token(email : str, user_id: int, expires_delta: timedelta):
    encode = {'sub':email, 'id':user_id}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, os.getenv('SECRET_KEY'), algorithm=os.getenv('ALGORITHM'))

async def get_current_user(token_bearer: HTTPAuthorizationCredentials = Depends(http_bearer), db:Session= Depends(get_db)):
    try:
        print(token_bearer.credentials)
        token = token_bearer.credentials 
        payload = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=os.getenv('ALGORITHM'))
        email : str = payload.get('sub')
        user_id: int = payload.get('id')
        if email is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user 1')
        return crud.get_one(db, crud._model.email == email)
        
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not valitdate user 2')
    

def authenticate_user(email : str, password : str, db):
    user = crud.find_user_by_email(db=db, email=email)
    if not user:
        return False
    elif not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user
