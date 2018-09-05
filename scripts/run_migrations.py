import os
import psycopg2
from urllib.parse import urlparse

from app import config


class Migrate(object):

    def __init__(self):
        self._patches_dir = 'migrations'
        result = urlparse(config.SQLALCHEMY_DATABASE_URI)
        username = result.username
        password = result.password
        database = result.path[1:]
        host = result.hostname
        self._conn = psycopg2.connect(database=database, host=host, password=password, user=username)
        self._conn.autocommit = True

    def _execute(self, sql):
        cur = self._conn.cursor()
        cur.execute(sql)
        cur.close()

    def migrate(self):
        patches = os.listdir(self._patches_dir)
        patches.sort()
        patch_level = 0

        for idx, patch in enumerate(patches[patch_level:]):
            patch_path = "%s/%s" % (self._patches_dir, patch)
            patch_sql = open(patch_path, 'r').read()

            try:
                self._execute(patch_sql)
                print("%s: Executed patch - %s" % (idx, patch))
            except:
                pass

        return True


if __name__ == '__main__':
    migration = Migrate()
    migration.migrate()
