from app.response import ListResponse
from .models import *
from sqlalchemy.orm import Session
from ..entities.user import User
from ..entities.group import Group
from ..entities.group_member import GroupMember
from ..base_crud import CRUDRepository

class GroupMemberRepo(CRUDRepository):
    def validate_group_member(self, user_id: int, group_id : int, db : Session):
        return db.query(GroupMember).filter(GroupMember.group_id == group_id, GroupMember.user_id == user_id).first()
    
    def get_group_members(self, db : Session, group_id : int, page : int = 1, limit : int = 20):
        filter = {GroupMember.group_id == group_id}
        group_members_page = self.get_many(db, *filter, page = page, limit = limit)
        return group_members_page


    def convert_to_group_member_out(self, db : Session, group_member):
        """
        Conver group_member(ORM Object) to GroupMemberOut(BaseModel)
        
        input : 

        """
        member_id = group_member.user_id
        member_data = (db.query(User)
                .filter(User.id == member_id)
                .first()
                )
        member = Member.model_validate(member_data)
        group_member.member = member
        return GroupMemberOut.model_validate(group_member)




crud = GroupMemberRepo(GroupMember)
user_repo = CRUDRepository(User)
group_repo = CRUDRepository(Group)
    
