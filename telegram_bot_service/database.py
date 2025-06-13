from databases import Database
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

from request_manager.applications.models import Application

SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://emilmardanov:samsepi0l@localhost/db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Асинхронный движок
async_engine = create_async_engine(
    "postgresql+asyncpg://emilmardanov:samsepi0l@localhost/request_manager_db",
    echo=True  # Для отладки SQL-запросов
)

# Асинхронная сессия
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

async def handle_application(update, context):
    try:
        parts = update.message.text.split(',')
        if len(parts) != 4:
            raise ValueError
        
        course, name, email, phone = [part.strip() for part in parts]
        
        async with AsyncSession(engine) as session:
            new_app = Application(
                course_name=course,
                user_name=name,
                email=email,
                phone=phone,
                user_id=update.message.chat_id
            )
            session.add(new_app)
            await session.commit()
            
        await update.message.reply_text("✅ Заявка успешно сохранена!")
        
    except Exception as e:
        await update.message.reply_text("❌ Ошибка формата. Введите:\nКурс, Имя, Email, Телефон")


DATABASE_URL = "postgresql+asyncpg://emilmardanov:samsepi0l@localhost:5432/request_manager_db"

# Для SQLAlchemy ORM
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Для raw async queries
database = Database(DATABASE_URL)