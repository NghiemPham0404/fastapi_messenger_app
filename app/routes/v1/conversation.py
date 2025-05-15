import datetime
from sqlalchemy.orm import Session
from ...db.database import get_db
from fastapi import APIRouter,Depends, HTTPException, Path, status
from ...schemas.conversation_base import *
from ...schemas.user_base import UserOut
from ...schemas.message_base import MessageOut
from ...crud.conversation import crud
from ...crud.user import crud as user_repo
from ...crud.conversation_people import crud as con_peo_repo
from typing import Annotated, List
from ...encrypt_message import decrypt_message

router = APIRouter(prefix="/conversations", 
                   tags=["conversations"])


@router.get("/{conversation_id}", 
            response_model=ConversationOut)
def get_conversation(conversation_id : Annotated[int, Path(description="conversation id")], 
                     db:Annotated[Session, Depends(get_db)]):
    """
    Get a conversation by id
    """
    conversation = crud.get_one(db, crud._model.id == conversation_id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return conversation


@router.get("/", 
            response_model=List[ConversationOut])
def get_conversations(db:Annotated[Session, Depends(get_db)], 
                      skip : int=0, 
                      limit = 20):
    """
    Get conversations
    """
    return crud.get_many(db, skip=skip, limit= limit)


@router.post("/", 
             response_model=ConversationOut)
def create_conversation(conversation_create : ConversationCreate, 
                        db:Annotated[Session, Depends(get_db)]):
    """
    Create a conversation
    """
    conversation =  ConversationInDB(**conversation_create.model_dump()) 
    return crud.create(db, conversation)


@router.put("/{conversation_id}", 
            response_model=ConversationOut)
def update_conversation(id : Annotated[int, Path(description="conversation id")], 
                        conversation_update : ConversationUpdate, 
                        db:Annotated[Session, Depends(get_db)]):
    """"
    Update a conversation by id"
    """
    # check if conversation exists in db
    conversation = crud.get_one(db, crud._model.id == id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    # update conversation
    conversation_in_db =  ConversationInDB(**conversation_update.model_dump()) 
    return crud.update(db, conversation, conversation_in_db)


@router.delete("/{conversation_id}", response_model=ConversationBase)
def delete_conversation(conversation_id : int, 
                        db:Annotated[Session, Depends(get_db)]):
    """
    Delete a conversation by id
    """
    # check if conversation exists in db
    conversation = crud.get_one(db, crud._model.id == conversation_id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    # delete conversation
    return crud.delete(db, conversation)


@router.get("/{conversation_id}/people", 
            response_model=List[UserOut])
def get_people(conversation_id : Annotated[int, Path(description="conversation id")], 
               db:Annotated[Session, Depends(get_db)]):
    """
    Get people in a conversation by id
    """
    #check if conversation exists in db
    conversation = crud.get_one(db, crud._model.id == conversation_id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    # get conversation people in conversation
    conversation_people = con_peo_repo.get_many(db, con_peo_repo._model.conversation_id == conversation_id)
    people_ids = [conversation_person.user_id for conversation_person in conversation_people]
    # get people in db
    people = user_repo.get_many(db, user_repo._model.id.in_(people_ids))
    return people


@router.get("/{conversation_id}/messages", 
            response_model=List[MessageOut])
async def get_conversation_messages(conversation_id : Annotated[int, Path(description="conversation id")],
                                    skip: int = 0, 
                                    limit: int = 50, 
                                    start : str = "1970-01-01 00:00:00", 
                                    end : str = None, 
                                    db:Session = Depends(get_db)):
    """
    Get messages in a conversation by id
    """
    end = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %z") if end is None else end
    # check if conversation exists in db
    conversation = crud.get_one(db, crud._model.id == conversation_id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    # get messages in conversation
    messages = crud.get_conversation_messages(conversation_id, skip, limit, start, end, db)
    messages.sort(key= lambda msg : msg.timestamp)
    decrypt_messages = []
    for message in messages :
        message_out = MessageOut.model_validate(message);    
        message_out.content=decrypt_message(message.content)
        decrypt_messages.append(message_out)
    return decrypt_messages
