import os
from pathlib import Path

SHOW_TOOLBAR_CALLBACK = True
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY", "12421415")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DEBUG", False) == "True"

ALLOWED_HOSTS = (
    os.environ.get("ALLOWED_HOSTS").split(",")
    if os.environ.get("ALLOWED_HOSTS")
    else ["127.0.0.1"]
)


AWS_ACCESS_KEY_ID = os.environ.get("MINIO_ACCESS_KEY")
AWS_SECRET_ACCESS_KEY = os.environ.get("MINIO_SECRET_KEY")
AWS_STORAGE_BUCKET_NAME = os.environ.get("BUCKET_NAME")
AWS_S3_ENDPOINT_URL = os.environ.get("MINIO_HOST")

# FileAPI
FILE_API_HOST = os.environ.get("FILE_API_HOST")
FILE_API_PORT = os.environ.get("FILE_API_PORT")

LOCALE_PATHS = ["movies/locale"]


INTERNAL_IPS = [
    "127.0.0.1",
]
# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "debug_toolbar",
    "rest_framework",  # Django REST Framework
    "movies.apps.MoviesConfig",
    "custom_auth.apps.AuthConfig",
    "notifications.apps.NotificationsConfig",  # Наше приложение уведомлений
    "django_celery_beat",
    "django_celery_results",
]

# Django REST Framework settings
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",  # Только JSON рендерер
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",  # Только JSON парсер
    ],
    "UNAUTHENTICATED_USER": None,  # Отключаем аутентификацию
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware", 
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# AuthUser
AUTH_USER_MODEL = "custom_auth.User"

AUTHENTICATION_BACKENDS = [
    "custom_auth.auth.CustomBackend",
    # 'django.contrib.auth.backends.ModelBackend',
]

AUTH_API_LOGIN_URL = os.environ.get("AUTH_API_LOGIN_URL")

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "ru-RU"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
if os.getenv('STATIC_ROOT'):
    STATIC_ROOT = os.getenv('STATIC_ROOT')
else:
    STATIC_ROOT = os.path.join(BASE_DIR, "static")

#STATIC_ROOT = "/opt/app/staticfiles"  # Папка для сбора статики

# Оптимизация хранения статических файлов
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

EVENT_URL = os.environ.get("EVENT_URL")

# Celery
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers.DatabaseScheduler"
CELERY_TIMEZONE = os.environ.get("TIME_ZONE", "UTC")
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_BROKER_CONNECTION_RETRY = True
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_BROKER_CONNECTION_MAX_RETRIES = 10
CELERY_BROKER_URL = os.environ.get(
    "CELERY_BROKER_URL", "amqp://rmuser:rmpassword@rabbitmq:5672//"
)
CELERY_RESULT_BACKEND = os.environ.get(
    "CELERY_RESULT_BACKEND", "rpc://rmuser:rmpassword@rabbitmq:5672//"
)

CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 1

API_URL = "http://notification_api:8765/api/v1"
