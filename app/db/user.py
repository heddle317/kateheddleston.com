from app.db import app_db as db
from app.db import get
from app.db import save

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID

from uuid import uuid4


class User(db.Model):
    __tablename__ = 'users'
    uuid = db.Column(UUID, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    role = db.Column(db.SmallInteger)
    password_hash = db.Column(db.String(60), unique=False)
    email_verification_token = db.Column(db.String(50), unique=False)
    created_at = db.Column(db.DateTime(), unique=False, default=func.now())


def create_user(email, password_hash):
    role = 0
    if get(User, email=email):
        raise Exception('A User with that email has already been created.')
    user = User(uuid=str(uuid4()),
                email=email,
                role=role,
                password_hash=password_hash,
                email_verification_token=str(uuid4()))
    save(user)
