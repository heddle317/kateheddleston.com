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
    # Retrieve our source image from a URL
    fp = urllib.urlopen(url)
    content_type = fp.info().get('content-type')
    # Load the URL data into an image
    img = cStringIO.StringIO(fp.read())
    img_original = Image.open(img)

    change_image_resolution(gallery_uuid, filename, img_original, content_type, 500, key)
    change_image_resolution(gallery_uuid, filename, img_original, content_type, 1000, key)
    change_image_resolution(gallery_uuid, filename, img_original, content_type, 2000, key)
    change_image_resolution(gallery_uuid, filename, img_original, content_type, 4000, key)
    change_image_resolution(gallery_uuid, filename, img_original, content_type, 6000, key)


def change_image_resolution(gallery_uuid, filename, img_original, content_type, width, key):
    # Resize the image
    new_size = get_width_height(img_original.size, width)
    img_resized = img_original.resize(new_size, Image.NEAREST)

    # NOTE, we're saving the image into a cStringIO object to avoid writing to disk
    out_location = cStringIO.StringIO()
    file_type = get_file_type(content_type)
    img_resized.save(out_location, file_type)

    key.key = 'galleries/{}/{}'.format(gallery_uuid, new_filename(filename, width))
    key.set_contents_from_string(out_location.getvalue(),
                                 headers={'Content-Type': content_type},
                                 replace=True,
                                 policy='public-read')
    out_location.close()


def get_file_type(content_type):
    c, ext = content_type.split('/')
    return ext


def get_width_height(original_size, width):
    if width >= original_size[0]:
        return original_size
    percent = float(width) / float(original_size[0])
    height = int(original_size[1] * percent)
    return (width, height)


def new_filename(filename, width):
    name, ext = os.path.splitext(filename)
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
    return "{}_{}".format(name, additional_name)
