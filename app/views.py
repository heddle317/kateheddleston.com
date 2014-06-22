from app import app
from app.utils.decorators.template_globals import use_template_globals
from flask import render_template


@app.route('/')
@use_template_globals
def index():
    return render_template('home.html')
