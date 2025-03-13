import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from routes.v1.websocket import ChatRoomManager, getChatRoomsManager
from db.database import get_db
from models.messages import Message
from models.users import User
from models.conversation_people import ConversationPeople
from schemas.message_base import MessageCreate, MessageUpdate, MessageInDB, MessageBaseExtended
from crud.message import crud
from crud.conversation_people import crud as con_peo_repo
from typing import List


router = APIRouter(prefix="/messages", tags=["messages"])

@router.post("/", response_model=MessageBaseExtended)
async def send_message(message_create : MessageCreate, db: Session = Depends(get_db), room_manager:ChatRoomManager = Depends(getChatRoomsManager)):
    user_id = message_create.user_id
    conversation_id = message_create.conversation_id
    message_text = message_create.message
    cp_id = con_peo_repo.get_one(db, con_peo_repo._model.user_id == user_id, con_peo_repo._model.conversation_id == conversation_id).id
    message_in_db = MessageInDB(cp_id=cp_id, message=message_text)
    message = crud.create(db, message_in_db)
    message_extended = convert_to_message_extend(message.id, db)
    if room_manager:
        await room_manager.broadcast(conversation_id, message_extended)
    return message_extended

@router.put("/", response_model=MessageBaseExtended)
async def update_message(message_id: int , message_update: MessageUpdate, db: Session = Depends(get_db), room_manager:ChatRoomManager = Depends(getChatRoomsManager)):
    message = crud.get_one(db, crud._model.id == message_id)
    if not message:
        raise HTTPException(404, detail="Message not found")
    message = crud.update(db, message, message_update)
    message_extended = convert_to_message_extend(message.id, db)
    if room_manager:
        room_manager.broadcast(message_extended.conversation_id, message_extended)
    return message_extended

@router.delete("/{message_id}", response_model=MessageBaseExtended)
async def delete_message(message_id: int ,db: Session = Depends(get_db), room_manager:ChatRoomManager = Depends(getChatRoomsManager)):
    message = crud.get_one(db, crud._model.id == message_id)
    message.message = None
    db.commit()
    message_extended = convert_to_message_extend(message.id, db)
    if room_manager:
        room_manager.broadcast(message_extended.conversation_id, message_extended)
    return message_extended

def convert_to_message_extend(message_id : id, db:Session) -> MessageBaseExtended:
    return (db.query(
        Message.id,
        Message.cp_id, 
        Message.message, 
        Message.timestamp, 
        User.name, 
        User.avatar,
        ConversationPeople.conversation_id)
        .join(ConversationPeople, Message.cp_id == ConversationPeople.id)
        .join(User, User.id == ConversationPeople.user_id)
        .where(Message.id == message_id)
        .first()
    )
    