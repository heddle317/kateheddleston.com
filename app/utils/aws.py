import io
import os
import urllib

from app import config

from boto.s3.connection import S3Connection
from boto.s3.key import Key

from PIL import Image


def s3_change_image_resolutions(image_route, filename):
    conn = S3Connection(config.AWS_ACCESS_KEY_ID, config.AWS_SECRET_ACCESS_KEY)
    bucket = conn.get_bucket(config.AWS_IMAGE_BUCKET)
    key = Key(bucket)

    url = "{}/{}/{}".format(config.AWS_IMAGES_BASE, image_route, filename)
    # Retrieve our source image from a URL
    fp = urllib.urlopen(url)
    content_type = fp.info().get('content-type')
    # Load the URL data into an image
    img = io.StringIO(fp.read())
    img_original = Image.open(img)

    change_image_resolution(image_route, filename, img_original, content_type, 500, key)
    change_image_resolution(image_route, filename, img_original, content_type, 1000, key)
    change_image_resolution(image_route, filename, img_original, content_type, 2000, key)
    change_image_resolution(image_route, filename, img_original, content_type, 4000, key)
    change_image_resolution(image_route, filename, img_original, content_type, 6000, key)

    img.close()
    fp.close()


def update_image_headers(image_route, filename):
    conn = S3Connection(config.AWS_ACCESS_KEY_ID, config.AWS_SECRET_ACCESS_KEY)
    bucket = conn.get_bucket(config.AWS_IMAGE_BUCKET)
    key = Key(bucket)

    url = "{}/{}/{}".format(config.AWS_IMAGES_BASE, image_route, filename)
    # Retrieve our source image from a URL
    fp = urllib.urlopen(url)
    content_type = fp.info().get('content-type')
    # Load the URL data into an image
    img = io.StringIO(fp.read())

    # img.seek(0, os.SEEK_END)
    # content_length = img.tell()
    # img.seek(0)

    key.key = '{}/{}'.format(image_route, filename)
    key.set_contents_from_string(img.getvalue(),
                                 headers={'Content-Type': content_type,
                                          'x-amz-meta-Cache-Control': 'max-age=31536000',
                                          'Cache-Control': 'max-age=31536000'},
                                 replace=True,
                                 policy='public-read')
    img.close()


def change_image_resolution(image_route, filename, img_original, content_type, width, key):
    # Resize the image
    new_size = get_width_height(img_original.size, width)
    img_resized = img_original.resize(new_size, Image.NEAREST)

    # NOTE, we're saving the image into a StringIO object to avoid writing to disk
    out_location = io.StringIO()
    file_type = get_file_type(content_type)
    img_resized.save(out_location, file_type)

    key.key = '{}/{}'.format(image_route, new_filename(filename, width))
    key.set_contents_from_string(out_location.getvalue(),
                                 headers={'Content-Type': content_type,
                                          'x-amz-meta-Cache-Control': 'max-age=31536000',
                                          'Cache-Control': 'max-age=31536000'},
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
