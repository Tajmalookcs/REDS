from config.settings import *

# ─────────────────────────────────────────
# LAN DEPLOYMENT SETTINGS
# ─────────────────────────────────────────

# Allow all hosts on LAN
ALLOWED_HOSTS = ['*']

# Turn off debug in production
DEBUG = False

# Secret key — change this in real deployment
SECRET_KEY = 'reds-lan-secret-key-change-this-2026'

# Static files served locally
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL  = '/static/'

# Media files
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL  = '/media/'

# SQLite stays same — no change needed for LAN
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Security settings — relaxed for LAN only
SESSION_COOKIE_SECURE   = False
CSRF_COOKIE_SECURE      = False
SECURE_SSL_REDIRECT     = False