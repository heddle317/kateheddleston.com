import datetime
import string

from app import config
from app.db import Base
from app.db import BaseModelObject
from app.db import delete
from app.db import update
from app.db.categories import Category
from app.db.subscriptions import Subscription
from app.db.user import User
from app.utils.datetime_tools import format_date
from app.utils.datetime_tools import relative_time

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID


class Gallery(Base, BaseModelObject):
    __tablename__ = 'galleries'
    uuid = Column(UUID, primary_key=True)
    name = Column(String(500), nullable=False)
    subtitle = Column(String(500), nullable=False)
    published = Column(Boolean(), default=False, nullable=False)
    author = Column(String(256), nullable=True)
    cover_photo = Column(String(500), nullable=True)
    url_title = Column(String(1024), nullable=True)
    dead = Column(Boolean(), default=False, nullable=False)
    archived = Column(Boolean(), default=False, nullable=False)
    permanent = Column(Boolean(), default=False, nullable=False)
    created_at = Column(DateTime(), unique=False)
    published_at = Column(DateTime(), unique=False)

    def to_dict(self, admin=False):
        attr_dict = BaseModelObject.to_dict(self)
        base_url = '{}/galleries/{}'.format(config.AWS_IMAGES_BASE, self.uuid)
        gallery_categories = GalleryCategory.get_list(gallery_uuid=self.uuid, to_json=True)
        gallery_dict = {'cover_photo_url': '{}/{}'.format(base_url, self.cover_photo),
                        'base_url': base_url,
                        'url_title': self.latest_url_title(),
                        'description': self.description(),
                        'created_ago': relative_time(self.created_at),
                        'published_at_raw': format_date(self.published_at, format='%Y-%m-%dT%H:%M:%S'),
                        'published_ago': relative_time(self.published_at) if self.published_at else '',
                        'gallery_categories': gallery_categories,
                        'items': [item.to_dict() for item in self.items(admin=admin)],
                        'prev': Gallery.prev(self, attrs=['uuid', 'url_title'], sort_by='published_at',
                                             published=True, desc=False),
                        'next': Gallery.next(self, attrs=['uuid', 'url_title'], sort_by='published_at',
                                             published=True, desc=False)}
        attr_dict.update(gallery_dict)
        return attr_dict

    def description(self):
        items = GalleryItem.get_list(gallery_uuid=self.uuid, sort_by='position', desc=False)
        for item in items:
            if item.body:
                return item.body

    def latest_category(self):
        gallery_categories = GalleryCategory.get_list(gallery_uuid=self.uuid, to_json=True)
        if gallery_categories:
            return gallery_categories[0]['name']
        return None

    def category_uuids(self):
        gallery_categories = GalleryCategory.get_list(gallery_uuid=self.uuid)
        return [gc.category_uuid for gc in gallery_categories]

    def latest_url_title(self):
        titles = GalleryTitle.get_list(gallery_uuid=self.uuid, sort_by='created_at', desc=True)
        if len(titles) > 0:
            return titles[0].title
        if self.url_title:
            return self.url_title
        return self.uuid

    def url(self):
        return u'{}/blog/{}'.format(config.APP_BASE_LINK, self.latest_url_title())

    def items(self, admin=False):
        return GalleryItem.get_items(gallery_uuid=self.uuid, sort_by='position', desc=False, admin=admin)

    @staticmethod
    def blank():
        blank_item = dict((key, '') for key in GalleryItem.__dict__.keys() if key.find('_') > 0)
        blank_item['comments'] = []
        blank_gallery = dict((key, '') for key in Gallery.__dict__.keys() if key.find('_') > 0)
        blank_gallery.update({'items': [blank_item],
                              'published_at_raw': '',
                              'published_ago': '',
                              'gallery_categories': [],
                              'created_ago': '',
                              'published': False})
        return blank_gallery

    @staticmethod
    def create_gallery(**kwargs):
        if 'gallery_uuid' in kwargs.keys():
            kwargs.pop('gallery_uuid')
        gallery = Gallery.create(**kwargs)

        title = Gallery.create_url_title(kwargs.get('name'))
        GalleryTitle.add_title(gallery.uuid, title)
        for item_data in kwargs.get('items', []):
            if 'gallery_uuid' in item_data.keys():
                item_data.pop('gallery_uuid')
            GalleryItem.create(gallery_uuid=gallery.uuid, **item_data)
        return gallery

    @staticmethod
    def create_url_title(title):
        title = ''.join(ch for ch in title if ch not in set(string.punctuation.decode('utf-8')))
        title = title.rstrip()
        title = title.lower().replace(' ', '-')
        return title

    @staticmethod
    def update(uuid, **kwargs):
        gallery = Gallery.get(uuid=uuid)

        if not gallery.published and kwargs.get('published', False):
            kwargs['published_at'] = datetime.datetime.utcnow()

        title = Gallery.create_url_title(kwargs.get('name', gallery.name))
        GalleryTitle.add_title(uuid, title)
        gallery = update(gallery, kwargs)

        for item_data in kwargs.get('items', []):
            if 'gallery_uuid' in item_data.keys():
                item_data.pop('gallery_uuid')
            if item_data.get('uuid'):
                GalleryItem.update(item_data.pop('uuid'), **item_data)
            else:
                GalleryItem.create(gallery_uuid=gallery.uuid, **item_data)

        return gallery

    @staticmethod
    def send_emails(uuid):
        gallery = Gallery.get(uuid=uuid)
        Subscription.send_subscription_emails(gallery)

    @staticmethod
    def get_custom_url(url_title):
        gallery_title = GalleryTitle.get(title=url_title)
        if gallery_title:
            return Gallery.get(uuid=gallery_title.gallery_uuid)
        gallery = Gallery.get(url_title=url_title)
        if gallery:
            GalleryTitle.add_title(gallery.uuid, url_title)
            return gallery
        return None

    @staticmethod
    def delete(uuid=None):
        gallery = Gallery.get(uuid=uuid)
        GalleryItem.delete_list(uuid)
        delete(gallery)


class GalleryCategory(Base, BaseModelObject):
    __tablename__ = 'gallery_categories'
    uuid = Column(UUID, primary_key=True)
    gallery_uuid = Column(UUID)
    category_uuid = Column(UUID)

    def to_dict(self):
        attr_dict = BaseModelObject.to_dict(self)
        category = Category.get(uuid=self.category_uuid)
        attr_dict.update({'name': category.name})
        return attr_dict


class GalleryTitle(Base, BaseModelObject):
    __tablename__ = 'gallery_titles'
    uuid = Column(UUID, primary_key=True)
    gallery_uuid = Column(UUID, nullable=False)
    title = Column(String(500), nullable=False, unique=True)
    created_at = Column(DateTime(), unique=False)

    @staticmethod
    def add_title(gallery_uuid, url_title):
        gallery_title = GalleryTitle.get(title=url_title)
        if not gallery_title:
            gallery_title = GalleryTitle.create(gallery_uuid=gallery_uuid, title=url_title)
        return gallery_title


class GalleryItem(Base, BaseModelObject):
    __tablename__ = 'gallery_items'
    uuid = Column(UUID, primary_key=True)
    gallery_uuid = Column(UUID, nullable=False)
    title = Column(String(500), nullable=True)
    body = Column(String(), nullable=True)
    image_link = Column(String(500), nullable=True)
    image_name = Column(String(500), nullable=True)
    position = Column(Integer(), nullable=False)
    image_caption = Column(String(500), nullable=True)
    image_alt = Column(String(500), nullable=True)
    dead = Column(Boolean, default=False, nullable=False)

    def to_dict(self, admin=False):
        attr_dict = BaseModelObject.to_dict(self)
        if admin:
            attr_dict['comments'] = GalleryItemComment.get_list(to_json=True, gallery_item_uuid=self.uuid)
        return attr_dict

    def add_comment(self, **kwargs):
        comment = GalleryItemComment.create(gallery_item_uuid=self.uuid, **kwargs)
        return comment

    @staticmethod
    def get_items(admin=False, to_json=False, **kwargs):
        if admin:
            items = GalleryItem.get_list(**kwargs)
        else:
            items = GalleryItem.get_list(dead=False, **kwargs)
        if to_json:
            items = [item.to_dict(admin=admin) for item in items]
        return items

    @staticmethod
    def delete_list(gallery_uuid):
        items = GalleryItem.get_list(gallery_uuid=gallery_uuid)
        for item in items:
            GalleryItem.delete(uuid=item.uuid)

    @staticmethod
    def kill(item_uuid):
        item = GalleryItem.update(item_uuid, dead=True)
        return item


class GalleryItemComment(Base, BaseModelObject):
    __tablename__ = 'gallery_item_comments'
    uuid = Column(UUID, primary_key=True)
    gallery_item_uuid = Column(UUID, nullable=False)
    author_uuid = Column(UUID, nullable=False)
    body = Column(String(), nullable=True)
    resolved = Column(Boolean(), default=False, nullable=False)
    created_at = Column(DateTime(), unique=False)

    def to_dict(self, admin=False):
        attr_dict = BaseModelObject.to_dict(self)
        attr_dict.update({'author_email': self.author_name(),
                          'created_ago': relative_time(self.created_at)})
        return attr_dict

    def author_name(self):
        author = User.get(uuid=self.author_uuid)
        if author:
            return author.email
        return ''
