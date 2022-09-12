#!/usr/bin/env python

# /********************************************************************
# Filename: bittman_fast/app.py
# Author: AHN
# Creation Date: Sep 2022
# **********************************************************************/
#
# Pick a random recipe from 'How To Cook Everything Fast'
#

from pdb import set_trace as BP
from bittman_fast import app

#----------------------------
if __name__ == '__main__':
    app.run( host='0.0.0.0', port=8000, debug=True)
    # If you want to run with gunicorn:
    # $ gunicorn app:app -w 1 -b 0.0.0.0:8000 --reload --timeout 1000
