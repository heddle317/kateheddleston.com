import json

from app import app
from app.db.comments import Comment
from app.db.categories import Category
from app.db.galleries import Gallery
from app.db.subscriptions import Subscription
from app.db.subscriptions import SubscriptionCategory
from app.utils.aws import s3_change_image_resolutions
from app.utils.datetime_tools import format_date
from app.utils.datetime_tools import now_utc
from app.utils.email import send_contact_email

from flask import request


@app.route('/send/email', methods=['POST'])
def email_message():
    data = json.loads(request.data)
    email = data.get('email')
    subject = data.get('subject')
    body = data.get('body')
    if not email or not body:
        return_data = {'message': 'An email and body are required.'}
        return json.dumps(return_data), 500, {'Content-Type': 'application/json'}
    data = {'ip': request.remote_addr,
            'time': format_date(now_utc(), '%H:%M:%S, %B %d, %Y')}
    send_contact_email(email, subject, body, data=data)
    return json.dumps(data), 200, {'Content-Type': 'application/json'}


@app.route('/blog/<uuid>/comments', methods=['GET'])
def blog_comments(uuid):
    tweets = Comment.get_comments_json(gallery_uuid=uuid, sort_by='-created_at')
    data = {'comments': tweets, 'num_comments': len(tweets)}
    return json.dumps(data), 200, {'Content-Type': 'application/json'}


@app.route('/images/generate_sizes', methods=['POST'])
def create_multiple_photos():
    data = json.loads(request.data)
    s3_change_image_resolutions(data['image_route'], data['filename'])
    data = {'message': 'success'}
    return json.dumps(data), 200, {'Content-Type': 'application/json'}


@app.route('/subscriptions/subscribe', methods=['POST'])
def subscribe():
    data = json.loads(request.data)
    if not data.get('email'):
        return json.dumps({'message': 'An email address is required.'}), 200, {'content-type': 'application/json'}
    subscription, message = Subscription.create_or_update(data.get('email'), name=data.get('name'))
    message = {"message": message}
    return json.dumps(message), 200, {'content-type': 'application/json'}


@app.route('/gallery/<uuid>', methods=['GET'])
def get_gallery_ajax(uuid):
    gallery = Gallery.get(uuid=uuid)
    return json.dumps(gallery.to_dict()), 200, {'Content-Type': 'application/json'}


@app.route('/subscription/categories', methods=['GET'])
def subscription_categories():
    categories = Category.get_list(to_json=True)
    return json.dumps(categories), 200, {'Content-Type': 'application/json'}


@app.route('/subscription/<uuid>', methods=['POST'])
def edit_subscription(uuid):
    data = json.loads(request.data)
    subscription = Subscription.update_subscription(uuid, name=data.get('name'))
    return json.dumps(subscription.to_dict()), 200, {'Content-Type': 'application/json'}


@app.route('/subscription/<uuid>', methods=['DELETE'])
def api_cancel_subscription(uuid):
    subscription = Subscription.cancel_subscription(uuid)
    return json.dumps(subscription.to_dict()), 200, {'Content-Type': 'application/json'}


@app.route('/subscription/<subscription_uuid>/categories', methods=['POST'])
def subscription_add_category(subscription_uuid):
    category_uuid = json.loads(request.data).get('category_uuid')
    SubscriptionCategory.create(subscription_uuid=subscription_uuid, category_uuid=category_uuid)
    subscription = Subscription.get(uuid=subscription_uuid)
    return json.dumps(subscription.to_dict()), 200, {'Content-Type': 'application/json'}


@app.route('/subscription/<subscription_uuid>/categories/<category_uuid>', methods=['DELETE'])
def subscription_delete_category(subscription_uuid, category_uuid):
    SubscriptionCategory.delete(subscription_uuid=subscription_uuid, category_uuid=category_uuid)
    subscription = Subscription.get(uuid=subscription_uuid)
    return json.dumps(subscription.to_dict()), 200, {'Content-Type': 'application/json'}


@app.route('/ping', methods=["GET"])
def ping():
    return '', 200
