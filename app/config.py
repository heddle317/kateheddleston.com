import os

PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))
ROOT_PATH = BASE_DIR = os.path.join(os.path.dirname(__file__), '..')

# REDIS_URL='redis://localhost:6379'
PORT = 8000
STATIC_FOLDER = os.path.join(ROOT_PATH, 'static')
TEMPLATE_FOLDER = os.path.join(ROOT_PATH, 'templates')
SECRET_KEY = os.environ.get('SECRET_KEY')
CSRF_ENABLED = True
SQLALCHEMY_MIGRATE_REPO = os.path.join(ROOT_PATH, 'db_repository')
DATABASE_SERVICE = "kateheddleston-db"
MODEL_HASH = os.environ.get('MODEL_HASH')
IMAGES_BASE = 'http://images.kateheddleston.com'
STATIC_BASE = 'http://static.kateheddleston.com'

if os.environ.get('ENVIRONMENT') == 'dev':
    APP_BASE_LINK = 'http://localhost:' + str(PORT)
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/kateheddleston_db'
else:
    APP_BASE_LINK = ''
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
