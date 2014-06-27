import datetime
import json

from app import app
from app.db.talks import Talk

# from flask import g
# from flask import redirect
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
    talk = Talk.create_talk(**data)
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
