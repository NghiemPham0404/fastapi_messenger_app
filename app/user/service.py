from math import ceil
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from ..pagination import Page

from .models import Relationship, UserOut, UserOutExtend

from ..entities.contact import Contact
from ..group.models import GroupOut
from ..response import ListResponse

from ..base_crud import CRUDRepository
from ..entities.user import User
from ..entities.group import Group
from ..entities.group_member import GroupMember


class UserRepository(CRUDRepository):

    
    def get_users(self, db: Session, keyword, user_id : int, page : int = 1, limit : int = 20):
        users_page = crud.get_many(db, 
                                and_(
                                    or_(
                                        crud._model.name.like(f"%{keyword}%"),
                                        crud._model.email.like(f"%{keyword}%"),
                                ),
                                user_id != crud._model.id),
                                page=page,
                                limit=limit
                            )
        users_extend_page = self.convert_user_page_to_user_extend_response(db, users_page, user_id)
        return users_extend_page

    
    def find_user_by_email(self, db: Session, email: str):
        """
        Find a user by email
        """
        return self.get_one(db, self._model.email == email)
    
    
    def get_user_groups(self, db:Session, user_id : int, page, limit : int = 20):
        query =  (db.query(Group)
                .join(GroupMember, Group.id == GroupMember.group_id)
                .join(User, GroupMember.user_id ==  User.id)
                .filter(User.id == user_id)
                )
        groups_page = crud.pagination_query(query, page, limit)
        return groups_page
    


    def convert_user_to_user_extend(self, db:Session, result_user, user_id : int):
        '''
        Convert result user(searched user) to user extend (include is contact status). 
        extend contents are:

        contact_status:
            - -1 : user and this result user dont have any relationship
            - 0: pending contact request from bold of user and this result user 
            - 1: user and this result user are in contacts
        
        is_sent_request (contact_status = 0) : 
            - true if and user have sent result user
            - false if result user have sent result to user
        '''
        contact = (db.query(Contact)
                 .where(
                    and_(
                        or_(
                            (result_user.id == Contact.user_id) & (user_id == Contact.contact_user_id),
                            (result_user.id == Contact.contact_user_id) & (user_id == Contact.user_id),
                        ),
                        Contact.status != 2
                     )
                    )
                    .first()
                )
        contact_status = contact.status if contact else -1
        contact_id = contact.id if contact else -1

        if(contact_status == 0):
            is_sent_request = True if result_user.id == contact.contact_user_id else False
        else:
            is_sent_request = False

        result_user.relationship = Relationship(contact_id= contact_id, contact_status=contact_status, 
                                                is_sent_request=is_sent_request)
        
        return UserOutExtend.model_validate(result_user)

    def convert_user_page_to_user_extend_response(self, db:Session, user_page : Page, user_id : int):
        users_extend = [self.convert_user_to_user_extend(db, user, user_id) for user in user_page.items]
        return ListResponse(**user_page.model_dump(), results=users_extend)



crud = UserRepository(model=User)