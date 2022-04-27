import os
basedir = os.path.abspath(os.path.dirname(__name__))

username = ''
password = ''


class Config(object):
    SECRET_KEY = 'this-is-a-secret'
    DATABASE = os.path.join(basedir, 'app.db')
