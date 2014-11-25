import base64
import hashlib
import hmac
import json

from app import app
from app import config
from app.db.galleries import Gallery
from app.db.talks import Talk
from app.db.user import get_verified_user
from app.utils.decorators.template_globals import use_template_globals

from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user


policy_document = {"expiration": "2020-01-01T00:00:00Z",
                   "conditions": [{"bucket": "images.kateheddleston.com"},
                                  ["starts-with", "$key", ""],
                                  {"acl": "public-read"},
                                  ["starts-with", "$Content-Type", ""],
                                  ["starts-with", "$filename", ""],
                                  ["content-length-range", 0, 524288000]]}


@app.route('/login', methods=['GET'])
@use_template_globals
def login_template():
    return render_template('admin/login.html')


@app.route('/login', methods=["POST"])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    user = get_verified_user(email, password)
    if user:
        login_user(user, remember=True)
        return redirect('/admin/galleries')
    return redirect('/login')


@app.route('/logout', methods=["GET"])
@login_required
def logout():
    logout_user()
    return redirect('/login')


@app.route('/admin/talks', methods=['GET'])
@login_required
@use_template_globals
def get_talks():
    if request.is_xhr:
        talks = Talk.get_talks(published=False)
        return json.dumps(talks), 200, {'Content-Type': 'application/json'}
    g.nav_view = 'talks'
    return render_template('admin/talks.html')


@app.route('/admin/galleries', methods=['GET'])
@login_required
@use_template_globals
def get_galleries():
    if request.is_xhr:
        galleries = Gallery.get_galleries(published=False)
        return json.dumps(galleries), 200, {'Content-Type': 'application/json'}
    g.nav_view = 'galleries'
    return render_template('admin/galleries.html')


@app.route('/admin/gallery/<uuid>', methods=['GET'])
@login_required
@use_template_globals
def edit_gallery(uuid):
    gallery = Gallery.get_gallery(uuid)
    g.nav_view = 'galleries'
    policy = base64.b64encode(json.dumps(policy_document))
    signature = base64.b64encode(hmac.new(config.AWS_SECRET_ACCESS_KEY, policy, hashlib.sha1).digest())
    access_key = config.AWS_ACCESS_KEY_ID
    return render_template('admin/edit_gallery.html',
                           gallery=gallery,
                           gallery_json=json.dumps(gallery),
                           policy=policy,
                           signature=signature,
                           accessKey=access_key)


@app.route('/admin/gallery/<uuid>/preview', methods=['GET'])
@login_required
@use_template_globals
def preview_gallery(uuid):
    gallery = Gallery.get_gallery(uuid)
    g.nav_view = 'galleries'
    return render_template('admin/preview.html', post=gallery, post_json=json.dumps(gallery))
