#!/usr/bin/env python
"""
zSaveAndIncrement.py

Created by andy on 2007-05-15.
Copyright (c) 2008 Zoogloo LLC. All rights reserved.
This plugin is provided AS IS and WITHOUT WARRANTY
"""

__version__ = '$Revision: 185 $'
__author__  = '$Author: andy $'
__date__    = '$Date: 2009-02-06 21:04 -0800 $'

import win32com.client
from win32com.client import constants
from win32com.client import constants as c

xsi = Application
log = xsi.logmessage
null = None
false = 0
true = 1

def XSILoadPlugin( in_reg ):
	in_reg.Author = 'Andy Buecker'
	in_reg.Name = "zSaveAndIncrement"
	in_reg.Email = ""
	in_reg.URL = ""
	try:
		in_reg.Major = int(__version__.split(' ')[1])
	except:
		in_reg.Major = 1
	in_reg.Minor = 0

	
	in_reg.RegisterCommand("Save Increment", "zIncrementAndSave" )
	
	in_reg.RegisterMenu( c.siMenuMainFileSceneID, "ZooIncrementSaveMenu", False, False )
	
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

	return true
	
def ZooIncrementSaveMenu_Init( ctxt ):
	menu = ctxt.Source
	menu.AddCommandItem( "Increment && Save", "Save Increment" );


def XSIUnloadPlugin( in_reg ):
	strPluginName = in_reg.Name
	Application.LogMessage(str(strPluginName) + str(" has been unloaded."))
	return true

def SaveIncrement_Init( ctxt ):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = False

	return true

def SaveIncrement_Execute():

	Application.LogMessage("IncrementAndSave_Execute called")
	
	# get the full path of the current scene #
	fullpath = xsi.ActiveProject.ActiveScene.Parameters("Filename").Value
	
	# get the directory and the basename #
	import os
	dirPath = os.path.dirname( fullpath )
	baseName = os.path.basename( fullpath )
	
	# split on '.' #
	baseSplit = baseName.split( '.' )
	
	# reverse step through the splits and find the first integer #
	newBaseName = []
	for i in xrange( len( baseSplit ) ):
		current = baseSplit[(i+1)*-1]
		try:
			inc = int(current) + 1
			newBaseName.append( str(inc) )
		except:
			newBaseName.append( current )
			continue
	
	# reverese the new base name list #
	newBaseName.reverse()
	
	# build the new filename #
	import string		
	newFileName = string.join( newBaseName, '.' )
	
	# save the scene #
	xsi.logmessage( "Incrementing Save As: %s" % newFileName )
	xsi.SaveSceneAs( dirPath + os.sep + newFileName, False )
	

