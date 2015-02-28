from app import login_manager
from app.db import Base
from app.db import BaseModelObject
from app.utils.crypto import authenticate_password

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import SmallInteger
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID

from uuid import uuid4


class User(Base, BaseModelObject):
    __tablename__ = 'users'
    uuid = Column(UUID, primary_key=True)
    email = Column(String(120), unique=True)
    role = Column(SmallInteger)
    password_hash = Column(String(60), unique=False)
    email_verification_token = Column(String(50), unique=False)
    code = Column(String(512), unique=False)
    created_at = Column(DateTime(), unique=False)
    dead = Column(Boolean(), default=False, nullable=False)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.uuid)

    def get_code(self):
        return self.code

    def update_code(self, code):
        self.code = code
        User.update(self.uuid, code=code)

    def __repr__(self):
        return '<User %r>' % (self.email)


@login_manager.user_loader
def load_user(id):
    return User.get(uuid=id)


def create_user(email, password_hash):
    role = 0
    if User.get(email=email):
        raise Exception('A User with that email has already been created.')
    user = User.create(email=email,
                       role=role,
                       password_hash=password_hash,
                       email_verification_token=str(uuid4()))
    return user


def get_verified_user(email, password):
    user = User.get(email=email)
    if user:
        verified = authenticate_password(password, user.password_hash.encode('utf-8'))
        if verified:
            return user
    return None
