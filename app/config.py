import os

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
TWITTER_KEY = os.environ.get('TWITTER_KEY')
TWITTER_SECRET = os.environ.get('TWITTER_SECRET')
CONSUMER_KEY = os.environ.get('CONSUMER_KEY')
CONSUMER_SECRET = os.environ.get('CONSUMER_SECRET')

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_IMAGE_BUCKET_KEY = 'images.kateheddleston.com'

STATIC_BASE = 'https://s3.amazonaws.com/static.kateheddleston.com'
IMAGES_BASE = 'https://s3.amazonaws.com/images.kateheddleston.com'

if os.environ.get('ENVIRONMENT') == 'dev':
    APP_BASE_LINK = 'http://localhost:' + str(PORT)
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/kateheddleston_db'
else:
    APP_BASE_LINK = 'https://www.kateheddleston.com'
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
