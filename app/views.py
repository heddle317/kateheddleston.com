from app import app
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
