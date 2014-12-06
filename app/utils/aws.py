import cStringIO
import os
import urllib

from app import config

from boto.s3.connection import S3Connection
from boto.s3.key import Key

from PIL import Image


def s3_change_image_resolutions(gallery_uuid, filename):
    conn = S3Connection(config.AWS_ACCESS_KEY_ID, config.AWS_SECRET_ACCESS_KEY)
    bucket = conn.get_bucket(config.IMAGE_BUCKET)
    key = Key(bucket)

    url = "{}/galleries/{}/{}".format(config.IMAGES_BASE, gallery_uuid, filename)
    print url
    # Retrieve our source image from a URL
    fp = urllib.urlopen(url)
    print fp
    content_type = fp.info().get('content-type')
    print content_type
    # Load the URL data into an image
    img = cStringIO.StringIO(fp.read())
    img_original = Image.open(img)
    print img_original

    change_image_resolution(gallery_uuid, filename, img_original, content_type, .05, key)
    change_image_resolution(gallery_uuid, filename, img_original, content_type, .10, key)
    change_image_resolution(gallery_uuid, filename, img_original, content_type, .25, key)
    change_image_resolution(gallery_uuid, filename, img_original, content_type, .50, key)
    change_image_resolution(gallery_uuid, filename, img_original, content_type, .75, key)
    change_image_resolution(gallery_uuid, filename, img_original, content_type, 1, key)


def change_image_resolution(gallery_uuid, filename, img_original, content_type, size_percent, key):
    # Resize the image
    size = (int(img_original.size[0] * size_percent), int(img_original.size[1] * size_percent))
    print img_original.size
    print size
    img_resized = img_original.resize(size, Image.NEAREST)

    # NOTE, we're saving the image into a cStringIO object to avoid writing to disk
    out_location = cStringIO.StringIO()
    file_type = get_file_type(content_type)
    print file_type
    img_resized.save(out_location, file_type)

    key.key = 'galleries/{}/{}'.format(gallery_uuid, new_filename(filename, size))
    print key.key
    key.set_contents_from_string(out_location.getvalue(),
                                 headers={'Content-Type': content_type},
                                 replace=False,
                                 policy='public-read')
    out_location.close()


def get_file_type(content_type):
    c, ext = content_type.split('/')
    return ext


def new_filename(filename, size):
    name, ext = os.path.splitext(filename)
    width = size[0]
    if width <= 500:
        additional_name = 'thumbnail'
    elif width <= 1000:
        additional_name = 'small'
    elif width <= 2000:
        additional_name = 'medium'
    elif width <= 4000:
        additional_name = 'large'
    elif width <= 6000:
        additional_name = 'grande'
    else:
        additional_name = 'jumbo'
    print name, additional_name
    return "{}_{}".format(name, additional_name)
