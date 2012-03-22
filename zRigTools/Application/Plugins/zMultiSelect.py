"""
zMultiSelect.py

Created by andy on 2008-02-15.
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
	in_reg.Name = "zMultiSelector"
	in_reg.Email = ""
	in_reg.URL = ""
	try:
		in_reg.Major = int(__version__.split(' ')[1])
	except:
		in_reg.Major = 1
	in_reg.Minor = 0

	in_reg.RegisterCommand("zEnableMultiSelect")
	in_reg.RegisterCommand("zDisableMultiSelect")
	in_reg.RegisterCommand("zApplyMultiSelect")
	in_reg.RegisterCommand("zViewMultiSelect")

	in_reg.RegisterProperty("zMultiSelect") 
	
	# in_reg.RegisterEvent("zMultiSelectEvent", c.siOnSelectionChange)
	in_reg.RegisterEvent("zMultiSelectEvent", c.siOnKeyUp)
	
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

#-----------------------------------------------------------------------------
# Property
#-----------------------------------------------------------------------------
def zMultiSelect_Define(ctxt):

	prop = ctxt.Source

	# setup the parameters #
	prop.AddParameter3('Enable', c.siBool, True, None, None, False)
	prop.AddParameter3('Deselect', c.siBool, False, None, None, False)
	prop.AddParameter3('Objects', c.siString)
	prop.AddGridParameter('ObjectsGrid')

	return True

def zMultiSelect_OnInit():
	ppg = PPG.Inspected(0)
	zMultiSelect_RebuildLayout(ppg)

def zMultiSelect_RebuildLayout(ppg):
	
	lo = dispatch(ppg.PPGLayout)
	lo.Clear()
	
	# get the OM to the grid object #
	grid = ppg.ObjectsGrid.Value
	grid.SetColumnLabel(0, 'Objects')

	# clear any grid data #
	grid.RowCount = 0
	grid.Data = [[]]
	
	lo.AddGroup('Zoogloo Multi Selector')
	lo.AddItem('Enable')
	lo.AddItem('Deselect', 'Deselect Original')
	lo.AddRow()
	lo.AddSpacer()
	gridItem = lo.AddItem('ObjectsGrid')
	gridItem.SetAttribute(c.siUIGridSelectionMode, c.siSelectionHeader)
	gridItem.SetAttribute(c.siUIGridReadOnlyColumns, '1')
	gridItem.SetAttribute(c.siUINoLabel, True)
	gridItem.SetAttribute(c.siUIGridColumnWidths, '35:')
	lo.AddSpacer()
	lo.EndRow()

	# get the objects string #
	objStr = ppg.Objects.Value
	if len(objStr):
		# split the objects to a list #
		objList = objStr.split(',')
		# set the row labels #
		for i in xrange(len(objList)):
			grid.SetRowLabel(i, str(i+1))
		# set the row count equal to the obj list #
		grid.RowCount = len(objList)
		# populate the data #
		grid.Data = [objList]
	
	lo.AddRow()
	lo.AddButton('AddObjects', 'Add From Selection')
	lo.AddSpacer()
	lo.AddButton('RemoveObjects', 'Remove Selected Rows')
	lo.EndRow()
	lo.EndGroup()
	
def zMultiSelect_AddObjects_OnClicked():
	prop = PPG.Inspected(0)
	
	# convert the objects string to a list #
	objStr = prop.Objects.Value
	objList = []
	if len(objStr):
		objList = objStr.split(',')
	
	# step through the xsi selection #
	for item in xsi.selection:
		item = dispatch(item)
		
		# catch unselectable items #
		if item.Families != '3D Objects':
			log('Item "%s" not selectable.' % item.FullName, c.siWarning)
			continue
			
		# skip over items all ready in the list #
		if item.FullName in objList:
			log('Item "%s" all ready in selection list.' % item.FullName,
				c.siWarning)
			continue
			
		# add the item to the list #
		objList.append(item.Name)
		
	# convert the object list back to a string #
	if len(objList):
		prop.Objects.Value = ','.join(objList)
	
	# redraw the ppg #
	zMultiSelect_RebuildLayout(prop)
		
def zMultiSelect_RemoveObjects_OnClicked():
	prop = PPG.Inspected(0)
	
	# convert the objects string to a list #
	objStr = prop.Objects.Value
	objList = []
	if len(objStr):
		objList = objStr.split(',')

	# get the grid from the prop #
	grid = prop.ObjectsGrid.Value

	# get the data object #
	objectList = grid.Data
	if not objectList:
		objectList = [[]]
	objectList = list(objectList)
	objectList[0] = list(objectList[0])
	
	# step through each row on the grid and find selected rows #
	widget = grid.GridWidget
	selectedRows = []
	for r in xrange(grid.RowCount):
		if widget.IsRowSelected(r):
			selectedRows.append(r)
	
	# remove the rows in reverse #
	selectedRows.reverse()
	for r in selectedRows:
		objList.pop(r)
		
	# set the objects string #
	if len(objList):
		prop.Objects.Value = ','.join(objList)
	else:
		prop.Objects.Value = ''
		
	# redraw the ppg #
	zMultiSelect_RebuildLayout(prop)

def zMultiSelectEvent_OnEvent(ctxt):
	
	# capture Ctrl + B #
	key = ctxt.GetAttribute('KeyCode')
	mask = ctxt.GetAttribute('ShiftMask')
	# log('Key %s  Mask %s' % (key, mask))
	if key != 66 and mask != 2:
		return False
	
	# cache the original selection #
	sel = dispatch('XSI.Collection')
	sel.AddItems(xsi.selection)
	
	# step through the selection #
	for item in sel:
		if item.Families != '3D Objects':
			log('Item "%s" not selectable.' % item.FullName, c.siWarning)
			continue

		# get the zMultiSelect property #
		prop = item.Properties('zMultiSelect')
		
		# skip over items without the property #
		if not prop: continue
		prop = dispatch(prop)
		
		# skip if not enabled #
		if not prop.Enable.Value: continue
		
		# skip if the grid has no objects #
		if not prop.Objects.Value:
			log('No objects in zMultiSelect property.', c.siWarning)
			return False
			
		# get the object list #
		objs = list(prop.Objects.Value.split(','))
		modelName = item.model.Name
		if modelName != 'Scene_Root':
			for o in xrange(len(objs)):
				objs[o] = modelName + '.' + objs[o]
		
		# create a collection of objects #
		col = dispatch('XSI.Collection')
		col.SetAsText(','.join(objs))
		
		# select the objects #
		for i in col:
			i.Selected = True
			
		# deselect the original #
		if prop.Deselect.Value:
			prop.Parent.Selected = False
		
	return True
	

#-----------------------------------------------------------------------------
# Commands
#-----------------------------------------------------------------------------
def zEnableMultiSelect_Init( in_ctxt ):
	oCmd = in_ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = False
	return True

def zEnableMultiSelect_Execute():
	'''Enables the MultiSelect Event'''

	event = xsi.EventInfos('zMultiSelectEvent')
	if not event.Mute:
		log('zMultiSelect is all ready enabled.', c.siWarning)
		return False
	else:
		event.Mute = False

def zDisableMultiSelect_Init( in_ctxt ):
	oCmd = in_ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = False
	return True

def zDisableMultiSelect_Execute():
	'''Disables the MultiSelect Event'''

	event = xsi.EventInfos('zMultiSelectEvent')
	if event.Mute:
		log('zMultiSelect is all ready disabled.', c.siWarning)
		return False
	else:
		event.Mute = True


def zApplyMultiSelect_Init( in_ctxt ):
	oCmd = in_ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = True
	
	oCmd.Arguments.AddWithHandler('items', c.siArgHandlerCollection)
	oCmd.Arguments.Add('inspect', c.siArgumentInput, True, c.siBool)
	
	return True

def zApplyMultiSelect_Execute(items, inspect):
	'''
	Applies zMultiSelect to objects.  Returns a collection of all created 
	properties
	'''
		
	# make sure we have some items #
	if not items.Count:
		log('zMultiSelect: No objects given.', c.siWarning)
		return False
	
	# create a collection to hold all the properties #
	col = dispatch('XSI.Collection')	
	
	# step through each object and add property to the output collection #
	for item in items:
		
		# make sure the property doesn't all ready exist #
		prop = item.Properties('zMultiSelect')
		
		# add the prop if we don't have one #
		if not prop:
			prop = item.AddProperty('zMultiSelect', False)
			prop = dispatch(prop)
		else:
			log('"%s" all ready has a zMultiSelect property.  Skipping.' % \
			item.FullName, c.siWarning)
	
		# add the prop to the output collection #
		col.Add(prop)
		
	# show the items if the inspect flag is on #
	if inspect:
		xsi.InspectObj(col, None, 'zMultiSelects', c.siFollow)
			
	# return the property collection #
	return col
	
	
def zViewMultiSelect_Init( in_ctxt ):
	oCmd = in_ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = False
	
	oCmd.Arguments.AddWithHandler('items', c.siArgHandlerCollection)
	
	return True

def zViewMultiSelect_Execute(items):
	'''
	Applies zMultiSelect to objects.  Returns a collection of all created 
	properties
	'''
	
	# create a collection to hold the properties #
	col = dispatch('XSI.Collection')
		
	# step through the collection #
	for item in items:
		# if the prop is found at it to the collecton #
		prop = item.Properties('zMultiSelect')
		if prop:
			col.Add(prop)
			
	# view the collecton #
	xsi.InspectObj(col, None, 'zMultiSelects', c.siFollow)