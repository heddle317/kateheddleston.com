import os

ENV = os.environ.get('ENVIRONMENT')

PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))
ROOT_PATH = BASE_DIR = os.path.join(os.path.dirname(__file__), '..')

# REDIS_URL='redis://localhost:6379'
PORT = 8080
STATIC_FOLDER = os.path.join(ROOT_PATH, 'static')
TEMPLATE_FOLDER = os.path.join(ROOT_PATH, 'templates')
SECRET_KEY = os.environ.get('SECRET_KEY')
CSRF_ENABLED = True
SQLALCHEMY_MIGRATE_REPO = os.path.join(ROOT_PATH, 'db_repository')
DATABASE_SERVICE = "kateheddleston-db"
MODEL_HASH = os.environ.get('MODEL_HASH')
BUGSNAG_KEY = os.environ.get('BUGSNAG_KEY')
PERSONAL_EMAIL = os.environ.get('PERSONAL_EMAIL')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL')
POSTMARKAPP_API_KEY = os.environ.get('POSTMARKAPP_API_KEY')
TWITTER_CONSUMER_KEY = os.environ.get('TWITTER_CONSUMER_KEY')
TWITTER_CONSUMER_SECRET = os.environ.get('TWITTER_CONSUMER_SECRET')

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

IMAGE_BUCKET = os.environ.get('IMAGE_BUCKET')
STATIC_BUCKET = os.environ.get('STATIC_BUCKET')

S3_BASE = 'https://s3.amazonaws.com'
IMAGES_BASE = '{}/{}'.format(S3_BASE, IMAGE_BUCKET)
STATIC_BASE = '{}/{}'.format(S3_BASE, STATIC_BUCKET)

LOGENTRIES_TOKEN = os.environ.get('LOGENTRIES_TOKEN')


if ENV == 'dev':
    APP_BASE_LINK = 'http://localhost:' + str(PORT)
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/kateheddleston_db'
else:
    APP_BASE_LINK = 'https://www.kateheddleston.com'
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
