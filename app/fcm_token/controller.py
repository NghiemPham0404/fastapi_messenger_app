from typing import Annotated
from fastapi import APIRouter, Body, Depends, Path
from sqlalchemy.orm import Session

from app.entities.fcm_token import FCMToken
from app.exceptions import NotAuthorized

from ..response import MessageResponse, ObjectResponse

from ..database import get_mysql_db
from ..security import get_current_user
from ..user.models import UserOut

from .models import FCMTokenIn, FCMOut, FCMInDB

from .service import crud

router = APIRouter(prefix="/fcm_tokens", tags=["fcm_tokens"])

@router.post("", response_model=ObjectResponse[FCMOut])
def create_fcm_token(fcm_token_in : Annotated[FCMTokenIn, Body()], 
                     db : Annotated[Session, Depends(get_mysql_db)],
                     user : Annotated[UserOut, Depends(get_current_user)]
                     ):
    if user.id != fcm_token_in.user_id:
        raise NotAuthorized()
    fcm_token_in_db = FCMInDB(**fcm_token_in.model_dump())
    fcm = crud.create(db, fcm_token_in_db)
    return ObjectResponse(result = FCMOut.model_validate(fcm))

@router.delete("/{id}", response_model=MessageResponse)
def delete_fcm_token(id : Annotated[int, Path()], db : Annotated[Session, Depends(get_mysql_db)],
                     user : Annotated[UserOut, Depends(get_current_user)]):
    fcm_token = crud.get_one(db, crud._model.id == id)
    if fcm_token.user_id != user.id:
        raise NotAuthorized()
    crud.delete(db, fcm_token)
    return MessageResponse(message="Delete fcm token successfully")