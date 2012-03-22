"""
Simple XSI Plugin for hiding a collection of objects.  You can also hide the
icon display for the nulls by providing a second boolean value.

>>> Application.zHide(col_objects, True)
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
	in_reg.Name = "zHide"
	in_reg.Email = "andy@zoogloo.net"
	in_reg.URL = ""
	in_reg.Major = 1
	try:
		in_reg.Minor = int(__version__.split(' ')[1])
	except:
		in_reg.Minor = 0

	in_reg.RegisterCommand('zHide', 'zHide')
	
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
# Commands
#-----------------------------------------------------------------------------
def zHide_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.SetFlag(c.siNoLogging, True)

	oArgs = oCmd.Arguments
	oArgs.AddWithHandler('col_object', c.siArgHandlerCollection)
	oArgs.Add('null_icons', c.siArgumentInput, c.siBool, True)

	return True
	
def zHide_Execute(col_object, null_icons):

	# step through the collection #
	for item in col_object:
		
		# turn off the ogl display #
		item.Properties('Visibility').Parameters('viewvis').Value = 0
		
		# turn ogg the render display #
		item.Properties('Visibility').Parameters('rendvis').Value = 0
		
		# turn off the primary icon #
		if null_icons and item.Type == 'null':
			item.primary_icon.Value 	= 0
			item.shadow_icon.Value 	= 0
