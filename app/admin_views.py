import json

from app import app
from app.db.talks import Talk
from app.db.user import get_verified_user
from app.utils.decorators.template_globals import use_template_globals

from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user


@app.route('/admin')
@login_required
@use_template_globals
def admin():
    g.nav_view = 'admin'
    return render_template('admin.html')


@app.route('/login', methods=['GET'])
@use_template_globals
def login_template():
    return render_template('login.html')


@app.route('/login', methods=["POST"])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    user = get_verified_user(email, password)
    if user:
        login_user(user, remember=True)
        return redirect('/admin/talks')
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
    talks = Talk.get_talks()
    if request.is_xhr:
        return json.dumps(talks), 200, {'Content-Type': 'application/json'}
    g.current_user = current_user
    g.nav_view = 'talks'
    return render_template('edit_talks.html', talks=talks)
