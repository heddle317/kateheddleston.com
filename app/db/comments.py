import json

from app.db import Base
from app.db import BaseModelObject

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID


class Comment(Base, BaseModelObject):
    __tablename__ = 'comments'
    uuid = Column(UUID, primary_key=True)
    gallery_uuid = Column(UUID, nullable=False)
    social_id = Column(String(512), nullable=False)
    body = Column(String(), nullable=True)
    created_at = Column(DateTime(), unique=False)

    def json_body(self):
        body = json.loads(self.body)
        body['uuid'] = self.uuid
        body['gallery_uuid'] = self.gallery_uuid
        return body

    @staticmethod
    def get_comments_json(**kwargs):
        comments = Comment.get_list(**kwargs)
        return [comment.json_body() for comment in comments]

    @staticmethod
    def add_or_update(social_id, gallery_uuid, body):
        body = str(json.dumps(body))

        item = Comment.get(social_id=str(social_id), gallery_uuid=gallery_uuid)
        if item:
            item = Comment.update(item.uuid, body=body)
        else:
            args_dict = {'gallery_uuid': gallery_uuid,
                         'social_id': social_id,
                         'body': body}
            item = Comment.create(**args_dict)
        return item
