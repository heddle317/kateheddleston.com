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

from sqlalchemy.dialects.postgresql import UUID


class Talk(db.Model):
    __tablename__ = 'talks'
    uuid = db.Column(UUID, primary_key=True, nullable=False)
    title = db.Column(db.String(500), nullable=True)
    description = db.Column(db.String(), nullable=True)
    slides_link = db.Column(db.String(500), nullable=True)
    video_link = db.Column(db.String(500), nullable=True)
    image_name = db.Column(db.String(500), nullable=True)
    description_link = db.Column(db.String(500), nullable=True)
    location = db.Column(db.String(200), nullable=True)
    date = db.Column(db.DateTime(), unique=True)
    created_at = db.Column(db.DateTime(), unique=False)
    dead = db.Column(db.Boolean(), default=False, nullable=False)
    archived = db.Column(db.Boolean(), default=False, nullable=False)
    published = db.Column(db.Boolean(), default=False, nullable=False)

    def to_dict(self):
        data = {'uuid': self.uuid,
                'title': self.title,
                'description': self.description,
                'slides_link': self.slides_link,
                'video_link': self.video_link,
                'image_name': self.image_name,
                'base_url': '{}/talks/{}'.format(config.AWS_IMAGES_BASE, self.uuid),
                'description_link': self.description_link,
                'location': self.location,
                'date': datetime.datetime.strftime(self.date, '%B %d, %Y') if self.date else '',
                'published': self.published,
                'archived': self.archived,
                'next_uuid': next_uuid(Talk, self, sort_by='date', published=True),
                'prev_uuid': prev_uuid(Talk, self, sort_by='date', published=True),
                }
        return data

    @staticmethod
    def get_blank_gallery():
        data = {'uuid': None,
                'title': '',
                'description': '',
                'slides_link': '',
                'video_link': '',
                'image_name': '',
                'base_url': None,
                'description_link': '',
                'location': '',
                'date': '',
                'published': False
                }
        return data

    @staticmethod
    def get_talks(published=True):
        return [talk.to_dict() for talk in get_list(Talk, published=published, sort_by='date')]

    @staticmethod
    def get_talk(uuid):
        return get(Talk, uuid=uuid).to_dict()

    @staticmethod
    def create_talk(**kwargs):
        if not kwargs.get('title'):
            raise ValueError('title required')
        talk = create(Talk, **kwargs)
        return talk.to_dict()

    @staticmethod
    def update_talk(uuid, **kwargs):
        talk = get(Talk, uuid=uuid)
        talk = update(talk, kwargs)
        return talk.to_dict()

    @staticmethod
    def delete_talk(uuid):
        talk = get(Talk, uuid=uuid)
        delete(talk)
