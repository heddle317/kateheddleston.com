from app import app
from app.db.blogs import BlogPost
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
    return render_template('about.html')


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
    blog_posts = BlogPost.get_blogs()
    return render_template('blog.html', blog_posts=blog_posts)


@app.route('/blog/<uuid>', methods=['GET'])
@use_template_globals
def blog_post(uuid):
    blog_post = BlogPost.get_blog(uuid)
    return render_template('blog_post.html', blog_post=blog_post)
