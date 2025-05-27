from fastapi import FastAPI, Request
from pydantic import BaseModel
import httpx
from fastapi import Depends
from sqlalchemy.orm import Session
from databases import Database
from telegram import ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters


# from handlers import handle_application

def main():
    application = Application.builder().token('7726856222:AAEnn5XEVxWDuMR3MvLt2gsGT4wdgjdYD44').build()
    setup_handlers(application)
    application.run_polling()
# Клавиатура с кнопками
keyboard = [
    ["📝 Запись заявок"],
    ["📋 Просмотр заявок"],
    ["📊 Список количества на все курсы"]
]
reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update, context):
    await update.message.reply_text(
        "Выберите действие:",
        reply_markup=reply_markup
    )

async def handle_message(update, context):
    text = update.message.text
    if text == "📝 Запись заявок":
        await update.message.reply_text("Введите данные заявки в формате:\nКурс, Имя, Email, Телефон")
    elif text == "📋 Просмотр заявок":
        # Здесь логика получения заявок из БД
        applications = await get_applications_from_db()
        await update.message.reply_text(f"Ваши заявки:\n{applications}")
    elif text == "📊 Список количества на все курсы":
        stats = await get_course_stats()
        await update.message.reply_text(f"Статистика по курсам:\n{stats}")

def setup_handlers(application):
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

DATABASE_URL = "postgresql+asyncpg://emilmardanov:samsepi0l@localhost:5432/request_manager_db"

database = Database(DATABASE_URL)

app = FastAPI()

# Модель для уведомления
class Notification(BaseModel):
    event_type: str
    user_id: str
    data: dict

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
# Модель для регистрации
class CourseRegistration(BaseModel):
    user_id: int  # Telegram chat_id
    course_name: str
    email: str
    phone: str

@app.post("/register")
async def register(course_data: CourseRegistration):
    query = """
        INSERT INTO registrations (user_id, course_name, email, phone)
        VALUES (:user_id, :course_name, :email, :phone)
        RETURNING id
    """
    values = {
        "user_id": course_data.user_id,
        "course_name": course_data.course_name,
        "email": course_data.email,
        "phone": course_data.phone
    }
    
    record_id = await database.execute(query=query, values=values)
    
    # 2. Отправляем уведомление
    notification = Notification(
        event_type="course_registration",
        user_id=str(course_data.user_id),
        data={
            "course": course_data.course_name,
            "email": course_data.email
        }
    )
    await handle_notification(notification)
    
    return {"status": "success"}

# Конфигурация (можно вынести в settings.py)
BOT_CONFIG = {
    "webhook_url": "https://api.telegram.org/bot7726856222:AAEnn5XEVxWDuMR3MvLt2gsGT4wdgjdYD44/sendMessage",
    "templates": {
        "order_created": "🛒 Новый заказ #{order_id} от {user_name} на сумму {amount} ₽",
        "payment_received": "✅ Платеж получен: {amount} ₽ от {user_name}",
        "support_request": "🆘 Поддержка: {user_name} пишет: '{message}'"
    },
    "default_chat_id": 381381540
}

# Форматирование уведомления
def format_notification(notification: Notification) -> str:
    template = BOT_CONFIG["templates"].get(notification.event_type)
    if not template:
        return f"⚠️ Неизвестное событие: {notification.event_type}\nДанные: {notification.data}"
    
    try:
        return template.format(**notification.data)
    except KeyError as e:
        return f"⚠️ Ошибка форматирования: отсутствует ключ {e}"

# Эндпоинт для приема уведомлений
@app.post("/notify")
async def handle_notification(notification: Notification):
    formatted_message = format_notification(notification)
    async with httpx.AsyncClient() as client:
        await client.post(
            BOT_CONFIG["webhook_url"],
            json={
                "chat_id": notification.user_id or BOT_CONFIG["default_chat_id"],
                "text": formatted_message,
                "parse_mode": "MarkdownV2"  # Для форматирования
            }
        )
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                BOT_CONFIG["webhook_url"],
                json={
                    "chat_id": notification.user_id,  # Для Telegram
                    "text": formatted_message,
                    "parse_mode": "HTML"
                },
                timeout=10.0
            )
            print("Ответ сервера:", {
                "status": response.status_code,
                "body": response.text
            })
            response.raise_for_status()
    except Exception as e:
        print("!!! Ошибка отправки !!!:", str(e))
        raise
    print("\n=== Отправка уведомления ===")
    print("URL:", BOT_CONFIG["webhook_url"])
    print("Тело запроса:", {
        "chat_id": notification.user_id,
        "text": formatted_message
    })
    return {"status": "success"}

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

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

