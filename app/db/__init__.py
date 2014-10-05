import datetime

from app import app_db

from uuid import uuid4


def get(model, **kwargs):
    return app_db.session.query(model).filter_by(**kwargs).first()


def get_list(model, **kwargs):
    sort_by = kwargs.pop('sort_by', 'created_at')
    limit = kwargs.pop('limit', None)
    desc = kwargs.pop('desc', True)
    published = kwargs.pop('published', True)
    items = app_db.session.query(model).filter_by(**kwargs)
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
    obj = app_db.session.merge(obj)
    app_db.session.commit()

    if refresh:
        app_db.session.refresh(obj)

    return obj


def publish(obj):
    update(obj, {'publish`': True})
    save(obj)


def delete(obj, hard_delete=False):
    app_db.session.delete(obj)
    app_db.session.commit()


def update(obj, data):
    changed = False

    for field, val in data.items():
        if hasattr(obj, field):
            setattr(obj, field, val)
            changed = True

    if changed:
        return save(obj)

    return obj


def next_uuid(model, current_item, sort_by='created_at', published=True):
    items = get_list(model, published=published, sort_by=sort_by, desc=False)
    try:
        index = [index for index, item in enumerate(items) if item.uuid == current_item.uuid][0]
    except:
        next_uuid = None
    else:
        next_uuid = items[index + 1].uuid if index < len(items) - 1 else None

    return next_uuid


def prev_uuid(model, current_item, sort_by='created_at', published=True):
    items = get_list(model, published=published, sort_by=sort_by, desc=False)
    try:
        index = [index for index, item in enumerate(items) if item.uuid == current_item.uuid][0]
    except:
        prev_uuid = None
    else:
        prev_uuid = items[index - 1].uuid if index > 0 else None

    return prev_uuid


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
