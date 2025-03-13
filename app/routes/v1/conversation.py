import datetime
from sqlalchemy.orm import Session
from db.database import get_db
from fastapi import APIRouter,Depends, HTTPException, status
from schemas.conversation_base import *
from schemas.user_base import UserOut
from schemas.message_base import MessageBaseExtended
from crud.conversation import crud
from crud.user import crud as user_repo
from crud.conversation_people import crud as con_peo_repo
from typing import List

router = APIRouter(prefix="/conversations", tags=["conversations"])

@router.get("/{conversation_id}", response_model=ConversationOut)
def get_conversation(conversation_id : int, db:Session = Depends(get_db)):
    conversation = crud.get_one(db, crud._model.id == conversation_id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return conversation

@router.get("/")
def get_conversations(skip : int=0, limit = 20, db:Session = Depends(get_db)):
    return crud.get_many(db, skip=skip, limit= limit)

@router.post("/", response_model=ConversationOut)
def create_conversation(conversation_create : ConversationCreate, db:Session = Depends(get_db)):
    conversation =  ConversationInDB(**conversation_create.model_dump()) 
    return crud.create(db, conversation)

@router.put("/{conversation_id}", response_model=ConversationOut)
def update_conversation(id : int, conversation_update : ConversationUpdate, db:Session = Depends(get_db)):
    conversation = crud.get_one(db, crud._model.id == id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    conversation_in_db =  ConversationInDB(**conversation_update.model_dump()) 
    return crud.update(db, conversation, conversation_in_db)

@router.delete("/{conversation_id}", response_model=ConversationBase)
def delete_conversation(conversation_id : int, db:Session = Depends(get_db)):
    conversation = crud.get_one(db, crud._model.id == conversation_id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return crud.delete(db, conversation)

@router.get("/{conversation_id}/people", response_model=List[UserOut])
def get_people(conversation_id: int, db:Session = Depends(get_db)):
    conversation = crud.get_one(db, crud._model.id == conversation_id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    conversation_people = con_peo_repo.get_many(db, con_peo_repo._model.conversation_id == conversation_id)
    people_ids = [conversation_person.user_id for conversation_person in conversation_people]
    people = user_repo.get_many(db, user_repo._model.id.in_(people_ids))
    return people

@router.get("/{conversation_id}/messages", response_model=List[MessageBaseExtended])
async def get_conversation_messages(conversation_id: int,
                                    skip: int = 0, 
                                    limit: int = 50, 
                                    start : str = "1970-01-01 00:00:00", 
                                    end : str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %z"), 
                                    db:Session = Depends(get_db)):
    conversation = crud.get_one(db, crud._model.id == conversation_id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return crud.get_conversation_messages(conversation_id, skip, limit, start, end, db)