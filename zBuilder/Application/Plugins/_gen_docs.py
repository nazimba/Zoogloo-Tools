#!/usr/bin/env python
# encoding: utf-8
"""
genDocs.py

Created by  on 2007-12-14.
Copyright (c) 2007 Zoogloo LLC. All rights reserved.

"""

__version__ = '$Revision: 192 $'
__author__  = '$Author: andy $'
__date__    = '$Date: 2009-03-03 10:14 -0800 $'

import os


# cmd = 'epydoc -v --config epydoc.config --inheritance included'
cmd = 'epydoc -v --config _epydoc.config'

os.system(cmd)