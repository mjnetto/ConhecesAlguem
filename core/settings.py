"""
Django settings for Conheces Alguém? project.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Try to use django-environ if available, otherwise use os.environ
try:
    import environ
    env = environ.Env(DEBUG=(bool, False))
    environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
except ImportError:
    # Fallback to os.environ if django-environ is not installed
    import os as env
    def _get_env(key, default=None, cast=None):
        value = os.environ.get(key, default)
        if cast and value:
            return cast(value)
        return value
    env.get = _get_env
    env.list = lambda key, default=[]: os.environ.get(key, ','.join(default) if isinstance(default, list) else default).split(',')
    env.bool = lambda key, default=False: os.environ.get(key, str(default)).lower() in ('true', '1', 'yes')
    env.int = lambda key, default=0: int(os.environ.get(key, default))
    env.db = lambda key, default='sqlite:///db.sqlite3': os.environ.get(key, default)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-me-in-production-123456789')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
# Remove espaços em branco dos hosts
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS if host.strip()]

# Railway automatic host (Railway sets RAILWAY_PUBLIC_DOMAIN)
if os.environ.get('RAILWAY_PUBLIC_DOMAIN'):
    ALLOWED_HOSTS.append(os.environ.get('RAILWAY_PUBLIC_DOMAIN'))

# Adiciona domínios Railway comuns para healthcheck e outros serviços
if os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('RAILWAY_PUBLIC_DOMAIN'):
    ALLOWED_HOSTS.extend([
        'healthcheck.railway.app',
        '*.railway.app',
        '*.up.railway.app',
    ])
    # O middleware RailwayCommonMiddleware também aceita domínios Railway dinamicamente


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'phonenumber_field',
    'crispy_forms',
    'crispy_bootstrap5',
    
    # Local apps
    'accounts',
    'locations',
    'services',
    'bookings',
    'reviews',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # For static files in production
    'django.contrib.sessions.middleware.SessionMiddleware',
    'core.middleware.RailwayCommonMiddleware',  # CommonMiddleware customizado que aceita domínios Railway
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# WhiteNoise configuration for static files (production only)
if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

# Custom error pages
if not DEBUG:
    handler404 = 'core.views.handler404'
    handler403 = 'core.views.handler403'
    handler500 = 'core.views.handler500'

WSGI_APPLICATION = 'core.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL', '')

# Parse DATABASE_URL or use defaults
if DATABASE_URL and (DATABASE_URL.startswith('postgresql://') or DATABASE_URL.startswith('postgres://')):
    import urllib.parse
    url = urllib.parse.urlparse(DATABASE_URL)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': url.path[1:],
            'USER': url.username,
            'PASSWORD': url.password,
            'HOST': url.hostname,
            'PORT': url.port or 5432,
        }
    }
else:
    # Fallback to SQLite for development
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'pt-ao'

TIME_ZONE = 'Africa/Luanda'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
# Apenas adiciona STATICFILES_DIRS se a pasta existir (evita warning em build)
static_dir = BASE_DIR / 'static'
STATICFILES_DIRS = [static_dir] if static_dir.exists() else []

# Media files (User uploaded files)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Phone Number Field
PHONENUMBER_DEFAULT_REGION = 'AO'
PHONENUMBER_DB_FORMAT = 'INTERNATIONAL'

# Email Configuration
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', '')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() in ('true', '1', 'yes')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@conhecesalguem.ao')
BASE_URL = os.environ.get('BASE_URL', 'http://localhost:8000')
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', DEFAULT_FROM_EMAIL)

# CSRF Trusted Origins (para Railway e domínios de produção)
CSRF_TRUSTED_ORIGINS = []
if os.environ.get('RAILWAY_PUBLIC_DOMAIN'):
    domain = os.environ.get('RAILWAY_PUBLIC_DOMAIN')
    CSRF_TRUSTED_ORIGINS.extend([
        f'https://{domain}',
        f'https://*.railway.app',
        f'https://*.up.railway.app',
    ])
elif os.environ.get('BASE_URL'):
    base_url = os.environ.get('BASE_URL')
    if base_url.startswith('https://'):
        CSRF_TRUSTED_ORIGINS.append(base_url)
# Em produção no Railway, aceita todos os domínios Railway
if os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('RAILWAY_PUBLIC_DOMAIN'):
    CSRF_TRUSTED_ORIGINS.extend([
        'https://*.railway.app',
        'https://*.up.railway.app',
    ])

# Security Settings (for production)
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

