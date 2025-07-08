from typing import Annotated
from fastapi import APIRouter, Body, Depends, Path, Query
from sqlalchemy.orm import Session

from .exceptions import ContactNotFound, CreateContactConflict, CreateContactExistConflict, CreateContactOtherNotFound, InvalidContactsList
from .service import crud
from .models import *

from ..database import get_mysql_db
from ..user.models import UserOut
from ..user.service import crud as user_repo
from ..security import get_current_user
from ..response import ListResponse, ObjectResponse, MessageResponse
from ..exceptions import NotAuthorized


router = APIRouter(prefix="/contacts", 
                   tags=["Contacts"])

contact_type_dict = {
    "pending":0,
    "accept":1,
    "block":2,
    "request":3
}

@router.get("/", 
            response_model = ListResponse[ContactOut],
            name="Get contacts of a user")
async def get_user_contact(
                           user : Annotated[UserOut, Depends(get_current_user)], 
                           db : Annotated[Session, Depends(get_mysql_db)],
                           type : Annotated[str, Query(openapi_examples={
                                "all contacts":{
                                    "summary":"all contacts of an user",
                                    "value": "accept"
                                },
                                "pending contacts":{
                                    "summary":"all pending contacts of an user",
                                    "value": "pending"
                                },
                                "blocked users":{
                                    "summary":"all blocked contact requests of an user",
                                    "value": "block"
                                },
                                "sent request":{
                                    "summary":"all sent contact requests of an user",
                                    "value": "request"
                                }                              
                            })] = "accept",
                           ):
    user_id = user.id
    # get pending contacts requests of a user
    if contact_type_dict[type] == 0:
        contacts_page =  crud.get_pending_requests(db, user_id)
    # get pending contacts requests of a user
    elif contact_type_dict[type] == 1:
        contacts_page =  crud.get_all_contacts(db, user_id)
    # get waiting accept requests of a user
    elif contact_type_dict[type] == 2:
        contacts_page = crud.get_block_list(db, user_id)
    # get waiting accept requests of a user
    elif contact_type_dict[type] == 3:
        contacts_page = crud.get_waiting_requests(db, user_id)
    else:
        # raise invalid contacts list exception
        raise InvalidContactsList()
    
    return crud.convert_contacts_page_to_response(db, user_id, contacts_page)


@router.post("/", 
             response_model=ObjectResponse[ContactOut], 
             name="Send a contact request")
async def send_contact_request(user : Annotated[UserOut, Depends(get_current_user)], 
                               contact_create : Annotated[ContactCreate, Body(
                                   openapi_examples={
                                        "send contact request":{
                                            "summary":"send contact request",
                                            "value": {
                                                "user_id":1,
                                                "contact_user_id":2,
                                                "status":0
                                            }
                                        },
                                        "block a user":{
                                            "summary":"block a user",
                                            "value": {
                                                "user_id":1,
                                                "contact_user_id":2,
                                                "status":2
                                            }
                                        },
                                   }
                               )] , 
                               db : Annotated[Session, Depends(get_mysql_db)]):

    # check if user_id and contact_user_id are the same
    if user.id == contact_create.contact_user_id:
        raise CreateContactConflict()
    
    # check if contact_user_id is exist in db
    contact_user_id = contact_create.contact_user_id
    contact_user = user_repo.get_one(db, user_repo._model.id == contact_user_id)    
    if not contact_user:
        raise CreateContactOtherNotFound()
    
    # check if contact is exist in db
    if crud.check_contact_exist(db, user.id, contact_user_id):
        raise CreateContactExistConflict()
    
    # finally create contact
    contact_in_db = ContactInDB(**contact_create.model_dump())
    contact =  crud.create(db, contact_in_db)
    contact = crud.convert_contact_to_contact_out(contact, user.id ,db = db)
    return ObjectResponse(result=contact)

@router.put("/{id}", 
            response_model=ObjectResponse[ContactOut], 
            name="Accept a contact request")
async def update_contact(id : Annotated[int, Path()],
                                 contact_update : Annotated[ContactUpdate, Body(
                                     openapi_examples={
                                        "accept-friend-request":{
                                            "summary":"accept friend",
                                            "value":{                                               
                                                "action": "accept"
                                            }
                                        },
                                        "block-a-contact":{
                                            "summary":"block user",
                                            "value":{
                                                "action": "block"
                                            }
                                        }
                                     }
                                 )],
                                 user : Annotated[UserOut, Depends(get_current_user)], 
                                 db : Session = Depends(get_mysql_db)):
    user_id = user.id
    # check if contact exist in db
    contact = crud.get_one(db, crud._model.id == id)
    if not contact:
        raise ContactNotFound()
    # check if user legit
    if(user.id != contact.contact_user_id & user.id != contact.user_id):
        raise NotAuthorized()
    # finally update contact
    contact.status = contact_type_dict[contact_update.action]
    db.commit()
    db.refresh(contact)
    contact = crud.convert_contact_to_contact_out(contact, user_id, db)
    return ObjectResponse(result=contact)
    


@router.delete("/{id}", 
               response_model=MessageResponse, 
               name="Delete a contact (Unfriend)")
async def delete_contact_request(user : Annotated[UserOut, Depends(get_current_user)], 
                                 id : Annotated[int, Path()],
                                 db : Session = Depends(get_mysql_db)):
    
    user_id = user.id
    # check if contact exist in db
    contact = crud.get_one(db, crud._model.id == id)
    if not contact:
        raise ContactNotFound()
    # check if user legit
    if contact.user_id != user_id and contact.contact_user_id != user_id:
        raise NotAuthorized()
    # finally delete contact 
    # crud.delete(contact) # real
    return MessageResponse(success=True, message="contact deleted successfully") # mock