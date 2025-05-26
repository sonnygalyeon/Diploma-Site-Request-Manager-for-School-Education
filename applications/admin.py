from django.contrib import admin
from .models import Application

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'phone')
    actions = ['mark_as_processed']

    def mark_as_processed(self, request, queryset):
        queryset.update(status='processed')
    mark_as_processed.short_description = "Пометить как обработанные"
