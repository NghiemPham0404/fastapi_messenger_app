# import datetime
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from ...routes.v1.websocket import ChatRoomManager, getChatRoomsManager
from ...db.database import get_db
from ...models.messages import Message
from ...models.users import User
from ...models.conversation_people import ConversationPeople
from ...schemas.message_base import MessageCreate, MessageUpdate, MessageInDB, MessageOut
from ...crud.message import crud
from ...crud.conversation_people import crud as con_peo_repo
from typing import Annotated, List
from ...encrypt_message import encrypt_message, decrypt_message


router = APIRouter(prefix="/messages", tags=["messages"])

@router.post("/", 
             response_model=MessageOut)
async def send_message(message_create : MessageCreate, 
                       db: Annotated[Session, Depends(get_db)], 
                       room_manager: Annotated[ChatRoomManager ,Depends(getChatRoomsManager)]):
    """
    Send a message to a conversation
    """
    # Extract user_id and conversation_id and message from the request body
    user_id = message_create.user_id
    conversation_id = message_create.conversation_id
    message_text = message_create.content
    # Check if the conversation exists in the database
    cp_id = con_peo_repo.get_one(db, con_peo_repo._model.user_id == user_id, con_peo_repo._model.conversation_id == conversation_id).id
    if not cp_id:
        raise HTTPException(status_code=404, detail="Conversation people not found")
    message_in_db = MessageInDB(cp_id=cp_id, content=encrypt_message(message_text))
    message = crud.create(db, message_in_db)
    # extend message to include user name and avatar
    message_extended = convert_to_message_extend(message.id, db)
    # broadcast message to all users in the conversation
    if room_manager:
        await room_manager.broadcast(conversation_id, message_extended)
    return message_extended

@router.put("/", response_model=MessageOut)
async def update_message(message_id: Annotated[int, Path(description="message id")],
                         message_update: MessageUpdate, 
                         db: Annotated[Session, Depends(get_db)], 
                         room_manager: Annotated[ChatRoomManager , Depends(getChatRoomsManager)]):
    """
    Update a message by id
    """
    # check if message exists in db
    message = crud.get_one(db, crud._model.id == message_id)
    if not message:
        raise HTTPException(404, detail="Message not found")
    # update message
    message_update = MessageUpdate(**message_update.model_dump(), content=encrypt_message(message_update.content))
    message = crud.update(db, message, message_update)
    # extend message to include user name and avatar
    message_extended = convert_to_message_extend(message.id, db)
    # broadcast message to all users in the conversation
    if room_manager:
        room_manager.broadcast(message_extended.conversation_id, message_extended)
    return message_extended

@router.delete("/{message_id}", 
               response_model=MessageOut)
async def delete_message(message_id: Annotated[int, Path(description="message id")],
                         db: Annotated[Session, Depends(get_db)], 
                         room_manager: Annotated[ChatRoomManager , Depends(getChatRoomsManager)]):
    """
    Delete a message by id
    """
    # check if message exists in db
    message = crud.get_one(db, crud._model.id == message_id)
    if not message:
        raise HTTPException(404, detail="Message not found")
    # delete message
    message.message = None
    db.commit()
    # extend message to include user name and avatar
    message_extended = convert_to_message_extend(message.id, db)
    # broadcast message to all users in the conversation
    if room_manager:
        room_manager.broadcast(message_extended.conversation_id, message_extended)
    return message_extended

def convert_to_message_extend(message_id : id, db:Session) -> MessageOut:
    message_in_db =  (db.query(
        Message.id,
        Message.cp_id,
        Message.content, 
        Message.timestamp,

        User.id.label('user_id'),
        User.name, 
        User.avatar,
        ConversationPeople.conversation_id)
        .join(ConversationPeople, Message.cp_id == ConversationPeople.id)
        .join(User, User.id == ConversationPeople.user_id)
        .where(Message.id == message_id)
        .first()
    )
    message_out= MessageOut.model_validate(message_in_db)
    message_out.content = decrypt_message(message_out.content)
    return message_out
    