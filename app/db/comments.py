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
    social_id = db.Column(db.String(512), nullable=False)
    body = db.Column(db.String(), nullable=True)
    created_at = db.Column(db.DateTime(), unique=False)

    def to_dict(self, to_json=False):
        if json:
            body = json.loads(self.body)
            body['uuid'] = self.uuid
            body['gallery_uuid'] = self.gallery_uuid
            return body
        else:
            return {'uuid': self.uuid,
                    'gallery_uuid': self.gallery_uuid,
                    'social_id': self.social_id,
                    'body': self.body,
                    }

    @staticmethod
    def get_comments(gallery_uuid=None, to_json=False):
        if gallery_uuid:
            item_list = [comment.to_dict(to_json) for comment in get_list(Comment, gallery_uuid=gallery_uuid)]
        else:
            item_list = [comment.to_dict(to_json) for comment in get_list(Comment)]
        item_list = sorted(item_list, key=lambda x: x.get('created_time', ''), reverse=True)
        return item_list

    @staticmethod
    def add_or_update(social_id, gallery_uuid, body):
        body = str(json.dumps(body))

        item = get(Comment, social_id=str(social_id), gallery_uuid=gallery_uuid)
        if item:
            item = update(item, {'body': body})
        else:
            args_dict = {'gallery_uuid': gallery_uuid,
                         'social_id': social_id,
                         'body': body}
            item = create(Comment, **args_dict)
        return item.to_dict()

    @staticmethod
    def delete(uuid):
        talk = get(Comment, uuid=uuid)
        delete(talk)
