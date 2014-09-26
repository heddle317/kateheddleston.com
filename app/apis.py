import json

from app import app
from app.utils.email import send_email

from flask import request


@app.route('/send/email', methods=['POST'])
def email_message():
    data = json.loads(request.data)
    email = data.get('email')
    subject = data.get('subject')
    body = data.get('body')
    if not email or not body:
        return json.dumps({'message': 'An email and body are required.'}), 500, {'Content-Type': 'application/json'}
    send_email(email, subject, body)
    return json.dumps(data), 200, {'Content-Type': 'application/json'}
