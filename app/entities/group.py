from sqlalchemy import Integer, String, Boolean, Column, TEXT
from ..database import Base


class Group(Base):
    __tablename__ = "group"

    id = Column(Integer, primary_key = True, index= True)
    subject = Column(String(255), nullable=False)
    avatar = Column(String(255), nullable=True)
    is_public = Column(Boolean, default=False)
    is_member_mute = Column(Boolean, default = False)