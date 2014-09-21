from app import config

import bugsnag
from bugsnag.flask import handle_exceptions

from flask import Flask
from flask import g
from flask_assets import Bundle
from flask_assets import Environment
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
handle_exceptions(app)

CsrfProtect(app)
app_db = SQLAlchemy(app)
assets = Environment(app)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.login_message = None
login_manager.init_app(app)


base_js = Bundle('js/external/jquery-1.11.1.min.js',
                 'js/external/bootstrap.min.js',
                 'js/external/angular.min.js',
                 'js/external/angular-resource.min.js',
                 'js/external/sanitize.js',
                 'js/external/masonry.pkgd.min.js',
                 'js/external/imagesloaded.pkgd.min.js',
                 'js/internal/angular_app_module.js',
                 'js/internal/gallery.js',
                 filters='jsmin', output='gen/base.%(version)s.js')

admin_js = Bundle('js/internal/admin.js',
                  filters='jsmin', output='gen/admin.%(version)s.js')

base_css = Bundle('css/external/bootstrap.min.css',
                  'css/external/bootstrap-theme.min.css',
                  'css/internal/base.css',
                  'css/internal/navbar.css',
                  filters='cssmin', output='gen/base.%(version)s.css')

post_css = Bundle('css/internal/header.css',
                  'css/internal/gallery.css',
                  filters='cssmin', output='gen/post.%(version)s.css')

about_css = Bundle('css/internal/header.css',
                   'css/internal/about.css',
                   'css/internal/gallery.css',
                   filters='cssmin', output='gen/post.%(version)s.css')

talk_css = Bundle('css/internal/talk.css',
                  'css/internal/footer.css',
                  'css/internal/header.css',
                  filters='cssmin', output='gen/talk.%(version)s.css')

tiles_css = Bundle('css/internal/tiles.css',
                   filters='cssmin', output='gen/tiles.%(version)s.css')

admin_css = Bundle('css/internal/admin.css',
                   filters='cssmin', output='gen/admin.%(version)s.css')

assets.register('base_js', base_js)
assets.register('admin_js', admin_js)
assets.register('base_css', base_css)
assets.register('post_css', post_css)
assets.register('about_css', about_css)
assets.register('talk_css', talk_css)
assets.register('tiles_css', tiles_css)
assets.register('admin_css', admin_css)


@app.before_request
def before_request():
    g.user = current_user

from app import views  # NOQA
from app import admin_views  # NOQA
from app import apis  # NOQA
