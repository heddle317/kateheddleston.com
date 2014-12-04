import datetime

from app.db import app_db as db
from app.db import create
from app.db import delete
from app.db import get
from app.db import get_list
from app.db import next_uuid
from app.db import prev_uuid
from app.db import update
from app.utils.datetime_tools import format_date
from app.utils.datetime_tools import relative_time

from sqlalchemy.dialects.postgresql import UUID


class Gallery(db.Model):
    __tablename__ = 'galleries'
    uuid = db.Column(UUID, primary_key=True)
    name = db.Column(db.String(500), nullable=False)
    published = db.Column(db.Boolean(), default=False, nullable=False)
    author = db.Column(db.String(256), nullable=True)
    cover_photo = db.Column(db.String(500), nullable=True)
    dead = db.Column(db.Boolean(), default=False, nullable=False)
    created_at = db.Column(db.DateTime(), unique=False)
    published_at = db.Column(db.DateTime(), unique=False)

    def to_dict(self):
        items = [item.to_dict() for item in get_list(GalleryItem, gallery_uuid=self.uuid)]
        items.sort(key=lambda x: x['position'])
        data = {'uuid': self.uuid,
                'name': self.name,
                'author': self.author,
                'cover_photo': self.cover_photo,
                'created_ago': relative_time(self.created_at),
                'created_at': format_date(self.created_at, format='%B %d, %Y'),
                'published_ago': relative_time(self.published_at) if self.published_at else '',
                'published': self.published,
                'items': items,
                'next_uuid': next_uuid(Gallery, self, sort_by='created_at', published=True),
                'prev_uuid': prev_uuid(Gallery, self, sort_by='created_at', published=True),
                }
        return data

    @staticmethod
    def get_galleries(published=True):
        item_list = get_list(Gallery, published=published, sort_by='published_at')
        return [gallery.to_dict() for gallery in item_list]

    @staticmethod
    def get_gallery(uuid):
        return get(Gallery, uuid=uuid).to_dict()

    @staticmethod
    def create_gallery(**kwargs):
        if not kwargs.get('name'):
            raise ValueError('name required')
        gallery = create(Gallery, **kwargs)
        for item in kwargs.get('items', []):
            item['gallery_uuid'] = gallery.uuid
            GalleryItem.add_item(**item)
        return gallery.to_dict()

    @staticmethod
    def update_gallery(uuid, **kwargs):
        gallery = get(Gallery, uuid=uuid)
        if not gallery.published and kwargs.get('published', False):
            kwargs['published_at'] = datetime.datetime.utcnow()
        gallery = update(gallery, kwargs)

        current_items = [item.get('uuid') for item in kwargs.get('items', [])]
        item_list = get_list(GalleryItem, gallery_uuid=gallery.uuid)

        delete_items = [item.uuid for item in item_list if item.uuid not in current_items]
        for uuid in delete_items:
            GalleryItem.delete(uuid)

        for item in kwargs.get('items', []):
            if item.get('uuid'):
                GalleryItem.update(uuid=item.pop('uuid'), **item)
            else:
                item['gallery_uuid'] = gallery.uuid
                GalleryItem.add_item(**item)
        return gallery.to_dict()

    @staticmethod
    def delete_gallery(uuid):
        gallery = get(Gallery, uuid=uuid)
        for item in get_list(GalleryItem, gallery_uuid=uuid):
            delete(item)
        delete(gallery)


class GalleryItem(db.Model):
    __tablename__ = 'gallery_items'
    uuid = db.Column(UUID, primary_key=True)
    gallery_uuid = db.Column(UUID, nullable=False)
    title = db.Column(db.String(500), nullable=True)
    body = db.Column(db.String(), nullable=True)
    image_link = db.Column(db.String(500), nullable=True)
    image_name = db.Column(db.String(500), nullable=True)
    position = db.Column(db.Integer(), nullable=False)

    def to_dict(self):
        data = {'uuid': self.uuid,
                'gallery_uuid': self.gallery_uuid,
                'title': self.title,
                'body': self.body,
                'image_link': self.image_link,
                'image_name': self.image_name,
                'position': self.position
                }
        return data

    @staticmethod
    def update(uuid, **kwargs):
        item = get(GalleryItem, uuid=uuid)
        item = update(item, kwargs)
        return item.to_dict()

    @staticmethod
    def add_item(**kwargs):
        if not kwargs.get('gallery_uuid'):
            raise ValueError('gallery_uuid required')
        if not kwargs.get('position'):
            raise ValueError('position required')
        item = create(GalleryItem, **kwargs)
        return item.to_dict()

    @staticmethod
    def delete(uuid):
        talk = get(GalleryItem, uuid=uuid)
        delete(talk)
