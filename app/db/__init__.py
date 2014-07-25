from app import app_db


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


def update(obj, data, allow_none=False):
    changed = False

    for field, val in data.items():
        if val is not None or allow_none:
            if hasattr(obj, field):
                setattr(obj, field, val)
                changed = True

    if changed:
        return save(obj)

    return obj


def create(model, **kwargs):
    m = model()
    for k, v in kwargs.items():
        if hasattr(m, k):
            setattr(m, k, v)

    return save(m)
