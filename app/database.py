from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

Base = declarative_base()


MYSQL_DATABASE_URL =  os.getenv("MYSQL_DATABASE_URL")
engine = create_engine(url= MYSQL_DATABASE_URL, pool_pre_ping=True,
    pool_recycle=1800)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_mysql_db():
    '''
    get Mysql database session
    '''
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


MONGO_URL = os.getenv("MONGO_DB_URL")
client = AsyncIOMotorClient(MONGO_URL)
mongodb = client["chatting_app"]
message_collection = mongodb["messages"]

def get_mongo_db():
    return mongodb
