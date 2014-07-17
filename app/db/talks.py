import datetime

from app.db import app_db as db
from app.db import delete
from app.db import get
from app.db import get_list
from app.db import save
from app.db import update
from app.utils.exceptions import TalkException

from sqlalchemy.dialects.postgresql import UUID

from uuid import uuid4


REQUIRED_FIELDS = ['title',
                   'description',
                   'video_link',
                   'image_link',
                   'location',
                   'date']


class Talk(db.Model):
    __tablename__ = 'talks'
    uuid = db.Column(UUID, primary_key=True, nullable=False)
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.String(), nullable=False)
    slides_link = db.Column(db.String(500), nullable=True)
    video_link = db.Column(db.String(500), nullable=True)
    image_link = db.Column(db.String(500), nullable=True)
    description_link = db.Column(db.String(500), nullable=True)
    location = db.Column(db.String(200), nullable=True)
    date = db.Column(db.DateTime(), unique=False)
    created_at = db.Column(db.DateTime(), unique=False, default=datetime.datetime.utcnow())

    def to_dict(self):
        return {'uuid': self.uuid,
                'title': self.title,
                'description': self.description,
                'slides_link': self.slides_link,
                'video_link': self.video_link,
                'description_link': self.description_link,
                'location': self.location,
                'date': datetime.datetime.strftime(self.date, '%B %d, %Y'),
                'image_link': self.image_link
                }

    @staticmethod
    def get_talks():
        return [talk.to_dict() for talk in get_list(Talk)]

    @staticmethod
    def get_talk(uuid):
        return get(Talk, uuid=uuid).to_dict()

    @staticmethod
    def create_talk(**kwargs):
        for field in REQUIRED_FIELDS:
            if not kwargs.get(field):
                raise TalkException('%s required' % field)
        talk = Talk(uuid=str(uuid4()),
                    title=kwargs.get('title', ''),
                    description=kwargs.get('description', ''),
                    slides_link=kwargs.get('slides_link'),
                    video_link=kwargs.get('video_link', ''),
                    description_link=kwargs.get('description_link'),
                    location=kwargs.get('location'),
                    date=kwargs.get('date'),
                    image_link=kwargs.get('image_link', ''))
        talk = save(talk)
        return talk.to_dict()

    @staticmethod
    def update_talk(uuid, **kwargs):
        talk = get(Talk, uuid)
        update(talk, **kwargs)
        return talk.to_dict()

    @staticmethod
    def delete_talk(uuid):
        talk = get(Talk, uuid=uuid)
        delete(talk)
