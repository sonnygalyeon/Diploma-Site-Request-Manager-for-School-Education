from celery import shared_task
import requests
from django.conf import settings
import logging


logger = logging.getLogger(__name__)

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
    try:
        text = (
            "📌 *Новая заявка*\n\n"
            f"*ID*: {app_data['id']}\n"
            f"*Имя*: {app_data['name']}\n"
            f"*Телефон*: `{app_data['phone']}`\n"
            f"*Сообщение*: {app_data['message']}\n"
            f"*Дата*: {app_data['created_at']}"
        )

        response = requests.post(
            f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                'chat_id': settings.TELEGRAM_CHAT_ID,
                'text': text,
                'parse_mode': 'Markdown'
            },
            timeout=10
        )
        response.raise_for_status()
        
    except Exception as e:
        logger.error(f"Telegram notification failed: {str(e)}")
        self.retry(exc=e, countdown=60)