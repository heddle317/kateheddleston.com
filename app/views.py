import datetime
import json

from app import app
from app.db.galleries import Gallery
from app.db.subscriptions import Subscription
from app.db.talks import Talk
from app.utils.decorators.template_globals import use_template_globals

from flask import g
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
    gallery = Gallery.get_gallery(uuid='7baf4d66-afa2-46dd-8fee-8b113d255d14')
    return render_template('about.html', gallery=json.dumps(gallery))


@app.route('/talks')
@use_template_globals
def talks():
    g.nav_view = 'talks'
    talks = Talk.get_talks()
    return render_template('talks.html', talks=talks)


@app.route('/talk/<uuid>', methods=['GET'])
@use_template_globals
def talk(uuid):
    talk = Talk.get_talk(uuid)
    return render_template('talk.html', talk=talk)


@app.route('/blog', methods=["GET"])
@use_template_globals
def blog():
    g.nav_view = 'blog'
    posts = Gallery.get_galleries()
    return render_template('blog.html', posts=posts)


@app.route('/blog/<uuid>', methods=['GET'])
@use_template_globals
def blog_post(uuid):
    post = Gallery.get_gallery(uuid)
    return render_template('post.html', post=post, post_json=json.dumps(post))


@app.route('/blog/feed.atom', methods=['GET'])
@use_template_globals
def blog_feed():
    posts = Gallery.get_galleries()

    feed_url = "{}/blog/feed.atom".format(g.app_base_link)
    feed = AtomFeed('Recent Posts',
                    feed_url=feed_url,
                    url=g.app_base_link)

    for post in posts:
        post_html = []
        for item in post.get('items'):
            post_html.append(item.get('body'))
        text = '</p><br><br><p>'.join(post_html)
        text = '<p>' + text + '</p>'

        post_url = "{}/blog/{}".format(g.app_base_link, post.get('uuid'))
        published_at = datetime.datetime.strptime(post['published_at_raw'], '%Y-%m-%dT%H:%M:%SZ')
        feed.add(post.get('name'),
                 unicode(text),
                 content_type='html',
                 author=post.get('author'),
                 url=post_url,
                 updated=published_at,
                 published=published_at)
    return feed.get_response()


@app.route('/contact', methods=['GET'])
@use_template_globals
def contact():
    g.nav_view = 'contact'
    return render_template('contact.html')


@app.route('/verify_email/<verification_code>', methods=["GET"])
@use_template_globals
def verify_email(verification_code):
    subscription = Subscription.verify_email(verification_code)
    return render_template("email_verified.html", subscription=subscription)
