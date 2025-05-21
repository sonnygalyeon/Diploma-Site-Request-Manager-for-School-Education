import os
from celery import Celery
from celery.schedules import crontab

# Установка переменной окружения для Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'request_manager.settings')

# Создание экземпляра Celery
app = Celery('request_manager')

# Загрузка настроек из settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоподгрузка задач из всех зарегистрированных Django-приложений
app.autodiscover_tasks()

# Настройка расписания периодических задач
app.conf.beat_schedule = {
    'send-daily-report': {
        'task': 'applications.tasks.send_daily_report',
        'schedule': crontab(hour=9, minute=0),  # Каждый день в 9:00
        'args': (),  # Можно передавать аргументы если нужно
    },
}

# Опционально: глобальные настройки Celery
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Europe/Moscow',  # Установите ваш часовой пояс
    enable_utc=True,
)