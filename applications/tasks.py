from celery import shared_task
import requests
from django.conf import settings
import logging

TELEGRAM_BOT_TOKEN = '7726856222:AAEnn5XEVxWDuMR3MvLt2gsGT4wdgjdYD44'


logger = logging.getLogger(__name__)
webhook_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"


@shared_task
def send_daily_report():
    from django.db.models import Count
    from django.core.mail import send_mail
    
    stats = Application.objects.values('status').annotate(count=Count('id'))
    message = "\n".join([f"{item['status']}: {item['count']}" for item in stats])
    
    send_mail(
        'Ежедневный отчёт по заявкам',
        message,
        'noreply@yourdomain.com',
        ['admin@yourdomain.com']
    )


@shared_task(bind=True, max_retries=3)
def send_telegram_notification(self, app_data):
    buttons = {
        'inline_keyboard': [[
            {
                'text': '✅ Одобрить',
                'callback_data': f'approve_{app_data["id"]}'
            },
            {
                'text': '❌ Отклонить',
                'callback_data': f'reject_{app_data["id"]}'
            }
        ]]
    }

    requests.post(
    "http://localhost:8000/notify",
    json={
        "event_type": "order_created",
        "user_id": "123",
        "data": {
            "order_id": "789",
            "user_name": "Иван",
            "amount": "1500"
        }
    }
)
    try:
        # Проверка настроек
        if not settings.TELEGRAM_BOT_TOKEN:
            raise ValueError("Токен бота не настроен в settings.TELEGRAM_BOT_TOKEN")
        
        if not settings.TELEGRAM_CHAT_ID:
            raise ValueError("Chat ID не настроен в settings.TELEGRAM_CHAT_ID")

        text = (
            "📌 *Новая заявка*\n\n"
            f"*ID*: {app_data['id']}\n"
            f"*Имя*: {app_data['name']}\n"
            f"*Телефон*: `{app_data['phone']}`\n"
            f"*Сообщение*: {app_data.get('message', 'Не указано')}\n"
            f"*Дата*: {app_data.get('created_at', 'Не указана')}"
        )

        response = requests.post(
            f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                'chat_id': settings.TELEGRAM_CHAT_ID,
                'text': text,
                'parse_mode': 'Markdown',
                'disable_web_page_preview': True
            },
            timeout=10
        )
        response.raise_for_status()
        return True
    except Exception as e:
        logger.error(f"Ошибка отправки в Telegram: {str(e)}")
        self.retry(exc=e, countdown=60)
        return False