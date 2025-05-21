# applications/tasks.py
from celery import shared_task
import requests
from django.conf import settings
from models import Application

@shared_task
def send_telegram_notification(app_id):
    app = Application.objects.get(id=app_id)
    text = f"""
    🚀 Новая заявка!
    Имя: {app.name}
    Телефон: {app.phone}
    Email: {app.email}
    Сообщение: {app.message}
    """
    
    requests.post(
        f'https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage',
        json={'chat_id': settings.TELEGRAM_CHAT_ID, 'text': text}
    )