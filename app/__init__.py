import bugsnag
import logging

from app import config

from bugsnag.flask import handle_exceptions

from flask import Flask
from flask import g
from flask import redirect
from flask import request

from flask_assets import Bundle
from flask_assets import Environment

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
handle_exceptions(app)

CsrfProtect(app)
app_db = SQLAlchemy(app)
assets = Environment(app)

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


about_css = Bundle('css/internal/about.css',
                   filters='cssmin', output='gen/post.%(version)s.css')

admin_css = Bundle('css/internal/admin.css',
                   filters='cssmin', output='gen/admin.%(version)s.css')

base_css = Bundle('css/external/bootstrap.min.css',
                  'css/external/bootstrap-theme.min.css',
                  'css/internal/base.css',
                  'css/internal/navbar.css',
                  filters='cssmin', output='gen/base.%(version)s.css')

comment_css = Bundle('css/internal/comments.css',
                     filters='cssmin', output='gen/comment.%(version)s.css')

contact_css = Bundle('css/internal/contact.css',
                     filters='cssmin', output='gen/contact.%(version)s.css')

header_css = Bundle('css/internal/header.css',
                    filters='cssmin', output='gen/header.%(version)s.css')

post_css = Bundle('css/internal/gallery.css',
                  'css/internal/gallery_nav.css',
                  filters='cssmin', output='gen/post.%(version)s.css')

talk_css = Bundle('css/internal/talk.css',
                  'css/internal/footer.css',
                  'css/internal/header.css',
                  filters='cssmin', output='gen/talk.%(version)s.css')

tiles_css = Bundle('css/internal/tiles.css',
                   filters='cssmin', output='gen/tiles.%(version)s.css')

assets.register('about_css', about_css)
assets.register('admin_css', admin_css)
assets.register('base_css', base_css)
assets.register('comment_css', comment_css)
assets.register('contact_css', contact_css)
assets.register('header_css', header_css)
assets.register('post_css', post_css)
assets.register('talk_css', talk_css)
assets.register('tiles_css', tiles_css)


if config.ENV == 'production':
    admin_js = Bundle('js/internal/angular_app_module_admin.js',
                      'js/internal/admin.js',
                      filters='jsmin', output='gen/admin.%(version)s.js')

    angular_admin_js = Bundle('js/external/angular-file-upload-shim.min.js',
                              'js/external/angular.min.js',
                              'js/external/angular-file-upload.min.js',
                              'js/external/angular-resource.min.js',
                              'js/external/angular-sanitize.min.js',
                              filters='jsmin', output='gen/angular_admin.%(version)s.js')

    angular_base_js = Bundle('js/external/angular.min.js',
                             'js/external/angular-resource.min.js',
                             'js/external/angular-sanitize.min.js',
                             'js/internal/angular_app_module.js',
                             filters='jsmin', output='gen/angular.%(version)s.js')

    base_js = Bundle('js/external/jquery-1.11.1.min.js',
                     'js/external/bootstrap.min.js',
                     filters='jsmin', output='gen/base.%(version)s.js')

    blog_js = Bundle('js/internal/subscriptions.js',
                     'js/external/masonry.pkgd.min.js',
                     'js/external/imagesloaded.pkgd.min.js',
                     filters='jsmin', output='gen/blog.%(version)s.js')

    comment_js = Bundle('js/internal/comments.js',
                        filters='jsmin', output='gen/comment.%(version)s.js')

    contact_js = Bundle('js/internal/contact.js',
                        filters='jsmin', output='gen/contact.%(version)s.js')

    post_js = Bundle('js/internal/gallery.js',
                     filters='jsmin', output='gen/post.%(version)s.js')
else:
    admin_js = Bundle('js/internal/angular_app_module_admin.js',
                      'js/internal/admin.js',
                      output='gen/admin.%(version)s.js')

    angular_admin_js = Bundle('js/external/angular-file-upload-shim.js',
                              'js/external/angular.js',
                              'js/external/angular-file-upload.js',
                              'js/external/angular-resource.js',
                              'js/external/angular-sanitize.js',
                              output='gen/angular_admin.%(version)s.js')

    angular_base_js = Bundle('js/external/angular.min.js',
                             'js/external/angular-resource.js',
                             'js/external/angular-sanitize.js',
                             'js/internal/angular_app_module.js',
                             output='gen/angular.%(version)s.js')

    base_js = Bundle('js/external/jquery-1.11.1.min.js',
                     'js/external/bootstrap.min.js',
                     output='gen/base.%(version)s.js')

    blog_js = Bundle('js/internal/subscriptions.js',
                     'js/external/masonry.pkgd.min.js',
                     'js/external/imagesloaded.pkgd.min.js',
                     output='gen/blog.%(version)s.js')

    comment_js = Bundle('js/internal/comments.js',
                        output='gen/comment.%(version)s.js')

    contact_js = Bundle('js/internal/contact.js',
                        output='gen/contact.%(version)s.js')

    post_js = Bundle('js/internal/gallery.js',
                     output='gen/post.%(version)s.js')

assets.register('admin_js', admin_js)
assets.register('angular_admin_js', angular_admin_js)
assets.register('angular_base_js', angular_base_js)
assets.register('base_js', base_js)
assets.register('blog_js', blog_js)
assets.register('comment_js', comment_js)
assets.register('contact_js', contact_js)
assets.register('post_js', post_js)


@app.before_request
def before_request():
    g.user = current_user
    if request.headers.get('X_FORWARDED_PROTO') == 'http' and config.ENV != 'dev':
        return redirect(request.url.replace("http://", "https://"))


from app import views  # NOQA
from app import apis  # NOQA
from app.admin import views  # NOQA
from app.admin import apis  # NOQA
