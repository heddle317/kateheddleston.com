import datetime

from app import config
from app.db import app_db as db
from app.db import create
from app.db import delete
from app.db import get
from app.db import get_list
from app.db import next_uuid
from app.db import prev_uuid
from app.db import update
from app.db.subscriptions import Subscription
from app.utils.datetime_tools import format_date
from app.utils.datetime_tools import relative_time

from sqlalchemy.dialects.postgresql import UUID


class Gallery(db.Model):
    __tablename__ = 'galleries'
    uuid = db.Column(UUID, primary_key=True)
    name = db.Column(db.String(500), nullable=False)
    subtitle = db.Column(db.String(500), nullable=False)
    published = db.Column(db.Boolean(), default=False, nullable=False)
    author = db.Column(db.String(256), nullable=True)
    cover_photo = db.Column(db.String(500), nullable=True)
    dead = db.Column(db.Boolean(), default=False, nullable=False)
    created_at = db.Column(db.DateTime(), unique=False)
    published_at = db.Column(db.DateTime(), unique=False)

    def to_dict(self):
        items = GalleryItem.get_list(self.uuid)
        items.sort(key=lambda x: x['position'])
        base_url = '{}/galleries/{}'.format(config.IMAGES_BASE, self.uuid)
        data = {'uuid': self.uuid,
                'name': self.name,
                'subtitle': self.subtitle,
                'author': self.author,
                'cover_photo': self.cover_photo,
                'cover_photo_url': '{}/{}'.format(base_url, self.cover_photo),
                'base_url': base_url,
                'description': self.description(),
                'created_ago': relative_time(self.created_at),
                'created_at': format_date(self.created_at, format='%B %d, %Y'),
                'published_at_raw': format_date(self.published_at, format='%Y-%m-%dT%H:%M:%S') if self.published_at else '',
                'published_ago': relative_time(self.published_at) if self.published_at else '',
                'published': self.published,
                'items': items,
                'next_uuid': next_uuid(Gallery, self, sort_by='published_at', published=True),
                'prev_uuid': prev_uuid(Gallery, self, sort_by='published_at', published=True),
                }
        return data

    def description(self):
        items = get_list(GalleryItem, gallery_uuid=self.uuid, sort_by='position', desc=False)
        for item in items:
            if item.body:
                return item.body

    @staticmethod
    def get_blank_gallery():
        items = [{'gallery_uuid': None,
                  'title': '',
                  'body': '',
                  'image_name': '',
                  'image_caption': '',
                  'position': 1}]
        data = {'uuid': None,
                'name': '',
                'author': '',
                'cover_photo': '',
                'created_ago': '',
                'created_at': '',
                'published_at_raw': None,
                'published_ago': '',
                'published': False,
                'items': items
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
            link = "{}/blog/{}".format(config.APP_BASE_LINK, uuid)
            Subscription.send_subscription_emails(link, gallery.name)
        gallery = update(gallery, kwargs)

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
    image_caption = db.Column(db.String(500), nullable=True)
    dead = db.Column(db.Boolean, default=False, nullable=False)

    def to_dict(self):
        data = {'uuid': self.uuid,
                'gallery_uuid': self.gallery_uuid,
                'title': self.title,
                'body': self.body,
                'image_link': self.image_link,
                'image_name': self.image_name,
                'position': self.position,
                'image_caption': self.image_caption
                }
        return data

    @staticmethod
    def get_list(gallery_uuid):
        items = [item.to_dict() for item in get_list(GalleryItem, gallery_uuid=gallery_uuid, dead=False)]
        return items

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
        item = get(GalleryItem, uuid=uuid)
        item = update(item, {'dead': True})
