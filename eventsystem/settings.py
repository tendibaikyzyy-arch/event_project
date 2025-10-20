import os
from pathlib import Path

# 🔹 Базалық жол
BASE_DIR = Path(__file__).resolve().parent.parent

# 🔹 Құпия кілт (өз кілтіңмен алмастырсаң да болады)
SECRET_KEY = 'django-insecure-kini-yessenov-secret-key'

DEBUG = True
ALLOWED_HOSTS = ['*']  # PythonAnywhere үшін '*' немесе нақты хост атауы

# 🔹 Орнатылған қосымшалар
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'events',  # Біздің қолданба
]

# 🔹 Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'eventsystem.urls'

# 🔹 Шаблондар (HTML)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'events' / 'templates'],
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

WSGI_APPLICATION = 'eventsystem.wsgi.application'

# 🔹 Деректер қоры (SQLite)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 🔹 Құпия сөз ережелері
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# 🔹 Тіл және уақыт
LANGUAGE_CODE = 'ru'
TIME_ZONE = 'Asia/Aqtau'
USE_I18N = True
USE_TZ = True

# 🔹 Статикалық файлдар
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'events' / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# 🔹 Медиа (егер суреттер жүктелсе)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# 🔹 Редирект параметрлері
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# 🔹 Email (позже егер Reminder жүйесін қосатын болсақ)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'