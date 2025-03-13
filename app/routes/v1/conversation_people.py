from sqlalchemy.orm import Session
from db.database import get_db
from fastapi import APIRouter,Depends, HTTPException, status
from crud.conversation import crud as conversation_repo
from crud.user import crud as user_repo
from crud.conversation_people import crud
from typing import List
from schemas.conversation_people_base import *

router = APIRouter(prefix="/conversation_people", tags=["conversation peoples"])

@router.post("/{conversation_id}", response_model=ConversationPeopleOut)
async def add_person_to_conversation(conversation_people_create: ConversationPeopleCreate, db : Session = Depends(get_db)):
    conversation = conversation_repo.get_one(db, conversation_repo._model.id == conversation_people_create.conversation_id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="conversation not found")
    
    user = user_repo.get_one(db, user_repo._model.id == conversation_people_create.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    
    conversation_people = crud.get_one(db, crud._model.user_id == conversation_people_create.user_id, crud._model.conversation_id == conversation_people_create.conversation_id)
    if conversation_people:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="this resources is already exist")
    conversation_people_in_db = ConversationPeopleInDB(**conversation_people_create.model_dump())
    return crud.create(db, conversation_people_in_db)

@router.post("/{conversation_id}/people", response_model=List[ConversationPeopleOut])
async def add_people_to_conversation(people_id: List[int], conversation_id:int, db : Session = Depends(get_db)):
    conversation = conversation_repo.get_one(db, conversation_repo._model.id == conversation_id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="conversation not found")
    
    valid_people = user_repo.get_many(db, user_repo._model.id.in_(people_id))
    valid_people_ids = [valid_person.id for valid_person in valid_people]
    print(valid_people_ids)
    invalid_people_id = [user_id for user_id in people_id if user_id not in valid_people_ids]
    if invalid_people_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Users with ids not found: {invalid_people_id}")
    
    exist_conversation_people = crud.get_many(db, crud._model.user_id.in_(valid_people_ids), crud._model.conversation_id == conversation_id)
    exist_con_peo_ids = [ecp.user_id for ecp in exist_conversation_people]
    valid_con_peo_ids = [user_id for user_id in valid_people_ids if user_id not in exist_con_peo_ids]
    print(valid_con_peo_ids)
    valid_con_peo = [ConversationPeopleInDB(user_id=user_id, conversation_id=conversation_id) for user_id in valid_con_peo_ids]
    added_people = []
    for con_peo in valid_con_peo:
        added_people.append(crud.create(db, con_peo))
    return added_people

@router.delete("/")
async def delete_person_from_conversation(conversation_people_delete : ConversationPeopleDelete, db : Session = Depends(get_db)): 
    conversation_person = conversation_repo.get_one(db, conversation_repo._model.id == conversation_people_delete.conversation_id)
    if not conversation_person:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="conversation people not found")
    crud.delete(db, conversation_person)