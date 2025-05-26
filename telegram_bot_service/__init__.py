# Может быть пустым или содержать экспорты
from .database import Database
from .models import CourseRegistration

__all__ = ['Database', 'CourseRegistration']