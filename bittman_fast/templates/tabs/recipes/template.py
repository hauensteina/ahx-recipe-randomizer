"""
Definition of action_handler(), which handles button and link clicks and generates
html for {{ search_html }} and {{ display_html }}.
Imported on the fly and called by tabgen.gen_body().

AHN, Sep 2022
"""

from pdb import set_trace as BP
import datetime
from flask import flash, url_for

def action_handler(parms):
    """ Get the _action parameter and banch to the appropriate handler """
    return { 'search_html':'', 'display_html':'', 'error':f'', 'redirect':'' }

