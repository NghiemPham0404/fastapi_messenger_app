from db.database import Base
from sqlalchemy import Integer, Column, ForeignKey

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, index = True, primary_key = True)
    user_id = Column (Integer, ForeignKey("users.id"), nullable=False)
    contact_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Integer, default=0)