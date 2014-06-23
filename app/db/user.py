from app import db

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID


class User(db.Model):
    __tablename__ = 'users'
    uuid = db.Column(UUID, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    role = db.Column(db.SmallInteger)
    password_hash = db.Column(db.String(60), unique=False)
    email_verification_token = db.Column(db.String(50), unique=False)
    created_at = db.Column(db.DateTime(), unique=False, default=func.now())
