import json

from app import app
from app import config
from app.twitter import get_tweet_comments
from app.utils.email import send_email

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
    send_email(email, subject, body)
    return json.dumps(data), 200, {'Content-Type': 'application/json'}


@app.route('/blog/<uuid>/comments', methods=['GET'])
def blog_comments(uuid):
    # post = Gallery.get_gallery(uuid)
    url = '{}/blog/{}'.format(config.APP_BASE_LINK, uuid)
    tweets = get_tweet_comments(url)
    data = {'comments': tweets, 'num_comments': len(tweets)}
    return json.dumps(data), 200, {'Content-Type': 'application/json'}


@app.route('/ping', methods=["GET"])
def ping():
    return '', 200
