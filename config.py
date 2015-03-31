# config.py

import os

# grabs the folder where the script runs
basedir = os.path.abspath(os.path.dirname(__file__))

DATABASE = "flasktaskr.db"
USERNAME = 'admin'
PASSWORD = 'admin'
WTF_CSRF_ENABLED = True
SECRET_KEY = 'my_precious'

# defines the full path for the database
DATABASE_PATH = os.path.join(basedir, DATABASE)

# the database uri (this is the only place SQLite is referenced when SQLAlchemy is initiated) (it also appears to be a default variable for SQLalchemy, because the variable is not explicitly used anywhere else)
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_PATH


