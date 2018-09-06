import base64
import hashlib
import hmac
import json
import requests
import urllib

from app import app
from app import config
from app.db.galleries import Gallery
from app.db.user import get_verified_user
from app.db.user import User
from app.db.user import update_user
from app.utils.decorators.template_globals import use_template_globals

from flask import abort
from flask import g
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user


policy_document = {"expiration": "2020-01-01T00:00:00Z",
                   "conditions": [{"bucket": config.AWS_IMAGE_BUCKET},
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
    g.nav_view = 'talks'
    return render_template('admin/talks.html')


@app.route('/admin/talk', methods=['GET'])
@app.route('/admin/talk/<uuid>', methods=['GET'])
@login_required
@use_template_globals
def edit_talk(uuid=None):
    g.nav_view = 'talks'
    policy = base64.b64encode(json.dumps(policy_document).encode('utf-8'))
    signature = base64.b64encode(hmac.new(config.AWS_SECRET_ACCESS_KEY.encode('utf-8'), policy, hashlib.sha1).digest())
    access_key = config.AWS_ACCESS_KEY_ID
    return render_template('admin/edit_talk.html',
                           talk_uuid=uuid or '',
                           policy=policy,
                           signature=signature,
                           accessKey=access_key)


@app.route('/admin/galleries', methods=['GET'])
@login_required
@use_template_globals
def get_galleries():
    g.nav_view = 'galleries'
    return render_template('admin/galleries.html')


@app.route('/admin/gallery/create', methods=['GET'])
@login_required
def get_admin_gallery(uuid=None):
    gallery = Gallery.blank()
    return json.dumps(gallery), 200, {'Content-Type': 'application/json'}


@app.route('/admin/gallery', methods=['GET'])
@app.route('/admin/gallery/<uuid>', methods=['GET'])
@login_required
@use_template_globals
def edit_gallery(uuid=None):
    g.nav_view = 'galleries'
    policy = base64.b64encode(json.dumps(policy_document).encode('utf-8'))
    signature = base64.b64encode(hmac.new(config.AWS_SECRET_ACCESS_KEY.encode('utf-8'), policy, hashlib.sha1).digest())
    access_key = config.AWS_ACCESS_KEY_ID
    return render_template('admin/edit_gallery.html',
                           gallery_uuid=uuid or '',
                           policy=policy,
                           signature=signature,
                           accessKey=access_key)


@app.route('/admin/subscribers', methods=['GET'])
@login_required
@use_template_globals
def subscribers():
    g.nav_view = 'subscribers'
    return render_template('admin/subscribers.html')


@app.route('/admin/users', methods=['GET'])
@login_required
@use_template_globals
def admin_users():
    g.nav_view = 'users'
    return render_template('admin/admin_users.html')


@app.route('/admin/auth', methods=['GET'])
@login_required
@use_template_globals
def social_auth():
    if request.args.get('code'):
        code = request.args.get('code')
        route = "https://graph.facebook.com/oauth/access_token"
        params = {'client_id': config.FACEBOOK_APP_ID,
                  'client_secret': config.FACEBOOK_APP_SECRET,
                  'code': code,
                  'redirect_uri': '{}/admin/auth'.format(config.APP_BASE_LINK)}
        path = route + "?" + urllib.urlencode(params)
        response = requests.get(path)
        access_token, expires = response.text.split('&')
        access_token = access_token.split('=')[1]
        g.current_user.update_code(access_token)
    g.nav_view = 'auth'
    return render_template('admin/social_login.html')


@app.route("/admin/auth/facebook", methods=['GET'])
@login_required
def facebook_auth_redirect():
    redirect_uri = '{}/admin/auth'.format(config.APP_BASE_LINK)
    scope = 'public_profile,publish_actions,read_stream'
    params = {'client_id': config.FACEBOOK_APP_ID,
              'redirect_uri': redirect_uri,
              'scope': scope,
              'response_type': 'code'}
    return redirect('https://www.facebook.com/dialog/oauth?{}'.format(urllib.urlencode(params)))


@app.route("/admin/users/<uuid>", methods=['GET'])
@use_template_globals
def accept_invite(uuid):
    user = User.get(uuid=uuid)
    if not user:
        abort(404)
    return render_template('admin/register.html', user=user)


@app.route("/admin/users/<uuid>", methods=['POST'])
@use_template_globals
def update_user_info(uuid):
    user = User.get(uuid=uuid)
    existing = True if user.password_hash else False
    if not user:
        abort(404)
    email = request.form.get('email')
    name = request.form.get('name')
    new_password = request.form.get('new_password')
    password_verification = request.form.get('password_verification')
    if new_password != password_verification:
        flash('Passwords do not match.', 'danger')
        return render_template('admin/register.html', user=user)
    current_password = request.form.get('current_password')
    try:
        user = update_user(uuid, email, name, new_password, current_password)
    except:
        flash('Incorrect current password for updating account.', 'danger')
        return render_template('admin/register.html', user=user)
    if existing:
        return render_template('admin/register.html', user=user)
    return redirect('/login')
