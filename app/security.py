from datetime import timedelta, datetime
from fastapi import  Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from passlib.context import CryptContext
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError
import os

from app.entities.user import User
from .database import get_mysql_db

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
    expire = datetime.utcnow() +  timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return create_token(to_encode, expire, SECRET_KEY)

# create refresh token
def create_refresh_token(user_id):
    to_encode = {'id':user_id}
    expire = datetime.utcnow() +  timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    return create_token(to_encode, expire, REFRESH_SECRET_KEY)

def create_token(to_encode, expire, key):
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, key, algorithm=ALGORITHM)

# dependency get current user
async def get_current_user(token_bearer: HTTPAuthorizationCredentials = Depends(http_bearer), 
                           db:Session= Depends(get_mysql_db)):
    try:
        print(token_bearer.credentials)
        token = token_bearer.credentials 
        payload = decode_access_token(token)
        email : str = payload.get('sub')
        user_id: int = payload.get('id')
        if email is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user')
        return db.query(User).filter(User.email == email).first()
        
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

