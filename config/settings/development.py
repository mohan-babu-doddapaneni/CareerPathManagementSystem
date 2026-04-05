"""
Development settings — local machine only.
"""
from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

SECRET_KEY = 'dev-secret-key-not-for-production-use'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'CareerPath',
        'USER': 'postgres',
        'PASSWORD': os.environ.get('DB_PASSWORD', '1172'),
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

# Local file storage for development
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# Celery — use synchronous execution in dev (no Redis needed)
CELERY_TASK_ALWAYS_EAGER = True
CELERY_BROKER_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

# Email — print to console in dev
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# WhiteNoise for dev static files
INSTALLED_APPS = ['whitenoise.runserver_nostatic'] + INSTALLED_APPS
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

ACCOUNT_EMAIL_VERIFICATION = 'none'
