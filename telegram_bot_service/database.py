from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from databases import Database

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