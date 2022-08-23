import mysql.connector
from flask import g
import os

def get_db():
    if 'db' not in g:
        g.db = mysql.connector.connect(
            host=os.environ['DATABASE_HOST'],
            user=os.environ['DATABASE_USER'],
            password=os.environ['DATABASE_PASSWORD'],
            database=os.environ['DATABASE']
        )
        g.c = g.db.cursor(dictionary=True)
    return g.db, g.c


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()
