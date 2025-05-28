# telegram_bot_service/models.py
from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base  # Теперь это будет работать

class Course(Base):
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)

class Application(Base):
    __tablename__ = 'applications'
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey('courses.id'))