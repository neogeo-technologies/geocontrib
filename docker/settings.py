"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 2.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'geocontrib-secret-key'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*", "geocontrib"]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.gis',
    'rest_framework',
    'rest_framework_gis',
    'geocontrib',
    'api',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
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
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'geocontrib.context_processors.custom_contexts',
            ],
        },
    },
]
WSGI_APPLICATION = 'config.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'geocontrib',
        'USER': 'geocontrib',
        'PASSWORD': 'geocontrib',
        'HOST': 'database',
        'PORT': '5432'
    },
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators
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


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# Extended properties

AUTH_USER_MODEL = 'geocontrib.User'
LOGIN_URL = 'geocontrib:login'
LOGIN_REDIRECT_URL = 'geocontrib:index'
LOGOUT_REDIRECT_URL = 'geocontrib:index'
DEFAULT_SENDING_FREQUENCY = 'never'  # A choisir parmi: 'never', 'instantly', 'daily', 'weekly'

# Logging properties

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {pathname}, @{lineno} :\n {message} \n',
            'style': '{',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',  # On evite de garder des log de debug
            'propagate': True,
        },
    },
}


# SMTP dev confs

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = 'CHANGEME'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'CHANGEME'
EMAIL_HOST_PASSWORD = 'CHANGEME'
DEFAULT_FROM_EMAIL = 'no-reply@geocontrib.fr'


# Custom Contexts: cf 'geocontrib.context_processors.custom_contexts'

APPLICATION_NAME = 'Collab'
APPLICATION_ABSTRACT = "Description de l'application"
LOGO_PATH = '/media/logo.png'
IMAGE_FORMAT = "application/pdf,image/png,image/jpeg"
FILE_MAX_SIZE = 10000000
SITE_ID = 1

DEFAULT_BASE_MAP = {
    'SERVICE': 'https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png',
    'OPTIONS': {
        'attribution': '&copy; contributeurs d\'<a href="https://osm.org/copyright">OpenStreetMap</a>',
        'maxZoom': 20
    }
}

# Emprise par défaut de la carte
# France métropolitaine
DEFAULT_MAP_VIEW = {
    'center': [47.0, 1.0],
    'zoom': 4
}