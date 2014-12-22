import sys

from app.twitter import get_comments_for_item
from app.twitter import get_comments_for_items


if __name__ == '__main__':
    if len(sys.argv) > 1:
        gallery_uuid = sys.argv[1]
        get_comments_for_item(gallery_uuid)
    else:
        get_comments_for_items()
