import sys

from app.db.galleries import Gallery
from app.utils.aws import s3_change_image_resolutions


if __name__ == '__main__':
    gallery_uuid = sys.argv[1]
    if len(sys.argv) > 2:
        filename = sys.argv[2]
        s3_change_image_resolutions(gallery_uuid, filename)
    else:
        gallery = Gallery.get_gallery(uuid=gallery_uuid)
        for item in gallery.get('items', []):
            if item.get('image_name'):
                print item.get('image_name')
                s3_change_image_resolutions(gallery_uuid, item.get('image_name'))
