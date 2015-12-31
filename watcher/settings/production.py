import os

from watcher.settings.dev import *

DEBUG = False


def get_db_pass():
    from watcher.settings.dbpass import password
    return password

prod_db_pass = os.environ.get('LCTVADBPASS')

if not prod_db_pass:
    prod_db_pass = get_db_pass()


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': 'lctva.cxs4sbhzhwlk.us-east-1.rds.amazonaws.com',
        'NAME': 'lctvadb',
        'USER': 'lctvauser',
        'PASSWORD': prod_db_pass
    }
}
