from fastapi import FastAPI, Request
from pydantic import BaseModel
import httpx
from fastapi import Depends
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import CourseRegistration

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
    # 1. Сохраняем в базу данных (пример для SQLite)
    import sqlite3
    conn = sqlite3.connect('courses.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO registrations (user_id, course_name, email, phone)
        VALUES (?, ?, ?, ?)
    ''', (course_data.user_id, course_data.course_name, course_data.email, course_data.phone))
    conn.commit()
    
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