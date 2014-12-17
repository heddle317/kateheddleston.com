import sys

from app.twitter import update_facebook_comments


if __name__ == '__main__':
    url = sys.argv[1]
    gallery_uuid = sys.argv[2]
    update_facebook_comments(url, gallery_uuid)
