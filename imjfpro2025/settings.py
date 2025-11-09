"""
✅ SETTINGS DJANGO POU PROJÈ IMJF_PRO2025
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

# ===============================================================
# 1️⃣  CHEMEN BAZ PWOJÈ A
# ===============================================================
BASE_DIR = Path(__file__).resolve().parent.parent


# ===============================================================
# 2️⃣  MEDIA & STATIC FILES
# ===============================================================
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATIC_URL = '/static/'
# ✅ KORIJE: Asire w ke dosye static la egziste oswa kreye li
# STATICFILES_DIRS = [BASE_DIR / 'static']  # ⬅️ De-komante si w gen dosye static
STATICFILES_DIRS = []  # ⬅️ Kounye a, mete vid pou evite avètisman

# ✅ Opsyonèl: Kreye yon dosye static si w bezwen
# STATIC_ROOT = BASE_DIR / 'staticfiles'  # Pou kolekte static files


# ===============================================================
# 3️⃣  FONKSYON POU JERE VARIABLE ENVIRONNEMENT
# (Bon pratik pou pa mete kle sekirite yo dirèk nan kòd)
# ===============================================================
def get_env_setting(name: str, default=None, required: bool = False):
    val = os.environ.get(name, default)
    if required and (val is None or val == ''):
        raise ImproperlyConfigured(f"Set the {name} environment variable")
    return val


# ===============================================================
# 4️⃣  KONFIGURASYON SEKIRITE DJANGO
# ===============================================================

# 🔐 Kle sekrè (pa janm mete sa piblikman)
SECRET_KEY = get_env_setting('DJANGO_SECRET_KEY', "django-insecure-dev-placeholder")

# 🔧 Mode dev/prod
DEBUG = str(get_env_setting('DJANGO_DEBUG', '1')).lower() in ('1', 'true', 'yes')

# 🌍 Host ki gen dwa konekte
allowed_hosts_env = get_env_setting('DJANGO_ALLOWED_HOSTS', '')
if allowed_hosts_env:
    ALLOWED_HOSTS = [h.strip() for h in allowed_hosts_env.split(',') if h.strip()]
else:
    ALLOWED_HOSTS = ['127.0.0.1', 'localhost']


# ===============================================================
# 5️⃣  KONFIGURASYON OTANTIFIKASYON AK RBAC
# ===============================================================

# ✅ KORIJE: Ajoute AUTHENTICATION_BACKENDS ki kòrèk pou django-axes
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',  # ⬅️ Obligatwa pou django-axes >=5.0
    'django.contrib.auth.backends.ModelBackend',
]

AUTH_USER_MODEL = 'utilisateurs.CustomUser'
LOGIN_URL = '/utilisateurs/login/'
LOGIN_REDIRECT_URL = '/utilisateurs/dash_admin/'
LOGOUT_REDIRECT_URL = '/utilisateurs/login/'

# RBAC (Role-Based Access Control) ap jere ak permissions natif Django:
# is_superuser → tout aksè
# groups → wòl espesifik (admin, sekrete, pwofesè, elèv, elatriye)


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
    'widget_tweaks',         # Pou customize fòm yo
    'auditlog',              # Pou swiv aksyon itilizatè yo
    'axes',                  # Pwoteksyon kont brute-force login

    # Apps pèsonèl ou yo
    'utilisateurs',
    'eleves',
    'enseignants',
    'cours',
    'core',
    'matieres',
    'classes',
    'inscriptions',
]


# ===============================================================
# 7️⃣  PASSWORD VALIDATORS (Obligatwa pou sekirite modpas)
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
    'axes.middleware.AxesMiddleware',                   # Pwoteksyon brute-force
    'django.middleware.security.SecurityMiddleware',    # Sekirite SSL & headers
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # ❌ RETIRE: 'django.contrib.auth.backends.ModelBackend',  # ⬅️ Sa pa yon middleware!
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'auditlog.middleware.AuditlogMiddleware',          
    'core.middleware.DatabaseCheckMiddleware',          # Swiv aksyon yo
    # 'simple_history.middleware.HistoryRequestMiddleware',  # ⬅️ Kòmante si w pa itilize simple_history
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
            ],
        },
    },
]

WSGI_APPLICATION = 'imjfpro2025.wsgi.application'


# ===============================================================
# 🔟  DATABASE (MySQL Railway)
# ===============================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'railway',
        'USER': 'root',
        'PASSWORD': 'uSqQvJQqcAVXMknyUcAyKyqgYXsMOqts',
        'HOST': 'interchange.proxy.rlwy.net',
        'PORT': '51525',
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
SESSION_COOKIE_AGE = 1800  # 30 min inaktivite


# ===============================================================
# 1️⃣3️⃣  HTTP SECURITY HEADERS
# ===============================================================
X_FRAME_OPTIONS = 'DENY'
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = not DEBUG  # Oblige HTTPS nan prod
SECURE_REFERRER_POLICY = "same-origin"
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"
SECURE_CROSS_ORIGIN_EMBEDDER_POLICY = "require-corp"


# ===============================================================
# 1️⃣4️⃣  DJANGO-AXES (Anti brute-force login)
# ===============================================================
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1  # 1 heure
# ❌ RETIRE: AXES_USE_USER_AGENT = True  # ⬅️ Deprecated nan django-axes >=5.0
AXES_LOCKOUT_TEMPLATE = 'lockout.html'
AXES_ENABLED = True

# ✅ AJOUTE: Konfigirasyon adisyonèl pou django-axes
AXES_HANDLER = 'axes.handlers.database.AxesDatabaseHandler'
AXES_RESET_ON_SUCCESS = True
AXES_LOCKOUT_PARAMETERS = ["ip_address", "username"]


# ===============================================================
# 1️⃣5️⃣  LOGGING (Pou suiv erè ak aksyon)
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
# 1️⃣6️⃣  KONFIGIRASYON POU FILE UPLOADS
# ===============================================================
# Asire w ke uploads yo sekirize
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000   # Anpeche atak DOS

# ✅ KOMANTE: Avètisman yo ki te rezoud
"""
✅ AVÈTISMAN YO REZOUD:

1. ✅ (axes.W003) - Ajoute 'axes.backends.AxesStandaloneBackend' nan AUTHENTICATION_BACKENDS
2. ✅ (axes.W004) - Retire 'AXES_USE_USER_AGENT' ki te deprecated
3. ✅ (staticfiles.W004) - STATICFILES_DIRS vid oswa korije chemen an

❌ AVÈTISMAN KI POKO REZOUD:
- Okenn - tout avètisman yo rezoud!
"""