
from pathlib import Path
import os
from django.core.exceptions import ImproperlyConfigured

# 1️⃣ Defini baz pwojè a
BASE_DIR = Path(__file__).resolve().parent.parent

#  Media files (pou jere foto itilizatè)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

def get_env_setting(name: str, default=None, required: bool = False):
    val = os.environ.get(name, default)
    if required and (val is None or val == ''):
        raise ImproperlyConfigured(f"Set the {name} environment variable")
    return val

# SECURITY WARNING: keep the secret key used in production secret!
# Load from environment in production; fall back to a non-secret dev key only for local development
SECRET_KEY = get_env_setting('DJANGO_SECRET_KEY', "django-insecure-dev-placeholder")

# SECURITY WARNING: don't run with debug turned on in production!
# Use environment variable DJANGO_DEBUG ("1"/"0" or "true"/"false")
DEBUG = str(get_env_setting('DJANGO_DEBUG', '1')).lower() in ('1', 'true', 'yes')

# In production set DJANGO_ALLOWED_HOSTS to a comma-separated list of hosts
allowed_hosts_env = get_env_setting('DJANGO_ALLOWED_HOSTS', '')
if allowed_hosts_env:
    ALLOWED_HOSTS = [h.strip() for h in allowed_hosts_env.split(',') if h.strip()]
else:
    # Default for local development
    ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
# -----------------------------------------------------
AUTH_USER_MODEL = 'utilisateurs.CustomUser'
STATIC_URL = '/static/'
LOGIN_URL = '/utilisateurs/login/'
LOGIN_REDIRECT_URL = '/utilisateurs/dash_admin/'
LOGOUT_REDIRECT_URL = '/utilisateurs/login/'
# ------------------------------------------------------
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'widget_tweaks',
    'utilisateurs',
    'eleves',
    'enseignants',
    'cours',
    'core',
    'matieres',
    'classes',
    'inscriptions',
]
# -------------------------------------------------------------------------------
# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
# ----------------------------------------------------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'imjfpro2025.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ BASE_DIR / 'templates'], 
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

WSGI_APPLICATION = 'imjfpro2025.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# Default: sqlite for local development. Production DB should be configured via env vars.
DEFAULT_DB = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': BASE_DIR / 'db.sqlite3',
}

DATABASES = {
        'default': {
            'ENGINE':'django.db.backends.mysql',
            'NAME':'railway',
            'USER': 'root',
            'PASSWORD': 'hdrSblIWPxixCHSVyaVRpypVdrTqnfUZ',
            'HOST': 'ballast.proxy.rlwy.net',
            'PORT': '53755',
            'OPTIONS': {
                'charset': 'utf8mb4',
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            },   # Additional options can be provided via DB_OPTIONS as JSON if needed
        },
} 


# NOTE: The previous monkeypatch of socket.getaddrinfo was removed. If you rely on
# special DNS/hostname behavior for a specific hosting platform, please reintroduce
# a safer, documented approach and keep secrets out of source control.



# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

# STATIC_URL = 'static/'

# STATICFILES_DIRS = [BASE_DIR / 'static']
# AXES_ENABLED = True
# Sesyon
SESSION_COOKIE_AGE = 1209600  # 2 semèn
SESSION_SAVE_EVERY_REQUEST = True  # Renouvle chak reqèt
SESSION_COOKIE_SECURE = False  # False dev, True prod
SESSION_COOKIE_HTTPONLY = True  # Pi sekirite
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Sesyon rete louvri

# CSRF
CSRF_COOKIE_AGE = 1209600  # 2 semèn
CSRF_COOKIE_SECURE = False  # False dev, True prod  
CSRF_COOKIE_HTTPONLY = False  # Pèmèt JavaScript aksede

# Sekirite Headers
X_FRAME_OPTIONS = 'DENY'
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000  # 1 ane
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Lòt Sekirite
SECURE_SSL_REDIRECT = False  # True sèlman ak SSL
SECURE_PROXY_SSL_HEADER = None  # Si w pa dèyè proxy


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
