import datetime

from app.db import app_db as db
from app.db import delete
from app.db import get
from app.db import get_list
from app.db import save
from app.db import update
from app.utils.datetime_tools import format_date
from app.utils.datetime_tools import relative_time

from sqlalchemy.dialects.postgresql import UUID

from uuid import uuid4


class Gallery(db.Model):
    __tablename__ = 'galleries'
    uuid = db.Column(UUID, primary_key=True)
    name = db.Column(db.String(500), nullable=False)
    published = db.Column(db.Boolean(), default=False, nullable=False)
    author = db.Column(db.String(256), nullable=True)
    cover_photo = db.Column(db.String(500), nullable=True)
    dead = db.Column(db.Boolean(), default=False, nullable=False)
    created_at = db.Column(db.DateTime(), unique=False)

    def to_dict(self):
        items = [item.to_dict() for item in get_list(GalleryItem, gallery_uuid=self.uuid)]
        items.sort(key=lambda x: x['position'])
        data = {'uuid': self.uuid,
                'name': self.name,
                'author': self.author,
                'cover_photo': self.cover_photo,
                'created_ago': relative_time(self.created_at),
                'created_at': format_date(self.created_at, format='%B %d, %Y'),
                'published': self.published,
                'items': items
                }
        data.update(self.get_next_prev_posts())
        return data

    def get_next_prev_posts(self):
        gallery_items = get_list(Gallery, published=True)
        try:
            index = gallery_items.index(self)
        except:
            prev_uuid = None
            next_uuid = None
        else:
            prev_uuid = gallery_items[index - 1].uuid if index > 0 else None
            next_uuid = gallery_items[index + 1].uuid if index < len(gallery_items) - 1 else None

        return {'next_uuid': next_uuid,
                'prev_uuid': prev_uuid}

    @staticmethod
    def get_galleries(published=True):
        return [gallery.to_dict() for gallery in get_list(Gallery, published=published)]

    @staticmethod
    def get_gallery(uuid):
        return get(Gallery, uuid=uuid).to_dict()

    @staticmethod
    def create_gallery(**kwargs):
        if not kwargs.get('name'):
            raise ValueError('name required')
        gallery = Gallery(uuid=str(uuid4()),
                          name=kwargs.get('name'),
                          author=kwargs.get('author'),
                          cover_photo=kwargs.get('cover_photo'),
                          created_at=datetime.datetime.utcnow())
        gallery = save(gallery)
        for item in kwargs.get('items', []):
            item['gallery_uuid'] = gallery.uuid
            GalleryItem.add_item(**item)
        return gallery.to_dict()

    @staticmethod
    def update_gallery(uuid, **kwargs):
        gallery = get(Gallery, uuid=uuid)
        gallery = update(gallery, kwargs)
        current_items = [item.get('uuid') for item in kwargs.get('items', [])]
        delete_items = [item.uuid for item in get_list(GalleryItem, gallery_uuid=gallery.uuid) if item.uuid not in current_items]
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
    position = db.Column(db.Integer(), nullable=False)

    def to_dict(self):
        data = {'uuid': self.uuid,
                'gallery_uuid': self.gallery_uuid,
                'title': self.title,
                'body': self.body,
                'image_link': self.image_link,
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
        item = GalleryItem(uuid=str(uuid4()),
                           gallery_uuid=kwargs.get('gallery_uuid'),
                           title=kwargs.get('title'),
                           body=kwargs.get('body'),
                           image_link=kwargs.get('image_link'),
                           position=kwargs.get('position'))
        item = save(item)
        return item.to_dict()

    @staticmethod
    def delete(uuid):
        item = get(GalleryItem, uuid=uuid)
        delete(item)
