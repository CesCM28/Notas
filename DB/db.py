from dis import Instruction
from flask import flash
import flask
import mysql.connector
import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    if 'db' not in g:
        g.db = mysql.connector.connect(
            host='dbeldemocrata.cggi3z2t9ytu.us-east-1.rds.amazonaws.com', #current_app.config['DATABASE_HOST'],
            user='admin', #current_app.config['DATABASE_USER'],
            password='UPgnR6LnDYka&VW*2T8pYfFDw', #current_app.config['DATABASE_PASSWORD'],
            database='ElDemocrata'#current_app.config['DATABASE']
        )
        g.c = g.db.cursor(dictionary=True)
    return g.db, g.c


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()
