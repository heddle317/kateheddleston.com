import datetime
import json

from app import app
from app import config
from app.db.galleries import Gallery
from app.db.subscriptions import Subscription
from app.db.talks import Talk
from app.utils.decorators.template_globals import use_template_globals

from flask import abort
from flask import g
from flask import redirect
from flask import render_template
from werkzeug.contrib.atom import AtomFeed


@app.route('/')
@use_template_globals
def index():
    g.nav_view = 'home'
    return render_template('home.html')


@app.route('/about')
@use_template_globals
def about():
    g.nav_view = 'about'
    gallery = Gallery.get(uuid='7baf4d66-afa2-46dd-8fee-8b113d255d14')
    return render_template('about.html',
                           gallery=gallery.to_dict(),
                           gallery_items=[item.to_dict() for item in gallery.items()],
                           gallery_uuid='7baf4d66-afa2-46dd-8fee-8b113d255d14')


@app.route('/contact', methods=['GET'])
@use_template_globals
def contact():
    g.nav_view = 'contact'
    gallery = Gallery.get(uuid='3d93674d-8331-4ac1-a318-26c7bb415fd9')
    return render_template('contact.html', gallery=gallery.to_dict(), gallery_uuid='3d93674d-8331-4ac1-a318-26c7bb415fd9', contact=True)


@app.route('/talks')
@use_template_globals
def talks():
    g.nav_view = 'talks'
    talks = Talk.get_list(published=True, sort_by='date', to_json=True)
    return render_template('talks.html', talks=talks)


@app.route('/talk/<uuid>', methods=['GET'])
@use_template_globals
def talk(uuid):
    talk = Talk.get(uuid=uuid)
    if not talk:
        abort(404)
    return render_template('talk.html', talk=talk.to_dict())


@app.route('/blog', methods=["GET"])
@use_template_globals
def blog():
    g.nav_view = 'blog'
    posts = Gallery.get_list(published=True, to_json=True, sort_by='published_at')
    return render_template('blog.html', posts=posts)


@app.route('/blog/<blog_attr>', methods=['GET'])
@use_template_globals
def blog_post_title(blog_attr):
    gallery = Gallery.get_custom_url(blog_attr)

    if gallery is None:
        gallery = Gallery.get(uuid=blog_attr)
        if gallery is None:
            abort(404)
    latest_title_url = gallery.latest_url_title()
    if blog_attr != latest_title_url:
        return redirect(u'{}/blog/{}'.format(config.APP_BASE_LINK, latest_title_url))
    current_url = u"{}/blog/{}".format(config.APP_BASE_LINK, blog_attr)
    return render_template('post.html',
                           gallery_uuid=gallery.uuid,
                           gallery=gallery.to_dict(),
                           gallery_items=[item.to_dict() for item in gallery.items()],
                           current_url=current_url,
                           facebook_app_id=config.FACEBOOK_APP_ID,
                           full_page=True)


@app.route('/blog/feed.atom', methods=['GET'])
@use_template_globals
def blog_feed():
    posts = Gallery.get_list(published=True, to_json=True)

    feed_url = "{}/blog/feed.atom".format(g.app_base_link)
    feed = AtomFeed('KateHeddleston.com Blog Posts',
                    feed_url=feed_url,
                    url='{}/blog'.format(g.app_base_link))

    for post in posts:
        post_html = []
        for item in post.get('items'):
            item_text = ""
            if item.get('title'):
                item_text += u'<h2>{}</h2><br>'.format(item.get('title'))
            if item.get('image_name'):
                img_src = u'{}/{}'.format(post.get('base_url'), item.get('image_name'))
                item_text += u"<img src='{}' />".format(img_src)
            if item.get('image_caption'):
                item_text += u"<div>{}</div>".format(item.get('image_caption'))
            item_text += '<br>'
            item_text += item.get('body')
            post_html.append(item_text)
        text = '</p><p>'.join(post_html)
        text = '<p>' + text + '</p>'

        post_url = "{}/blog/{}".format(g.app_base_link, post.get('uuid'))
        published_at = datetime.datetime.strptime(post['published_at_raw'], '%Y-%m-%dT%H:%M:%S')
        feed.add(post.get('name'),
                 text,
                 content_type='html',
                 author=post.get('author'),
                 url=post_url,
                 updated=published_at,
                 published=published_at)
    return feed.get_response()


@app.route('/verify_email/<verification_code>', methods=["GET"])
@use_template_globals
def verify_email(verification_code):
    subscription = Subscription.verify_email(verification_code)
    if not subscription:
        abort(404)
    return redirect('/subscription/{}'.format(subscription.uuid))


@app.route('/subscription/<uuid>', methods=['GET'])
@use_template_globals
def manage_subscription(uuid):
    subscription = Subscription.get(uuid=uuid)
    if not subscription:
        abort(404)
    if not subscription.verified:
        Subscription.verify_email(subscription.email_verification_token)
    return render_template("edit_subscription.html", subscription=json.dumps(subscription.to_dict()))


@app.route('/subscription/<uuid>/cancel', methods=['GET'])
@use_template_globals
def cancel_subscription(uuid):
    subscription = Subscription.get(uuid=uuid)
    subscription = Subscription.cancel_subscription(uuid)
    return redirect('/subscription/{}'.format(subscription.uuid))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
