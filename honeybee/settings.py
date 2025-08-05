from pathlib import Path  
from decouple import config  
import dj_database_url  

SECRET_KEY          = config('SECRET_KEY')  
DEBUG               = config('DEBUG', default=False, cast=bool)  
SQUARE_ACCESS_TOKEN = config('SQUARE_ACCESS_TOKEN')  
SQUARE_LOCATION_ID  = config('SQUARE_LOCATION_ID')  

BASE_DIR = Path(__file__).resolve().parent.parent

# 4. Allow all hosts for now:
ALLOWED_HOSTS = ['*']


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 5. Add your orders app here:
    'orders',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # 6. Whitenoise middleware for serving static files:
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'honeybee.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # you can add custom template dirs here later
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'honeybee.wsgi.application'


# pick up DATABASE_URL from .env if present, otherwise use a SQLite file beside manage.py
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}


# Password validation (unchanged) …
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]


# Internationalization (unchanged) …
LANGUAGE_CODE = 'en-us'
TIME_ZONE     = 'UTC'
USE_I18N      = True
USE_TZ        = True


# 8. Static files served by Whitenoise:
STATIC_URL  = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'


# Default primary key field type (unchanged) …
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
STATICFILES_STORAGE = (
    "whitenoise.storage.CompressedManifestStaticFilesStorage"
)
