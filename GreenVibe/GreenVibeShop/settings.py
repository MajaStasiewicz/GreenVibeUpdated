import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-=3p6dydz10e$2$kvvb(tbtr69#*rbnfd4*x&$+1@8ue7yb$gdz'

DEBUG = True

ALLOWED_HOSTS = ['*'] 

handler404 = 'shop.views.handler404'
handler500 = 'shop.views.handler500'
handler403 = 'shop.views.handler403'
handler400 = 'shop.views.handler400'
handler401 = 'shop.views.handler401'
handler503 = 'shop.views.handler503'
handler429 = 'shop.views.handler429'
handler502 = 'shop.views.handler502'
handler504 = 'shop.views.handler504'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'shop',
    'blog',
    'survey',
    'training',
    'stripe',
    'products.apps.ProductsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'GreenVibeShop.urls'

STRIPE_PUBLIC_KEY = 'pk_test_51OSI7sFPjlUSYagTUUDX7n384Ham8qfjl2yrzHcUDNS7y5AQgCiElVxAMkYUbL5QRlq4guWRe52yIynAo9zA1mBF00UI2cgNV9'
STRIPE_SECRET_KEY = 'sk_test_51OSI7sFPjlUSYagTXnxTdFRqyOda6ZmfcOF5SOSvJmOQfPdINr2yGXIVsuCZfCfqWUme5U7N3aexQklFYNw2VXry00nREQV5oi'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'GreenVibeShop.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

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

LANGUAGE_CODE = 'pl'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA_URL = '/media/'

if DEBUG:
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')
    STATIC_URL = '/static/'
else:
    STATIC_URL = '/static/'
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

SESSION_ENGINE = 'django.contrib.sessions.backends.db'  
SESSION_SAVE_EVERY_REQUEST = True  
SESSION_COOKIE_LENGTH = 32

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_FROM = "greenvibeteam@gmail.com"
EMAIL_HOST_USER = "greenvibeteam@gmail.com"
EMAIL_HOST_PASSWORD = "nozg jxhf lydb lhdt"
EMAIL_USE_TLS = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',  
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}