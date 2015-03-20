from app import config
from app.db import Base
from app.db import BaseModelObject
from app.utils.datetime_tools import format_date
from app.utils.datetime_tools import parse_date

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
                          'formatted_date': format_date(self.date, format='%B %d, %Y'),
                          'next': Talk.next(self, attrs=['uuid'], sort_by='date', published=True, desc=False),
                          'prev': Talk.prev(self, attrs=['uuid'], sort_by='date', published=True, desc=False)})
        return attr_dict

    @staticmethod
    def update_talk(uuid, **kwargs):
        if kwargs.get('date'):
            date = kwargs.pop('date')
            parsed_date = parse_date(date, '%B %d, %Y')
            kwargs['date'] = parsed_date
        return Talk.update(uuid, **kwargs)

    @staticmethod
    def blank():
        blank_talk = dict((key, '') for key in Talk.__dict__.keys() if key.find('_') > 0)
        blank_talk.update({'published': False})
        return blank_talk
