import pystmark

from app import config
from app import env
from app.utils.datetime_tools import format_date

from flask import render_template


def send_subscription_email(subscription, gallery):
    description = u'{}...'.format(gallery.description()[:400]) if gallery.description() else ''
    category = gallery.latest_category()
    template = env.get_template('subscription_email.txt')
    body_text = template.render(user_name=subscription.name,
                                blog_url=gallery.url(),
                                cancel_url=subscription.cancel_url(),
                                published_at=format_date(gallery.published_at),
                                category=category,
                                unsubscribe_url=subscription.url())
    template = env.get_template('subscription_email.html')
    body_html = template.render(user_name=subscription.name,
                                blog_url=gallery.url(),
                                gallery_title=gallery.name,
                                subtitle=gallery.subtitle,
                                published_at=format_date(gallery.published_at),
                                author=gallery.author,
                                description=description,
                                category=category,
                                cancel_url=subscription.cancel_url(),
                                unsubscribe_url=subscription.url())
    send_email(subscription.email, gallery.name, body_text=body_text, body_html=body_html)


def send_verification_email(subscription):
    subject = "Please verify your email address for KateHeddleston.com."
    link = u"{}/verify_email/{}".format(config.APP_BASE_LINK, subscription.email_verification_token)
    body_text = render_template("verify_email.txt",
                                user_name=subscription.name,
                                verify_url=link)
    body_html = render_template("verify_email.html",
                                user_name=subscription.name,
                                verify_url=link)
    send_email(subscription.email, subject, body_text=body_text, body_html=body_html)


def send_contact_email(from_email, subject, body, data=None):
    subject = u'[kateheddleston.com] {}'.format(subject)
    body = u"\n This email was sent by {}\n\n".format(from_email) + body
    if data:
        body = body + "\n\n"
        for key, value in data.items():
            body = body + "\n{}: {}".format(key.capitalize(), value)
    send_email(config.EMAIL_PERSONAL, subject, body_text=body)


def send_invite(user):
    subject = 'You have been invited to be an admin on KateHeddleston.com!'
    body = 'Click here to accept your invitation to KateHeddleston.com.' \
           '\n\n{}/admin/users/{}'.format(config.APP_BASE_LINK, user.uuid)
    send_email(user.email, subject, body)


def send_email(to, subject, body_text=None, body_html=None):
    # Send a single message
    message = pystmark.Message(sender=config.EMAIL_SENDER,
                               to=to,
                               subject=subject,
                               text=body_text,
                               html=body_html)
    pystmark.send(message, api_key=config.POSTMARKAPP_API_KEY)
