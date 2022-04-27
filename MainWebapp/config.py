import os
basedir = os.path.abspath(os.path.dirname(__name__))

username = 'jwhit1074'
password = 'Jacjacjac_3210'


class Config(object):
    SECRET_KEY = 'this-is-a-secret'
    DATABASE = os.path.join(basedir, 'app.db')
