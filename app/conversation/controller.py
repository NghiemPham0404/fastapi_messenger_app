from typing import Annotated
from fastapi import Depends, APIRouter, Path, Query
from motor.motor_asyncio import AsyncIOMotorClient

from ..user.models import UserOut

from .models import *
from .service import conversation_repo

from ..exceptions import NotAuthorized
from ..message.models import MessageOut
from ..response import ListResponse
from ..database import get_mysql_db, get_mongo_db
from ..security import get_current_user
from ..group_member.service import crud as group_member_crud
from ..group_member.exceptions import NotGroupMember

router = APIRouter(tags=['Conversation & chat history'])

@router.get("/users/{user_id}/conversations", response_model=list[ConversationOut])
async def get_recent_conversations_messages(user_id : Annotated[int, Path()],
                                            user : Annotated[UserOut, Depends(get_current_user)], 
                                            mongo_db : Annotated[AsyncIOMotorClient, Depends(get_mongo_db)],
                                            mysql_db : Annotated[AsyncIOMotorClient, Depends(get_mysql_db)],
                                            ):
    if user_id != user.id:
        raise NotAuthorized()
    return await conversation_repo.get_recent_conversations(user_id, mysql_db, mongo_db)

@router.get("/groups/{group_id}/messages", response_model=ListResponse[MessageOut])
async def get_group_message(group_id : Annotated[int, Path()],
                            user : Annotated[UserOut, Depends(get_current_user)],
                            mongo_db : Annotated[AsyncIOMotorClient, Depends(get_mongo_db)],
                            mysql_db : Annotated[AsyncIOMotorClient, Depends(get_mysql_db)],
                            page : int = 1
                            ):
    is_group_member = group_member_crud.validate_group_member(db = mysql_db, user_id=user.id, group_id=group_id)
    if not is_group_member:
        raise NotGroupMember()

    group_messages_page =  await conversation_repo.get_group_messages(group_id = group_id, 
                                                      page = page, 
                                                      mongo_db=mongo_db, 
                                                      mysql_db=mysql_db,
                                                      )
    return ListResponse(**group_messages_page.model_dump(), 
                        results=group_messages_page.items
                        )

@router.get("/users/{user_id}/messages",  response_model=ListResponse[MessageOut])
async def get_user_direct_messages(user_id : Annotated[int, Path()],
                                            other_user_id : Annotated[int, Query()],
                                            user : Annotated[UserOut, Depends(get_current_user)], 
                                            mongo_db : Annotated[AsyncIOMotorClient, Depends(get_mongo_db)],
                                            mysql_db : Annotated[AsyncIOMotorClient, Depends(get_mysql_db)],
                                            page : int = 1
                                            ):
    if user_id != user.id:
        raise NotAuthorized()
    direct_messages_page =  await conversation_repo.get_direct_messages(mysql_db=mysql_db,
                                                       mongo_db=mongo_db,
                                                       user_id=user_id, 
                                                       other_user_id=other_user_id, 
                                                       page=page)
    return ListResponse(**direct_messages_page.model_dump(),
                        results=direct_messages_page.items
                        )