# config.py

import os

# grabs the folder where the script runs
basedir = os.path.abspath(os.path.dirname(__file__))

DATABASE = 'flasktasker.db'

WTF_CSRF_ENABLED = True
SECRET_KEY = 'wwACIw6U8l3MDoO9D0huJL2s4pQz3J5g'

# defines the full path for the database
DATABASE_PATH = os.path.join(basedir, DATABASE)

# the database uri
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_PATH

DEBUG = False
