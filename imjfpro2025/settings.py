"""
✅ SETTINGS DJANGO POU IMJF_PRO2025
Vèsyon sekirize ak konfigirasyon pou:
 - HTTPS & Cookies sekirite
 - Upload Validation
 - Brute-force pwoteksyon
 - Auditlog & RBAC
 - Bon pratik sekirite pou pwodiksyon
"""

from pathlib import Path
import os
from django.core.exceptions import ImproperlyConfigured
from datetime import timedelta  # ✅ AJOUTE POU AXES_COOLOFF_TIME

# ===============================================================
# 1️⃣  CHEMEN BAZ PWOJÈ A
# ===============================================================
BASE_DIR = Path(__file__).resolve().parent.parent


# ===============================================================
# 2️⃣  MEDIA & STATIC FILES
# ===============================================================
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATIC_URL = 'static/'
# STATICFILES_DIRS = [BASE_DIR / 'static']  # Folder pou dev
#STATIC_ROOT = BASE_DIR / 'staticfiles'   # Pou prod + collectstatic


# ===============================================================
# 3️⃣  FONKSYON POU JERE VARIABLE ENVIRONNEMENT
# ===============================================================
def get_env_setting(name: str, default=None, required: bool = False):
    val = os.environ.get(name, default)
    if required and (val is None or val == ''):
        raise ImproperlyConfigured(f"Set the {name} environment variable")
    return val


# ===============================================================
# 4️⃣  KONFIGIRASYON SEKIRITE DJANGO
# ===============================================================
SECRET_KEY = get_env_setting('DJANGO_SECRET_KEY', "django-insecure-dev-placeholder")
DEBUG = str(get_env_setting('DJANGO_DEBUG', '1')).lower() in ('1', 'true', 'yes')

allowed_hosts_env = get_env_setting('DJANGO_ALLOWED_HOSTS', '')
ALLOWED_HOSTS = [h.strip() for h in allowed_hosts_env.split(',') if h.strip()] if allowed_hosts_env else ['127.0.0.1', 'localhost']


# ===============================================================
# 5️⃣  OTANTIFIKASYON & RBAC
# ===============================================================
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
]

AUTH_USER_MODEL = 'utilisateurs.CustomUser'
LOGIN_URL = '/utilisateurs/login/'
LOGIN_REDIRECT_URL = '/utilisateurs/dash_admin/'
LOGOUT_REDIRECT_URL = '/utilisateurs/login/'


# ===============================================================
# 6️⃣  APPS YO
# ===============================================================
INSTALLED_APPS = [
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Ekstansyon
    'widget_tweaks',         
    'auditlog',              
    'axes',                  

    # Apps pèsonèl
    'utilisateurs',
    'eleves',
    'enseignants',
    'cours',
    'core',
    'annee_scolaire',
    'matieres',
    'classes',
    'inscriptions',
    'parametre',
    # Storage for production (S3) - django-storages
    'storages',
]

# Default model used by django-auditlog (prevents AttributeError if missing)
AUDITLOG_LOGENTRY_MODEL = 'auditlog.LogEntry'


# ===============================================================
# 7️⃣  PASSWORD VALIDATORS
# ===============================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ===============================================================
# 8️⃣  MIDDLEWARE
# ===============================================================
MIDDLEWARE = [
    'axes.middleware.AxesMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'auditlog.middleware.AuditlogMiddleware',          
    'core.middleware.DatabaseCheckMiddleware',          
]


# ===============================================================
# 9️⃣  TEMPLATES
# ===============================================================
ROOT_URLCONF = 'imjfpro2025.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                
                'annee_scolaire.context_processors.annee_scolaire_actuelle',
            ],
        },
    },
]

WSGI_APPLICATION = 'imjfpro2025.wsgi.application'


# ===============================================================
# 🔟  DATABASE (MySQL via Railway)
# ===============================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'railway',
        'USER': 'root',
        'PASSWORD': 'WrspyRaJxoIuUOMUkFedxcGCQkTNFYrC',
        'HOST': 'interchange.proxy.rlwy.net',
        'PORT': '18186',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    },
}


# ===============================================================
# 1️⃣1️⃣  LANG & TIMEZONE
# ===============================================================
LANGUAGE_CODE = 'fr'
TIME_ZONE = 'America/Port-au-Prince'
USE_I18N = True
USE_TZ = True


# ===============================================================
# 1️⃣2️⃣  COOKIES & SESSIONS SEKIRITE
# ===============================================================
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 1800  # 30 min


# ===============================================================
# 1️⃣3️⃣  HTTP SECURITY HEADERS
# ===============================================================
X_FRAME_OPTIONS = 'DENY'
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = not DEBUG
SECURE_REFERRER_POLICY = "same-origin"
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"
SECURE_CROSS_ORIGIN_EMBEDDER_POLICY = "require-corp"


# ===============================================================
# 1️⃣4️⃣  DJANGO-AXES (Anti brute-force login)
# ===============================================================
AXES_FAILURE_LIMIT = 10  # ✅ Ogmante limit: 10 tantativ avan blokaj
AXES_COOLOFF_TIME = timedelta(minutes=1)  # Debloke apre 1 minit
# AXES_LOCKOUT_TEMPLATE = None  # Oswa ou ka kreye 'lockout.html'
AXES_ENABLED = True
AXES_HANDLER = 'axes.handlers.database.AxesDatabaseHandler'
AXES_RESET_ON_SUCCESS = True  # Efase konte echwe apre siksè
AXES_LOCKOUT_PARAMETERS = ["username"]  # ✅ Jis bloke selon username (pa IP)


# ===============================================================
# 1️⃣5️⃣  LOGGING
# ===============================================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'auditlog': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'axes': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}


# ===============================================================
# 1️⃣6️⃣  FILE UPLOADS
# ===============================================================
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000


# ===============================================================
# 1️⃣7️⃣  DEFAULT PRIMARY KEY (bon pratik Django 3.2+)
# ===============================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ------------------ S3 / django-storages configuration ------------------
# Enable S3-backed media storage by setting USE_S3=1 in environment.
USE_S3 = str(get_env_setting('USE_S3', '0')).lower() in ('1', 'true', 'yes')

if USE_S3:
    # Use django-storages S3 backend for uploaded files
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

    AWS_ACCESS_KEY_ID = get_env_setting('AWS_ACCESS_KEY_ID', required=True)
    AWS_SECRET_ACCESS_KEY = get_env_setting('AWS_SECRET_ACCESS_KEY', required=True)
    AWS_STORAGE_BUCKET_NAME = get_env_setting('AWS_STORAGE_BUCKET_NAME', required=True)
    AWS_S3_REGION_NAME = get_env_setting('AWS_S3_REGION_NAME', '')
    # Optional custom domain (CloudFront)
    AWS_S3_CUSTOM_DOMAIN = get_env_setting('AWS_S3_CUSTOM_DOMAIN', f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com")

    # Recommended: do not use canned ACLs
    AWS_DEFAULT_ACL = None
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }

    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/'
else:
    # Local filesystem fallback (already defined above)
    MEDIA_URL = MEDIA_URL
    MEDIA_ROOT = MEDIA_ROOT