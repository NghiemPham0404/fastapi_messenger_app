# import datetime
from datetime import timedelta, timezone
from fastapi import APIRouter, Body, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session
from typing import Annotated

from .models import *
from .service import *
from .exceptions import (MessageNotFound, 
                         SendMessageFail, 
                         SendMessageForbiden, 
                         UpdateMessageFail, 
                         DeleteMessageTimeout, 
                         EditMessageTimeout,)

from ..websocket import ChatRoomManager, getChatRoomsManager
from ..database import get_mysql_db
from ..group_member.service import crud as group_member_repo
from ..group_member.exceptions import NotGroupMember
from ..user.service import crud as user_crud
from ..user.exceptions import UserNotFound
from ..group.exceptions import GroupNotFound
from ..group.service import crud as group_crud
from ..security import get_current_user
from ..exceptions import NotAuthorized
from ..response import MessageResponse, ObjectResponse


router = APIRouter(tags=["Messages"])


@router.post("/messsages", 
             response_model=ObjectResponse[MessageOut])
async def send_direct_message(
                              message_create : Annotated[
                                DirectMessageCreate, 
                                Body(openapi_examples={
                                    "regular text":{
                                       "summary": "Simple message",
                                       "value" : {
                                            "user_id": 1,
                                            "receiver_id": 2,
                                            "content": "Hello Bro, are you doing oke ?",
                                            "timestamp": datetime.datetime.now(timezone.utc)
                                        }
                                    },
                                    "include text and images":{
                                        "summary": "Text with image",
                                        "value" :{
                                            "user_id": 2,
                                            "receiver_id": 1,
                                            "content": "Hi bro, check it out",
                                            "images":["hhttps://picsum.photos/300/400"],
                                            "timestamp": datetime.datetime.now(timezone.utc)
                                        }
                                    },
                                    "file": {
                                        "summary": "Send file",
                                        "value": {
                                            "user_id": 3,
                                            "receiver_id": 2,
                                            "content": "Here is the docs",
                                            "file": "file.pdf",
                                            "timestamp": datetime.datetime.now(timezone.utc)
                                        }
                                    }
                                })
                            ], 
                       db: Annotated[Session, Depends(get_mysql_db)], 
                       room_manager: Annotated[ChatRoomManager ,Depends(getChatRoomsManager)],
                       user = Depends(get_current_user)):
    """
    Send a message to a person
    """
    if message_create.user_id != user.id:
        raise NotAuthorized()

    receiver_id = message_create.receiver_id

    if receiver_id:
        receiver = user_crud.get_one(db, user_crud._model.id == receiver_id)
        if not receiver:
            raise UserNotFound()

    message = await create(message_create)
    if not message:
        raise SendMessageFail()
        
    # extend message to include user name and avatar
    message_extended = await convert_to_message_extend(message, db)
    # broadcast message to all users in the conversation
    if room_manager:
        await room_manager.broadcast(receiver_id, message_extended)
    return ObjectResponse(result = message_extended)


@router.post("/groups/{group_id}/messsages", 
             response_model=ObjectResponse[MessageOut])
async def send_group_message(group_id : Annotated[int, Path()],
                              message_create : Annotated[
                                GroupMessageCreate, 
                                Body(openapi_examples={
                                    "regular text":{
                                        "summary": "Simple message",
                                        "value" : {
                                            "user_id": 1,
                                            "group_id": 2,
                                            "content": "Hello everyone, im new here",
                                            "timestamp": datetime.datetime.now(timezone.utc)
                                        }
                                    },
                                    "include text and images":{
                                        "summary": "Text with image",
                                        "value" :{
                                            "user_id": 2,
                                            "group_id": 3,
                                            "content": "Guys, check it out",
                                            "images":["https://picsum.photos/300/400"],
                                            "timestamp": datetime.datetime.now(timezone.utc)
                                        }
                                    },
                                    "file":{
                                        "summary": "Send file",
                                        "value": {
                                            "user_id": 3,
                                            "group_id": 5,
                                            "content": "This is our group princibles",
                                            "file":"file.pdf",
                                            "timestamp": datetime.datetime.now(timezone.utc)
                                        }
                                    }
                                })
                            ], 
                       db: Annotated[Session, Depends(get_mysql_db)], 
                       room_manager: Annotated[ChatRoomManager ,Depends(getChatRoomsManager)],
                       user = Depends(get_current_user)):
    """
    Send a message to a group
    """

    # check if user have the right to send message
    if user.id != message_create.user_id:
        raise NotAuthorized()

    # check if message detail is valid
    # is group exist ?
    group_id = message_create.group_id
    if group_id:  
        group = group_crud.get_one(db, group_crud._model.id == group_id)
        if not group:
            raise GroupNotFound()
        if group.is_member_mute:
             raise SendMessageForbiden()

        # is valid group member ?
        group_member = group_member_repo.get_one(db, group_member_repo._model.user_id == user.id, 
                                                 group_member_repo._model.group_id == group_id)
        if not group_member:
            raise NotGroupMember()

    # create message (send)
    message = await create(message_create)
    if not message:
        raise SendMessageFail()
        
    # extend message to include user name and avatar
    message_extended = await convert_to_message_extend(message, db)
    # broadcast message to all users in the conversation
    if room_manager:
        await room_manager.broadcast_group(group_id, message_extended)
    return ObjectResponse(result = message_extended)


@router.put("/messages/{message_id}", 
            response_model=ObjectResponse[MessageOut])
async def update_message(message_id: Annotated[str, Path(description="message id")],
                        message_update: MessageUpdate, 
                        db: Annotated[Session, Depends(get_mysql_db)],
                        room_manager: Annotated[ChatRoomManager , Depends(getChatRoomsManager)],
                        user = Depends(get_current_user)):
    """
    Update a message by id
    """
    # check if message exist
    original_message = await read_one(message_id)
    if not original_message:
        raise MessageNotFound()
    
    # check if authorized
    if  original_message['user_id'] != user.id:
        raise NotAuthorized()
    
    # can't update message after 5 mins sent
    timestamp = original_message["timestamp"]

    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)

    print(timestamp)
    print(datetime.datetime.now(timezone.utc))
    print(datetime.datetime.now(timezone.utc) - timestamp)

    if datetime.datetime.now(timezone.utc) - timestamp > timedelta(minutes=5):
        raise EditMessageTimeout()

    # update message
    message = await update(message_id, message_update)
    if not message:
        raise UpdateMessageFail()

    # extend message to include user name and avatar
    message_extended = await convert_to_message_extend(message, db)
    return ObjectResponse(result = message_extended)


@router.delete("/messages/{message_id}", 
               response_model=MessageResponse)
async def delete_message(message_id: Annotated[str, Path(description="message id")],
                        user = Depends(get_current_user),):
    """
    Delete a message by id
    """
    # check if message exist
    original_message = await read_one(message_id)
    if not original_message:
        raise MessageNotFound()
    
    # check if authorized
    if original_message['user_id'] != user.id:
        raise NotAuthorized()
    
    # can't update message after 5 mins sent
    timestamp = original_message["timestamp"]

    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)

    if datetime.datetime.now(timezone.utc) - timestamp > timedelta(minutes=5):
        raise DeleteMessageTimeout()
    
    # delete message
    result = await delete(message_id)
    if result:
        return {"success" : True,"message":"Message deleted successfully"}
    else:
        return {"success" : False, "message":"Message deleted unsuccessfully"}
    