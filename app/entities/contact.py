from ..database import Base
from sqlalchemy import Integer, Column, ForeignKey

class Contact(Base):
    __tablename__ = "contact"

    id = Column(Integer, index = True, primary_key = True)
    user_id = Column (Integer, ForeignKey("user.id"), nullable=False)
    contact_user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    status = Column(Integer, default=0)