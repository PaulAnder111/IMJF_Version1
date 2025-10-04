
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-ch22z%!mjwic7lb3byy-tkq@c6&##j+fnk@9pa6b%8-^rkjn35'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']
# -----------------------------------------------------
AUTH_USER_MODEL = 'utilisateurs.CustomUser'
STATIC_URL = '/static/'
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/utilisateurs/dash_admin/'
LOGOUT_REDIRECT_URL = '/login/'
# ------------------------------------------------------
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'utilisateurs',
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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

DATABASES= {
    'default': {
      'ENGINE': 'django.db.backends.mysql',  # Oswa 'django.db.backends.postgresql' si w ap itilize PostgreSQL
        'NAME': 'railway',  # Oswa non baz done ou nan Supabase
        'USER': 'root',  # Non itilizatè Supabase
        'PASSWORD': 'IZLZXjXURkyeSQEtOKfpRZHkluXFNKbO',  # Modpas baz done
        'HOST': 'tramway.proxy.rlwy.net',  # Hostname ou
        'PORT': '25355',
        'OPTIONS': {
           'charset': 'utf8mb4',  # Pou MySQL, asire w ke w ap itilize utf8mb4 pou sipòte tout karaktè
              'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
        },
    }
}
import socket
socket.getaddrinfo = lambda *args: [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (args[0], args[1]))]



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