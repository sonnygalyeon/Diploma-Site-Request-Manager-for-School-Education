from sqlalchemy import Column, Integer, String
from .database import Base

class CourseRegistration(Base):
    __tablename__ = "registrations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)  # Telegram chat_id
    course_name = Column(String)
    email = Column(String)
    phone = Column(String)