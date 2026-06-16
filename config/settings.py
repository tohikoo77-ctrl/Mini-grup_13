import os
from pathlib import Path
from datetime import timedelta
import os
import environ
env = environ.Env()


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

SECRET_KEY = env(
    "SECRET_KEY",
    default="fkdashf3unfuh437fh439h78",
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", default=False)

#allowed hosts
ALLOWED_HOSTS = env.list(
    "ALLOWED_HOSTS",
    default=[
        "localhost",
        "127.0.0.1",
        "deployminigroup13.pythonanywhere.com",
    ],
)


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
   # my apps
    'product',
    'order',
    'payment',
    'user',
    'category',
    'cart',
    'commerce_extras',
    'delivery',
    'company',
    'feedback',
    'contact',
    'faq',
    # other apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_spectacular',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR/'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# drf-spectacular settings
SPECTACULAR_SETTINGS = {
    'TITLE': 'Mini Group 13 API',
    'DESCRIPTION': 'API documentation for Mini Group 13 project',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,

    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": "",
    "AUDIENCE": None,
    "ISSUER": None,
    "JSON_ENCODER": None,
    "JWK_URL": None,
    "LEEWAY": 0,

    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    "ON_LOGIN_SUCCESS": "rest_framework_simplejwt.serializers.default_on_login_success",
    "ON_LOGIN_FAILED": "rest_framework_simplejwt.serializers.default_on_login_failed",

    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",

    "JTI_CLAIM": "jti",

    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),
    

    "TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
    "TOKEN_VERIFY_SERIALIZER": "rest_framework_simplejwt.serializers.TokenVerifySerializer",
    "TOKEN_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenBlacklistSerializer",
    "SLIDING_TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainSlidingSerializer",
    "SLIDING_TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSlidingSerializer",

    "CHECK_REVOKE_TOKEN": False,
    "REVOKE_TOKEN_CLAIM": "hash_password",
    "CHECK_USER_IS_ACTIVE": True,
}

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/


STATIC_URL = 'static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


MEDIA_URL = 'media/'
MEDIA_ROOT = 'media/'
# This is a list of additional directories where Django will look for static files 
# during development (and for collectstatic to copy from).
if DEBUG:
    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, "static"),
    ]

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    **globals().get("REST_FRAMEWORK", {}),
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
}

if "drf_spectacular" in INSTALLED_APPS:
    REST_FRAMEWORK = {
        **REST_FRAMEWORK,
        "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    }

    SPECTACULAR_SETTINGS = {
        "TITLE": "Mini Group 13 API",
        "DESCRIPTION": "API documentation",
        "VERSION": "1.0.0",
        "SERVE_INCLUDE_SCHEMA": False,
    }

AUTH_USER_MODEL = "user.User"



CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS",
    default=[
        "https://group-13-main-zeta.vercel.app/kirish/",
    ],
)
CSRF_TRUSTED_ORIGINS = env.list(
    "CSRF_TRUSTED_ORIGINS",
    default=[
        "https://group-13-main-zeta.vercel.app/kirish/",
    ],
)

if not DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SAMESITE = "None"
    SESSION_COOKIE_SAMESITE = "None"

# PythonAnywhere does not provide a local Redis/SMTP service for this app by
# default. Admin login writes the session during POST, so cache-backed sessions
# can raise ConnectionRefusedError when they point at localhost.
SESSION_ENGINE = "django.contrib.sessions.backends.db"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "mini-grup-13-cache",
    }
}

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Final production overrides for PythonAnywhere. Keep these at the end so they
# take precedence over any local development cache/session/email settings above.
SESSION_ENGINE = "django.contrib.sessions.backends.db"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "mini-grup-13-cache",
    }
}

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Real email delivery. Set these environment variables on PythonAnywhere:
# EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, and optionally DEFAULT_FROM_EMAIL.
import os

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True").lower() == "true"
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)

# Transactional email: one configured sender account can send verification
# codes to any registered user's email address. Put the real credentials in
# PythonAnywhere environment variables, not in source code.
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True").lower() == "true"
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL") or EMAIL_HOST_USER
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# Final email configuration.
# - Local/dev without SMTP credentials: print emails in the console and avoid
#   ValueError from an empty sender address.
# - Production with credentials: send real emails to any registered user.
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True").lower() == "true"
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = (
    os.environ.get("DEFAULT_FROM_EMAIL")
    or EMAIL_HOST_USER
    or "webmaster@localhost"
)
SERVER_EMAIL = DEFAULT_FROM_EMAIL

if EMAIL_HOST_USER and EMAIL_HOST_PASSWORD:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Swagger request bodies for custom auth actions whose serializers are not
# visible to drf-spectacular.
_spectacular_settings = globals().get("SPECTACULAR_SETTINGS", {})
SPECTACULAR_SETTINGS = {
    **_spectacular_settings,
    "POSTPROCESSING_HOOKS": [
        *(_spectacular_settings.get("POSTPROCESSING_HOOKS") or []),
        "config.swagger_hooks.add_write_method_request_bodies",
    ],
}
