import re
import os

from app import config
from flask import g
from flask import request
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


def is_mobile():
    g.browser = request.user_agent.browser
    g.version = request.user_agent.version and int(request.user_agent.version.split('.')[0])
    g.platform = request.user_agent.platform
    g.uas = request.user_agent.string
    g.is_mobile = False
    if g.platform == 'android' or g.platform == 'iphone' or re.search('iPad', g.uas) \
    or re.search('Windows Phone OS', g.uas) or re.search('BlackBerry', g.uas):
        g.is_mobile = True
