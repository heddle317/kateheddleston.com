import pystmark

from app import config


def send_subscription_email(subscription, post_link, post_name):
    unsubscribe = "{}/subscriptions/cancel/{}".format(config.APP_BASE_LINK, subscription.get('uuid'))
    body = "Hi {},\n\nThere is a new blog post available at KateHeddleston.com: {}\n\n" \
           "I hope you're having a wonderful day!\nKate Heddleston\n\n\n" \
           "To unsubscribe from these emails, click here: {}".format(subscription['name'], post_link, unsubscribe)
    send_email(subscription['email'], post_name, body)


def send_verification_email(subscription):
    subject = "Please verify your email address for KateHeddleston.com."
    link = "{}/verify_email/{}".format(config.APP_BASE_LINK, subscription.email_verification_token)
    body = "Thanks so much for subscribing to my blog! Click the link below to verify your " \
           "email address and to receive email notifications of new blog posts.\n\n{}\n\nSincerely,\nKate Heddleston".format(link)
    send_email(subscription.email, subject, body)


def send_contact_email(from_email, subject, body):
    subject = '[kateheddleston.com] ' + subject
    body = "\n This email was sent by {}\n\n".format(from_email) + body
    send_email(config.EMAIL_PERSONAL, subject, body)


def send_email(to, subject, body):
    # Send a single message
    message = pystmark.Message(sender=config.EMAIL_SENDER,
                               to=to,
                               subject=subject,
                               text=body)
    pystmark.send(message, api_key=config.POSTMARKAPP_API_KEY)
