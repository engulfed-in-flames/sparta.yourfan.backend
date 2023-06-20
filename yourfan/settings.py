import os
from datetime import timedelta
from pathlib import Path

from dotenv import read_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE_PATH = BASE_DIR / ".env"
read_dotenv(str(ENV_FILE_PATH))

SECRET_KEY = str(os.environ.get("DJANGO_SECRET_KEY"))

DEBUG = str(os.environ.get("DEBUG")) == "1"

YOUTUBE_API_KEY = str(os.environ.get("YOUTUBE_API_KEY"))

SYSTEM_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

CUSTOM_APPS = [
    "users.apps.UsersConfig",
    "community",
    "chat",
    "youtube",
    "medias.apps.MediasConfig",
]

THIRD_PARTY_APPS = [
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    "storages",
    "channels",
    "django_bleach",
]

INSTALLED_APPS = SYSTEM_APPS + CUSTOM_APPS + THIRD_PARTY_APPS


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "yourfan.urls"

TEMPLATE_DIR = BASE_DIR / "templates/"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [TEMPLATE_DIR],
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

WSGI_APPLICATION = "yourfan.wsgi.application"

DB_ENGINE = os.environ.get("POSTGRES_ENGINE")
DB_NAME = os.environ.get("POSTGRES_NAME")
DB_USERNAME = os.environ.get("POSTGRES_USER")
DB_PW = os.environ.get("POSTGRES_PASSWORD")
DB_HOST = os.environ.get("POSTGRES_HOST")
DB_PORT = os.environ.get("POSTGRES_PORT")
IS_DB_AVAIL = all(
    [
        DB_ENGINE,
        DB_NAME,
        DB_USERNAME,
        DB_PW,
        DB_HOST,
        DB_PORT,
    ]
)

IS_POSTGRES_READY = str(os.environ.get("POSTGRES_READY")) == "1"

if IS_DB_AVAIL and IS_POSTGRES_READY:
    DATABASES = {
        "default": {
            "ENGINE": DB_ENGINE,
            "NAME": DB_NAME,
            "USER": DB_USERNAME,
            "PASSWORD": DB_PW,
            "HOST": DB_HOST,
            "PORT": DB_PORT,
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 8,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=1000),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "TOKEN_OBTAIN_SERIALIZER": "users.serializers.CustomTokenObtainPairSerializer",
}


LANGUAGE_CODE = "ko-kr"

TIME_ZONE = "Asia/Seoul"

USE_I18N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "users.CustomUser"

# 정적 파일 관련
STATIC_URL = "api/static/"
STATIC_ROOT = BASE_DIR / "static"


# CORS 관련

CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

ALLOWED_HOSTS = str(os.environ.get("DJANGO_ALLOWED_HOST")).split(" ")

CORS_ORIGIN_WHITELIST = CSRF_TRUSTED_ORIGINS

# 이메일 인증 기반 로그인

EMAIL_BACKEND = str(os.environ.get("EMAIL_BACKEND"))
EMAIL_HOST = str(os.environ.get("EMAIL_HOST"))
EMAIL_PORT = str(os.environ.get("EMAIL_PORT"))
EMAIL_HOST_USER = str(os.environ.get("EMAIL_HOST_USER"))
EMAIL_HOST_PASSWORD = str(os.environ.get("EMAIL_HOST_PASSWORD"))
EMAIL_USE_TLS = str(os.environ.get("EMAIL_USE_TLS"))
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_EMAIL_REQUIRED = True

ACCOUNT_EMAIL_VERIFICATION = "mandatory"

ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 1

LOGIN_REDIRECT_URL = "/"

# 셀러리
CELERY_BROKER_URL = "redis://redis:6379"
CELERY_RESULT_BACKEND = "redis://redis:6379"

CHANNEL_HOST = (
    str(os.environ.get("CHANNEL_HOST"))
    if str(os.environ.get("CHANNEL_HOST")) == "redis"
    else "localhost"
)

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(CHANNEL_HOST, 6379)],
        },
    },
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": "chatroom.log",
        },
    },
    "loggers": {
        "chat.consumers": {
            "handlers": ["file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

CF_API_TOKEN = str(os.environ.get("CF_API_TOKEN"))
CF_ACCOUNT_ID = str(os.environ.get("CF_ACCOUNT_ID"))

KAKAO_API_KEY = str(os.environ.get("KAKAO_API_KEY"))
KAKAO_CLIENT_SECRET = str(os.environ.get("KAKAO_CLIENT_SECRET"))
KAKAO_REDIRECT_URI = str(os.environ.get("KAKAO_REDIRECT_URI"))

GH_CLIENT_ID = str(os.environ.get("GH_CLIENT_ID"))
GH_CLIENT_SECRET = str(os.environ.get("GH_CLIENT_SECRET"))
GH_REDIRECT_URI = str(os.environ.get("GH_REDIRECT_URI"))
