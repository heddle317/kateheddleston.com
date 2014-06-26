import boto
import os

from boto.s3.key import Key


def connect_s3():
    s3 = boto.connect_s3()
    bucket_key = Key(os.environ.get('AWS_BUCKET_KEY'))
