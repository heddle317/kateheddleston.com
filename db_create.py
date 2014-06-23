#!flask/bin/python
from app import app_db as db


db.create_all()
