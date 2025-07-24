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
                            status : Annotated[int, Query(openapi_examples={
                                "group members":{
                                    "summary":"all current member of a group",
                                    "value": 1
                                },
                                "send request":{
                                    "summary":"all sending member request of a group",
                                    "value": 0
                                },
                                "waiting":{
                                    "summary":"all wait member request of a group",
                                    "value": 2
                                },                            
                            })] = 1,
                            page : int = 1):
    group_members_page =  crud.get_group_members(db=db, group_id=group_id, status=status, page=page)
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

@router.get("/{group_id}/members-check")
async def get_group_member(db : Annotated[Session , Depends(get_mysql_db)],
                                group_id : Annotated[int,  Path()],
                                user_ids : Annotated[List[int], Query()]):
    
    group_members = db.query(crud._model).filter(
        crud._model.group_id == group_id,
        crud._model.user_id.in_(user_ids)
    ).all()

    group_member_map = {gm.user_id: gm for gm in group_members}
    checked_group_members = []
    for user_id in user_ids:
        group_member = group_member_map.get(user_id)
        
        if group_member is None:
            checked_group_member = GroupMemberCheck(
                user_id=user_id,
                is_host=False,
                is_sub_host=False,
                status=-1
            )
        else:
            checked_group_member = GroupMemberCheck(
                group_member_id= group_member.id,
                user_id=user_id,
                is_host=group_member.is_host,
                is_sub_host=group_member.is_sub_host,
                status=group_member.status
            )

        checked_group_members.append(checked_group_member)

    return ListResponse(
        results=checked_group_members, 
        page = 1, 
        total_pages=1, 
        total_results=len(checked_group_members))


@router.put("/{group_id}/members/{group_member_id}", response_model=ObjectResponse[GroupMemberOut])
async def update_group_member(db : Annotated[Session , Depends(get_mysql_db)],
                                group_id : Annotated[int,  Path()],
                                group_member_id : Annotated[int , Path()],
                                group_member_update : GroupMemberUpdate
                                ):
    '''Update a member of a group'''
    group_member = crud.get_one(db, crud._model.id == group_member_id)
    if not group_member:
        raise GroupMemberNotFound()

    group_member = crud.update(db=db, db_obj= group_member, obj_update= group_member_update)
    group_member = crud.convert_to_group_member_out(db, group_member)
    return ObjectResponse(result=group_member)



@router.delete("/{group_id}/members/{group_member_id}", 
               response_model=MessageResponse)
async def delete_member_from_group(db : Annotated[Session , Depends(get_mysql_db)],
                                   group_id : Annotated[int,  Path()],
                                   group_member_id : Annotated[int , Path()]
                                    ): 
    '''Delete a member from a group'''
    # check if group_people exists in db
    group_member = crud.get_one(db, crud._model.id == group_member_id)
    if not group_member:
        raise GroupMemberNotFound()
    
    # delete group_people
    crud.delete(db, group_member)
    return MessageResponse(message = "group member removed successfully")