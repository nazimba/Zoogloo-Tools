"""
zPickWalk.py

Description:
Adds the ability to "pick walk" through nodes using keyboard shortcuts.

Installation:
You will need to assign the following commands to hot keys:

	For Single Selection Mode
	----------------------------
	zPickWalkUp
	zPickWalkDown
	zPickWalkLeft
	zPickWalkRight

	Multiple Selection Mode (Add to Selection)
	---------------------------------------------
	zPickWalkUpAdd
	zPickWalkDownAdd
	zPickWalkLeftAdd
	zPickWalkRightAdd

Usage:
Use the hot keys to navigate through the nodes.  If there is a 
zPickWalk property on the node, it will navigate you to the corresponding
node in the direction associated with the key press.

I{Created by Andy Buecker on 2008-04-08.
Copyright (c) 2008 Zoogloo LLC. All rights reserved.

Modification or distribution of this tool is not permitted without the
consent of Zoogloo LLC.}
"""

__version__ = '$Revision: 185 $'
__author__  = '$Author: andy $'
__date__    = '$Date: 2009-02-06 21:04 -0800 $'

import win32com.client
from win32com.client import constants
from win32com.client import constants as c
from win32com.client import Dispatch as dispatch
xsi = Application
log = xsi.logmessage

null = None
false = 0
true = 1

class zPickWalkError(Exception): pass

def XSILoadPlugin(in_reg):
	in_reg.Author = "Andy Buecker"
	in_reg.Name = "zPickWalk"
	in_reg.Email = ""
	in_reg.URL = ""
	try:
		in_reg.Major = int(__version__.split(' ')[1])
	except:
		in_reg.Major = 1
	in_reg.Minor = 0

	in_reg.RegisterProperty("zPickWalk")
	
	in_reg.RegisterCommand("zPickWalk")
	
	in_reg.RegisterCommand("zPickWalkUp")
	in_reg.RegisterCommand("zPickWalkDown")
	in_reg.RegisterCommand("zPickWalkLeft")
	in_reg.RegisterCommand("zPickWalkRight")

	in_reg.RegisterCommand("zPickWalkUpAdd")
	in_reg.RegisterCommand("zPickWalkDownAdd")
	in_reg.RegisterCommand("zPickWalkLeftAdd")
	in_reg.RegisterCommand("zPickWalkRightAdd")

	in_reg.RegisterCommand("zPickWalkInstall")

	in_reg.RegisterMenu(c.siMenuMCPSelectBottomID, 'zPickWalkMenu', False)

	# copyright message #
	msg = '''
------------------------------------------
  %s (v.%d.%d)
  Copyright 2008 Zoogloo LLC.
  All rights Reserved.
------------------------------------------
	''' % (in_reg.Name, in_reg.Major, in_reg.Minor)
	log(msg)

	return True

def XSIUnloadPlugin(in_reg):
	strPluginName = in_reg.Name
	Application.LogMessage(str(strPluginName) + str(" has been unloaded."))
	return true
	
	
#-----------------------------------------------------------------------------
# Menus
#-----------------------------------------------------------------------------
def zPickWalkMenu_Init(ctxt):
	menu = ctxt.Source
	
	item = menu.AddCommandItem('zPickWalkInstall', 'zPickWalkInstall')
	item.Name = '(z) Pick Walk'

#-----------------------------------------------------------------------------
# Properties
#-----------------------------------------------------------------------------
def zPickWalk_Define(ctxt):
	
	prop = ctxt.Source
	
	prop.AddParameter3("Mute", c.siBool, False, None, None, False)
	prop.AddParameter3("Up", c.siString, '', None, None, False, True)
	prop.AddParameter3("Down", c.siString, '', None, None, False, True)
	prop.AddParameter3("Left", c.siString, '', None, None, False, True)
	prop.AddParameter3("Right", c.siString, '', None, None, False, True)
	
	
def zPickWalk_DefineLayout(ctxt):
	lo = ctxt.Source
	lo.Clear()

	lo.AddGroup('Zoogloo Pick Walk')

	lo.AddRow()
	lo.AddItem('Up')
	lo.AddButton('PickUp', 'Pick')
	lo.EndRow()

	lo.AddRow()
	lo.AddItem('Down')
	lo.AddButton('PickDown', 'Pick')
	lo.EndRow()

	lo.AddRow()
	lo.AddItem('Left')
	lo.AddButton('PickLeft', 'Pick')
	lo.EndRow()
	
	lo.AddRow()
	lo.AddItem('Right')
	lo.AddButton('PickRight', 'Pick')
	lo.EndRow()

	lo.AddGroup('Options')
	lo.AddItem('Mute')
	lo.EndGroup()

	lo.EndGroup()
	
	
def zPickWalk_PickUp_OnClicked():
	prop = PPG.Inspected(0)

	# pick element #
	picker = xsi.PickElement(None, 'Pick Target Item', 'Pick Target Item')
	# catch right clicks #
	if not picker[0]: 
		log('Canceled.', c.siError)
		return
	# add picked items to the selection #
	picked = picker[2]
	
	# store the name #
	prop.Up.Value = picked.Name
	
def zPickWalk_PickDown_OnClicked():
	prop = PPG.Inspected(0)

	# pick element #
	picker = xsi.PickElement(None, 'Pick Target Item', 'Pick Target Item')
	# catch right clicks #
	if not picker[0]: 
		log('Canceled.', c.siError)
		return
	# add picked items to the selection #
	picked = picker[2]

	# store the name #
	prop.Down.Value = picked.Name

def zPickWalk_PickLeft_OnClicked():
	prop = PPG.Inspected(0)

	# pick element #
	picker = xsi.PickElement(None, 'Pick Target Item', 'Pick Target Item')
	# catch right clicks #
	if not picker[0]: 
		log('Canceled.', c.siError)
		return
	# add picked items to the selection #
	picked = picker[2]

	# store the name #
	prop.Left.Value = picked.Name
	
def zPickWalk_PickRight_OnClicked():
	prop = PPG.Inspected(0)

	# pick element #
	picker = xsi.PickElement(None, 'Pick Target Item', 'Pick Target Item')
	# catch right clicks #
	if not picker[0]: 
		log('Canceled.', c.siError)
		return
	# add picked items to the selection #
	picked = picker[2]

	# store the name #
	prop.Right.Value = picked.Name


#-----------------------------------------------------------------------------
# Properties
#-----------------------------------------------------------------------------
def zPickWalk_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""

	oArgs = oCmd.Arguments
	oArgs.Add("direction", c.siArgumentInput, 'Down', c.siString)
	oArgs.Add("addToSelection", c.siArgumentInput, False, c.siBool)

	return true


def zPickWalk_Execute(direction, addToSelection):
	
	# cache the selection #
	sel = dispatch('XSI.Collection')
	sel.AddItems(xsi.selection)
	
	# create collections to hold selects #
	col_sel 	= dispatch('XSI.Collection')
	
	
	# step through each item in the selection #
	for item in sel:
		# get the property #
		prop = item.Properties('zPickWalk')
		# skip over the object if the prop is not found #
		if not prop: continue
		# do the dispatch hack #
		prop = dispatch(prop)
		# get the target name #
		targetName = prop.Parameters(direction).Value
		# skip if there are no targets #
		if not targetName:
			continue
		# find the node #
		targetObject = prop.Model.FindChild(targetName)
		# skip if the object isn't found #
		if not targetObject:
			log('Unable to locate "%s"' % targetObject, c.siWarning)
			continue
		# select it #
		# targetObject.Selected = True
		col_sel.Add(targetObject)
		# deselect the original object #
		# if not addToSelection:
		# 	# item.Selected = False
		# if we are adding to the selection keep the original item #
		if addToSelection: col_sel.Add(item)
	
	# use SelectObj command to trigger any transform setups, they are ignored 
	# when going through the object model
	xsi.SelectObj(col_sel)

#------------------------------------------------------
# Individual Pick walk commands
#------------------------------------------------------
# UP #
def zPickWalkUp_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = False
	oCmd.SetFlag(constants.siNoLogging, False)

def zPickWalkUp_Execute():
	xsi.zPickWalk('Up')
	
# DOWN #
def zPickWalkDown_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = False
	oCmd.SetFlag(constants.siNoLogging, False)

def zPickWalkDown_Execute():
	xsi.zPickWalk('Down')
	
# LEFT #
def zPickWalkLeft_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = False
	oCmd.SetFlag(constants.siNoLogging, False)

def zPickWalkLeft_Execute():
	xsi.zPickWalk('Left')
	
# RIGHT #
def zPickWalkRight_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = False
	oCmd.SetFlag(constants.siNoLogging, False)

def zPickWalkRight_Execute():
	xsi.zPickWalk('Right')


#-------------------------------------------------
# Commands to add to the selection
#-------------------------------------------------
# UP ADD #
def zPickWalkUpAdd_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = False
	oCmd.SetFlag(constants.siNoLogging, False)

def zPickWalkUpAdd_Execute():
	xsi.zPickWalk('Up', True)
	
# DOWN ADD #
def zPickWalkDownAdd_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = False
	oCmd.SetFlag(constants.siNoLogging, False)

def zPickWalkDownAdd_Execute():
	xsi.zPickWalk('Down', True)
	
# LEFT ADD #
def zPickWalkLeftAdd_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = False
	oCmd.SetFlag(constants.siNoLogging, False)

def zPickWalkLeftAdd_Execute():
	xsi.zPickWalk('Left', True)
	
# RIGHT ADD #
def zPickWalkRightAdd_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = False
	oCmd.SetFlag(constants.siNoLogging, False)

def zPickWalkRightAdd_Execute():
	xsi.zPickWalk('Right', True)


#-----------------------------------------------------------------------------
def zPickWalkInstall_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = False
	# oCmd.SetFlag(constants.siNoLogging, False)

def zPickWalkInstall_Execute():
	# create a collection to hold the properties #
	col = dispatch('XSI.Collection')
	# step through the selection #
	for item in xsi.selection:
		# get or create the property #
		prop = item.Properties('zPickWalk')
		if not prop:
			prop = item.AddProperty('zPickWalk')
		# add it to the collection #
		col.Add(prop)
			
	# inspect the properties #
	xsi.InspectObj(col, '', '', c.siLockAndForceNew)
