from django.db import models
from django.core.validators import MinLengthValidator
from django.contrib.auth.models import User

class Application(models.Model):
    
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name='Пользователь'
    )
    
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('processed', 'Обработана'),
        ('rejected', 'Отклонена')
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new'
    )

    name = models.CharField(
        max_length=100,
        verbose_name='Имя',
        validators=[MinLengthValidator(2)]
    )
    phone = models.CharField(
        max_length=20,
        verbose_name='Телефон',
        validators=[MinLengthValidator(5)]
    )
    message = models.TextField(
        verbose_name='Сообщение',
        blank=True,
        null=True
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name='Статус'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    
    
    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} - {self.phone} ({self.status})'
    

class ApplicationLog(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)