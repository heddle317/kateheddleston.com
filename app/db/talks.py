import datetime

from app.db import app_db as db
from app.db import delete
from app.db import get
from app.db import get_list
from app.db import save
from app.db import update

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID

from uuid import uuid4


class Talk(db.Model):
    __tablename__ = 'talks'
    uuid = db.Column(UUID, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.String(), nullable=False)
    slides_link = db.Column(db.String(500), nullable=True)
    video_link = db.Column(db.String(500), nullable=True)
    image_link = db.Column(db.String(500), nullable=True)
    description_link = db.Column(db.String(500), nullable=True)
    location = db.Column(db.String(200), nullable=True)
    date = db.Column(db.DateTime(), unique=False)
    created_at = db.Column(db.DateTime(), unique=False, default=func.now())

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
        talk = Talk(uuid=str(uuid4()),
                    title=kwargs.pop('title', ''),
                    description=kwargs.pop('description', ''),
                    slides_link=kwargs.pop('slides_link'),
                    video_link=kwargs.pop('video_link', ''),
                    description_link=kwargs.pop('description_link'),
                    location=kwargs.pop('location'),
                    date=kwargs.pop('date'),
                    image_link=kwargs.pop('image_link', ''))
        save(talk)
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
