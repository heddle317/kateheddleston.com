from app.db import Base
from app.db import BaseModelObject
from app.utils.email import send_subscription_email
from app.utils.email import send_verification_email

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID

from uuid import uuid4


class Subscription(Base, BaseModelObject):
    __tablename__ = 'subscriptions'
    uuid = Column(UUID, primary_key=True)
    name = Column(String(500), nullable=False)
    email = Column(String(500), nullable=False, unique=True)
    verified = Column(Boolean(), nullable=False, default=False)
    email_verification_token = Column(String(50), unique=False)
    dead = Column(Boolean(), nullable=False, default=False)
    created_at = Column(DateTime(), unique=False)

    @staticmethod
    def send_subscription_emails(post_link, post_name):
        subscriptions = Subscription.get_list(dead=False, verified=True)
        for subscription in subscriptions:
            send_subscription_email(subscription, post_link, post_name)

    @staticmethod
    def create_or_update(**kwargs):
        if not kwargs.get('name'):
            raise ValueError('name required')
        if not kwargs.get('email'):
            raise ValueError('email required')
        subscription = Subscription.get(email=kwargs.get('email'))
        if subscription:
            subscription = Subscription.update(subscription.uuid, dead=False, name=kwargs.get('name'))
            if not subscription.verified:
                send_verification_email(subscription)
        else:
            kwargs['email_verification_token'] = str(uuid4())
            subscription = Subscription.create(**kwargs)
            send_verification_email(subscription)
        return subscription

    @staticmethod
    def verify_email(email_verification_token):
        subscription = Subscription.get(email_verification_token=email_verification_token)
        subscription = Subscription.update(subscription.uuid, verified=True)
        return subscription

    @staticmethod
    def cancel_subscription(uuid):
        subscription = Subscription.update(uuid, dead=True, verified=False)
        return subscription
