from fastapi import FastAPI, Request
from pydantic import BaseModel
import httpx
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import select, func, Integer, String, DateTime, Column
from telegram import ReplyKeyboardMarkup
from telegram.ext import Application as TelegramApp, CommandHandler, MessageHandler, filters
from typing import List, Tuple

# Инициализация FastAPI
app = FastAPI()

# Инициализация Telegram бота
telegram_app = TelegramApp.builder().token("YOUR_BOT_TOKEN").build()

# Настройка базы данных
DATABASE_URL = "postgresql+asyncpg://emilmardanov:samsepi0l@localhost:5432/request_manager_db"
engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Базовая декларация моделей SQLAlchemy
Base = declarative_base()

# Модель Application
class Application(Base):
    __tablename__ = 'applications'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    course_name = Column(String)
    user_name = Column(String)
    email = Column(String)
    phone = Column(String)
    created_at = Column(DateTime, server_default=func.now())

# Клавиатура
def get_main_keyboard():
    keyboard = [
        ["📝 Запись заявок"],
        ["📋 Просмотр заявок"],
        ["📊 Список количества на все курсы"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Обработчики Telegram
async def start(update, context):
    await update.message.reply_text(
        "Выберите действие:",
        reply_markup=get_main_keyboard()
    )

async def handle_message(update, context):
    text = update.message.text
    if text == "📝 Запись заявок":
        await update.message.reply_text("Введите данные заявки в формате:\nКурс, Имя, Email, Телефон")
    elif text == "📋 Просмотр заявок":
        applications = await get_applications_from_db(update.message.chat_id)
        response = "Ваши заявки:\n" + "\n".join(applications) if applications else "У вас нет заявок"
        await update.message.reply_text(response)
    elif text == "📊 Список количества на все курсы":
        stats = await get_course_stats()
        response = "Статистика по курсам:\n" + "\n".join([f"{course}: {count}" for course, count in stats])
        await update.message.reply_text(response)

def setup_handlers(application):
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# FastAPI endpoint
class Notification(BaseModel):
    event_type: str
    user_id: str
    data: dict

@app.post("/notify")
async def handle_notification(notification: Notification):
    formatted_message = format_notification(notification)
    async with httpx.AsyncClient() as client:
        await client.post(
            "https://api.telegram.org/botYOUR_BOT_TOKEN/sendMessage",
            json={
                "chat_id": notification.user_id,
                "text": formatted_message,
                "parse_mode": "MarkdownV2"
            }
        )
    return {"status": "success"}

# Функции асинхронного взаимодействия с базой данных
async def get_applications_from_db(user_id):
    async_session = AsyncSessionLocal()
    stmt = select(Application.course_name, Application.user_name, Application.email, Application.phone)\
           .where(Application.user_id == user_id)
    result = await async_session.execute(stmt)
    rows = result.fetchall()
    return [f"Курс: {row.course_name}, Пользователь: {row.user_name}, Email: {row.email}, Тел.: {row.phone}" for row in rows]

async def get_course_stats():
    async_session = AsyncSessionLocal()
    stmt = select(Application.course_name, func.count())\
           .group_by(Application.course_name)
    result = await async_session.execute(stmt)
    return [(row.course_name, row.count_) for row in result.fetchall()]

# Запуск приложения
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

def run_bot():
    setup_handlers(telegram_app)
    telegram_app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(init_db())
    run_bot()