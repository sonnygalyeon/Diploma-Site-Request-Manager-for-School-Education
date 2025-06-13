from .base import *

DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', '127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'request_manager_db',
        'USER': 'emilmardanov',
        'PASSWORD': 'samsepi0l',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# HTTPS settings
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True

# Static files
STATIC_ROOT = '/var/www/request_manager/static/'
