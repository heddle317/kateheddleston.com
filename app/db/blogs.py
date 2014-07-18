import datetime

from app.db import app_db as db
from app.db import delete
from app.db import get
from app.db import get_list
from app.db import save
from app.db import update
from app.utils.datetime_tools import format_date
from app.utils.datetime_tools import relative_time
from app.utils.exceptions import BlogException

from sqlalchemy.dialects.postgresql import UUID

from uuid import uuid4


REQUIRED_FIELDS = ['title',
                   'body',
                   'image_link']


class BlogPost(db.Model):
    __tablename__ = 'blog_posts'
    uuid = db.Column(UUID, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    body = db.Column(db.String(), nullable=False)
    image_link = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime(), unique=False)

    def to_dict(self):
        data = {'uuid': self.uuid,
                'title': self.title,
                'body': self.body,
                'image_link': self.image_link,
                'created_ago': relative_time(self.created_at),
                'created_at': format_date(self.created_at, format='%B %d, %Y')
                }
        data.update(self.get_next_prev_posts())
        return data

    def get_next_prev_posts(self):
        blogs = get_list(BlogPost)
        index = blogs.index(self)
        prev_uuid = blogs[index - 1].uuid if index > 0 else None
        next_uuid = blogs[index + 1].uuid if index < len(blogs) - 1 else None

        return {'next_uuid': next_uuid,
                'prev_uuid': prev_uuid}

    @staticmethod
    def get_blogs():
        return [blog.to_dict() for blog in get_list(BlogPost)]

    @staticmethod
    def get_blog(uuid):
        return get(BlogPost, uuid=uuid).to_dict()

    @staticmethod
    def create_blog(**kwargs):
        for field in REQUIRED_FIELDS:
            if not kwargs.get(field):
                raise BlogException('%s required' % field)
        blog = BlogPost(uuid=str(uuid4()),
                        title=kwargs.get('title', ''),
                        body=kwargs.get('body', ''),
                        image_link=kwargs.get('image_link', ''),
                        created_at=datetime.datetime.utcnow())
        blog = save(blog)
        return blog.to_dict()

    @staticmethod
    def update_blog(uuid, **kwargs):
        blog = get(BlogPost, uuid=uuid)
        update(blog, kwargs)
        return blog.to_dict()

    @staticmethod
    def delete_blog(uuid):
        blog = get(BlogPost, uuid=uuid)
        delete(blog)
