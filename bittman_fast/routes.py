# /********************************************************************
# Filename: bittman_fast/routes.py
# Author: AHN
# Creation Date: Sep, 2022
# **********************************************************************/
#
# GUI endpoints
#

from pdb import set_trace as BP

import os, sys, re, json, shutil, datetime, shortuuid
from flask import request, render_template, flash, redirect, url_for, send_from_directory
from bittman_fast import app,tabgen,helpers

@app.before_request
def before_request():
    if (not request.is_secure) and ('PRODUCTION_FLAG' in os.environ):
        url = request.url.replace('http://', 'https://', 1)
        code = 301
        return redirect(url)

@app.route('/ttest')
def ttest():
    """ Try things here """
    parms = dict(request.args)
    fname = parms['fname']
    return render_template( 'ttest.html', msg=f'{fname}')

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def index():
    """ Main entry point """
    if request.method == 'POST': # Active screen submitted a form
        parms = dict(request.form)
    else:
        parms = dict(request.args)
    # strip all input parameters    
    parms = { k:v.strip() for k, v in parms.items()}
    print(f'>>>>>>>>>PARMS:{parms}')
    active_tab = parms.get('_active_tab','')
    active_screen = parms.get('_active_screen','')
    tab_html, rredirect = tabgen.gen_html( active_tab, active_screen, parms)
    if rredirect: return rredirect
    return render_template( 'index.html', tabs=tab_html)

