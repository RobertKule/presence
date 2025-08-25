from pathlib import Path
from decouple import config, Csv
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------
# Sécurité & Config de base
# ---------------------------
SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="127.0.0.1", cast=Csv())

# Auth
LOGIN_URL = 'core:login'  
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = 'core:login'
AUTH_USER_MODEL = "core.User"

# ---------------------------
# Applications
# ---------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'widget_tweaks',
    # Apps internes
    'core.apps.CoreConfig',  # au lieu de juste 'core'
    
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.EnseignantRestrictionMiddleware',
]

ROOT_URLCONF = 'gestion_presences.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
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

WSGI_APPLICATION = 'gestion_presences.wsgi.application'

# ---------------------------
# Base de données
# ---------------------------
DATABASES = {
    'default': dj_database_url.config(
        default=config("DATABASE_URL", default=f"sqlite:///{BASE_DIR}/dbpresence.sqlite3"),
        conn_max_age=600,
        ssl_require=False
    ),
    'OPTIONS': {
            'timeout': 20,  # secondes
        }
}

# ---------------------------
# Sécurité & Auth
# ---------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {"NAME": 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {"NAME": 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {"NAME": 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ---------------------------
# Internationalisation
# ---------------------------
LANGUAGE_CODE = "fr"
TIME_ZONE = 'Africa/Johannesburg'  # UTC+2 toute l'année (Afrique du Sud)
USE_I18N = True
USE_TZ = True

# ---------------------------
# Fichiers statiques & médias
# ---------------------------

STATIC_URL = "/static/"

STATICFILES_DIRS = [BASE_DIR / "static"]  # tes fichiers locaux (CSS, JS, etc.)
STATIC_ROOT = BASE_DIR / "staticfiles"    # dossier où collectstatic copie tout

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Stockage des fichiers statiques en production
if not DEBUG:  
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


# ---------------------------
# Clé auto
# ---------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

