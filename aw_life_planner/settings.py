"""
Django settings for aw_life_planner project.

"""

import os
import dj_database_url
import sys

from pathlib import Path
from dotenv import load_dotenv
from django.contrib.messages import constants as messages


# Load environment variables
load_dotenv()

# BASE DIR
BASE_DIR = Path(__file__).resolve().parent.parent

# SECRET KEY
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-development-key')

# DEBUG: kör lokalt med DEVELOPMENT=True i .env
DEBUG = os.environ.get('DEVELOPMENT') == 'True'

if not DEBUG:
    # Production security settings
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# HOSTS
ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    'aw-life-planner-ms4-f700cbfe6055.herokuapp.com',
]

# Application definition
INSTALLED_APPS = [
    # Core Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # Third-party
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'crispy_forms',
    'crispy_bootstrap5',
    'storages',

    'django_extensions',

    # Local apps
    'accounts',
    'diary',
    'shop',
    'checkout',
    'modules',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # fallback if not using AWS
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'aw_life_planner.urls'

# Templates
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(BASE_DIR, 'templates', 'allauth'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
            ],
            'builtins': [
                'crispy_forms.templatetags.crispy_forms_tags',
                'crispy_forms.templatetags.crispy_forms_field',
            ],
        },
    },
]

WSGI_APPLICATION = 'aw_life_planner.wsgi.application'

# Database
if 'DATABASE_URL' in os.environ:
    DATABASES = {'default': dj_database_url.parse(os.environ.get
                                                  ('DATABASE_URL'))}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': (
        'django.contrib.auth.password_validation.'
        'UserAttributeSimilarityValidator'
        )},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': (
        'django.contrib.auth.password_validation.CommonPasswordValidator'
        )},
    {'NAME': (
        'django.contrib.auth.password_validation.NumericPasswordValidator'
        )},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# CSRF trusted origins (Heroku + local dev)
CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://localhost:8000',
    'https://aw-life-planner-ms4-f700cbfe6055.herokuapp.com',
    'https://*.herokuapp.com',
]

# ============================
# STATIC & MEDIA FILES
# ============================

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')

# S3 Settings
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_DEFAULT_ACL = 'public-read'
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_LOCATION = 'static'
AWS_S3_FILE_OVERWRITE = False

# Static files settings
STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/'
STATICFILES_STORAGE = 'custom_storages.StaticStorage'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles_temp')

# Media files (optional)
DEFAULT_FILE_STORAGE = 'custom_storages.MediaStorage'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'

# Remove STATIC_ROOT when using S3 storage
# STATIC_ROOT = None  # Don't set this when using S3

# This is the key change - use the basic S3Boto3Storage class


STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
# ============================
# AUTHENTICATION & ACCOUNTS
# ============================

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 1

# Allauth settings (striktare än default)
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_SIGNUP_EMAIL_ENTER_TWICE = True
ACCOUNT_USERNAME_MIN_LENGTH = 4
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'


# Add this to your settings.py in the EMAIL section

# ============================
# EMAIL CONFIGURATION
# ============================

if DEBUG:
    # Development - print emails to console
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    # Production - use real email backend
    EMAIL_BACKEND = os.environ.get(
        'EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend'
        )
    EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
    EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

DEFAULT_FROM_EMAIL = os.environ.get(
    'DEFAULT_FROM_EMAIL', 'noreply@awlifeplanner.com'
    )
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# Account email verification settings
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3

# ============================
# STRIPE & SHOP SETTINGS
# ============================

FREE_DELIVERY_THRESHOLD = 50
STANDARD_DELIVERY_PERCENTAGE = 10
STRIPE_CURRENCY = 'usd'
STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY', '')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', '')
STRIPE_WH_SECRET = os.getenv('STRIPE_WH_SECRET', '')

# ============================
# SECURITY (Production only)
# ============================

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Messages -> Bootstrap tags
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# HTML Validator Configuration
HTML_VALIDATOR_ENABLED = DEBUG  # Only validate in development
HTML_VALIDATOR_OUTPUT_DIR = os.path.join(BASE_DIR, 'html_validation_reports')

# Security logging
if DEBUG:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'security': {
                'format': '[SECURITY] {asctime} {levelname} {message}',
                'style': '{',
            },
        },
        'handlers': {
            'security_file': {
                'level': 'INFO',
                'class': 'logging.FileHandler',
                'filename': str(BASE_DIR / "logs/security.log"),
                'formatter': 'security',
            },
            'console': {
                'level': 'WARNING',
                'class': 'logging.StreamHandler',
                'stream': sys.stdout,
            },
        },
        'loggers': {
            'diary.views': {
                'handlers': ['security_file', 'console'],
                'level': 'INFO',
                'propagate': False,
            },
            'modules.views': {
                'handlers': ['security_file', 'console'],
                'level': 'INFO',
                'propagate': False,
            },
        },
    }
else:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'security': {
                'format': '[SECURITY] {asctime} {levelname} {message}',
                'style': '{',
            },
        },
        'handlers': {
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'stream': sys.stdout,
                'formatter': 'security',
            },
        },
        'loggers': {
            'diary.views': {
                'handlers': ['console'],
                'level': 'INFO',
                'propagate': False,
            },
            'modules.views': {
                'handlers': ['console'],
                'level': 'INFO',
                'propagate': False,
            },
        },
    }
