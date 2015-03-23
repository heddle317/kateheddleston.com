from app import config
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

    def send_verification_email(self):
        send_verification_email(self)

    def send_subscription_email(self, gallery):
        send_subscription_email(self, gallery)

    def cancel_url(self):
        return u"{}/subscriptions/cancel/{}".format(config.APP_BASE_LINK, self.uuid)

    @staticmethod
    def send_subscription_emails(gallery):
        subscriptions = Subscription.get_list(dead=False, verified=True)
        for subscription in subscriptions:
            send_subscription_email(subscription, gallery)

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
                message = "A verification email has been sent to your email address. Be sure to check your " \
                          "spam folder if you don't see it in a few minutes." \
                          "<br><br>Thanks!".format(subscription.email)
                return subscription, message
            return subscription, "Email address {} is already subscribed to this blog. Thanks!".format(subscription.email)
        else:
            kwargs['email_verification_token'] = str(uuid4())
            subscription = Subscription.create(**kwargs)
            send_verification_email(subscription)
        message = "You have successfully subscribed to my blog with email address {}.<br><br>" \
                  "A verification email has been sent to your email address. Be sure to check your spam folder if you " \
                  "don't see it after a few minutes.<br><br>Thanks!".format(subscription.email)
        return subscription, message

    @staticmethod
    def verify_email(email_verification_token):
        subscription = Subscription.get(email_verification_token=email_verification_token)
        subscription = Subscription.update(subscription.uuid, verified=True)
        return subscription

    @staticmethod
    def cancel_subscription(uuid):
        subscription = Subscription.update(uuid, dead=True, verified=False)
        return subscription
