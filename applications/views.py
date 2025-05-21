from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
import json
import logging
from .models import Application
from .tasks import send_telegram_notification

from rest_framework import serializers
from .models import Application



class ApplicationSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Application
        fields = '__all__'
        read_only_fields = ('status', 'created_at', 'updated_at')

logger = logging.getLogger(__name__)

@csrf_exempt
def create_application(request):
    if request.method != 'POST':
        return JsonResponse(
            {'status': 'error', 'message': 'Only POST method allowed'},
            status=405
        )

    try:
        # Парсинг JSON
        try:
            data = json.loads(request.body.decode('utf-8'))
            logger.debug(f"Received data: {data}")
        except json.JSONDecodeError:
            return JsonResponse(
                {'status': 'error', 'message': 'Invalid JSON format'},
                status=400
            )

        # Валидация полей
        required_fields = ['name', 'phone']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return JsonResponse(
                {'status': 'error', 'message': f'Missing fields: {", ".join(missing_fields)}'},
                status=400
            )

        # Создание заявки
        try:
            application = Application.objects.create(
                name=data['name'].strip(),
                phone=data['phone'].strip(),
                message=data.get('message', '').strip()
            )
        except ValidationError as e:
            return JsonResponse(
                {'status': 'error', 'message': str(e)},
                status=400
            )

        # Подготовка данных для уведомления
        notification_data = {
            'id': application.id,
            'name': application.name,
            'phone': application.phone,
            'message': application.message,
            'status': application.status,
            'created_at': application.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

        # Асинхронная отправка уведомления
        send_telegram_notification.delay(notification_data)

        return JsonResponse({
            'status': 'success',
            'application_id': application.id,
            'created_at': notification_data['created_at']
        })

    except Exception as e:
        logger.exception("Unexpected error in create_application")
        return JsonResponse(
            {'status': 'error', 'message': 'Internal server error'},
            status=500
        )