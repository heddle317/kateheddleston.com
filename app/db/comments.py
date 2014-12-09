import json

from app.db import app_db as db
from app.db import create
from app.db import delete
from app.db import get
from app.db import get_list
from app.db import update

from sqlalchemy.dialects.postgresql import UUID


class Comment(db.Model):
    __tablename__ = 'comments'
    uuid = db.Column(UUID, primary_key=True)
    gallery_uuid = db.Column(UUID, nullable=False)
    twitter_id = db.Column(db.String(512), nullable=False)
    body = db.Column(db.String(), nullable=True)
    created_at = db.Column(db.DateTime(), unique=False)

    def to_dict(self):
        data = {'uuid': self.uuid,
                'gallery_uuid': self.gallery_uuid,
                'twitter_id': self.twitter_id,
                'body': self.body,
                }
        return data

    @staticmethod
    def get_comments(gallery_uuid):
        item_list = get_list(Comment, gallery_uuid=gallery_uuid, sort_by='created_at')
        return [comment.to_dict() for comment in item_list]

    @staticmethod
    def get_comment_json(gallery_uuid):
        item_list = get_list(Comment, gallery_uuid=gallery_uuid, sort_by='created_at')
        return [json.loads(comment.body) for comment in item_list]

    @staticmethod
    def add_or_update(twitter_id, gallery_uuid, body):
        body = str(json.dumps(body))

        item = get(Comment, twitter_id=str(twitter_id), gallery_uuid=gallery_uuid)
        if item:
            item = update(item, {'body': body})
        else:
            args_dict = {'gallery_uuid': gallery_uuid,
                         'twitter_id': twitter_id,
                         'body': body}
            item = create(Comment, **args_dict)
        return item.to_dict()

    @staticmethod
    def delete(uuid):
        talk = get(Comment, uuid=uuid)
        delete(talk)
