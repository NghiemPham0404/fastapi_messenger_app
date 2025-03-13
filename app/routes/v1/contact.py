from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
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

router = APIRouter(prefix="/contacts", tags=["contacts"])

@router.get("/", response_model = List[UserOut],name="Lấy các liên hệ của một người")
def get_user_contact(user : Annotated[UserOut, Depends(get_current_user)], db : Session = Depends(get_db)):
    user_id = user.id
    return (db.query(User)
        .join(Contact, User.id == Contact.contact_user_id)
        .filter(Contact.user_id == user_id, Contact.status == 1)
    .union(
        db.query(User)
        .join(Contact, User.id == Contact.user_id)
        .filter(Contact.contact_user_id == user_id , Contact.status == 1)
    )
    .all()
    )

@router.post("/", response_model=ContactOut, name="Gửi kết bạn")
def send_contact_request(contactCreate : ContactCreate, user : Annotated[UserOut, Depends(get_current_user)], db : Session = Depends(get_db)):
    if(user.id != contactCreate.user_id):
        raise HTTPException(status_code=401, detail = "Not Authorized")
    contact_user_id = contactCreate.contact_user_id
    contact_user = user_repo.get_one(db, user_repo._model.id == contact_user_id)
    if not contact_user:
        raise HTTPException(status_code=404, detail = "requested user not found")
    return crud.create(db, contactCreate)

@router.get("/pending", response_model = List[UserOut],name="Lấy danh sách những người đang muốn kết bạn với 1 người")
def get_user_contact(user : Annotated[UserOut, Depends(get_current_user)], db : Session = Depends(get_db)):
    user_id = user.id
    return (db.query(User)
        .join(Contact, User.id == Contact.user_id)
        .filter(Contact.contact_user_id == user_id, Contact.status == 0)
        .all()
    )

@router.put("/{contact_id}", response_model=ContactOut, name="Chấp nhận kết bạn")
def accept_contact_request(contactUpdate: ContactUpdate, user : Annotated[UserOut, Depends(get_current_user)], db : Session = Depends(get_db)):
    if(user.id != contactUpdate.contact_user_id):
        raise HTTPException(status_code=401, detail = "Not Authorized")
    contact = crud.get_one(db, crud._model.user_id == contactUpdate.user_id, 
                           crud._model.contact_user_id == contactUpdate.contact_user_id)
    if not contact:
        raise HTTPException(status_code=404, detail = "requested contact not found")
    contact_in_db = ContactInDB(**contactUpdate.model_dump(), status= 1)
    return crud.update(db, contact, contact_in_db)



@router.delete("/{other_user_id}", response_model=ContactOut, name="Xóa bạn, Xóa kết bạn")
def delete_contact_request(user : Annotated[UserOut, Depends(get_current_user)], other_user_id : int, db : Session = Depends(get_db)):
    user_id = user.id
    contact = db.query(Contact).filter(
        or_(
            (Contact.user_id == user_id) & (Contact.contact_user_id == other_user_id),
            (Contact.user_id == other_user_id) & (Contact.contact_user_id == user_id)
        )
    ).first()
    if contact.user_id != user.id and contact.contact_user_id != user.id:
         raise HTTPException(status_code=401, detail = "Not Authorized")
    return crud.delete(db, contact)
