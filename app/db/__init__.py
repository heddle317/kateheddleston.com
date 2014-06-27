from app import app_db


def get(model, **kwargs):
    return app_db.session.query(model).filter_by(**kwargs).first()


def get_list(model, **kwargs):
    items = app_db.session.query(model).filter_by(**kwargs)
    return items.all()


def save(obj, refresh=True):
    obj = app_db.session.merge(obj)
    app_db.session.commit()

    if refresh:
        app_db.session.refresh(obj)

    return obj


def delete(obj):
    app_db.session.delete(obj)
    app_db.session.commit()


def update(obj, data, allow_none=False):
    changed = False

    for field, val in data.items():
        if val or allow_none:
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
