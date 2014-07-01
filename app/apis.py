import datetime
import json

from app import app
from app.db.blogs import BlogPost
from app.db.talks import Talk
from app.utils.exceptions import BlogException
from app.utils.exceptions import TalkException

# from flask import g
# from flask import redirect
from flask import flash
from flask import request
from flask_login import login_required


@app.route('/admin/talks', methods=['POST'])
@login_required
def create_talk():
    data = json.loads(request.data)
    date = data.get('date')
    if date:
        date = datetime.datetime.strptime(date, '%B %d, %Y')
        data['date'] = date
    try:
        talk = Talk.create_talk(**data)
    except TalkException as e:
        flash(e.message, 'danger')
        return json.dumps({'message': e.message}), 400, {'Content-Type': 'application/json'}
    return json.dumps(talk), 200, {'Content-Type': 'application/json'}


@app.route('/admin/talks/<uuid>', methods=['PUT'])
@login_required
def edit_talk(uuid):
    talk = Talk.update_talk(uuid, **request.form)
    return json.dumps(talk), 200, {'Content-Type': 'application/json'}


@app.route('/admin/talks/<uuid>', methods=['DELETE'])
@login_required
def delete_talk(uuid):
    Talk.delete_talk(uuid)
    return json.dumps({'message': 'Your talk was successfully deleted.'}), 200, {'Content-Type': 'application/json'}


@app.route('/admin/blog_post', methods=['GET'])
@login_required
def get_blog_posts():
    blogs = BlogPost.get_blogs()
    return json.dumps(blogs), 200, {'Content-Type': 'application/json'}


@app.route('/admin/blog_post', methods=['POST'])
@login_required
def create_blog_post():
    data = json.loads(request.data)
    date = data.get('date')
    if date:
        date = datetime.datetime.strptime(date, '%B %d, %Y')
        data['date'] = date
    try:
        blog = BlogPost.create_blog(**data)
    except BlogException as e:
        flash(e.message, 'danger')
        return json.dumps({'message': e.message}), 400, {'Content-Type': 'application/json'}
    return json.dumps(blog), 200, {'Content-Type': 'application/json'}


@app.route('/admin/blog_post/<uuid>', methods=['PUT'])
@login_required
def edit_blog_post(uuid):
    blog = BlogPost.update_blog(uuid, **request.form)
    return json.dumps(blog), 200, {'Content-Type': 'application/json'}


@app.route('/admin/blog_post/<uuid>', methods=['DELETE'])
@login_required
def delete_blog(uuid):
    BlogPost.delete_blog(uuid)
    return json.dumps({'message': 'Your blog was successfully deleted.'}), 200, {'Content-Type': 'application/json'}
