from app import db


def get(model, **kwargs):
    return db.get_session().query(model).filter_by(**kwargs).first()


def save(obj, refresh=True):
    obj = db.get_session().merge(obj)
    db.get_session().commit()

    if refresh:
        db.get_session().refresh(obj)

    return obj


def delete(obj):
    db.get_session().delete(obj)
    db.get_session().commit()


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
