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

# http_bearer for authentication
http_bearer = HTTPBearer()

# bcrypt_context to hash password
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated = 'auto')

ALGORITHM=os.getenv('ALGORITHM')
SECRET_KEY=os.getenv('SECRET_KEY')
ACCESS_TOKEN_EXPIRE_MINUTES=int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))
REFRESH_SECRET_KEY=os.getenv('REFRESH_SECRET_KEY')
REFRESH_TOKEN_EXPIRE_DAYS=int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS'))


# create access tokken
def create_access_token(email : str, user_id: int):
    to_encode = {'sub':email, 'id':user_id}
    expires = datetime.utcnow() +  timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expires})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# create refresh token
def create_refresh_token(user_id):
    to_encode = {'id':user_id}
    expire = datetime.utcnow() +  timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)

# dependency get current user
async def get_current_user(token_bearer: HTTPAuthorizationCredentials = Depends(http_bearer), db:Session= Depends(get_db)):
    try:
        print(token_bearer.credentials)
        token = token_bearer.credentials 
        payload = decode_access_token(token)
        email : str = payload.get('sub')
        user_id: int = payload.get('id')
        if email is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user')
        return crud.get_one(db, crud._model.email == email)
        
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not valitdate user')
    
# decode access token
def decode_access_token(jwt_bearer_token:str):
    try:
        payload = jwt.decode(jwt_bearer_token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
    
# decode refresh token 
def decode_refresh_token(refresh_token:str):
    try:
        payload = jwt.decode(refresh_token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def authenticate_user(email : str, password : str, db):
    user = crud.find_user_by_email(db=db, email=email)
    if not user:
        return False
    elif not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user
