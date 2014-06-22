from app import db
from app.db import Base

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID


class BlogPosts(Base):
    __tablename__ = 'blog_posts'
    uuid = db.Column(UUID, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    body = db.Column(db.String(), nullable=False)
    image_link = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime(), unique=False, default=func.now())
