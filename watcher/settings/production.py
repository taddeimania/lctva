import os

from watcher.settings.dev import *

DEBUG = True
ALLOWED_HOSTS = ['*']


def get_db_pass():
    from watcher.settings.dbpass import password
    return password

prod_db_pass = os.environ.get('LCTVADBPASS')

if not prod_db_pass:
    prod_db_pass = get_db_pass()


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': 'localhost',
        'NAME': 'lctvadb',
        'USER': 'lctvauser',
        'PASSWORD': prod_db_pass
    }
}
