"""
XSI Plugin with a custom property, command and menu for information such as date, version, author, etc.

Created by andy on 2008-08-04.
Copyright (c) 2008 Zoogloo LLC. All rights reserved.
"""

__version__ = '$Revision: 185 $'
__author__  = '$Author: andy $'
__date__    = '$Date: 2009-02-06 21:04 -0800 $'

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
	in_reg.Name = "zInfo"
	in_reg.Email = "andy@zoogloo.net"
	in_reg.URL = ""
	in_reg.Major = 1
	try:
		in_reg.Minor = int(__version__.split(' ')[1])
	except:
		in_reg.Minor = 0
	

	in_reg.RegisterProperty('zInfo')

	in_reg.RegisterCommand('zInfo', 'zInfo')

	in_reg.RegisterMenu(c.siMenuTbAnimateActionsStoreID, 'zInfoMenu', False)
	
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
def zInfoMenu_Init(ctxt):
	menu = ctxt.Source
	
	item = menu.AddCommandItem('zInfoGUI', 'zInfoGUI')
	item.Name = '(z) zInfo'

#-----------------------------------------------------------------------------
# Properties
#-----------------------------------------------------------------------------
def zInfo_Define(ctxt):
	info = ctxt.Source

	# get the time and build a version #
	import time
	t = time.localtime()
	version = '%2s%02d%02d' % (str(t[0])[-2:], t[1], t[2])
	
	# add rig version info
	info.AddParameter3('Author', c.siString, '', None, None, False, True)
	info.AddParameter3('Month', c.siUInt2, t[1], 0, 12, False, True)
	info.AddParameter3('Day',   c.siUInt2, t[2], 0, 31, False, True)
	info.AddParameter3('Year',  c.siUInt2, t[0], 2008, 3000, False, True)
	info.AddParameter3('Hour',  c.siUInt2, t[3], 0, 24, False, True)
	info.AddParameter3('Min',   c.siUInt2, t[4], 0, 60, False, True)
	info.AddParameter3('Revision', c.siUInt2, 0, 0, 65535, False, True)
	info.AddParameter2('Itteration', c.siUInt2, 1, 0, 65535, 1, 10, c.siClassifUnknown)
	info.AddParameter3('Version', c.siString, version, None, None, False, True)
	info.AddParameter3('Prefix', c.siString, 'PFX', None, None, False, True)

	
def zInfo_OnInit():

	# get the property #
	info = PPG.Inspected(0)
	info = dispatch(info)

	# get the layout #
	lo = info.PPGLayout
	lo.Clear()

	# build the ppg layout #
	lo.AddGroup('Zoogloo Information')
	lo.AddGroup('Rig: %s.%s.%s' % (info.Prefix.Value, info.Version.Value, info.Itteration.Value))
	lo.AddRow()
	lo.AddStaticText('Author: %s' % (info.Author.Value))
	lo.AddSpacer()
	lo.AddStaticText('Revision: %d' % (info.Revision.Value))
	lo.EndRow()
	lo.AddRow()
	lo.AddStaticText('Date: %d/%d/%d' % (info.Month.Value, info.Day.Value, info.Year.Value))
	lo.AddSpacer()
	lo.AddStaticText('Time: %d:%02d' % (info.Hour.Value, info.Min.Value))
	lo.EndRow()
	it = lo.AddItem('Itteration')
	lo.EndGroup()
	lo.EndGroup()
	it.SetAttribute(c.siUITreadmill, True)

#-----------------------------------------------------------------------------
# Commands
#-----------------------------------------------------------------------------
def zInfo_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	#oCmd.SetFlag(constants.siNoLogging,false)

	#oArgs = oCmd.Arguments
	#oArgs.Add('arg', c.siArgumentInput, '', c.siString)
	oArgs.AddObjectArgument('node')

	return True
	
def zInfo_Execute(node):
	pass
