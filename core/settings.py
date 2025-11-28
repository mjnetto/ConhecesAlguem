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


# Reporting/Blocking configuration
REPORTS_TO_BLOCK_PROFESSIONAL = int(os.environ.get('REPORTS_TO_BLOCK_PROFESSIONAL', '5'))
REPORTS_TO_BLOCK_CLIENT = int(os.environ.get('REPORTS_TO_BLOCK_CLIENT', '5'))

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # Required for allauth
    
    # Third party apps
    'phonenumber_field',
    'crispy_forms',
    'crispy_bootstrap5',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    
    # Local apps
    'accounts',
    'locations',
    'services',
    'bookings',
    'reviews',
]

SITE_ID = 1  # Required for allauth

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # For static files in production
    'core.middleware.RailwayCommonMiddleware',  # CommonMiddleware customizado que aceita domínios Railway
    'django.contrib.sessions.middleware.SessionMiddleware',
    'core.middleware.RailwayCsrfMiddleware',  # CSRF middleware que aceita domínios Railway dinamicamente
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',  # Required for django-allauth
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Authentication backends
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
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

# Try to use dj-database-url if available (better parsing)
try:
    import dj_database_url
    if DATABASE_URL:
        DATABASES = {
            'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
        }
    else:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }
except ImportError:
    # Fallback to manual parsing if dj-database-url is not available
    if DATABASE_URL and (DATABASE_URL.startswith('postgresql://') or DATABASE_URL.startswith('postgres://')):
        import urllib.parse
        try:
            # URL decode first (Railway pode passar URLs codificadas)
            if '%' in DATABASE_URL:
                DATABASE_URL = urllib.parse.unquote(DATABASE_URL)
            
            url = urllib.parse.urlparse(DATABASE_URL)
            
            DATABASES = {
                'default': {
                    'ENGINE': 'django.db.backends.postgresql',
                    'NAME': url.path[1:] if url.path else 'railway',
                    'USER': url.username or 'postgres',
                    'PASSWORD': url.password or '',
                    'HOST': url.hostname or 'localhost',
                    'PORT': url.port or 5432,
                    'CONN_MAX_AGE': 600,
                    'OPTIONS': {
                        'connect_timeout': 10,
                    }
                }
            }
        except Exception as e:
            print(f"⚠️  Erro ao parsear DATABASE_URL: {e}")
            DATABASES = {
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': BASE_DIR / 'db.sqlite3',
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
# Django não aceita wildcards (*), então usamos middleware customizado para aceitar domínios Railway dinamicamente
CSRF_TRUSTED_ORIGINS = []

# Adiciona domínio específico se fornecido
if os.environ.get('RAILWAY_PUBLIC_DOMAIN'):
    domain = os.environ.get('RAILWAY_PUBLIC_DOMAIN')
    CSRF_TRUSTED_ORIGINS.append(f'https://{domain}')

# Adiciona BASE_URL se fornecido
if os.environ.get('BASE_URL'):
    base_url = os.environ.get('BASE_URL', '').rstrip('/')
    if base_url.startswith('https://'):
        if base_url not in CSRF_TRUSTED_ORIGINS:
            CSRF_TRUSTED_ORIGINS.append(base_url)

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
    # Force HTTPS for allauth URLs
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    USE_TLS = True

# Django Allauth Configuration (updated for allauth 0.57+)
ACCOUNT_LOGIN_METHODS = {'email'}  # Use email for login
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']  # Required fields
ACCOUNT_EMAIL_VERIFICATION = 'none'  # Opcional: 'mandatory' para exigir verificação
ACCOUNT_UNIQUE_EMAIL = True
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_AUTO_SIGNUP = True  # Cria User automaticamente
SOCIALACCOUNT_ADAPTER = 'accounts.adapters.CustomSocialAccountAdapter'
ACCOUNT_ADAPTER = 'accounts.adapters.CustomAccountAdapter'
LOGIN_REDIRECT_URL = '/accounts/google-callback/'
ACCOUNT_SIGNUP_REDIRECT_URL = '/accounts/choose-user-type/'
SOCIALACCOUNT_LOGIN_REDIRECT_URL = '/accounts/choose-user-type/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'
SOCIALACCOUNT_LOGIN_ON_GET = True
# Force HTTPS for OAuth redirects in production
if not DEBUG:
    ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'
    # Railway sets X-Forwarded-Proto header, so Django knows it's HTTPS
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    # Ensure allauth uses HTTPS for redirect URIs
    import django.contrib.sites.models
    # Override Site.get_current() to force HTTPS if needed

# Google OAuth Settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'APP': {
            'client_id': os.environ.get('GOOGLE_OAUTH_CLIENT_ID', ''),
            'secret': os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET', ''),
            'key': ''
        }
    }
}

