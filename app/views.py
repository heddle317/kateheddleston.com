import json

from app import app
from app.db.galleries import Gallery
from app.db.talks import Talk
from app.utils.decorators.template_globals import use_template_globals

from flask import g
from flask import render_template


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
    g.nav_view = 'talks'
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
    g.nav_view = 'blog'
    post = Gallery.get_gallery(uuid)
    return render_template('post.html', post=post, post_json=json.dumps(post))


@app.route('/contact', methods=['GET'])
def contact():
    g.nav_view = 'contact'
    return render_template('contact.html')
