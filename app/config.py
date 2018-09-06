import os

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_S3_BASE = 'https://s3.amazonaws.com'
AWS_IMAGE_BUCKET = os.environ.get('AWS_IMAGE_BUCKET')
AWS_STATIC_BUCKET = os.environ.get('AWS_STATIC_BUCKET')
AWS_IMAGES_BASE = '{}/{}'.format(AWS_S3_BASE, AWS_IMAGE_BUCKET)
AWS_STATIC_BASE = 'https://s3-us-west-2.amazonaws.com/{}'.format(AWS_STATIC_BUCKET)

BUGSNAG_KEY = os.environ.get('BUGSNAG_KEY')

EMAIL_PERSONAL = os.environ.get('EMAIL_PERSONAL')
EMAIL_SENDER = os.environ.get('EMAIL_SENDER')

ENVIRONMENT = os.environ.get('ENVIRONMENT')

FACEBOOK_APP_ID = os.environ.get('FACEBOOK_APP_ID')
FACEBOOK_APP_SECRET = os.environ.get('FACEBOOK_APP_SECRET')

FLASK_CSRF_ENABLED = True
FLASK_PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))
FLASK_ROOT_PATH = BASE_DIR = os.path.join(os.path.dirname(__file__), '..')
FLASK_STATIC_FOLDER = os.path.join(FLASK_ROOT_PATH, 'static')
FLASK_TEMPLATE_FOLDER = os.path.join(FLASK_ROOT_PATH, 'templates')
MODEL_HASH = os.environ.get('FLASK_MODEL_HASH')
SECRET_KEY = os.environ.get('SECRET_KEY')
WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY')

LOGENTRIES_TOKEN = os.environ.get('LOGENTRIES_TOKEN')

REDIS_URL= os.environ.get('REDIS_URL', 'redis://localhost:6379')

POSTMARKAPP_API_KEY = os.environ.get('POSTMARKAPP_API_KEY')

TWITTER_CONSUMER_KEY = os.environ.get('TWITTER_CONSUMER_KEY')
TWITTER_CONSUMER_SECRET = os.environ.get('TWITTER_CONSUMER_SECRET')

SQLALCHEMY_MIGRATE_REPO = os.path.join(FLASK_ROOT_PATH, 'db_repository')

if ENVIRONMENT == 'dev':
    PORT = 8000
    APP_BASE_LINK = 'http://localhost:' + str(PORT)
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/kateheddleston_db'
else:
    APP_BASE_LINK = 'https://www.kateheddleston.com'
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
