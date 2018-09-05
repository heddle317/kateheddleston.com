import sys

from app.db.galleries import Gallery
from app.utils.aws import update_image_headers


def update_gallery_images():
    galleries = Gallery.get_galleries(published=False)
    for gallery in galleries:
        for item in gallery.get('items', []):
            if item.get('image_name'):
                print("{}    {}".format(gallery.get('uuid'), item.get('image_name')))
                update_image_headers('galleries/{}'.format(gallery.get('uuid')), item.get('image_name'))
                update_image_headers('galleries/{}'.format(gallery.get('uuid')), "{}_thumbnail".format(item.get('image_name')))
                update_image_headers('galleries/{}'.format(gallery.get('uuid')), "{}_small".format(item.get('image_name')))
                update_image_headers('galleries/{}'.format(gallery.get('uuid')), "{}_medium".format(item.get('image_name')))
                update_image_headers('galleries/{}'.format(gallery.get('uuid')), "{}_large".format(item.get('image_name')))
                update_image_headers('galleries/{}'.format(gallery.get('uuid')), "{}_grande".format(item.get('image_name')))
                update_image_headers('galleries/{}'.format(gallery.get('uuid')), "{}_jumbo".format(item.get('image_name')))


if __name__ == '__main__':
    if len(sys.argv) > 1:
        image_route = sys.argv[1]
        filename = sys.argv[2]
        update_image_headers(image_route, filename)
    else:
        update_gallery_images()
