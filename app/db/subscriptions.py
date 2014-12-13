from app.db import app_db as db
from app.db import create
from app.db import get
from app.db import get_list
from app.db import update
from app.utils.email import send_subscription_email
from app.utils.email import send_verification_email

from sqlalchemy.dialects.postgresql import UUID

from uuid import uuid4


class Subscription(db.Model):
    __tablename__ = 'subscriptions'
    uuid = db.Column(UUID, primary_key=True)
    name = db.Column(db.String(500), nullable=False)
    email = db.Column(db.String(500), nullable=False, unique=True)
    verified = db.Column(db.Boolean(), nullable=False, default=False)
    email_verification_token = db.Column(db.String(50), unique=False)
    dead = db.Column(db.Boolean(), nullable=False, default=False)
    created_at = db.Column(db.DateTime(), unique=False)

    def to_dict(self):
        data = {'uuid': self.uuid,
                'name': self.name,
                'email': self.email
                }
        return data

    @staticmethod
    def get_list(dead=False):
        item_list = get_list(Subscription, dead=False, verified=True)
        return [item.to_dict() for item in item_list]

    @staticmethod
    def get_subscription(uuid):
        return get(Subscription, uuid=uuid).to_dict()

    @staticmethod
    def send_subscription_emails(post_link, post_name):
        subscriptions = Subscription.get_list()
        for subscription in subscriptions:
            send_subscription_email(subscription, post_link, post_name)

    @staticmethod
    def create_subscription(**kwargs):
        if not kwargs.get('name'):
            raise ValueError('name required')
        if not kwargs.get('email'):
            raise ValueError('email required')
        subscription = get(Subscription, email=kwargs.get('email'))
        if subscription:
            subscription = update(subscription, {'dead': False, 'name': kwargs.get('name')})
            if not subscription.verified:
                send_verification_email(subscription)
        else:
            kwargs['email_verification_token'] = str(uuid4())
            subscription = create(Subscription, **kwargs)
            send_verification_email(subscription)
        return subscription.to_dict()

    @staticmethod
    def verify_email(email_verification_token):
        subscription = get(Subscription, email_verification_token=email_verification_token)
        subscription = update(subscription, {'verified': True})
        return subscription.to_dict()

    @staticmethod
    def cancel_subscription(uuid):
        subscription = get(Subscription, uuid=uuid)
        subscription = update(subscription, {'dead': True, 'verified': False})
        return subscription.to_dict()
