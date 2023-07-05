import os
from datetime import timedelta
from pathlib import Path


from dotenv import read_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE_PATH = BASE_DIR / ".env"
read_dotenv(str(ENV_FILE_PATH))

SECRET_KEY = str(os.environ.get("DJANGO_SECRET_KEY"))

DEBUG = str(os.environ.get("DEBUG")) == "1"

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
    "django_filters",
    "drf_yasg",
    "django_apscheduler",
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

WSGI_APPLICATION = "yourfan.wsgi.application"

DB_ENGINE = str(os.environ.get("POSTGRES_ENGINE"))
DB_NAME = str(os.environ.get("POSTGRES_NAME"))
DB_USER = str(os.environ.get("POSTGRES_USER"))
DB_PW = str(os.environ.get("POSTGRES_PASSWORD"))
DB_HOST = str(os.environ.get("POSTGRES_HOST"))
DB_PORT = str(os.environ.get("POSTGRES_PORT"))
IS_DB_AVAIL = all(
    [
        DB_ENGINE,
        DB_NAME,
        DB_USER,
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
            "USER": DB_USER,
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
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 8,
        },
    },
    {
        "NAME": "users.validators.PasswordFormatValidator",
    },
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "TOKEN_OBTAIN_SERIALIZER": "users.serializers.CustomTokenObtainPairSerializer",
}


LANGUAGE_CODE = "ko-kr"

TIME_ZONE = "Asia/Seoul"

USE_I18N = True

USE_TZ = False

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "users.CustomUser"

# 정적 파일 관련
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"

# CORS 관련

CORS_ALLOW_CREDENTIALS = True

CSRF_COOKIE_SECURE = True

CSRF_TRUSTED_ORIGINS = [
    "https://www.devinferno.com",
    "http://127.0.0.1:3000",
    "http://localhost:3000",
]

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "api.devinferno.com",
    ".devinferno.com",
]

CORS_ORIGIN_WHITELIST = CSRF_TRUSTED_ORIGINS

# 이메일 인증 기반 로그인


LOGIN_REDIRECT_URL = "/"

# 셀러리
CELERY_BROKER_URL = "redis://redis:6379"
CELERY_RESULT_BACKEND = "redis://redis:6379"

REDIS_CHANNEL_HOST = str(os.environ.get("REDIS_CHANNEL_HOST", "localhost"))
REDIS_PORT = str(os.environ.get("REDIS_PORT", 6379))


CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(REDIS_CHANNEL_HOST, REDIS_PORT)],
        },
    },
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": "chatroom.log",
            "formatter": "verbose",
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

BLEACH_ALLOWED_TAGS = ["span","p","b","i","u","em","strong","a","img","h1","h2","h3","h4","h5","h6","br","pre","blockquote","hr","del","sub","sup","table","td","tr","tbody","div",]

APSCHEDULER_DATETIME_FORMAT = "N j, Y, f:s a"

SCHEDULER_DEFAULT = True

YOUTUBE_API_KEY = str(os.environ.get("YOUTUBE_API_KEY"))

CF_API_TOKEN = str(os.environ.get("CF_API_TOKEN"))
CF_ACCOUNT_ID = str(os.environ.get("CF_ACCOUNT_ID"))

KAKAO_API_KEY = str(os.environ.get("KAKAO_API_KEY"))
KAKAO_CLIENT_SECRET = str(os.environ.get("KAKAO_CLIENT_SECRET"))
KAKAO_REDIRECT_URI = str(os.environ.get("KAKAO_REDIRECT_URI"))

GH_CLIENT_ID = str(os.environ.get("GH_CLIENT_ID"))
GH_CLIENT_SECRET = str(os.environ.get("GH_CLIENT_SECRET"))
GH_REDIRECT_URI = str(os.environ.get("GH_REDIRECT_URI"))

NAVER_SERVICE_ID = str(os.environ.get("NAVER_SERVICE_ID"))
NAVER_ACCESS_KEY = str(os.environ.get("NAVER_ACCESS_KEY"))
NAVER_SECRET_KEY = str(os.environ.get("NAVER_SECRET_KEY"))
SENDER_PHONE_NUMBER = str(os.environ.get("SENDER_PHONE_NUMBER"))
