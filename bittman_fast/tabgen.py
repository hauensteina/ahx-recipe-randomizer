# /********************************************************************
# Filename: bittman_fast/tabgen.py
# Author: AHN
# Creation Date: Sep, 2022
# **********************************************************************/
#
# Generate html for the tabbed index page from stuff we find in the file system.
# Set focus on the specified tab and subscreen.
# This lets you add screens by just adding files in the right places, without editing
# any html outside the new page.
# Look at bittman_fast/templates/tabs .

from pdb import set_trace as BP

import os, sys, re, json
import glob 
#import importlib

from flask import render_template, flash, redirect, url_for
from bittman_fast import log
from bittman_fast import tab_modules

import sys

def gen_html( active_tab='', active_screen='', parms={}):
    """ 
    Generate html for tabbed interface, showing active_screen in active_tab.
    Returns a pair (html, redirect). Called from routes.py.
    """
    tabnames = _get_tabnames()
    res = '<div class=tabset>\n' + _gen_top(tabnames, active_tab)
    tab_bodies = {}
    for tabname in tabnames:
        tab_bodies[tabname], rredirect = _gen_body(tabname, active_tab, active_screen, parms)
        if rredirect: return '',rredirect
    res += _gen_rest(tab_bodies) 
    return res,''

def _get_tabnames():
    """ Get the tab names from the file system """
    tabnames = os.listdir( 'bittman_fast/templates/tabs')
    tabnames = sorted( [ x for x in tabnames if x[0] != '.' and x != 'example'])
    return tabnames

def _gen_top( tabnames, active_tab):
    """ Generate the first part of the tabbed html """
    if not active_tab: active_tab = tabnames[0]
    res = ''
    for tabname in tabnames:
        res += f'''
        <input
        type="radio"
        name="tabset_1"
        id="tabset_1_{tabname}"
        hidden
        aria-hidden="true"
        '''
        if tabname == active_tab: res += 'checked="true"'
        res += '>'
    return res

def _gen_body( tabname, active_tab, active_screen, parms):
    """ 
    Generate html content for active_tab, active_screen.
    The hidden tabs just render tabs/<tabname>/template.html . 
    Returns page html and maybe a redirect.
    """

    # See if we find generator functions next to the template
    search_html = display_html = rredirect = ''
    search_error = display_error = submit_error = ''

    res = '<section>\n'
    tail = '\n</section>\n'
    res += f'<h2>{tabname}</h2>' 
    tabscreens = _get_html_files( tabname)
    if not 'template.html' in tabscreens: 
        return res + 'nothing here' + tail, ''
    if not active_tab: active_tab = _get_tabnames()[0]
    if not active_screen: active_screen = 'template'
    template = 'tabs/' + tabname + '/' + active_screen + '.html'
    modname = f'bittman_fast.templates.tabs.{active_tab}.{active_screen}'
    modpy = modname.replace( '.', '/') + '.py'
    modhtml = modname.replace( '.', '/') + '.html'
    # No html file for this screen. This should never happen.
    if not os.path.exists(modhtml):
        return f'ERROR:tabgen(): Screen html file {active_tab}/{modhtml} not found',''
    # No python file for this screen. Just render the verbatim template.
    elif not os.path.exists(modpy):
        links = _get_screen_links( tabname, active_tab, active_screen) 
        res += render_template( template, screen_links=links, active_tab=active_tab, active_screen=active_screen) + tail 
        return res,''
    # The foreground tab. Show the active screen.
    elif tabname == active_tab: 
        mod = tab_modules[modname] # importlib.import_module( modname)
        log( f'tabgen: found module for {active_tab}.{active_screen}')
        search_html, display_html, error, rredirect = mod.action_handler(parms).values()
        if rredirect: return '',rredirect
        links = _get_screen_links( tabname, active_tab, active_screen) 
        res += render_template( template, screen_links=links, error=error, 
                                search_html=search_html, display_html=display_html,
                                active_tab=active_tab, active_screen=active_screen) + tail
        return res,''
    # A background tab. Just render the verbatim template.
    elif tabname != active_tab: 
        links = _get_screen_links( tabname, active_tab, active_screen) 
        template = 'tabs/' + tabname + '/' + 'template.html'
        res += render_template( template, screen_links=links, error='',
                               active_tab=active_tab, active_screen=active_screen) + tail
        return res, ''
    return '', 'tabgen():_gen_body fell through'

def _gen_rest( bodies):
    """ Tail of tabbed interface """
    # A hidden tab list for css magic
    res = '\n<ul hidden aria-hidden="true">'
    for tabname in sorted(bodies.keys()):
        name = tabname
        title = _get_title( tabname)
        res += f'\n<li><label for="tabset_1_{name}">{title}</label></li>'
    res += '\n</ul>'
    res += '\n<div>\n'
    # A section per tab, with tab content
    for tabname in sorted(bodies.keys()):
        res += bodies[tabname]
    res += '\n</div></div>'
    return res

def _get_title( screen):
    """ 'my_tab.html' -> 'My Tab' """
    title = os.path.splitext(screen)[0].split('_')
    title = [ x.capitalize() for x in title ]
    title = ' '.join(title)
    return title

def _get_html_files( tabname):
    """ Get the base filenames of all the html files for this tab """
    tabpath = 'bittman_fast/templates/tabs/' + tabname
    tabscreens = [ x for x in os.listdir( tabpath) if os.path.splitext(x)[1] == '.html' ]     
    tabscreens = sorted( [ x for x in tabscreens if x[0] != '.' ])
    return tabscreens

def _get_screens( tabname):
    """ Get the base filenames of all the tab screens """
    tabscreens = _get_html_files( tabname)
    tabscreens = [ x for x in tabscreens if x != 'template.html' ]
    return tabscreens

def _get_screen_links( tabname, active_tab, active_screen):
    """ Generate HTML for the screen links at the top of the tab """
    screens = _get_screens( tabname)
    if not screens: return ''
    screens = [ os.path.splitext(x)[0] for x in screens ]
    links = []
    for screen in screens:
        cclass = 'screenlink'
        if tabname == active_tab and screen == active_screen:
            cclass += ' active_screen'
        link = f'''
        <a href="{url_for('index', _active_tab=tabname,_active_screen=screen,_action='init')}" class="{cclass}">
        {_get_title(screen)}</a>'''            
        links.append(link)

    html = ' | '.join(links)
    return html 
