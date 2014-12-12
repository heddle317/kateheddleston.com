import json

from app import app
from app import config
from app.db.subscriptions import Subscription
from app.twitter import get_tweet_comments
from app.twitter import update_tweet_comments
from app.utils.aws import s3_change_image_resolutions
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
    send_contact_email(email, subject, body)
    return json.dumps(data), 200, {'Content-Type': 'application/json'}


@app.route('/blog/<uuid>/comments', methods=['GET'])
def blog_comments(uuid):
    tweets = get_tweet_comments(uuid)
    data = {'comments': tweets, 'num_comments': len(tweets)}
    return json.dumps(data), 200, {'Content-Type': 'application/json'}


@app.route('/blog/<uuid>/comments/update', methods=['GET'])
def update_blog_comments(uuid):
    # post = Gallery.get_gallery(uuid)
    url = '{}/blog/{}'.format(config.APP_BASE_LINK, uuid)
    tweets = update_tweet_comments(url, uuid)
    data = {'comments': tweets, 'num_comments': len(tweets)}
    return json.dumps(data), 200, {'Content-Type': 'application/json'}


@app.route('/blog/<gallery_uuid>/<image_name>/generate_sizes', methods=['GET'])
def create_multiple_photos(gallery_uuid, image_name):
    s3_change_image_resolutions(gallery_uuid, image_name)
    data = {'message': 'success'}
    return json.dumps(data), 200, {'Content-Type': 'application/json'}


@app.route('/subscriptions/subscribe', methods=['POST'])
def subscribe():
    data = json.loads(request.data)
    Subscription.create_subscription(**data)
    message = "You have successfully subscribed to KateHeddleston.com's blog with email address {}.<br><br>" \
              "You will receive an email to verify your email address shortly. Be sure to check your spam folder if you " \
              "don't see it after a few minutes. Thanks!".format(data.get('email'))
    message = {"message": message}
    return json.dumps(message), 200, {'Content-Type': 'application/json'}


@app.route('/subscriptions/cancel/<email>', methods=['GET'])
def cancel_subscription(email):
    Subscription.cancel_subscription(email)
    message = "You have successfully unsubscribed email address {} from KateHeddleston.com's blog.".format(email)
    message = {"message": message}
    return json.dumps(message), 200, {'Content-Type': 'application/json'}


@app.route('/ping', methods=["GET"])
def ping():
    return '', 200
