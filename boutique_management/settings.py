"""
Django settings for boutique_management project.
"""

from pathlib import Path
import os
import dj_database_url
import environ

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file if it exists (local development)
env = environ.Env()
env_file = BASE_DIR / ".env"
if env_file.exists():
    environ.Env.read_env(str(env_file))

# SECURITY: SECRET_KEY must be set via environment variable in production.
# Generate one with: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    import sys
    _is_server = (
        'runserver' in sys.argv
        or 'gunicorn' in str(sys.argv)
        or os.environ.get("VERCEL")        # Vercel serverless
        or os.environ.get("RAILWAY_ENVIRONMENT")  # Railway
    )
    _is_management_cmd = not _is_server
    if _is_management_cmd:
        # During management commands (migrate, collectstatic, etc.) use a temp key
        SECRET_KEY = "temp-key-for-management-commands-only"
    elif os.environ.get("DEBUG", "false").lower() == "true":
        SECRET_KEY = "dev-only-insecure-key-change-in-production"
    else:
        raise RuntimeError(
            "SECRET_KEY environment variable is not set. "
            "Set it before running in production."
        )

# SECURITY: DEBUG defaults to False. Set DEBUG=true in your environment only for local dev.
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"

# SECURITY: ALLOWED_HOSTS should be explicitly set in production, not wildcarded.
_allowed_hosts_env = os.environ.get("ALLOWED_HOSTS", "")
if _allowed_hosts_env:
    ALLOWED_HOSTS = [h.strip() for h in _allowed_hosts_env.split(",") if h.strip()]
else:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1"] if DEBUG else []

# Vercel deployment: allow .vercel.app subdomains
VERCEL_URL = os.environ.get("VERCEL_URL")
if VERCEL_URL:
    ALLOWED_HOSTS.append(VERCEL_URL)
    ALLOWED_HOSTS.append(".vercel.app")

# Railway deployment: allow .railway.app subdomains
RAILWAY_PUBLIC_DOMAIN = os.environ.get("RAILWAY_PUBLIC_DOMAIN")
if RAILWAY_PUBLIC_DOMAIN:
    ALLOWED_HOSTS.append(RAILWAY_PUBLIC_DOMAIN)
    ALLOWED_HOSTS.append(".railway.app")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "boutique_management.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'templates'],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "boutique_management.wsgi.application"

DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Supabase / cloud Postgres: enable SSL and configure for connection pooler
_db_url = os.environ.get("DATABASE_URL", "")
if _db_url and "sqlite" not in _db_url:
    DATABASES["default"]["OPTIONS"] = {
        "sslmode": "require",
    }
    # Supabase Supavisor pooler uses port 6543 in transaction mode.
    # Django must disable server-side cursors when using transaction pooling
    # because prepared statements don't persist across pooled connections.
    if "pooler.supabase.com" in _db_url or os.environ.get("SUPABASE_DB_POOLER") == "true":
        DATABASES["default"]["DISABLE_SERVER_SIDE_CURSORS"] = True

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# CSRF trusted origins
CSRF_TRUSTED_ORIGINS = []
if VERCEL_URL:
    CSRF_TRUSTED_ORIGINS.append(f"https://{VERCEL_URL}")
if RAILWAY_PUBLIC_DOMAIN:
    CSRF_TRUSTED_ORIGINS.append(f"https://{RAILWAY_PUBLIC_DOMAIN}")
_csrf_origins_env = os.environ.get("CSRF_TRUSTED_ORIGINS", "")
if _csrf_origins_env:
    CSRF_TRUSTED_ORIGINS.extend([o.strip() for o in _csrf_origins_env.split(",") if o.strip()])

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'
LOGIN_URL = '/login/'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Logging: output errors to console/stdout so Railway captures them
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "WARNING",
        },
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}

# Security headers (active in production when DEBUG=False)
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_SSL_REDIRECT = os.environ.get("SECURE_SSL_REDIRECT", "false").lower() == "true"
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
