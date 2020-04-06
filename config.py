import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'WEvZt&hk$8QKZD5'
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

class ProductionConfig(Config):
    DEBUG = False

class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True

class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True

class TestingConfig(Config):
    TESTING = True

if os.environ.get('DATABSE_URL') is None:
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/patient_record'
else:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']