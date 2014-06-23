from app import config
from flask import Flask
from flask_assets import Bundle
from flask_assets import Environment
from flask.ext.sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CsrfProtect


app = Flask(__name__,
            template_folder=config.TEMPLATE_FOLDER,
            static_folder=config.STATIC_FOLDER)
app.config.from_object(config)

CsrfProtect(app)
app_db = SQLAlchemy(app)
assets = Environment(app)

base_js = Bundle('js/external/jquery-1.11.1.min.js',
                 'js/external/bootstrap.min.js',
                 'js/external/angular.min.js',
                 'js/external/angular-resource.min.js',
                 'js/internal/angular_app_module.js',
                 filters='jsmin', output='gen/base.%(version)s.js')

base_css = Bundle('css/external/bootstrap.min.css',
                  'css/external/bootstrap-theme.min.css',
                  'css/external/font-awesome.min.css',
                  'css/internal/style.css',
                  filters='cssmin', output='gen/auth.%(version)s.css')

assets.register('base_js', base_js)
assets.register('base_css', base_css)

from app import views
