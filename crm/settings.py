# File: crm/settings.py

# Standard Django settings would be here...
# Below are the additions specific to this project

# Add django_crontab to INSTALLED_APPS
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'graphene_django',
    'django_crontab',  # Add this line
    'crm',
]

# GraphQL configuration
GRAPHENE = {
    'SCHEMA': 'crm.schema.schema'
}

# Configure cron jobs
CRONJOBS = [
    # Heartbeat logger - every 5 minutes
    ('*/5 * * * *', 'crm.cron.log_crm_heartbeat'),
    
    # Low stock update - every 12 hours
    ('0 */12 * * *', 'crm.cron.update_low_stock'),
]

# Optional: Configure cron job logging
CRONTAB_LOCK_JOBS = True
CRONTAB_COMMAND_SUFFIX = '2>&1'

# Database configuration (example)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

CELERY_BEAT_SCHEDULE = {
    'generate-crm-report': {
        'task': 'crm.tasks.generate_crm_report',
        'schedule': crontab(day_of_week='mon', hour=6, minute=0),
    },
}

# Other standard Django settings...
SECRET_KEY = 'your-secret-key-here'
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Static files configuration
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Time zone
USE_TZ = True
TIME_ZONE = 'UTC'