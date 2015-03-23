import datetime
import json

from app import app
from app.db.galleries import Category
from app.db.galleries import Gallery
from app.db.galleries import GalleryCategory
from app.db.galleries import GalleryItem
from app.db.galleries import GalleryItemComment
from app.db.subscriptions import Subscription
from app.db.subscriptions import SubscriptionCategory
from app.db.talks import Talk

from flask import g
# from flask import redirect
from flask import flash
from flask import request
from flask_login import login_required


@app.route('/admin/api/talks', methods=['GET'])
@login_required
def api_get_talks():
    talks = Talk.get_list(published=False, to_json=True, sort_by='date')
    return json.dumps(talks), 200, {'Content-Type': 'application/json'}


@app.route('/admin/api/talks', methods=['POST'])
@login_required
def create_talk():
    data = json.loads(request.data)
    date = data.get('date')
    if date:
        date = datetime.datetime.strptime(date, '%B %d, %Y')
        data['date'] = date
    try:
        talk = Talk.create(**data)
    except ValueError as e:
        flash(e.message, 'danger')
        return json.dumps({'message': e.message}), 400, {'Content-Type': 'application/json'}
    return json.dumps(talk.to_dict()), 200, {'Content-Type': 'application/json'}


@app.route('/admin/api/talks', methods=['GET'])
@app.route('/admin/api/talks/<uuid>', methods=['GET'])
@login_required
def api_edit_talk(uuid=None):
    if uuid:
        talk = Talk.get(uuid=uuid).to_dict()
    else:
        talk = Talk.blank()
    return json.dumps(talk), 200, {'Content-Type': 'application/json'}


@app.route('/admin/api/talks/<uuid>', methods=['PUT'])
@login_required
def update_talk(uuid):
    data = json.loads(request.data)
    talk = Talk.update_talk(uuid, **data)
    return json.dumps(talk.to_dict()), 200, {'Content-Type': 'application/json'}


@app.route('/admin/api/talks/<uuid>', methods=['DELETE'])
@login_required
def delete_talk(uuid):
    Talk.delete(uuid=uuid)
    return_data = {'message': 'Your talk was successfully deleted.'}
    return json.dumps(return_data), 200, {'Content-Type': 'application/json'}


@app.route('/admin/api/galleries', methods=['GET'])
@login_required
def api_get_galleries():
    galleries = Gallery.get_list(published=False, to_json=True, sort_by='published_at')
    return json.dumps(galleries), 200, {'Content-Type': 'application/json'}


@app.route('/admin/api/galleries', methods=['POST'])
@login_required
def create_gallery():
    data = json.loads(request.data)
    try:
        gallery = Gallery.create_gallery(**data)
    except ValueError as e:
        flash(e.message, 'danger')
        return json.dumps({'message': e.message}), 400, {'Content-Type': 'application/json'}
    return json.dumps(gallery.to_dict(admin=True)), 200, {'Content-Type': 'application/json'}


@app.route('/admin/api/gallery', methods=['GET'])
@app.route('/admin/api/gallery/<uuid>', methods=['GET'])
@login_required
def api_edit_gallery(uuid=None):
    if uuid:
        gallery = Gallery.get(uuid=uuid).to_dict(admin=True)
    else:
        gallery = Gallery.blank()
    return json.dumps(gallery), 200, {'Content-Type': 'application/json'}


@app.route('/admin/api/gallery/<uuid>', methods=['PUT'])
@login_required
def update_gallery(uuid=None):
    data = json.loads(request.data)
    gallery = Gallery.update(uuid, **data)
    return json.dumps(gallery.to_dict(admin=True)), 200, {'Content-Type': 'application/json'}


@app.route('/admin/api/gallery/<uuid>', methods=['DELETE'])
@login_required
def delete_gallery(uuid):
    Gallery.delete(uuid=uuid)
    return_data = {'message': 'Your gallery was successfully deleted.'}
    return json.dumps(return_data), 200, {'Content-Type': 'application/json'}


@app.route('/admin/api/gallery/item', methods=['POST'])
@login_required
def create_gallery_item():
    data = json.loads(request.data)
    item = GalleryItem.create(**data)
    return json.dumps(item.to_dict(admin=True)), 200, {'Content-Type': 'application/json'}


@app.route('/admin/api/gallery/item/<uuid>', methods=['POST'])
@login_required
def update_gallery_item(uuid):
    item = GalleryItem.get(uuid=uuid)
    if not item:
        return '', 404, {'Content-Type': 'application/json'}
    data = json.loads(request.data)
    if 'uuid' in data.keys():
        data.pop('uuid')
    item = GalleryItem.update(uuid, **data)
    return json.dumps(item.to_dict(admin=True)), 200, {'Content-Type': 'application/json'}


@app.route('/admin/api/gallery/item/<uuid>', methods=['DELETE'])
@login_required
def delete_gallery_item(uuid):
    GalleryItem.delete(uuid=uuid)
    return_data = {'message': 'The gallery item {} was successfully deleted.'.format(uuid)}
    return json.dumps(return_data), 200, {'Content-Type': 'application/json'}


@app.route('/admin/api/gallery/item/<item_uuid>/comments', methods=['POST'])
@login_required
def gallery_item_create_comment(item_uuid):
    item = GalleryItem.get(uuid=item_uuid)
    if not item:
        return '', 404, {'Content-Type': 'application/json'}
    data = json.loads(request.data)
    item.add_comment(author_uuid=g.user.uuid, **data)
    item = GalleryItem.get(uuid=item_uuid)
    return json.dumps(item.to_dict(admin=True)), 200, {'Content-Type': 'application/json'}


@app.route('/admin/api/gallery/item/<item_uuid>/comments/<comment_uuid>', methods=['POST'])
@login_required
def gallery_item_comment_update(item_uuid, comment_uuid):
    data = json.loads(request.data)
    GalleryItemComment.update(comment_uuid, **data)
    item = GalleryItem.get(uuid=item_uuid)
    return json.dumps(item.to_dict(admin=True)), 200, {'Content-Type': 'application/json'}


@app.route('/admin/api/gallery/item/<item_uuid>/comments/<comment_uuid>', methods=['DELETE'])
@login_required
def gallery_item_comment_delete(item_uuid, comment_uuid):
    GalleryItemComment.delete(uuid=comment_uuid)
    item = GalleryItem.get(uuid=item_uuid)
    return json.dumps(item.to_dict(admin=True)), 200, {'Content-Type': 'application/json'}


@app.route('/admin/api/subscribers', methods=['GET'])
@login_required
def get_subscribers():
    subscribers = Subscription.get_list(sort_by='created_at', desc=True, to_json=True)
    return json.dumps(subscribers), 200, {'Content-Type': 'application/json'}


@app.route('/admin/api/subscribers/<uuid>/verify', methods=['POST'])
@login_required
def verify_subscriber(uuid):
    subscriber = Subscription.get(uuid=uuid)
    subscriber.send_verification_email()
    return json.dumps(subscriber.to_dict()), 200, {'Content-Type': 'application/json'}


@app.route('/admin/api/categories', methods=['GET'])
@login_required
def api_get_categories(subscribers_uuid):
    categories = Category.get_list(to_json=True)
    return json.dumps(categories), 200, {'Content-Type': 'application/json'}


@app.route('/admin/api/subscribers/<subscriber_uuid>/categories', methods=['POST'])
@login_required
def subscriber_add_category(subscriber_uuid):
    category_uuid = json.loads(request.data).get('category_uuid')
    SubscriptionCategory.create(subscriber_uuid=subscriber_uuid, category_uuid=category_uuid)
    subscriber_categories = SubscriptionCategory.get_list(subscriber_uuid=subscriber_uuid, to_json=True)
    return json.dumps(subscriber_categories), 200, {'Content-Type': 'application/json'}


@app.route('/admin/api/subscribers/<subscriber_uuid>/categories/<subscriber_category_uuid>', methods=['DELETE'])
@login_required
def subscriber_delete_category(subscriber_uuid, subscriber_category_uuid):
    SubscriptionCategory.delete(uuid=subscriber_category_uuid)
    subscriber_categories = SubscriptionCategory.get_list(subscriber_uuid=subscriber_uuid, to_json=True)
    return json.dumps(subscriber_categories), 200, {'Content-Type': 'application/json'}


@app.route('/admin/api/gallery/<gallery_uuid>/categories', methods=['POST'])
@login_required
def gallery_add_category(gallery_uuid):
    category_uuid = json.loads(request.data).get('category_uuid')
    GalleryCategory.create(gallery_uuid=gallery_uuid, category_uuid=category_uuid)
    gallery_categories = GalleryCategory.get_list(gallery_uuid=gallery_uuid, to_json=True)
    return json.dumps(gallery_categories), 200, {'Content-Type': 'application/json'}


@app.route('/admin/api/gallery/<gallery_uuid>/categories/<category_uuid>', methods=['DELETE'])
@login_required
def gallery_delete_category(gallery_uuid, category_uuid):
    GalleryCategory.delete(uuid=category_uuid)
    gallery_categories = GalleryCategory.get_list(gallery_uuid=gallery_uuid, to_json=True)
    return json.dumps(gallery_categories), 200, {'Content-Type': 'application/json'}
