import bugsnag
import logging

from app import config
from bugsnag.flask import handle_exceptions
from flask import Flask
from flask import g
from flask import redirect
from flask import request
from flask import send_from_directory

from flask_bcrypt import Bcrypt
from flask_compress import Compress
from flask_login import current_user
from flask_sqlalchemy import SQLAlchemy

from flask_login import LoginManager
from flask_wtf.csrf import CsrfProtect

from jinja2 import Environment
from jinja2 import FileSystemLoader

from rq import Queue
from worker import conn


q = Queue(connection=conn)
env = Environment(loader=FileSystemLoader(config.FLASK_TEMPLATE_FOLDER))

app = Flask(__name__,
            template_folder=config.FLASK_TEMPLATE_FOLDER,
            static_folder=config.FLASK_STATIC_FOLDER)
app.config.from_object(config)
Compress(app)
CsrfProtect(app)
bcrypt = Bcrypt(app)
app_db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.login_message = None
login_manager.init_app(app)

if config.ENVIRONMENT == 'production':
    # Configure Bugsnag
    bugsnag.configure(
        api_key=config.BUGSNAG_KEY,
        project_root=config.FLASK_PROJECT_PATH,
    )
    handle_exceptions(app)

    # Configure Logging
    stream_handler = logging.StreamHandler()
    app.logger.addHandler(stream_handler)
    app.logger.setLevel(logging.INFO)
else:
    # Configure local logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('logs/kateheddleston.log', 'a', 1 * 1024 * 1024, 10)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)


@app.before_request
def before_request():

    g.user = current_user
    if request.headers.get('X_FORWARDED_PROTO') == 'http' and config.ENVIRONMENT != 'dev':
        return redirect(request.url.replace("http://", "https://"))


@app.route('/static/<path:path>')
def send_js(path):
    return send_from_directory('static', path)


from app import assets  # NOQA
from app import views  # NOQA
from app import apis  # NOQA
from app.admin import views  # NOQA
from app.admin import apis  # NOQA
