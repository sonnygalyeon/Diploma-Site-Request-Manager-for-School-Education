from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
import json
import logging
from .models import Application
from .tasks import send_telegram_notification

from rest_framework import serializers
from .models import Application

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import ApplicationSerializer

from rest_framework import generics
from .serializers import ApplicationSerializer

from django.views.decorators.csrf import csrf_exempt
import json


@csrf_exempt
def telegram_webhook(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        callback_data = data.get('callback_query', {}).get('data')
        
        if callback_data.startswith('approve_'):
            app_id = callback_data.split('_')[1]
            # Обновляем статус в БД
            Application.objects.filter(id=app_id).update(status='approved')
            
        elif callback_data.startswith('reject_'):
            app_id = callback_data.split('_')[1]
            Application.objects.filter(id=app_id).update(status='rejected')
            
    return JsonResponse({'status': 'ok'})

class ApplicationListAPI(generics.ListCreateAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer

class ApplicationDetailAPI(generics.RetrieveUpdateAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer

@api_view(['GET'])
def application_list(request):
    applications = Application.objects.all()
    serializer = ApplicationSerializer(applications, many=True)
    return Response(serializer.data)

@csrf_exempt
def create_application(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            app = Application.objects.create(
                name=data['name'],
                phone=data['phone'],
                message=data.get('message', '')
            )
            
            # Формируем данные для уведомления
            notification_data = {
                'id': app.id,
                'name': app.name,
                'phone': app.phone,
                'message': app.message,
                'created_at': app.created_at.strftime('%Y-%m-%d %H:%M:%S')  # Добавляем дату
            }
            
            send_telegram_notification.delay(notification_data)
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)