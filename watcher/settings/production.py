import os

from watcher.settings.dev import *
from watcher.settings.dbpass import password

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': 'lctva.cxs4sbhzhwlk.us-east-1.rds.amazonaws.com',
        'NAME': 'lctvadb',
        'USER': 'lctvauser',
        'PASSWORD': os.environ.get('LCTVADBPASS') or password
    }
}
