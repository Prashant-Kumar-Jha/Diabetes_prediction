import os
from pathlib import Path
from django.contrib.messages import constants as messages

# ✅ Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# ✅ Secret key for development (keep it secret in production)
SECRET_KEY = 'your-secret-key'

# ✅ Debug mode
DEBUG = True

# ✅ Hosts allowed to serve the project
ALLOWED_HOSTS = ['diabetes-prediction-tr8y.onrender.com', 'localhost', '127.0.0.1']

# ✅ Installed apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'main',  # your app
]

# ✅ Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ✅ URL configuration
ROOT_URLCONF = 'core.urls'

# ✅ Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # Custom template directory
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

# ✅ WSGI application path
WSGI_APPLICATION = 'core.wsgi.application'

# ✅ Database configuration (SQLite for dev)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ✅ Password validation (empty for development)
AUTH_PASSWORD_VALIDATORS = []

# ✅ Localization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# ✅ Static files settings
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# ✅ Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ✅ Login redirect settings
LOGIN_URL = '/login/'

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'