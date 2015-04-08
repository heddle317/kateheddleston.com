import sys

from app import app
from app.db.subscriptions import Subscription
from app.db.galleries import Gallery


if __name__ == "__main__":
    email = sys.argv[1]
    gallery_uuid = sys.argv[2]
    gallery = Gallery.get(uuid=gallery_uuid)
    with app.app_context():
        Subscription.send_subscription_email(email, gallery)
