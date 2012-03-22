"""
zPrintMatrix.py

Created by andy on 2008-09-04.
Copyright (c) 2008 Zoogloo LLC. All rights reserved.
"""

__version__ = '$Revision: 214 $'
__author__  = '$Author: andy $'
__date__    = '$Date: 2009-12-30 00:36 -0800 $'

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
	in_reg.Name = "zPrintMatrix"
	in_reg.Email = "andy@zoogloo.net"
	in_reg.URL = ""
	in_reg.Major = 1
	in_reg.Minor = 1

	in_reg.RegisterCommand('zPrintMatrix', 'zPrintMatrix')
	in_reg.RegisterCommand('zPrintMatrixFromObject', 'zPrintMatrixFromObject')
	in_reg.RegisterCommand('zPrintMatrixFromSelection', 'zPrintMatrixFromSelection')

	in_reg.RegisterMenu(c.siMenuMCPEditID, 'zPrintMatrixMenu', False)
	
	# copyright message #
	msg = '''
------------------------------------------
  %s (v.%d.%d)
  Copyright 2008 Zoogloo LLC.
  All rights Reserved.
------------------------------------------
	''' % (in_reg.Name, in_reg.Major, in_reg.Minor)
	log(msg)

	return true

def XSIUnloadPlugin(in_reg):
	strPluginName = in_reg.Name
	Application.LogMessage(str(strPluginName) + str(" has been unloaded."))
	return true

#-----------------------------------------------------------------------------
# Menus
#-----------------------------------------------------------------------------
def zPrintMatrixMenu_Init(ctxt):
	menu = ctxt.Source
	
	item = menu.AddCommandItem('zPrintMatrixFromSelection', 'zPrintMatrixFromSelection')
	item.Name = '(z) Print Global Matrix'

# #-----------------------------------------------------------------------------
# # Properties
# #-----------------------------------------------------------------------------
# def zPrintMatrix_Define(ctxt):
# 	prop = ctxt.Source
# 	
# 	#prop.AddParameter3("ParamName", c.siString, '')
# 
# 	
# def zPrintMatrix_DefineLayout(ctxt):
# 	lo = ctxt.Source
# 	lo.Clear()
# 
# 	lo.AddItem('ParamName')

#-----------------------------------------------------------------------------
# Commands
#-----------------------------------------------------------------------------
def zPrintMatrixFromObject_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	#oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments
	oArgs.AddObjectArgument('item')
	oArgs.Add('local', c.siArgumentInput, False, c.siBool)

	return True
	
def zPrintMatrixFromObject_Execute(item, local):

	# get the matrix #
	mtx = None
	if local:
		mtx = item.Kinematics.Local.Transform.Matrix4
	else:
		mtx = item.Kinematics.Global.Transform.Matrix4

	# build line separators #
	line_top = '+-------------------------------------------+'
	line_sep = '+----------+----------+----------+----------+'

	# print the matrix #
	log(line_top)
	if not local:
		log('|' + ('Global Matrix: %s' % item.FullName).center(45-2) + '|')
	else:
		log('|' + ('Local Matrix: %s' % item.FullName).center(45-2) + '|')
		
	log(line_sep)
	log('| ' + ('%0.3f'%mtx.Value(0,0)).rjust(8) + ' | ' + ('%0.3f'%mtx.Value(0,1)).rjust(8) + ' | ' + ('%0.3f'%mtx.Value(0,2)).rjust(8) + ' | ' + ('%0.3f'%mtx.Value(0,3)).rjust(8) + ' |')
	log(line_sep)
	log('| ' + ('%0.3f'%mtx.Value(1,0)).rjust(8) + ' | ' + ('%0.3f'%mtx.Value(1,1)).rjust(8) + ' | ' + ('%0.3f'%mtx.Value(1,2)).rjust(8) + ' | ' + ('%0.3f'%mtx.Value(1,3)).rjust(8) + ' |')
	log(line_sep)
	log('| ' + ('%0.3f'%mtx.Value(2,0)).rjust(8) + ' | ' + ('%0.3f'%mtx.Value(2,1)).rjust(8) + ' | ' + ('%0.3f'%mtx.Value(2,2)).rjust(8) + ' | ' + ('%0.3f'%mtx.Value(2,3)).rjust(8) + ' |')
	log(line_sep)
	log('| ' + ('%0.3f'%mtx.Value(3,0)).rjust(8) + ' | ' + ('%0.3f'%mtx.Value(3,1)).rjust(8) + ' | ' + ('%0.3f'%mtx.Value(3,2)).rjust(8) + ' | ' + ('%0.3f'%mtx.Value(3,3)).rjust(8) + ' |')
	log(line_sep)

#-----------------------------------------------------------------------------
def zPrintMatrix_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	#oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments
	oArgs.AddWithHandler('matrix_col', c.siArgHandlerCollection)
	# oArgs.AddObjectArgument('matrix')

	return True

def zPrintMatrix_Execute(matrix_col):

	mtx = matrix_col(0)
	log(mtx)
	return
	
#-----------------------------------------------------------------------------
		
def zPrintMatrixFromSelection_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	#oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments
	oArgs.Add('local', c.siArgumentInput, False, c.siBool)

	return True

def zPrintMatrixFromSelection_Execute(local):

	# step through each item in the selection #
	for item in xsi.selection:
		
		# print the matrix #
		xsi.zPrintMatrixFromObject(item, local)