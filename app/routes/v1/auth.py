from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Form
from pydantic import BaseModel
from schemas.user_base import UserCreate, UserInDB, UserOut
from sqlalchemy.orm import Session
from starlette import status
from db.database import get_db
from fastapi.security import OAuth2PasswordRequestForm
from crud.user import crud
from security import bcrypt_context, authenticate_user, create_access_token, create_refresh_token, decode_refresh_token

router = APIRouter(
    prefix="/auth",
    tags=['auth']
)


class Token(BaseModel):
    """
    Token model for JWT
    """
    access_token: str
    token_type : str
    refresh_token : str


class LoginWithEmailForm(BaseModel):
    """
    Login Form with email and password
    """
    email: str
    password: str


@router.post("/sign-up",
            response_model=UserOut,
            status_code=status.HTTP_201_CREATED,
            name="sign up")
async def create_user(db : Annotated[Session, Depends(get_db)], 
                      user_sign_up : Annotated[LoginWithEmailForm, Depends()]):
    # check if user already exists
    user = crud.find_user_by_email(db=db, email = user_sign_up.email)
    if user:
        return HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"The user with this {user_sign_up.email} already exists \in the system")
    else:
        # create user
        user_in_db = UserInDB(**user_sign_up.model_dump(), hashed_password = bcrypt_context.hash(user_sign_up.password))
        return crud.create(db = db, obj_create=user_in_db)

@router.post("/token", 
            response_model=Token,
            status_code=status.HTTP_202_ACCEPTED,
            name="login for jwt token")
async def login_for_access_token(form_data : Annotated[LoginWithEmailForm, Depends()], 
                                 db:Annotated[Session, Depends(get_db)]):
    # authenticate user
    user = authenticate_user(form_data.email, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorized fail, email or password is incorrect")
    # return token
    token = create_access_token(user.email, user.id)
    refresh_token = create_refresh_token(user.id)
    return {'access_token':token, 'token_type':'bearer', 'refresh_token':refresh_token}


@router.post("/refresh")
async def refresh_token(refresh_token: str, db:Annotated[Session, Depends(get_db)]):
    payload = decode_refresh_token(refresh_token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token or expired token")
    user_id: int = payload.get('id')
    user = crud.get_one(db, crud._model.id == user_id)
    
    new_access_token = create_access_token(user.email, user.id)
    return {"access_token": new_access_token, "token_type": "bearer"}