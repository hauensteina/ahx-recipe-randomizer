"""
Show a dropdown with the book chapter at the top, pick a random recipe on submit,
show the recipe pdf below. 

AHN, Sep 2022
"""

from pdb import set_trace as BP
import os, sys, json, shortuuid, random
from flask import flash, url_for, request, send_from_directory
from pathvalidate import sanitize_filename
from bittman_fast import app, AppError, log
from bittman_fast.helpers import html_tag as H
import bittman_fast.helpers as helpers

# Define chapter dropdown
SEARCH_FORM = [ {'name':'chapter', 'choices':('user','admin')} ]

def action_handler(parms):
    """ Get the _action parameter and branch to the appropriate handler """
    action = parms.get('_action','init')
    if not action:
        return { 'search_html':'', 'display_html':'', 'error':'Parameter _action missing', 'redirect':'' }
    handler = ACTION_HANDLERS.get(action,'')
    if not handler:
        return { 'search_html':'', 'display_html':'', 'error':f'Handler for action {action} not found', 'redirect':'' }
    return handler(parms)

def _handle_init(parms):
    index, chapters = _get_index_and_chapters()
    dropdown = _gen_dropdown( parms, chapters)
    return { 'search_html':dropdown, 'display_html':'', 'error':'', 'redirect':'' }

def _handle_show(parms):
    index, chapters = _get_index_and_chapters()
    chapter = parms['Chapter']
    index = [ x for x in index if x['label'] == chapter ]
    random.shuffle(index)
    recipe = index[0]
    attachment_fname = sanitize_filename(recipe['title'] + '.pdf')
    display_html = '<br>' + H( 'h3', recipe['title'])
    folder,fname = recipe['fname'].split('/')
    link = url_for( 'download_recipe', fname=fname, folder=folder, attachment_fname=attachment_fname, 
                    _active_tab=parms['_active_tab'], _active_screen=parms['_active_screen'])
    display_html += H( f'a href="{link}"', 
                       'Download')
    
    log(recipe)
    return { 'search_html': _gen_dropdown( parms, chapters, default_choice=chapter),
             'display_html':display_html,
             'error':'', 
             'redirect':'' }

@app.route('/download_recipe')
def download_recipe():
    """ Custom endpoint for the Download link """
    parms = dict(request.args)
    fname = parms['fname']
    folder = parms['folder']
    attachment_fname = parms['attachment_fname']
    active_tab = parms['_active_tab']
    active_screen = parms['_active_screen']

    mypath = os.path.split(__file__)[0]
    TEMPFOLDER = mypath + '/' + 'tmp'
    helpers.delete_old_files( TEMPFOLDER)
    pdf = helpers.s3_read_file( folder + '/' + fname)
    if not os.path.exists( TEMPFOLDER):
        os.mkdir( TEMPFOLDER)
    tempfname = TEMPFOLDER + '/' + shortuuid.uuid() + '.pdf.'
    with open( tempfname, 'wb') as outf:
        outf.write(pdf)
    log(TEMPFOLDER)
    ddir = 'templates/' + TEMPFOLDER.split('/templates/')[1]
    log(ddir)
    ret = send_from_directory( directory=ddir, path=os.path.split(tempfname)[1], 
                               max_age=0, as_attachment=True,
                               download_name=attachment_fname )
    return ret

# Helper functions
#--------------------------

def _get_recipe_pdf( fname):
    pdf = helpers.s3_read_file(fname)
    return pdf

def _get_index_and_chapters():
    # Get the index from S3
    index_json = helpers.s3_read_file('index.json')
    index = json.loads(index_json)
    chapters = { x['label']:1 for x in index }.keys() # rem dups
    return index, chapters

def _gen_dropdown( parms, chapters, default_choice=''):
    return helpers.gen_dropdown( parms['_active_tab'], parms['_active_screen'], 
                                 action='show', title='Chapter',
                                 choices=chapters, btn='get_a_recipe',
                                 default_choice=default_choice)

ACTION_HANDLERS = { 
    'init': _handle_init 
    ,'show': _handle_show 
}

