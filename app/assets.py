from app import app
from app import config

from flask_assets import Bundle
from flask_assets import Environment


assets = Environment(app)


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

post_css = Bundle('css/internal/gallery.css',
                  'css/internal/gallery_nav.css',
                  'css/internal/post_footer.css',
                  filters='cssmin', output='gen/post.%(version)s.css')

talk_css = Bundle('css/internal/talk.css',
                  'css/internal/talk_footer.css',
                  filters='cssmin', output='gen/talk.%(version)s.css')

tiles_css = Bundle('css/internal/tiles.css',
                   filters='cssmin', output='gen/tiles.%(version)s.css')

assets.register('about_css', about_css)
assets.register('admin_css', admin_css)
assets.register('base_css', base_css)
assets.register('comment_css', comment_css)
assets.register('contact_css', contact_css)
assets.register('post_css', post_css)
assets.register('talk_css', talk_css)
assets.register('tiles_css', tiles_css)


if config.ENVIRONMENT == 'production':
    admin_js = Bundle('js/internal/angular_app_module_admin.js',
                      'js/internal/admin.js',
                      'js/internal/admin_auth.js',
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
                      'js/internal/admin_auth.js',
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