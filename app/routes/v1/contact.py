from typing import Annotated, List
from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session
from db.database import get_db
from models.contacts import Contact
from models.users import User
from schemas.contact_base import *
from schemas.user_base import UserOut
from crud.contact import crud
from crud.user import crud as user_repo
from security import get_current_user


router = APIRouter(prefix="/contacts", 
                   tags=["contacts"])


@router.get("/", 
            response_model = List[UserOut],
            name="Get all contacts of a user")
async def get_user_contact(user : Annotated[UserOut, Depends(get_current_user)], 
                           db : Annotated[Session, Depends(get_db)]):
    user_id = user.id
    return crud.get_all_contacts(db, user_id)


@router.post("/", 
             response_model=ContactOut, 
             name="Send a contact request")
async def send_contact_request(user : Annotated[UserOut, Depends(get_current_user)], 
                               contact_create : Annotated[ContactCreate, Body()] , 
                               db : Annotated[Session, Depends(get_db)]):
    # not authorized
    if(user.id != contact_create.user_id):
        raise HTTPException(status_code=401, detail = "Not Authorized") 
    # check if user_id and contact_user_id are the same
    if contact_create.user_id == contact_create.contact_user_id:
        raise HTTPException(status_code=400, detail = "user_id and contact_user_id must be different")
    # check if contact_user_id is exist in db
    contact_user_id = contact_create.contact_user_id
    contact_user = user_repo.get_one(db, user_repo._model.id == contact_user_id)
    # check if contact_user_id is exist in db
    if not contact_user:
        raise HTTPException(status_code=404, detail = "requested user not found")
    if crud.check_contact_exist(db, contact_create.user_id, contact_user_id):
        raise HTTPException(status_code=400, detail = "contact already exist")
    # finally create contact
    return crud.create(db, contact_create)


@router.get("/pending", 
            response_model = List[UserOut],
            name="Get all pending requests of a user")
async def get_user_contact(user : Annotated[UserOut, Depends(get_current_user)], 
                           db : Session = Depends(get_db)):
    user_id = user.id
    return crud.get_pending_requests(db, user_id)


@router.put("/{contact_id}", 
            response_model=ContactOut, 
            name="Accept a contact request")
async def accept_contact_request(contact_update: ContactUpdate, 
                                 user : Annotated[UserOut, Depends(get_current_user)], 
                                 db : Session = Depends(get_db)):
    # check if user legit
    if(user.id != contact_update.contact_user_id):
        raise HTTPException(status_code=401, detail = "Not Authorized")
    # check if contact exist in db
    contact = crud.get_one(db, crud._model.user_id == contact_update.user_id, 
                           crud._model.contact_user_id == contact_update.contact_user_id)
    if not contact:
        raise HTTPException(status_code=404, detail = "requested contact not found")
    # finally update contact
    contact_in_db = ContactInDB(**contact_update.model_dump(), status= 1)
    return crud.update(db, contact, contact_in_db)


@router.delete("/{other_user_id}", 
               response_model=ContactOut, 
               name="Delete a contact")
async def delete_contact_request(user : Annotated[UserOut, Depends(get_current_user)], 
                                 other_user_id : Annotated[int, Path(description="contact id of user you want to delete")], 
                                 db : Session = Depends(get_db)):
    # check if user legit
    user_id = user.id
    if contact.user_id != user_id and contact.contact_user_id != user_id:
         raise HTTPException(status_code=401, detail = "Not Authorized")
    # check if contact exist in db
    contact = crud.check_contact_exist(db, user_id, other_user_id)
    if not contact:
        raise HTTPException(status_code=404, detail = "requested contact not found")
    # finally delete contact
    return crud.delete(db, contact)