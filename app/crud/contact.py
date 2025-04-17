from sqlalchemy import or_
from models.users import User
from crud.base import CRUDRepository
from models.contacts import Contact

from sqlalchemy.orm import Session

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
    
    def get_all_contacts(self, db: Session, user_id: int):
        """
        Get all contacts of a user
        """
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
    
    def get_pending_requests(self, db: Session, user_id: int):
        return (db.query(User)
            .join(Contact, User.id == Contact.user_id)
            .filter(Contact.contact_user_id == user_id, Contact.status == 0)
            .all()
        )

crud = ContactRepository(Contact)