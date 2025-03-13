from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from schemas.user_base import UserCreate, UserInDB, UserOut
from sqlalchemy.orm import Session
from starlette import status
from db.database import get_db
from fastapi.security import OAuth2PasswordRequestForm
from crud.user import crud
from security import bcrypt_context, authenticate_user, create_access_token

router = APIRouter(
    prefix="/auth",
    tags=['auth']
)

class Token(BaseModel):
    access_token: str
    token_type : str

db_dependency = Annotated[Session, Depends(get_db)]

@router.post("/sign-up",
            response_model=UserOut,
            status_code=status.HTTP_201_CREATED,
            name="sign up")
async def create_user(db : db_dependency, user_sign_up : UserCreate):
    user = crud.find_user_by_email(db=db, email = user_sign_up.email)
    if user:
        return HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f"The user with this {user_sign_up.email} already exists \in the system")
    else:
        user_in_db = UserInDB(**user_sign_up.model_dump(), hashed_password = bcrypt_context.hash(user_sign_up.password))
        return crud.create(db = db, obj_create=user_in_db)


class OAuth2PasswordRequestFormEmail(BaseModel):
    email: str
    password: str

@router.post("/token", 
            response_model=Token,
            status_code=status.HTTP_202_ACCEPTED,
            name="login for jwt token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestFormEmail, Depends()], db:db_dependency):
    user = authenticate_user(form_data.email, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorized fail, email or password is incorrect")
    token = create_access_token(user.email, user.id, timedelta(hours=1))
    return {'access_token':token, 'token_type':'bearer'}