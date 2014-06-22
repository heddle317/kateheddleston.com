import os


# REDIS_URL='redis://localhost:6379'
PORT = 5000
STATIC_FOLDER = '../static'
TEMPLATE_FOLDER = '../templates'
SECRET_KEY = os.environ.get('SECRET_KEY')
CSRF_ENABLED = True
if os.environ.get('ENVIRONMENT') == 'dev':
    APP_BASE_LINK = 'http://localhost:5000'
    DEBUG = True
else:
    APP_BASE_LINK = ''
    DEBUG = False
