#!/usr/bin/env python
"""
zObjectMap.py

Created by Andy Buecker on 2008-03-14.
Copyright (c) 2008 Zoogloo LLC. All rights reserved.
"""
__version__ = '$Revision: 24 $'
__author__	= '$Author: andy $'
__date__	= '$Date: 2008-07-23 10:34 -0700 $'

import win32com.client
from win32com.client import constants
from win32com.client import constants as c
from win32com.client.dynamic import Dispatch as dispatch

xsi = Application
log = xsi.logmessage

null = None
false = 0
true = 1

inEvent = False
global inEvent

def XSILoadPlugin( in_reg ):
	in_reg.Author = "Andy Buecker"
	in_reg.Name = "zObjectMap"
	in_reg.Email = ""
	in_reg.URL = ""
	try:
		in_reg.Major = int(__version__.split(' ')[1])
	except:
		in_reg.Major = 1
	in_reg.Minor = 0

	in_reg.RegisterProperty("zObjectMap") 
	
	# copyright message #
	msg = '''
------------------------------------------
  %s (v.%s.%s)
  Copyright 2008 Zoogloo LLC.
  All rights Reserved.
------------------------------------------
	''' % (in_reg.Name, in_reg.Major, in_reg.Minor)
	log(msg)

	#RegistrationInsertionPoint - do not remove this line

def XSIUnloadPlugin(in_reg):
	strPluginName = in_reg.Name
	Application.LogMessage(str(strPluginName) + str(" has been unloaded."))
	return true

def zObjectMap_Define(ctxt):
	prop = ctxt.Source
	
	# prop.AddGridParameter('GridMap')
	
	prop.AddParameter3('NewSource', c.siString)
	prop.AddParameter3('NewTarget', c.siString)
		
def zObjectMap_OnInit():
	ppg = PPG.Inspected(0)
	zMultiSelect_RebuildLayout(ppg)

def zObjectMap_RebuildLayout(ppg):

	lo = dispatch(ppg.PPGLayout)
	lo.Clear()
	
	# items #
	# grid = lo.AddItem('GridMap', 'Mapper', c.siControlGrid)
	
	# buttons #
	lo.AddGroup('New Relation')
	lo.AddRow()
	lo.AddButton('Remove')
	lo.AddButton('New')
	lo.EndRow()
	lo.EndGroup()
