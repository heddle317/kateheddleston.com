import sys

from app.db.galleries import Gallery
from app.db.talks import Talk
from app.utils.aws import s3_change_image_resolutions


if __name__ == '__main__':
    db_table = sys.argv[1]
    if len(sys.argv) > 3:
        uuid = sys.argv[2]
        image_route = "{}/{}".format(db_table, uuid)
        filename = sys.argv[3]
        s3_change_image_resolutions(image_route, filename)
    elif len(sys.argv) > 2:
        uuid = sys.argv[2]
        image_route = "{}/{}".format(db_table, uuid)
        if db_table == 'galleries':
            db_item = Gallery.get_gallery(uuid=uuid)
            for item in db_item.get('items', []):
                if item.get('image_name'):
                    print(item.get('image_name'))
                    s3_change_image_resolutions(image_route, item.get('image_name'))
        elif db_table == 'talks':
            db_item = Talk.get_talk(uuid=uuid)
            if db_item.get('image_name'):
                print(db_item.get('image_name'))
                s3_change_image_resolutions(image_route, db_item.get('image_name'))
    else:
        if db_table == 'galleries':
            db_items = Gallery.get_galleries()
            for db_item in db_items:
                image_route = "{}/{}".format(db_table, db_item.get('uuid'))
                for item in db_item.get('items', []):
                    if item.get('image_name'):
                        print(item.get('image_name'))
                        s3_change_image_resolutions(image_route, item.get('image_name'))
        elif db_table == 'talks':
            db_items = Talk.get_talks()
            for db_item in db_items:
                image_route = "{}/{}".format(db_table, db_item.get('uuid'))
                if db_item.get('image_name'):
                    print(db_item.get('image_name'))
                    s3_change_image_resolutions(image_route, db_item.get('image_name'))
