from sqlalchemy.orm import Session
from typing import Annotated, List
from fastapi import APIRouter,Depends, HTTPException, Path, Query, status

from .service import crud, group_repo, user_repo
from .models import *
from .exceptions import CreateGroupMemberConflict, GroupMemberNotFound

from ..group.exceptions import GroupNotFound
from ..user.exceptions import UserNotFound
from ..response import ListResponse, MessageResponse, ObjectResponse
from ..database import get_mysql_db


router = APIRouter(prefix="/groups", tags=["Group member"])

@router.get("/{group_id}/members", response_model=ListResponse[GroupMemberOut])
async def get_group_members(group_id : Annotated[int,  Path()],
                            db : Annotated[Session , Depends(get_mysql_db)],
                            page : int = 1):
    group_members_page =  crud.get_group_members(db=db, group_id=group_id, page=page)
    group_members = [crud.convert_to_group_member_out(db, group_member) for group_member in group_members_page.items]
    return ListResponse(**group_members_page.model_dump(), results=group_members)


@router.post("/{group_id}/members", 
             response_model=ObjectResponse[GroupMemberOut])
async def add_member_to_group(group_id : Annotated[int,  Path()],
                            group_people_create: GroupMemberCreate, 
                            db : Annotated[Session , Depends(get_mysql_db)]):
    """
    Add a member to a group
    """
    # check if group exists in db
    group = group_repo.get_one(db, group_repo._model.id == group_id)
    if not group:
        raise GroupNotFound()
    
    # check if user exists in db
    user = user_repo.get_one(db, user_repo._model.id == group_people_create.user_id)
    if not user:
        raise UserNotFound()
    
    # check if group_people already exists in db
    group_people = crud.get_one(db, crud._model.user_id == group_people_create.user_id, 
                                       crud._model.group_id == group_people_create.group_id)
    if group_people:
        raise CreateGroupMemberConflict()
    
    # finally create group_people
    group_people_in_db = GroupMemberInDB(**group_people_create.model_dump())
    group_member =  crud.create(db, group_people_in_db)
    group_member = crud.convert_to_group_member_out(db, group_member)
    return ObjectResponse(result=group_member)


@router.delete("/{group_id}/members/{group_member_id}", 
               response_model=MessageResponse)
async def delete_member_from_group(db : Annotated[Session , Depends(get_mysql_db)],
                                   group_id : Annotated[int,  Path()],
                                   group_member_id : Annotated[int , Path()]
                                    ): 
    "Delete a member from a group"
    # check if group_people exists in db
    group_member = crud.get_one(db, crud._model.id == group_member_id)
    if not group_member:
        raise GroupMemberNotFound()
    
    # delete group_people
    crud.delete(db, group_member)
    return MessageResponse(message = "group member removed successfully")