from sqlalchemy import Integer, String, Boolean, Column, ForeignKey
from ..database import Base

class GroupMember(Base):
    __tablename__ = 'group_member'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    group_id = Column(Integer, ForeignKey("group.id"))
    is_host = Column(Boolean, default=False, nullable=False)
    is_sub_host = Column(Boolean, default=False, nullable = False)
    status = Column(Integer, default=0)