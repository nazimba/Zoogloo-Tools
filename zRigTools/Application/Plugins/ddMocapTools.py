"""
ddMocapTools.py
"""

__version__ = '$Revision: 11 $'
__author__  = '$Author: andy $'
__date__    = '$Date: 2008-07-21 15:20 -0700 $'

import win32com.client
from win32com.client import constants
from win32com.client import constants as c
from win32com.client.dynamic import Dispatch as dispatch
import os
import re

xsi = Application
log = xsi.logmessage

null = None
false = 0
true = 1

LNO_RMAP_PATH = r'\\mammoth\andy\Documents\work\Clients\D2\tcats\xsi\tcats_andy\Models\LNO_RMAP.080503.1.emdl'
SLI_RMAP_PATH = r'\\mammoth\andy\Documents\work\Clients\D2\tcats\xsi\tcats_andy\Models\SLI_RMAP.080502.3.emdl'
LNO_RIG_PATH  = r'\\mammoth\andy\Documents\work\Clients\D2\tcats\xsi\tcats_andy\Models\LNO080424.1\LNO1.emdl'
SLI_RIG_PATH  = r'\\mammoth\andy\Documents\work\Clients\D2\tcats\xsi\tcats_andy\Models\SLI080424.1\SLI1.emdl'

def XSILoadPlugin(in_reg):
	in_reg.Author = "Andy Buecker"
	in_reg.Name = "ddMocapTools"
	in_reg.Email = "andy@zoogloo.net"
	in_reg.URL = ""
	try:
		in_reg.Major = int(__version__.split(' ')[1])
	except:
		in_reg.Major = 1
	in_reg.Minor = 0

	# in_reg.RegisterProperty('ddMocapTools')

	in_reg.RegisterCommand('ddProcessMocap', 'ddProcessMocap')

	# in_reg.RegisterMenu(c.siMenuTbAnimateActionsStoreID, 'ddMocapToolsMenu', False)
	
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
def ddMocapToolsMenu_Init(ctxt):
	menu = ctxt.Source
	
	item = menu.AddCommandItem('ddMocapToolsGUI', 'ddMocapToolsGUI')
	item.Name = '(z) ddMocapTools'

#-----------------------------------------------------------------------------
# Properties
#-----------------------------------------------------------------------------
def ddMocapTools_Define(ctxt):
	prop = ctxt.Source
	
	#prop.AddParameter3("ParamName", c.siString, '')

	
def ddMocapTools_DefineLayout(ctxt):
	lo = ctxt.Source
	lo.Clear()

	lo.AddItem('ParamName')

#-----------------------------------------------------------------------------
# Commands
#-----------------------------------------------------------------------------
def ddProcessMocap_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	#oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments
	oArgs.Add('mocap_filein', c.siArgumentInput, '', c.siString)
	oArgs.Add('mocap_fileout', c.siArgumentInput, '', c.siString)
	oArgs.Add('fps', c.siArgumentInput, 30, c.siUInt2)

	return True
	
def ddProcessMocap_Execute(mocap_filein, mocap_fileout, fps):
	
	#
	xsi.NewScene(None, False)
	
	# set the frame rate #
	xsi.SetValue("PlayControl.Rate", fps, "")
	
	# parse the filename #
	setup, take, asset, cat, typ, version = os.path.basename(mocap_filein).split('_')
	
	# determine the prefix #
	prefix = None
	model = None
	if re.match('.*liono.*', asset, re.I):
		log('Importing Liono animation rig....')
		prefix = 'LNO'
		model = xsi.ImportModel(LNO_RMAP_PATH, xsi.ActiveSceneRoot, False)(1)
	if re.match('.*slithe.*', asset, re.I):
		log('Importing Slithe animation rig....')
		prefix = 'SLI'
		model = xsi.ImportModel(SLI_RMAP_PATH, xsi.ActiveSceneRoot, False)(1)
	
	# get the mocap model #
	model_mocap = None
	model_cons = None
	for mdl in model.Children:
		if mdl.Name == prefix + '_Mocap':
			model_mocap = mdl
		elif mdl.Name == prefix + '_Controls':
			model_cons = mdl
		
			
	# import the mocap #
	source = xsi.ImportAction(model_mocap, mocap_filein)
	source = dispatch(source)
	
	# apply the action #
	xsi.ApplyAction(source, model_mocap)
	
	# get the start and end times #
	start = source.FrameStart.Value
	end = source.FrameEnd.Value
	
	# plot the mocap #
	log('%s, %s, %s, %s' % (model_cons, mocap_fileout, start, end))
	xsi.zPlotMocapToFile(
		model_cons,
		mocap_fileout,
		None,
		start,
		end,
		1
	)

	# import the rig #
	model_rig = None
	if prefix == 'LNO':
		model_rig = xsi.ImportModel(LNO_RIG_PATH, xsi.ActiveSceneRoot, False)(1)
	if prefix == 'SLI':
		model_rig = xsi.ImportModel(SLI_RIG_PATH, xsi.ActiveSceneRoot, False)(1)
	
	# apply the new action #
	xsi.ImportActionAndApply(model_rig, mocap_fileout)
	
	