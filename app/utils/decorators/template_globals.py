import os

from app import config
from flask import g
from flask_login import current_user
from functools import wraps


def use_template_globals(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        g.app_base_link = config.APP_BASE_LINK
        g.current_user = current_user
        g.static_base = config.STATIC_BASE
        g.images_base = config.IMAGES_BASE
        g.env = os.environ.get('ENVIRONMENT', 'dev')
        return fn(*args, **kwargs)
    return wrapped
