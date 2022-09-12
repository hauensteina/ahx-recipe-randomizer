"""
Definition of action_handler(), which handles button and link clicks and generates
html for {{ search_html }} and {{ display_html }}.
Imported on the fly and called by tabgen.gen_body().

AHN, Aug 2022
"""

from pdb import set_trace as BP
import inspect
import datetime
import shortuuid
from flask import flash, url_for

def action_handler(parms):
    """ 
    Get the _action parameter and branch to the appropriate handler.
    Called from tabgen.py .
    Boilerplate. You probably never need to change this.
    """
    action = parms.get('_action','')
    if not action:
        return { 'search_html':'', 'display_html':'', 'error':'Parameter _action missing', 'redirect':'' }
    handler = ACTION_HANDLERS.get(action,'')
    if not handler:
        return { 'search_html':'', 'display_html':'', 'error':f'Handler for action {action} not found', 'redirect':'' }
    return handler(parms)

def _handle_init(parms):
    """ This happens when you first enter the screen """
    return { 'search_html':_gen_search_html(''), 'display_html':'', 'error':'', 'redirect':'' }

def _handle_search(parms):
    """ This happens when you click on Search """
    try:
        res = int(parms['some_number']) + 1
    except:
        # Something went wrong
        return { 'search_html':_gen_search_html(parms['some_number']), 
                 'display_html':'',
                 'error':'Invalid input', 'redirect':'' }
    # All is well
    return { 'search_html':_gen_search_html(parms['some_number']), 
             'display_html':int(parms['some_number']) + 1,
             'error':'', 'redirect':'' }

def _gen_search_html(num):
    return f'<input name=some_number type=number size=5 style="width:5em" value={num}> '

# Map action parameter values to handler functions 
ACTION_HANDLERS = { 
    'init': _handle_init 
    ,'search': _handle_search 
}

