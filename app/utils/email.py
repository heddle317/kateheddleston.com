import pystmark

from app import config


def send_email(from_email, subject, body):
    subject = '[kateheddleston.com] ' + subject
    body = "\n This email was sent by {}\n".format(from_email) + body
    # Send a single message
    message = pystmark.Message(sender=config.SENDER_EMAIL,
                               to=config.PERSONAL_EMAIL,
                               subject=subject,
                               text=body)
    pystmark.send(message, api_key=config.POSTMARKAPP_API_KEY)
