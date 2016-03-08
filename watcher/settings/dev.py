# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '(#p)nu9&^8!znw@ow!c0xmw!*4p-y4bad$$q!7^^p4$f8t5$_l'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost']


# Application definition

INSTALLED_APPS = (
    'app',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'watcher.middleware.TimezoneMiddleware'
)

ROOT_URLCONF = 'watcher.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'watcher.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en_US'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR + '/static'


from celery.schedules import crontab

CELERYBEAT_SCHEDULE = {
    'watch-viewers-every-5-seconds': {
        'task': 'app.tasks.watch_viewers',
        'schedule': 5,
    },
    # 'watch-viewers-every-5-seconds': {
    #     'task': 'app.tasks.legacy_watch_viewers',
    #     'schedule': 5,
    # },
    # 'check-streamers-every-1-minute': {
    #     'task': 'app.tasks.legacy_check_streamers',
    #     'schedule': 60,
    # },
    'check-friends-every-day': {
        'task': 'app.tasks.check_friends_and_total_viewers',
        'schedule': crontab(minute=0, hour=3),
    },
    'create-daily-leaderboard-every-day': {
        'task': 'app.tasks.create_daily_leaderboard',
        'schedule': crontab(minute=0, hour=3),
    },
}
LOGIN_REDIRECT_URL = "/live/"
LOGIN_URL = "/authorize-api/"
LOCALE_PATHS = [
    os.path.join(BASE_DIR, "..", "locale")
]
CORS_URLS_REGEX = r'^/api/online/.*$'
