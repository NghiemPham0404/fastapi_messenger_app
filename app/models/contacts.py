from db.database import Base
from sqlalchemy import Integer, Column

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, index = True, primary_key = True)
    user_id = Column (Integer)
    contact_user_id = Column(Integer)
    status = Column(Integer, default=0)