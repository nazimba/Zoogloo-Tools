"""
AMultiGator.py

Created by andy on 2009-02-17.
Copyright (c) 2009 Andy Buecker. All rights reserved.
"""

__version__ = '$Revision: 198 $'
__author__  = '$Author: andy $'
__date__    = '$Date: 2009-03-06 10:14 -0800 $'

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
	in_reg.Name = "AMultiGator"
	in_reg.Email = "andy@abuecker.com"
	in_reg.URL = ""
	in_reg.Major = 1
	try:
		in_reg.Minor = int(__version__.split(' ')[1])
	except:
		in_reg.Minor = 0

	# in_reg.RegisterProperty('AMultiGator')

	in_reg.RegisterCommand('AMultiGator', 'AMultiGator')

	in_reg.RegisterMenu(c.siMenuTbGetPropertyID, 'AMultiGatorMenu', False)
	
	# copyright message #
	msg = '''
------------------------------------------
  %s (v.%d.%d)
  Copyright 2009 Zoogloo LLC.
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
def AMultiGatorMenu_Init(ctxt):
	menu = ctxt.Source
	
	item = menu.AddCommandItem('AMultiGator', 'AMultiGator')
	item.Name = '(a) Multi Gator Transfer'

#-----------------------------------------------------------------------------
# Properties
#-----------------------------------------------------------------------------
# def AMultiGator_Define(ctxt):
# 	prop = ctxt.Source
# 	
# 	#prop.AddParameter3("ParamName", c.siString, '')
# 
# 	
# def AMultiGator_DefineLayout(ctxt):
# 	lo = ctxt.Source
# 	lo.Clear()
# 
# 	lo.AddItem('ParamName')

#-----------------------------------------------------------------------------
# Commands
#-----------------------------------------------------------------------------
def AMultiGator_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	#oCmd.SetFlag(constants.siNoLogging,false)

	#oArgs = oCmd.Arguments
	#oArgs.Add('arg', c.siArgumentInput, '', c.siString)
	#oArgs.AddObjectArgument('model')

	return True
	
def AMultiGator_Execute():

	# make sure something is selected #
	if not xsi.selection.count:
		log('Nothing is selected', c.siError)
		return False
		
	# pick the source object #
	picker = xsi.PickElement(c.siGeometryFilter, 'Pick the source geometry')

	# catch right click exits #
	if not picker[0]:
		log('Canceled.')
		return False

	# get the source geom #
	geom_source = picker[2]
	
	# step through each item in the selection #
	for item in xsi.selection:
		
		# apply the operator #
		op = xsi.ApplyGenOp("Gator", "", item.FullName + ";" + geom_source.FullName, 3, "siPersistentOperation", "siKeepGenOpInputs", "")
		
		# transfer the envelope and shapes #
		xsi.CopyAnimationAcrossGenerator(op, 0, "")
		xsi.SetValue(str(op) + ".inputreadregion", 0, "")
		
		# freeze the operator #
		xsi.FreezeObj(op)
