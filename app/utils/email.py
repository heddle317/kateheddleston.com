import pystmark

from app import config


def send_verification_email(subscription):
    subject = "Please verify your email address for KateHeddleston.com."
    link = "{}/verify_email/{}".format(config.APP_BASE_LINK, subscription.email_verification_token)
    body = "Thanks so much for subscribing to my blog! Click the link below to verify your " \
           "email address and to receive email notifications of new blog posts.\n\n{}\n\nSincerely,\nKate Heddleston".format(link)
    message = pystmark.Message(sender=config.SENDER_EMAIL,
                               to=subscription.email,
                               subject=subject,
                               text=body)
    pystmark.send(message, api_key=config.POSTMARKAPP_API_KEY)


def send_email(from_email, subject, body):
    subject = '[kateheddleston.com] ' + subject
    body = "\n This email was sent by {}\n\n".format(from_email) + body
    # Send a single message
    message = pystmark.Message(sender=config.SENDER_EMAIL,
                               to=config.PERSONAL_EMAIL,
                               subject=subject,
                               text=body)
    pystmark.send(message, api_key=config.POSTMARKAPP_API_KEY)
