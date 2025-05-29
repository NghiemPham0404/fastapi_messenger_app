from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.pagination import Page

from ..response import ListResponse
from ..entities.user import User
from ..base_crud import CRUDRepository
from ..entities.contact import Contact
from .models import *

class ContactRepository(CRUDRepository):


    def check_contact_exist(self,db: Session, user_id: int, contact_user_id: int):
        """
        Check if a contact exist in db
        """
        return db.query(Contact).filter(
            or_(
                (Contact.user_id == user_id) & (Contact.contact_user_id == contact_user_id),
                (Contact.user_id == contact_user_id) & (Contact.contact_user_id == user_id)
            )
        ).first()
    

    def get_all_contacts(self, db: Session, user_id: int, page : int = 1, limit = 20):
        """
        Get all contacts of a user
        """
        filter = (or_(Contact.user_id == user_id, Contact.contact_user_id == user_id),
                                            Contact.status == 1)
        contacts_page =  self.get_many(db, 
                                        *filter, 
                                        page=page, 
                                        limit=limit)
        return contacts_page

    
    def get_pending_requests(self, db: Session, user_id: int, page : int = 1, limit = 20):
        filter = (Contact.contact_user_id == user_id, Contact.status == 0)
        contacts_page =  self.get_many(db, 
                                        *filter, 
                                        page=page, 
                                        limit=limit)
        return contacts_page
    
    def get_waiting_requests(self, db: Session, user_id: int, page : int = 1, limit = 20):
        filter = (Contact.user_id == user_id, Contact.status == 0)
        contacts_page =  self.get_many(db, 
                                        *filter, 
                                        page=page, 
                                        limit=limit)
        return contacts_page
    
    def get_block_list_ids(self, db : Session, user_id: int):
        query_results = (db.query(Contact)
            .filter(Contact.status == 2, 
                    Contact.user_id == user_id).all())
        return [result.id for result in query_results]
        
    
    def get_block_list(self, db:Session, user_id: int, page : int = 1, limit = 20):
        filter = (Contact.status == 2, Contact.user_id == user_id)
        contacts_page =  self.get_many(db, 
                                        *filter, 
                                        page=page, 
                                        limit=limit)
        return contacts_page
    
    def convert_contact_to_contact_out(self, contact, current_user_id : int , db : Session):
        other_user_id = contact.contact_user_id if contact.user_id == current_user_id else contact.user_id
        other_user_data = (
            db.query(User.id, User.name, User.avatar)
            .where(User.id == other_user_id)
            .first()
        )
        other = OtherContactUser.model_validate(other_user_data)
        contact.other_user = other
        return ContactOut.model_validate(contact)
    
    def convert_contacts_page_to_response(self, db : Session, user_id : int, contacts_page : Page):
        results = [self.convert_contact_to_contact_out(contact, user_id, db) for contact in contacts_page.items]
        return ListResponse(**contacts_page.model_dump(), results=results)


crud = ContactRepository(Contact)