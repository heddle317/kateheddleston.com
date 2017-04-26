from app import config
from app import q
from app.db import Base
from app.db import BaseModelObject
from app.db.categories import Category
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

    def to_dict(self):
        attr_dict = BaseModelObject.to_dict(self)
        subscription_categories = SubscriptionCategory.get_list(subscription_uuid=self.uuid, to_json=True)
        attr_dict.update({'categories': subscription_categories})
        return attr_dict

    def send_verification_email(self):
        send_verification_email(self)

    def cancel_url(self):
        return u"{}/subscription/{}/cancel".format(config.APP_BASE_LINK, self.uuid)

    def url(self):
        return u"{}/subscription/{}".format(config.APP_BASE_LINK, self.uuid)

    def subscribed_to_categories(self, category_uuids):
        if not category_uuids:
            return True
        subscription_categories = SubscriptionCategory.get_list(subscription_uuid=self.uuid)
        sc_uuids = [sc.category_uuid for sc in subscription_categories]
        # Return true if any subscription categories are in the given categories
        for uuid in sc_uuids:
            if uuid in category_uuids:
                return True
        return False

    @staticmethod
    def send_subscription_email(email, gallery):
        subscription = Subscription.get(dead=False, verified=True, email=email)
        if not subscription:
            return
        gallery_category_uuids = gallery.category_uuids()
        if subscription.subscribed_to_categories(gallery_category_uuids):
            send_subscription_email(subscription, gallery)

    @staticmethod
    def send_subscription_emails(gallery):
        gallery_category_uuids = gallery.category_uuids()
        if gallery_category_uuids:
            subscription_uuids = list(set([s.subscription_uuid for s in SubscriptionCategory.get_list(category_uuid=gallery_category_uuids)]))
            subscriptions = Subscription.get_list(dead=False, verified=True, uuid=subscription_uuids)
        else:
            subscriptions = Subscription.get_list(dead=False, verified=True)
        for subscription in subscriptions:
            q.enqueue(send_subscription_email, subscription, gallery)

    @staticmethod
    def create_or_update(email, name=None):
        subscription = Subscription.get(email=email)
        if subscription:
            if subscription.verified:
                if subscription.dead:
                    message = "Email address {} has been re-subscribed to this blog. Thanks!".format(subscription.email)
                else:
                    message = "Email address {} is already subscribed to this blog. Thanks!".format(subscription.email)
            else:
                message = "A verification email has been sent to your email address. Be sure to check your " \
                          "spam folder if you don't see it in a few minutes." \
                          "<br><br>Thanks!".format(subscription.email)
            subscription = Subscription.update_subscription(subscription.uuid, name=name)
        else:
            subscription = Subscription.create_subscription(email, name)
            message = "You have successfully subscribed to my blog with email address {}.<br><br>" \
                      "A verification email has been sent to your email address. Be sure to check your " \
                      "spam folder if you don't see it in a few minutes." \
                      "<br><br>Thanks!".format(subscription.email)
        return subscription, message

    @staticmethod
    def create_subscription(email, name):
        if not email:
            raise ValueError('email required')
        if not name:
            raise ValueError('name required')
        subscription = Subscription.get(email=email)
        if subscription:
            raise ValueError('Subscription already exists')

        email_verification_token = str(uuid4())
        subscription = Subscription.create(name=name, email=email, email_verification_token=email_verification_token)
        categories = Category.get_list()
        for category in categories:
            SubscriptionCategory.create(subscription_uuid=subscription.uuid, category_uuid=category.uuid)
        send_verification_email(subscription)
        return subscription

    @staticmethod
    def update_subscription(uuid, name=None):
        subscription = Subscription.get(uuid=uuid)
        if name:
            subscription = Subscription.update(subscription.uuid, dead=False, name=name)
        else:
            subscription = Subscription.update(subscription.uuid, dead=False)
        if not subscription.verified:
            send_verification_email(subscription)
        return subscription

    @staticmethod
    def verify_email(email_verification_token):
        subscription = Subscription.get(email_verification_token=email_verification_token)
        subscription = Subscription.update(subscription.uuid, verified=True)
        return subscription

    @staticmethod
    def cancel_subscription(uuid):
        subscription = Subscription.update(uuid, dead=True)
        return subscription


class SubscriptionCategory(Base, BaseModelObject):
    __tablename__ = 'subscription_categories'
    uuid = Column(UUID, primary_key=True)
    subscription_uuid = Column(UUID)
    category_uuid = Column(UUID)

    def to_dict(self):
        attr_dict = BaseModelObject.to_dict(self)
        category = Category.get(uuid=self.category_uuid)
        attr_dict.update({'name': category.name})
        return attr_dict
