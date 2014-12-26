import bugsnag
import logging

from app import config

from bugsnag.flask import handle_exceptions

from flask import Flask
from flask import g
from flask import redirect
from flask import request


from flask.ext.compress import Compress
from flask.ext.login import current_user
from flask.ext.sqlalchemy import SQLAlchemy

from flask_login import LoginManager

from flask_wtf.csrf import CsrfProtect


# Configure Bugsnag
bugsnag.configure(
    api_key=config.BUGSNAG_KEY,
    project_root=config.PROJECT_PATH,
)


app = Flask(__name__,
            template_folder=config.TEMPLATE_FOLDER,
            static_folder=config.STATIC_FOLDER)
app.config.from_object(config)
Compress(app)
if config.ENV == 'production':
    handle_exceptions(app)

CsrfProtect(app)
app_db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.login_message = None
login_manager.init_app(app)

if config.ENV == 'production':
    stream_handler = logging.StreamHandler()
    app.logger.addHandler(stream_handler)
    app.logger.setLevel(logging.INFO)
else:
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('logs/kateheddleston.log', 'a', 1 * 1024 * 1024, 10)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)


@app.before_request
def before_request():
    g.user = current_user
    if request.headers.get('X_FORWARDED_PROTO') == 'http' and config.ENV != 'dev':
        return redirect(request.url.replace("http://", "https://"))


from app import assets  # NOQA
from app import views  # NOQA
from app import apis  # NOQA
from app.admin import views  # NOQA
from app.admin import apis  # NOQA
