import os

from typing import Annotated
from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session
from starlette import status

from .exceptions import (RefreshTokenException, 
                        SignUpUserExist,
                        LoginUserNotExist, 
                        LoginWrongPassword)
from .service import service
from .models import (LoginWithEmailForm, 
                    Token, 
                    SignUpWithEmailForm, 
                    RefreshTokenBody)

from ..user.models import UserInDB, UserOut
from ..database import get_mysql_db
from ..response import ObjectResponse
from ..security import (bcrypt_context,
                        get_current_user,
                        decode_refresh_token, 
                        create_access_token, 
                        create_refresh_token)

router = APIRouter(
    prefix="",
    tags=['SignUp & Authorization']
)

@router.post("/auth/token", 
            response_model=Token,
            status_code=status.HTTP_202_ACCEPTED,
            name="login for jwt token")
async def login_for_access_token(form_data : Annotated[LoginWithEmailForm, 
                                Body(example={
                                        "email": os.getenv("TEST_USERNAME"),
                                        "password": os.getenv("TEST_PASSWORD")
                                    }
                                )], 
                                db:Annotated[Session, Depends(get_mysql_db)]):
    user = service.find_user_by_email(db, email = form_data.email)
    if not user:
        raise LoginUserNotExist()
    elif not bcrypt_context.verify(form_data.password, user.hashed_password):
        raise LoginWrongPassword()
    else:
    # return token
        token = create_access_token(user.email, user.id)
        refresh_token = create_refresh_token(user.id)
        return Token(access_token=token, 
                        token_type="bearer", 
                        refresh_token=refresh_token
                        )


@router.get("/info",
            response_model=ObjectResponse[UserOut])
async def get_user_info(user: UserOut = Depends(get_current_user)):
    return ObjectResponse(result=user)


@router.post("/auth/sign-up",
            response_model=ObjectResponse[UserOut],
            status_code=status.HTTP_201_CREATED,
            name="sign up")
async def create_user(db : Annotated[Session, Depends(get_mysql_db)], 
                      user_sign_up : Annotated[SignUpWithEmailForm, Body()]):
    user = service.find_user_by_email(db=db, email = user_sign_up.email)
    if user:
        raise SignUpUserExist()
    else:
        user_in_db = UserInDB(**user_sign_up.model_dump(), hashed_password = bcrypt_context.hash(user_sign_up.password))
        user =  service.signUpUser(db, user_in_db)
        return ObjectResponse(result=user)


@router.post("/auth/refresh", response_model=Token)
async def refresh_token(refresh_body: RefreshTokenBody, 
                        db:Annotated[Session, Depends(get_mysql_db)]):
    refresh_token = refresh_body.refresh_token
    payload = decode_refresh_token(refresh_token)
    if payload is None:
            raise RefreshTokenException()
    user_id: int = payload.get('id')
    user = service.find_user_by_id(db, user_id)
    
    new_access_token = create_access_token(user.email, user.id)
    new_refresh_token = create_refresh_token(user.id)
    
    return Token(access_token=new_access_token, 
                    token_type="bearer", 
                    refresh_token=new_refresh_token
                    )