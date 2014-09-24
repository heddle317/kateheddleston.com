import json

from app import app
from app.utils.email import send_email

from flask import flash
from flask import request


@app.route('/send/email', methods=['POST'])
def email_message():
    data = json.loads(request.data)
    email = data.get('email')
    subject = data.get('subject')
    body = data.get('body')
    send_email(email, subject, body)
    flash('An email was successfully sent to Kate Heddleston.', 'success')
    return json.dumps(data), 200, {'Content-Type': 'application/json'}
