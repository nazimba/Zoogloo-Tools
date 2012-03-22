"""
zStretchyOp.py

Created by andy on 2008-09-17.
Copyright (c) 2008 Zoogloo LLC. All rights reserved.
"""

__version__ = '$Revision: 186 $'
__author__  = '$Author: andy $'
__date__    = '$Date: 2009-02-17 16:35 -0800 $'

import win32com.client
from win32com.client import constants
from win32com.client import constants as c
from win32com.client.dynamic import Dispatch as dispatch

xsi = Application
log = xsi.logmessage

null = None
false = 0
true = 1

def XSILoadPlugin(in_reg):
	in_reg.Author = "Andy Buecker"
	in_reg.Name = "zStretchyOp"
	in_reg.Email = "andy@zoogloo.net"
	in_reg.URL = ""
	in_reg.Major = 1
	in_reg.Minor = 0

	in_reg.RegisterOperator('zStretchyOp')

	# copyright message #
	msg = '''
#------------------------------------------#
  %s (v.%d.%d)
  Copyright 2008 Zoogloo LLC.
  All rights Reserved.
#------------------------------------------#
	''' % (in_reg.Name, in_reg.Major, in_reg.Minor)
	log(msg)

	return true

def XSIUnloadPlugin(in_reg):
	strPluginName = in_reg.Name
	Application.LogMessage(str(strPluginName) + str(" has been unloaded."))
	return true

#-----------------------------------------------------------------------------
# Operator
#-----------------------------------------------------------------------------
def zStretchyOp_Define(ctxt):
	op = ctxt.Source
	op.AlwaysEvaluate = false
	op.Debug = 0
	return true

def zStretchyOp_Update(ctxt):

	# get the inputs #
	curve_in	 	= ctxt.GetInputValue(0)
	length_rest		= ctxt.GetInputValue(1)

	# get the curve's current length #
	length_cur		= curve_in.Geometry.Curves(0).Length

	# get the scale value #
	scale 			= length_cur/length_rest

	# set the output value #
	ctxt.OutputPort.Value = scale

