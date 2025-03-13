from sqlalchemy import Integer, String, Boolean, Column
from db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key = True, index= True)
    name = Column (String(50), unique=True)
    hashed_password = Column(String(255))
    email = Column(String(255), unique=True)
    avatar = Column(String(255))


