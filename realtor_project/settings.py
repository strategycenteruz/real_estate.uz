import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-@ttn8sw+4mnws1_zw=gddu7jxnp&yv3-tt)4_ujn8n2j0j4juu'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'listings.apps.ListingsConfig',
    'rest_framework',
    'corsheaders',
    'django.contrib.humanize',
    'widget_tweaks',
    'crispy_forms',
    'crispy_bootstrap5',
    'users',
]

AUTH_USER_MODEL = "users.User"

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'realtor_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # <-- bu muhim
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

WSGI_APPLICATION = 'realtor_project.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

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

LANGUAGE_CODE = 'ru-Ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"


CORS_ALLOW_ALL_ORIGINS = True  # yoki xavfsizroq variant keyin qo‘shamiz

MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


# vaqtinchalik fayllar uchun alohida papka
TMP_UPLOAD_DIR = MEDIA_ROOT / "tmp"
os.makedirs(TMP_UPLOAD_DIR, exist_ok=True)

STATICFILES_DIRS = [
    BASE_DIR / "static",  # sizda "frontend" emas, "static" bo‘lsa
]

# STATIC_ROOT = BASE_DIR / "staticfiles"
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/


# Media fayllar uchun asosiy URL
SITE_URL = "http://127.0.0.1:4040"  # Localhost uchun
# Agar hosting/serverda bo‘lsa: "https://yourdomain.com"
ALLOWED_HOSTS = ["real-estate-uz-2.onrender.com", "localhost", "127.0.0.1"]


BOT_TOKEN = "7778665104:AAEEf4GljOHqIcQJ99yvjRVk-88NK8TLs6s"
CHANNEL_ID = -1002826333742   # albatta minus bilan!

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

TELEGRAM_BOT_TOKEN = "8017089429:AAF5PDZdUcKQEF-OJaQCbepREzQctfH4QZA"
TELEGRAM_CHANNEL_ID = "@realtor_price"  # yoki -1001234567890 (ID ko‘rinishida)
