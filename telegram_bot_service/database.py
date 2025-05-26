from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from databases import Database

DATABASE_URL = "postgresql+asyncpg://emilmardanov:samsepi0l@localhost:5432/request_manager_db"

# Для SQLAlchemy ORM
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Для raw async queries
database = Database(DATABASE_URL)