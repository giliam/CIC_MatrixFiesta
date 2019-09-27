"""
Django settings for matrix_fiesta project.

Generated by 'django-admin startproject' using Django 2.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

from matrix_fiesta.generate_secret_key import secret_key_from_file
if os.path.isfile('matrix_fiesta/parameters.py'):
    from matrix_fiesta import parameters
else:
    parameters = object

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = secret_key_from_file('secret_key')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = parameters.DEBUG if hasattr(parameters, "DEBUG") else False

ALLOWED_HOSTS = parameters.ALLOWED_HOSTS if hasattr(parameters, "ALLOWED_HOSTS") else ['127.0.0.1']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'common',
    'matrix',
    # 'django_extensions',
    # 'debug_toolbar',
    'django_cas_ng',
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_cas_ng.middleware.CASMiddleware',
]

if DEBUG:
    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]

ROOT_URLCONF = 'matrix_fiesta.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': parameters.TEMPLATES_DIRS if hasattr(parameters, "TEMPLATES_DIRS") else ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'matrix_fiesta.context_processors.activeNavbar',
                'matrix_fiesta.context_processors.discourseUrl',
                'django.template.context_processors.i18n',
            ],
        },
    },
]

WSGI_APPLICATION = 'matrix_fiesta.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = parameters.DATABASES if hasattr(parameters, "DATABASES") else {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
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

LANGUAGE_CODE = 'fr'
LANGUAGES = (
    ('en', 'English'),
    ('fr', 'Français'),
)

TIME_ZONE = 'Europe/Paris'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    parameters.STATICFILES_DIRS
    if hasattr(parameters, "STATICFILES_DIRS") else ("assets/",)
)

STATIC_ROOT = (
    parameters.STATIC_ROOT
    if hasattr(parameters, "STATIC_ROOT")
    else os.path.join(BASE_DIR, "static")
)

REST_FRAMEWORK = parameters.REST_FRAMEWORK if hasattr(parameters, "REST_FRAMEWORK") else {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ]
}

AUTHENTICATION_BACKENDS = (
     'django.contrib.auth.backends.ModelBackend',
#     'django_cas_ng.backends.CASBackend',
     'matrix.backends.MatrixCASBackend',
)

INTERNAL_IPS = [
    # ...
    '127.0.0.1',
    # ...
]

#LOGIN_URL = '/matrix/log_in/'

CAS_SERVER_URL = 'https://auth.mines-paristech.fr/cas/'
CAS_VERSION = 3
CAS_CREATE_USER = False

# According to
# https://blog.ionelmc.ro/2012/01/19/tweaks-for-making-django-admin-faster/
TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )),
)


LOGGING = parameters.LOGGING if hasattr(parameters, "LOGGING") else {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, '..', 'log', 'matrix.log'),
            'maxBytes': 1024*1024*30,
            'backupCount': 15,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': True,
        },
    },
}



if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
            'LOCATION': '127.0.0.1:11211',
        }
    }

DJANGO_LOG_LEVEL = "INFO"