from django.db import models
from django.core.validators import MinLengthValidator

class Application(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('processed', 'Обработана'),
        ('rejected', 'Отклонена')
    ]

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