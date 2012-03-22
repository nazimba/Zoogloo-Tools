"""
zObjImportTools.py
"""

__version__ = '$Revision: 11 $'
__author__  = '$Author: andy $'
__date__    = '$Date: 2008-07-21 15:20 -0700 $'

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
	in_reg.Name = "zObjImportTools"
	in_reg.Email = "andy@zoogloo.net"
	in_reg.URL = ""
	try:
		in_reg.Major = int(__version__.split(' ')[1])
	except:
		in_reg.Major = 1
	in_reg.Minor = 0

	in_reg.RegisterProperty('zImportMultiObjsGUI')

	in_reg.RegisterCommand('zImportMultiObjs', 'zImportMultiObjs')
	in_reg.RegisterCommand('zImportMultiObjsGUI', 'zImportMultiObjsGUI')

	in_reg.RegisterMenu(c.siMenuMainFileImportID, 'zObjImportToolsMenu', False)
	
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
def zObjImportToolsMenu_Init(ctxt):
	menu = ctxt.Source
	
	item = menu.AddCommandItem('zImportMultiObjsGUI', 'zImportMultiObjsGUI')
	item.Name = 'Import Multiple OBJ\'s (z)'

#-----------------------------------------------------------------------------
# Properties
#-----------------------------------------------------------------------------
def zImportMultiObjsGUI_Define(ctxt):
	prop = ctxt.Source
	
	prop.AddParameter3("Path", c.siString, xsi.ActiveProject2.Path)

	
def zImportMultiObjsGUI_DefineLayout(ctxt):
	lo = ctxt.Source
	lo.Clear()

	lo.AddGroup('Import Multiple OBJ\'s from Path...')
	lo.AddRow()
	lo.AddItem('Path')
	lo.AddButton('PickPath', '...')
	lo.EndRow()
	lo.EndGroup()
	
	lo.AddRow()
	lo.AddButton('Cancel')
	lo.AddSpacer()
	lo.AddButton('Load')
	lo.EndRow()
	

def zImportMultiObjsGUI_PickPath_OnClicked():
	prop = PPG.Inspected(0)
	prop = dispatch(prop)
	
	# launch a path picker #
	pathname = XSIUIToolkit.PickFolder(prop.Path.Value, 'Pick OBJ path...')
	if pathname:
		prop.Path.Value = pathname
		
def zImportMultiObjsGUI_Load_OnClicked():
	prop = PPG.Inspected(0)
	prop = dispatch(prop)
	
	# import obj's #
	xsi.zImportMultiObjs(prop.Path.Value)
	
	# close the ppg #
	PPG.Close()

def zImportMultiObjsGUI_Cancel_OnClicked():
	PPG.Close()
	
#-----------------------------------------------------------------------------
# Commands
#-----------------------------------------------------------------------------
def zImportMultiObjs_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	#oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments
	oArgs.Add('pathname', c.siArgumentInput, '', c.siString)
	#oArgs.AddObjectArgument('model')

	return True
	
def zImportMultiObjs_Execute(pathname):
	
	# get all the files in the path #
	import glob
	objs = glob.glob('%s/*.obj' % pathname)	
	if not len(objs):
		log('No obj files found in path: %s' % pathname, c.siWarning)
		return False
	
	# import all the objs' #
	for obj in objs:
		xsi.ObjImport(obj, 0, 0, 1, 1, 0, 1)
		
		
def zImportMultiObjsGUI_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	#oCmd.SetFlag(constants.siNoLogging,false)

	#oArgs = oCmd.Arguments
	# oArgs.Add('pathname', c.siArgumentInput, '', c.siString)
	#oArgs.AddObjectArgument('model')

	return True
	
def zImportMultiObjsGUI_Execute():
	# create the property if it doesn't exist on the scene root #
	prop = xsi.ActiveSceneRoot.Properties('zImportMultiObjsGUI')
	if not prop:
		prop = xsi.ActiveSceneRoot.AddProperty('zImportMultiObjsGUI')
	prop = dispatch(prop)
	
	# show the property #
	xsi.InspectObj(prop, None, None, c.siFollow)
	