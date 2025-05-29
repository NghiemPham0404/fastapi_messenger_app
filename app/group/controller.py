from typing import Annotated, List
from fastapi import APIRouter,Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from .exceptions import GroupNotFound
from .models import *
from .service import crud

from ..response import ListResponse, MessageResponse, ObjectResponse
from ..database import get_mysql_db
from ..user.service import crud as user_repo
from ..group_member.service import crud as group_member_repo
from ..user.models import UserOut

router = APIRouter(prefix="/groups", 
                   tags=["Group"])


@router.get("/", 
            response_model=ListResponse[GroupOut])
def get_groups(db:Annotated[Session, Depends(get_mysql_db)],
                keyword : Annotated[str,Query] = "",
                page : int = 1):
    """
    Get groups
    """
    groups_page =  crud.get_groups(db, keyword, page)
    return ListResponse(**groups_page.model_dump(), results = groups_page.items)



@router.post("/", 
             response_model=ObjectResponse[GroupOut])
def create_group(group_create : GroupCreate, 
                        db:Annotated[Session, Depends(get_mysql_db)]):
    """
    Create a group
    """
    group_in_db =  GroupInDB(**group_create.model_dump()) 
    group = crud.create(db, group_in_db)
    return ObjectResponse(result = group)



@router.get("/{id}", 
            response_model=ObjectResponse[GroupOut])
def get_group(id : Annotated[int, Path(description="group id")], 
                     db:Annotated[Session, Depends(get_mysql_db)]):
    """
    Get a group by id
    """
    group = crud.get_one(db, crud._model.id == id)
    if not group:
        raise GroupNotFound()
    return ObjectResponse(result = group)


@router.put("/{id}", 
            response_model=ObjectResponse[GroupOut])
def update_group(id : Annotated[int, Path(description="group id")], 
                        group_update : GroupUpdate, 
                        db:Annotated[Session, Depends(get_mysql_db)]):
    """"
    Update a group by id"
    """
    # check if group exists in db
    group = crud.get_one(db, crud._model.id == id)
    if not group:
        raise GroupNotFound()
    # update group
    group_in_db =  GroupInDB(**group_update.model_dump()) 
    group =  crud.update(db, group, group_in_db)
    return ObjectResponse(result = group)


@router.delete("/{id}", response_model=MessageResponse)
def delete_group(id : int, 
                        db:Annotated[Session, Depends(get_mysql_db)]):
    """
    Delete a group by id
    """
    # check if group exists in db
    group = crud.get_one(db, crud._model.id == id)
    if not group:
       raise GroupNotFound()
    # delete group
    return MessageResponse(message = "group deleted successfully")
