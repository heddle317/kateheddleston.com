import pystmark

from app import config

from flask import render_template


def send_subscription_email(subscription, post_link, gallery):
    unsubscribe = u"{}/subscriptions/cancel/{}".format(config.APP_BASE_LINK, subscription.uuid)
    description = u'{}...'.format(gallery.description()[:400]) if gallery.description() else ''
    body_text = render_template('subscription_email.txt',
                                user_name=subscription.name,
                                blog_url=post_link,
                                unsubscribe_url=unsubscribe)
    body_html = render_template('subscription_email.html',
                                user_name=subscription.name,
                                blog_url=post_link,
                                gallery_title=gallery.name,
                                subtitle=gallery.subtitle,
                                author=gallery.author,
                                description=description,
                                unsubscribe_url=unsubscribe)
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


def send_contact_email(from_email, subject, body):
    subject = u'[kateheddleston.com] {}'.format(subject)
    body = u"\n This email was sent by {}\n\n".format(from_email) + body
    send_email(config.EMAIL_PERSONAL, subject, body_text=body)


def send_email(to, subject, body_text=None, body_html=None):
    # Send a single message
    message = pystmark.Message(sender=config.EMAIL_SENDER,
                               to=to,
                               subject=subject,
                               text=body_text,
                               html=body_html)
    pystmark.send(message, api_key=config.POSTMARKAPP_API_KEY)
