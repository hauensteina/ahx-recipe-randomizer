# /********************************************************************
# Filename: bittman_fast/__init__.py
# Author: AHN
# Creation Date: Sep, 2022
# **********************************************************************/
#
# Imports and Globals
#

from pdb import set_trace as BP

import os,random
import uuid
import glob
import importlib

from flask import Flask
import boto3

AWS_KEY = os.environ['AWS_KEY']
AWS_SECRET = os.environ['AWS_SECRET']
#FLASK_SECRET = os.environ['AHX_FLASK_SECRET']
S3 = boto3.client('s3',
                  aws_access_key_id=AWS_KEY,
                  aws_secret_access_key=AWS_SECRET)
S3_BUCKET = 'ahn-uploads'
S3_FOLDER = 'bittman-fast'


app = Flask( __name__)

# Our own exception class
class AppError(Exception):
    pass

# Make some functions available in the jinja templates.
# Black Magic.
@app.context_processor
def inject_template_funcs():
    return { 'rrand':rrand }

def rrand():
    return str(random.uniform(0,1))

#---------------------------
def log( msg, level=''):
    """ Logging. Change as needed """
    print(msg, flush=True)
    
app.config.update(
    DEBUG = True,
    #SECRET_KEY = FLASK_SECRET
)

app.config['MAX_CONTENT_LENGTH'] = int(1E6)

# Modules in the tabbed interface
tab_modules = {}
for py in glob.glob('bittman_fast/templates/tabs/*/*.py'):
    # a/b.py -> a.b
    modname = os.path.splitext(py)[0].replace('/','.')
    log( f'Loading module {modname}')
    mod = importlib.import_module( modname)
    tab_modules[modname] = mod

# Endpoints for GUI
from bittman_fast import routes
