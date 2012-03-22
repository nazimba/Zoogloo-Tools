"""
zSaveScene.py

Created by Andy Buecker on 2007-06-13.
Copyright (c) 2008 Zoogloo LLC. All rights reserved.
"""

__version__ = '$Revision: 11 $'
__author__  = '$Author: andy $'
__date__    = '$Date: 2008-07-21 15:20 -0700 $'

import win32com.client
from win32com.client import constants
from win32com.client import constants as c
from win32com.client.dynamic import Dispatch as dispatch
import re
import time
import os

xsi = Application
log = xsi.logmessage

null = None
false = 0
true = 1

def XSILoadPlugin(in_reg):
	in_reg.Author = "andy"
	in_reg.Name = "zSaveScene"
	in_reg.Email = ""
	in_reg.URL = ""
	try:
		in_reg.Major = int(__version__.split(' ')[1])
	except:
		in_reg.Major = 1
	in_reg.Minor = 0

	in_reg.RegisterProperty("zSaveSceneGUI")
	
	in_reg.RegisterMenu(c.siMenuMainFileSceneID, 'zSaveSceneMenu', False)
	
	in_reg.RegisterCommand("zSaveSceneGUI","zSaveSceneGUI")
	
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

def zSaveSceneMenu_Init(ctxt):
	menu = ctxt.Source
	
	item = menu.AddCommandItem('zSaveSceneGUI', 'zSaveSceneGUI')
	item.Name = 'Save Scene (z)'
		
def zSaveSceneGUI_OnInit():
	
	prop = PPG.Inspected(0)
	prop = dispatch(prop)

	# set the asset name if we have a model selected #
	if xsi.selection.Count and xsi.selection(0).Type == '#model':
		prop.AssetName.Value = xsi.selection(0).Name

	# generate the version #
	t = time.localtime()
	version =  '%2s%02d%02d' % (str(t[0])[-2:], t[1], t[2])
	# reset the itteration if the day stamp changes #
	if version != prop.Version.Value:
		prop.Itter.Value = 1
	# set the version #
	prop.Version.Value = version
	
	# build the filename #
	BuildFileName(prop)
	
	# refresh the layout #
	PPG.Refresh()
	
def BuildFileName(prop):
	'''Assembles the filename from the fields.'''
	prop.FileName.Value = prop.AssetName.Value + '.'
	if prop.Description.Value:
		prop.FileName.Value += prop.Description.Value + '.'
	prop.FileName.Value += '%s.%s.scn' % (prop.Version.Value, prop.Itter.Value)
	
def zSaveSceneGUI_Define(ctxt):
	
	prop = ctxt.Source
	
	prop.AddParameter3("AssetName", c.siString, 'PFX')
	prop.AddParameter3("Description", c.siString, '')
	
	prop.AddParameter3("Version", c.siString, '')
	
	prop.AddParameter3("FileName", c.siString, '', None, None, False, True)
	prop.AddParameter3("FilePath", c.siString, xsi.ActiveProject.Path + os.sep + 'Scenes')

	prop.AddParameter3("Itter", c.siUInt2, 1, 1, 100, False)
	
	return True
	
def zSaveSceneGUI_DefineLayout(ctxt):
	lo = ctxt.Source
	lo.Delete()
	
	lo.AddGroup('Zoogloo - Save Scene')
		
	lo.AddItem('AssetName', 'Asset/Shot Name')
	lo.AddItem('Description')
	lo.AddRow()
	lo.AddItem('Version')
	item = lo.AddItem('Itter', 'Itteration')
	item.SetAttribute(c.siUITreadmill, True)
	lo.EndRow()
	lo.AddRow()
	lo.AddItem('FilePath')
	lo.AddButton('PickPath', '...')
	lo.EndRow()
	
	lo.AddGroup('Info')
	lo.AddItem('FileName')
	lo.EndGroup()
	
	lo.AddRow()
	lo.AddButton('Close')
	lo.AddSpacer()
	lo.AddButton('Save', 'Save Scene')
	lo.EndRow()
	lo.EndGroup
	
def zSaveSceneGUI_Description_OnChanged():
	prop = PPG.Inspected(0)
	prop = dispatch(prop)
	
	# remove any whitespaces #
	prop.Description.Value = re.subn('\s', '', prop.Description.Value)[0]
	
	# build the new name #
	BuildFileName(prop)

def zSaveSceneGUI_Itter_OnChanged():
	prop = PPG.Inspected(0)
	prop = dispatch(prop)
	
	# build the new name #
	BuildFileName(prop)

def zSaveSceneGUI_AssetName_OnChanged():
	prop = PPG.Inspected(0)
	prop = dispatch(prop)
	
	# build the new name #
	BuildFileName(prop)

def zSaveSceneGUI_Version_OnChanged():
	prop = PPG.Inspected(0)
	prop = dispatch(prop)
	
	# build the new name #
	BuildFileName(prop)
	
def zSaveSceneGUI_PickPath_OnClicked():
	prop = PPG.Inspected(0)
	prop = dispatch(prop)

	# build a filebrowser #
	path = XSIUIToolkit.PickFolder(prop.FilePath.Value, 'Pick Scene Directory:')
	if len(path):
		prop.FilePath.Value = path
		
def zSaveSceneGUI_Save_OnClicked():
	prop = PPG.Inspected(0)
	prop = dispatch(prop)
	
	# save the scene #
	xsi.SaveSceneAs(prop.FilePath.Value + os.sep + prop.FileName.Value)
	
	# increment #
	prop.Itter.Value += 1
	
	# close the ppg #
	PPG.Close()

def zSaveSceneGUI_Export_OnClicked():
	prop = PPG.Inspected(0)
	prop = dispatch(prop)
	
	# save the scene #
	xsi.ExportModel(xsi.selection(0), prop.FilePath.Value + os.sep + prop.FileName.Value)
	
	# increment #
	prop.Itter.Value += 1
	
	# close the ppg #
	PPG.Close()
	
def zSaveSceneGUI_Close_OnClicked():
	PPG.Close()

	
def zSaveSceneGUI_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	# oCmd.SetFlag(constants.siNoLogging,false)
	return True

def zSaveSceneGUI_Execute():
	# get the ui #
	prop = xsi.ActiveSceneRoot.Properties('zSaveSceneGUI')
	if not prop:
		prop = xsi.ActiveSceneRoot.AddProperty('zSaveSceneGUI')
	# display the property #
	xsi.Inspectobj(prop, '', None, c.siLock)

