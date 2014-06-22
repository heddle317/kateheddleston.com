from functools import wraps

from app import config
from flask import g


def use_template_globals(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        g.app_base_link = config.APP_BASE_LINK
        return fn(*args, **kwargs)
    return wrapped
