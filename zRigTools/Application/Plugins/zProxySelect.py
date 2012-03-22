"""
zProxySelect.py

I{Created by  on 2008-04-01.
Copyright (c) 2008 Zoogloo LLC. All rights reserved.}
"""
__version__ = '$Revision: 198 $'
__author__  = '$Author: andy $'
__date__    = '$Date: 2009-03-06 10:14 -0800 $'

import win32com.client
from win32com.client import constants
from win32com.client import constants as c
from win32com.client import Dispatch as dispatch
import time
import sys, os
import xml.dom.minidom as dom

xsi = Application
log = xsi.logmessage

null = None
false = 0
true = 1

class zTailError(Exception): pass

def XSILoadPlugin(in_reg):
	in_reg.Author = "Andy Buecker"
	in_reg.Name = "zProxySelect"
	in_reg.Email = ""
	in_reg.URL = ""
	try:
		in_reg.Major = int(__version__.split(' ')[1])
	except:
		in_reg.Major = 1
	in_reg.Minor = 0

	in_reg.RegisterProperty("zProxySelect")
	
	# in_reg.RegisterCommand("zCreateProxySelect")
	in_reg.RegisterCommand("zApplyProxySelect")
	in_reg.RegisterCommand("zEnableProxySelect")
	in_reg.RegisterCommand("zDisableProxySelect")
	in_reg.RegisterCommand("zLoadProxySelectMap")

	in_reg.RegisterMenu(c.siMenuMCPSelectTopID, 'zProxySelectMenu')

	in_reg.RegisterEvent("zProxySelectEvent", c.siOnSelectionChange)

	# copyright message #
	msg = '''
------------------------------------------
  %s (v.%s.%s)
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
	
	
def zProxySelectMenu_Init(ctxt):
	'''
	!! Doesn't work when anchored to the select menu
	'''
	menu = ctxt.Source
	
	# Submenu #
	# sub = menu.AddItem('zProxySelect', c.siMenuItemSubmenu)
	# add commands to enable and disable the event #
	enable = menu.AddCommandItem("Enable", "zEnableProxySelect")
	enable = dispatch(enable)
	disable = menu.AddCommandItem("Disable", "zDisableProxySelect") 
	disable = dispatch(disable)
	
	# get the state of the event #
	proxyEnabled = bool(1-int(xsi.EventInfos('zProxySelectEvent').Mute))
	
	if proxyEnabled:
		enable.Enabled = False
		disable.Enabled = True
	else:
		enable.Enabled = True
		disable.Enabled = False
	
	menu.AddSeparatorItem()
	
	menu.AddCommandItem('Apply', 'zApplyProxySelect')


def zProxySelect_Define(ctxt):
	
	prop = ctxt.Source
	
	prop.AddParameter3("Target", c.siString, '', None, None, False, True)
	prop.AddParameter3("Deselect", c.siBool, True)
	
	
def zProxySelect_DefineLayout(ctxt):
	lo = ctxt.Source
	lo.Clear()

	lo.AddGroup('Zoogloo Proxy Selector')
	lo.AddRow()
	lo.AddItem('Target', 'Target Items')
	lo.AddButton('Pick', 'Pick')
	lo.EndRow()
	lo.AddItem('Deselect')
	lo.EndGroup()
	
def zProxySelect_Pick_OnClicked():
	prop = PPG.Inspected(0)

	# pick elements #
	picked = dispatch('XSI.Collection')
	while True:
		picker = xsi.PickElement(None, 'Pick Target Items', 'Pick Target Items')
		# catch right clicks #
		if not picker[0]: break
		# make sure there is no proxy selector on the object #
		if picker[2].Properties('zProxySelect'):
			log('Unable to add "%s" to item list.  ' % picker[2].FullName + \
				'All ready has zProxySelect item.\nWould cause a undesired ' + \
				'behavior', c.siWarning)
			continue
		# add picked items to the selection #
		picked.Add(picker[2])
	
	# exit if we don't have any items #
	if not picked.Count:
		log('Canceled.', c.siWarning)
		return False
	
	# store the names #
	pickedString = ''
	for item in picked:
		pickedString += item.Name + ','
	pickedString = pickedString[:-1]
	prop.Target.Value = pickedString


def zProxySelectEvent_OnEvent(ctxt):
	
	# get thhe change mode, ignore removed events #
	changeMode = ctxt.GetAttribute('ChangeType')
	if changeMode == 1:
		return
		
	# step through all the items in the selection #
	sel = dispatch('XSI.Collection')
	sel.AddItems(xsi.selection)
	for item in sel:

		# skip anything other than an object selection #
		if item.Type != 'polymsh' and item.Type != 'surfmsh':
			continue

		# get the property #
		prop = item.Properties('zProxySelect')
		# skip over the object if the prop is not found #
		if not prop: continue
		prop = dispatch(prop)
		# get the item list #
		for target in prop.Target.Value.split(','):
			targetObject = prop.Model.FindChild(target)
			# skip if the object isn't found #
			if not targetObject:
				log('Unable to locate "%s"' % targetObject, c.siWarning)
				continue
			# select it #
			if not targetObject.Properties('zProxySelect'):
				targetObject.Selected = True
				
		# deselect the original object #
		if prop.Deselect.Value:
			item.Selected = False
				
		
def zApplyProxySelect_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	# oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments
	oArgs.AddWithHandler('objects', c.siArgHandlerCollection)
	oCmd.Arguments.Add('inspect', c.siArgumentInput, True, c.siBool)
	
	return true


def zApplyProxySelect_Execute(objects, inspect):
	
	# make sure we have some objects #
	if not objects.Count:
		log('zProxySelect: No objects given.', c.siWarning)
		return False

	# create an output collection #
	col = dispatch('XSI.Collection')
	
	# step through the objects collection #
	for item in objects:
		
		# add the property #
		prop = item.Properties('zProxySelect')
		if not prop:
			prop = item.AddProperty('zProxySelect', False)
			prop = dispatch(prop)
		else:
			log('"%s" all ready has a zProxySelect property.  Skipping.' % \
			item.FullName, c.siWarning)
		
		# add it to the collection #
		col.Add(prop)
	
	# inspect the collection #
	if inspect: xsi.InspectObj(col, None, 'zProxySelects', c.siFollow)
	
	# return the collection #
	return col
	
def zEnableProxySelect_Init( in_ctxt ):
	oCmd = in_ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = False
	return True

def zEnableProxySelect_Execute():
	'''Enables the ProxySelect Event'''

	event = xsi.EventInfos('zProxySelectEvent')
	if not event.Mute:
		log('zProxySelect is all ready enabled.', c.siWarning)
		return False
	else:
		event.Mute = False

def zDisableProxySelect_Init( in_ctxt ):
	oCmd = in_ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = False
	return True

def zDisableProxySelect_Execute():
	'''Disables the ProxySelect Event'''

	event = xsi.EventInfos('zProxySelectEvent')
	if event.Mute:
		log('zProxySelect is all ready disabled.', c.siWarning)
		return False
	else:
		event.Mute = True
		
		
def zLoadProxySelectMap_Init( in_ctxt ):
	oCmd = in_ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = False

	oArgs = oCmd.Arguments
	oCmd.Arguments.Add('filename', c.siArgumentInput, '', c.siString)
	oArgs.AddObjectArgument('model')

	return True

def zLoadProxySelectMap_Execute(filename, model):
	
	# if we don't have a model use the scene root #
	if not model:
		model = xsi.ActiveSceneRoot
		
	# make sure we have a model #
	if model.Type != '#model':
		log('Model argument is not of type "model".', c.siError)
		return False

	# make sure the file exists #
	if not os.path.exists(filename):
		log('File doesn\'t exist: %s' % filename, c.siError)
		return False

	# initialize a progress bar #
	pb = XSIUIToolkit.ProgressBar
	pb.Caption = 'Parsing: ' + os.path.basename(filename)
	pb.Step = 1
	if xsi.Interactive: pb.Visible = True

	# read in the xml file #
	tStart = time.time()
	xml = dom.parse(filename)
	doc = xml.documentElement
	tParse = time.time() - tStart
	log('Time to parse file: %02d:%02d.%02d' % (int(tParse/60), tParse%60, tParse%1*100))		
		
	# count all the elements #
	proxyCount = len(doc.getElementsByTagName('proxy'))

	# update progress bar #
	pb.Maximum = proxyCount
	import locale
	locale.setlocale(locale.LC_ALL, '')
	pb.StatusText = 'Processing: %s proxies' % locale.format('%d', proxyCount, True)
	
	
	# step through the geometry #
	tApply = time.time()
	x_proxies = xml.getElementsByTagName('proxy')
	for x_proxy in x_proxies:
		
		# check for cancel #
		if pb.CancelPressed: return False
		
		# increment the pb #
		pb.Increment()
		
		# create the proxy selecter #
		source = model.FindChild(x_proxy.getAttribute('source'))
		target = model.FindChild(x_proxy.getAttribute('target'))
		# log('Application.zCreateProxySelect("%s", "%s")' % (source, target))
		# make sure the items exist #
		if not source:
			log('No source object specified.', c.siError)
			return False
		if not target:
			log('No target object specified.', c.siError)
			return False
		# xsi.zCreateProxySelect(source, target)
		# apply the proxy prop #
		prop = source.AddProperty('zProxySelect')
		prop = dispatch(prop)
		prop.Target.Value = target.Name
		
		
	# get the time to apply the weights #
	tElapse = time.time() - tApply
	log('Time to apply proxies: %02d:%02d.%02d' % (int(tElapse/60), tElapse%60, tElapse%1*100))

	# get the total time #
	tTotal = time.time() - tStart
	log('Total Elapsed time: %02d:%02d.%02d' % (int(tTotal/60), tTotal%60, tTotal%1*100))
	
	
# def zCreateProxySelect_Init(ctxt):
# 	oCmd = ctxt.Source
# 	oCmd.Description = ""
# 	# oCmd.SetFlag(constants.siNoLogging,false)
# 
# 	oArgs = oCmd.Arguments
# 	oArgs.AddObjectArgument('source_obj')
# 	oArgs.AddObjectArgument('target_obj')
# 	
# 	return true
# 
# 
# def zCreateProxySelect_Execute(source_obj, target_obj):
# 	
# 	# apply the proxy prop #
# 	prop = source_obj.AddProperty('zProxySelect')
# 	prop = dispatch(prop)
# 	prop.Target.Value = target_obj
# 	
# 	# apply the proxy selection #
# 	# xsi.zApplyProxySelect(source_obj, False)