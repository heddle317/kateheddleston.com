import copy
import datetime

from app import app_db
from app.utils.datetime_tools import format_date

from sqlalchemy.ext.declarative import declarative_base

from uuid import uuid4


KateHeddlestonDB = app_db.session
Base = declarative_base()


def get(model, **kwargs):
    try:
        return KateHeddlestonDB.query(model).filter_by(**kwargs).first()
    except:
        return None


def get_list(model, **kwargs):
    sort_by = kwargs.pop('sort_by', 'created_at')
    limit = kwargs.pop('limit', None)
    desc = kwargs.pop('desc', True)
    published = kwargs.pop('published', True)
    items = KateHeddlestonDB.query(model)

    list_keys = []
    for key, value in kwargs.items():
        if isinstance(value, list):
            field = getattr(model, key)
            items = items.filter(field.in_(kwargs.get(key)))
            list_keys.append(key)
    for key in list_keys:
        kwargs.pop(key)
    items = items.filter_by(**kwargs)

    if published and hasattr(model, 'published'):
        items = items.filter_by(published=published)
    if hasattr(model, sort_by):
        order_by = getattr(model, sort_by)
        if desc:
            items = items.order_by(order_by.desc().nullslast())
        else:
            items = items.order_by(order_by.asc().nullslast())
    items = items.limit(limit)
    return items.all()


def save(obj, refresh=True):
    obj = KateHeddlestonDB.merge(obj)
    KateHeddlestonDB.commit()

    if refresh:
        KateHeddlestonDB.refresh(obj)

    return obj


def publish(obj):
    update(obj, {'publish`': True})
    save(obj)


def delete(obj, hard_delete=False):
    KateHeddlestonDB.delete(obj)
    KateHeddlestonDB.commit()


def update(obj, data):
    changed = False

    for field, val in data.items():
        if hasattr(obj, field):
            setattr(obj, field, val)
            changed = True

    if changed:
        return save(obj)

    return obj


def next_item(model, current_item, **kwargs):
    items = get_list(model, **kwargs)
    try:
        index = [index for index, item in enumerate(items) if item.uuid == current_item.uuid][0]
    except:
        next_item = None
    else:
        next_item = items[index + 1] if index < len(items) - 1 else None

    return next_item


def prev_item(model, current_item, **kwargs):
    items = get_list(model, **kwargs)
    try:
        index = [index for index, item in enumerate(items) if item.uuid == current_item.uuid][0]
    except:
        prev_item = None
    else:
        prev_item = items[index - 1] if index > 0 else None

    return prev_item


def create(model, **kwargs):
    m = model()
    if hasattr(m, 'uuid'):
        m.uuid = str(uuid4())
    if hasattr(m, 'created_at'):
        m.created_at = datetime.datetime.utcnow()
    for k, v in kwargs.items():
        if hasattr(m, k):
            setattr(m, k, v)

    return save(m)


def jsonify_model(obj):
    if obj is None:
        return {}
    if isinstance(obj, list):
        items = [item.to_dict() for item in obj]
        return items
    return obj.to_dict()


class BaseModelObject(object):

    def to_dict(self):
        attr_dict = copy.deepcopy(self.__dict__)
        for key, value in attr_dict.items():
            if isinstance(value, datetime.datetime):
                attr_dict[key] = format_date(value)
        if attr_dict.get('_sa_instance_state'):
            del attr_dict['_sa_instance_state']
        return attr_dict

    @classmethod
    def get_list(cls, to_json=False, **kwargs):
        items = get_list(cls, **kwargs)
        return jsonify_model(items) if to_json else items

    @classmethod
    def get(cls, to_json=False, **kwargs):
        item = get(cls, **kwargs)
        return jsonify_model(item) if to_json else item

    @classmethod
    def update(cls, uuid, **kwargs):
        if 'uuid' in kwargs.keys():
            kwargs.pop('uuid')
        item = get(cls, uuid=uuid)
        item = update(item, kwargs)
        return item

    @classmethod
    def create(cls, **kwargs):
        item = create(cls, **kwargs)
        return item

    @classmethod
    def delete(cls, **kwargs):
        item = get(cls, **kwargs)
        if item:
            delete(item)

    @classmethod
    def next(cls, current_item, attrs=None, **kwargs):
        n = next_item(cls, current_item, **kwargs)
        if attrs and n:
            return_dict = {}
            for field in attrs:
                if hasattr(n, field):
                    return_dict[field] = getattr(n, field)
            return return_dict
        return n

    @classmethod
    def prev(cls, current_item, attrs=None, **kwargs):
        prev = prev_item(cls, current_item, **kwargs)
        if attrs and prev:
            return_dict = {}
            for field in attrs:
                if hasattr(prev, field):
                    return_dict[field] = getattr(prev, field)
            return return_dict
        return prev
