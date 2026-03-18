from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Charge automatiquement le fichier .env à la racine du projet
load_dotenv(BASE_DIR / '.env')

SECRET_KEY = 'django-fatou-bravo-wolof-tts-secret-key-2026'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.staticfiles',
    'tts_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'fatou_tts.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'fatou_tts.wsgi.application'

# Base de données SQLite (nécessaire pour Django, même sans modèles custom)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

STATIC_URL = '/static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# LAfricaMobile API Configuration
LAM_API_BASE = os.environ.get("LAM_API_BASE", "https://ttsapi.lafricamobile.com")
LAM_LOGIN    = os.environ.get("LAM_LOGIN", "")
LAM_PASSWORD = os.environ.get("LAM_PASSWORD", "")
