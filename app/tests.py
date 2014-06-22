import unittest

from app import app
from app.db_calls import init_db

from flask.ext.testing import TestCase


class AppBaseTestCase(TestCase):

    def create_app(self):
        '''
           Creates a sqlite db in memory when testing.
        '''
        app.config['TESTING'] = True
        app.config['DATABASE'] = ':memory:'
        return app


class APITestCase(AppBaseTestCase):

    def test_api(self):
        pass


if __name__ == '__main__':
    unittest.main()
