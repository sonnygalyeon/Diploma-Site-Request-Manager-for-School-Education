# request_manager/telegram_bot_service/__init__.py
import os
from pathlib import Path

# Устанавливаем корневой путь пакета
PACKAGE_DIR = Path(__file__).parent

# Инициализация логгера
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Делаем основные компоненты доступными
from .main import main
from .database import Base, engine, SessionLocal
from .handlers import setup_handlers
from .models import Course, Application

# Автоматическая инициализация (опционально)
def init_db():
    """Создание таблиц в БД при первом импорте"""
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized")

# Версия пакета
__version__ = '0.1.0'