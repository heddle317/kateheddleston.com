import datetime
import json

from app import app
from app.db.galleries import Gallery
from app.db.talks import Talk

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
    except ValueError as e:
        flash(e.message, 'danger')
        return json.dumps({'message': e.message}), 400, {'Content-Type': 'application/json'}
    return json.dumps(talk), 200, {'Content-Type': 'application/json'}


@app.route('/admin/talks/<uuid>', methods=['PUT'])
@login_required
def edit_talk(uuid):
    data = json.loads(request.data)
    talk = Talk.update_talk(uuid, **data)
    return json.dumps(talk), 200, {'Content-Type': 'application/json'}


@app.route('/admin/talks/<uuid>', methods=['DELETE'])
@login_required
def delete_talk(uuid):
    Talk.delete_talk(uuid)
    return_data = {'message': 'Your talk was successfully deleted.'}
    return json.dumps(return_data), 200, {'Content-Type': 'application/json'}


@app.route('/admin/galleries', methods=['POST'])
@login_required
def create_gallery():
    data = json.loads(request.data)
    try:
        gallery = Gallery.create_gallery(**data)
    except ValueError as e:
        flash(e.message, 'danger')
        return json.dumps({'message': e.message}), 400, {'Content-Type': 'application/json'}
    return json.dumps(gallery), 200, {'Content-Type': 'application/json'}


@app.route('/admin/gallery/<uuid>', methods=['PUT'])
@login_required
def update_gallery(uuid):
    data = json.loads(request.data)
    gallery = Gallery.update_gallery(uuid, **data)
    return json.dumps(gallery), 200, {'Content-Type': 'application/json'}


@app.route('/admin/gallery/<uuid>', methods=['DELETE'])
@login_required
def delete_gallery(uuid):
    Gallery.delete_gallery(uuid)
    return_data = {'message': 'Your gallery was successfully deleted.'}
    return json.dumps(return_data), 200, {'Content-Type': 'application/json'}
