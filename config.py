import os

basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True
CSRF_SESSION_KEY = 'WEvZt&hk$8QKZD5'

if os.environ.get('DATABASE_URL') is None:
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/patient_record'
else:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']