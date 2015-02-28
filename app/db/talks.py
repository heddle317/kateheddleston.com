from app import config
from app.db import Base
from app.db import BaseModelObject
from app.db import next_uuid
from app.db import prev_uuid
from app.utils.datetime_tools import format_date

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID


class Talk(Base, BaseModelObject):
    __tablename__ = 'talks'
    uuid = Column(UUID, primary_key=True, nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(String(), nullable=True)
    slides_link = Column(String(500), nullable=True)
    video_link = Column(String(500), nullable=True)
    image_name = Column(String(500), nullable=True)
    description_link = Column(String(500), nullable=True)
    location = Column(String(200), nullable=True)
    date = Column(DateTime(), unique=True)
    created_at = Column(DateTime(), unique=False)
    dead = Column(Boolean(), default=False, nullable=False)
    archived = Column(Boolean(), default=False, nullable=False)
    published = Column(Boolean(), default=False, nullable=False)

    def to_dict(self):
        attr_dict = BaseModelObject.to_dict(self)
        attr_dict.update({'base_url': '{}/talks/{}'.format(config.AWS_IMAGES_BASE, self.uuid),
                          'date': format_date(self.date, '%B %d, %Y'),
                          'next_uuid': next_uuid(Talk, self, sort_by='date', published=True),
                          'prev_uuid': prev_uuid(Talk, self, sort_by='date', published=True)})
        return attr_dict

    @staticmethod
    def blank():
        blank_talk = dict((key, '') for key in Talk.__dict__.keys() if key.find('_') > 0)
        blank_talk.update({'published': False})
        return blank_talk
