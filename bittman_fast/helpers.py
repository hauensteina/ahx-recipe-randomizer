# /********************************************************************
# Filename: bittman_fast/helpers.py
# Author: AHN
# Creation Date: Sep, 2022
# **********************************************************************/
#
# Various utility functions
#

from pdb import set_trace as BP
import sys,os,datetime
from flask import request, url_for, redirect
from bittman_fast import S3_BUCKET, S3_FOLDER, S3, log

def gen_edit_form( row, columns, active_tab, active_screen, action, buttons=('save','cancel')):
    """
    Generate a form to edit the columns of row.
    Parameter columns is a list of dicts like
    {'name':'colname', 'choices':['one','two','three'], 'type':['password'|'email'|'number'|'text'|'date'], 'size':10}
    If choices are given, type will be 'select'.
    """
    header = f'''
    <input type=hidden name=_active_tab value={active_tab}>
    <input type=hidden name=_active_screen value={active_screen}>
    <input type=hidden name=_action value="{action}">
    '''
    if '_id' in row:
        header += f'<input type=hidden name=_id value={row["_id"]}>'

    # Hack to reliably disable autofill and autocomplete
    nofill_hack = f''' readonly onfocus="this.removeAttribute('readonly');" '''
    body = ''
    for col in columns:
        title = col.get('title', col['name'])
        if 'choices' in col:
            body += f'''
            <dt>{col['name']}:</dt>
            '''
            options = []
            for choice in col['choices']:
                if row.get(col['name'],'') == choice:
                    options.append( H( f'option value={choice} selected', choice))
                else:
                    options.append( H( f'option value={choice}', choice))
            options = '\n'.join(options)
            body += H( 'dd', H( f'select name={col["name"]}', options))
        else:
            body += f'''
            <dt>{title}:</dt>
            <dd><input type={col['type']} name={col['name']} value='{row.get(col["name"],"")}' 
              size={col['size']}
              {'readonly' if 'readonly' in col else ''}
              {nofill_hack if 'nofill' in col else ''}
             >  
            </dd>
            '''
    body = H('dl class="bottom-space-20"', body)        
    button_html = []
    for btn in buttons:
        button_html.append( f'''<input type=submit name="btn_{btn}" value="{btn.replace('_',' ').title()}">''')
    button_html = ' &nbsp '.join(button_html)    
    buttons = H('p', button_html)
    form = H('form method=post', header + body + buttons)
    return form

def gen_dropdown( active_tab, active_screen, action, title, choices, btn, default_choice=''):
    header = f'''
    <input type=hidden name=_active_tab value={active_tab}>
    <input type=hidden name=_active_screen value={active_screen}>
    <input type=hidden name=_action value="{action}">
    '''

    title_row = H('tr', H('td','Chapter:') + H('td','&nbsp')) 
    options = [ H( f'''option value="{choice}" {'selected' if choice == default_choice else ''}''', choice) for choice in choices ]
    options = '\n'.join(options)
    dropdown = H( f'select name={title}', options)
    button = f'''<input type=submit name="btn_{btn}" value="{btn.replace('_',' ').title()}">'''
    dropdown_row = H('tr', H('td', dropdown) + H('td', 3 * '&nbsp;' + button))
    body = H( 'table', title_row + dropdown_row)

    form = H('form method=post', header + body)
    return form
    
def gen_edit_list( rows, columns, active_tab, active_screen, action=''):
    """
    Generate html to display the rows (list of dicts), but only selected columns.
    If action is given, a link with that action is generated on the right.
    For styling, use class dbtable in main.css .
    """
    # Build table header
    theader = ''
    for col in columns:
        theader += H('th',col['name'])
    theader = H('tr',theader)
    # Build table body
    tbody = ''
    for idx,row in enumerate(rows):
        trow = ''
        for col in columns:
            trow += H('td',row[col['name']])
        if action:    
            trow += H('td', _gen_edit_link( row, active_tab, active_screen, action))    
        trow = H('tr',trow) 
        tbody += trow
    html = H('table class="dbtable"', theader + tbody)
    return html

def _gen_edit_link( row, active_tab, active_screen, action):   
    """ Generate an html link to edit this row """
    url = url_for( 'index', _active_tab=active_tab, _active_screen=active_screen, 
                   _id=row['_id'], _action=action)
    link = H(f'a href={url}', action.capitalize())
    return link

def gen_dialog( msg, parms, action, buttons, style='', pass_parms=['_id']):
    """ Generate a form asking a question """
    header = ''
    # Pass parameters on to the next url hit
    for parm in pass_parms + ['_active_tab', '_active_screen']:
        if parm in parms:
            header += f'<input type=hidden name={parm} value="{parms[parm]}">'
    header += f'<input type=hidden name=_action value="{action}">'

    body = H('div class="bottom-space-20"', msg, style)
    
    button_html = []
    for btn in buttons:
        button_html.append( f'<input type=submit name="btn_{btn}" value="{btn.capitalize()}">')
    button_html = ' &nbsp '.join(button_html)    
    buttons = H('p', button_html)

    form = H('form method=post', header + body + buttons)
    return form
    
def redir_blank( parms):
    """ Return a redirect to blank active_tab  """ 
    return redirect( url_for( 'index', _active_tab=parms['_active_tab']))

def html_tag( tag, content='', style=''):
    """
    Make a piece of HTML surrounded by tag,
    with content and style. Plus a hack for images.
    """
    if content is None: content = ''
    res = '\n'
    if type(content) not in  [list,tuple]:
        content = [content,'']
    cont = content[0]
    contstyle = content[1]
    res += f'<{tag} '
    res += f'style="{style}">\n'
    if cont.endswith( '.png') or cont.endswith( '.svg'):
        cont = f'<img src="{cont}" style="{contstyle}">'
    res += cont + '\n'
    res += f'</{tag.split()[0]}>\n'
    return res

def s3_read_file(fname):
    """ 
    Read data from a file in our S3 folder.
    fname can include a path like one/two/three.pdf .
    """
    response = S3.get_object( Bucket=S3_BUCKET, Key=f'{S3_FOLDER}/{fname}')
    bytes = response['Body'].read() 
    return bytes

def s3_write_to_file( data, fname):
    """ 
    Write data to a file in our S3 folder.
    fname can include a path like one/two/three.pdf .
    """
    key = f'{S3_FOLDER}/{fname}'
    S3.put_object( Body=data, Bucket=S3_BUCKET, Key=key)

def delete_old_files( folder, hours=1):
    for dirpath, dirnames, filenames in os.walk(folder):
       for fname in filenames:
          curpath = os.path.join( dirpath, fname)
          file_modified = datetime.datetime.fromtimestamp(os.path.getmtime(curpath))
          if datetime.datetime.now() - file_modified > datetime.timedelta(hours=hours):
              #log( f'delete_old_files():deleted {curpath}')
              os.remove(curpath)


# short function alias
H = html_tag 

