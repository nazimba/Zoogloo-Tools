"""
zPlot.py
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
	in_reg.Name = "zPlot"
	in_reg.Email = "andy@zoogloo.net"
	in_reg.URL = ""
	try:
		in_reg.Major = int(__version__.split(' ')[1])
	except:
		in_reg.Major = 1
	in_reg.Minor = 0

	in_reg.RegisterProperty('zPlot')

	in_reg.RegisterCommand('zGetPlotString', 'zGetPlotString')
	in_reg.RegisterCommand('zAddPlotTags', 'zAddPlotTags')
	in_reg.RegisterCommand('zAddPlotTagsLocalPosRot', 'zAddPlotTagsLocalPosRot')
	in_reg.RegisterCommand('zAddPlotTagsLocalRot', 'zAddPlotTagsLocalRot')
	in_reg.RegisterCommand('zPlotMocapToFile', 'zPlotMocapToFile')
	
	in_reg.RegisterFilter("zPlot_Nodes", c.siFilter3DObject);

	in_reg.RegisterMenu(c.siMenuTbAnimateToolsPlotID, 'zPlotMenu', False)
	
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
def zPlotMenu_Init(ctxt):
	menu = ctxt.Source
	
	item = menu.AddCommandItem('zAddPlotTags', 'zAddPlotTags')
	item.Name = 'Add Plot Tags (z)'
	item = menu.AddCommandItem('zAddPlotTagsLocalPosRot', 'zAddPlotTagsLocalPosRot')
	item.Name = 'Add Plot Tags [Lcl Pos/Rot] (z)'
	item = menu.AddCommandItem('zAddPlotTagsLocalRot', 'zAddPlotTagsLocalRot')
	item.Name = 'Add Plot Tags [Lcl Rot] (z)'

#-----------------------------------------------------------------------------
# Properties
#-----------------------------------------------------------------------------
def zPlot_Define(ctxt):
	prop = ctxt.Source
	
	prop.AddParameter3("Scale", c.siBool, False, None, None, False, False)
	prop.AddParameter3("SclLclX", c.siBool, False, None, None, False, False)
	prop.AddParameter3("SclLclY", c.siBool, False, None, None, False, False)
	prop.AddParameter3("SclLclZ", c.siBool, False, None, None, False, False)
	prop.AddParameter3("SclGlbX", c.siBool, False, None, None, False, False)
	prop.AddParameter3("SclGlbY", c.siBool, False, None, None, False, False)
	prop.AddParameter3("SclGlbZ", c.siBool, False, None, None, False, False)
	
	prop.AddParameter3("Rotation", c.siBool, False, None, None, False, False)
	prop.AddParameter3("RotLclX", c.siBool, False, None, None, False, False)
	prop.AddParameter3("RotLclY", c.siBool, False, None, None, False, False)
	prop.AddParameter3("RotLclZ", c.siBool, False, None, None, False, False)
	prop.AddParameter3("RotGlbX", c.siBool, False, None, None, False, False)
	prop.AddParameter3("RotGlbY", c.siBool, False, None, None, False, False)
	prop.AddParameter3("RotGlbZ", c.siBool, False, None, None, False, False)
	
	prop.AddParameter3("Translation", c.siBool, False, None, None, False, False)
	prop.AddParameter3("PosLclX", c.siBool, False, None, None, False, False)
	prop.AddParameter3("PosLclY", c.siBool, False, None, None, False, False)
	prop.AddParameter3("PosLclZ", c.siBool, False, None, None, False, False)
	prop.AddParameter3("PosGlbX", c.siBool, False, None, None, False, False)
	prop.AddParameter3("PosGlbY", c.siBool, False, None, None, False, False)
	prop.AddParameter3("PosGlbZ", c.siBool, False, None, None, False, False)

	prop.AddParameter3("Custom", c.siString, '')


def zPlot_OnInit():
	ppg = PPG.Inspected(0)
	ppg = dispatch(ppg)
	lo = ppg.PPGLayout
	showRot = ppg.Rotation.Value
	showPos = ppg.Translation.Value
	showScl = ppg.Scale.Value
	zPlot_DrawLayout(lo, showRot=showRot, showPos=showPos, showScl=showScl)
	PPG.Refresh()
	
# def zPlot_DefineLayout(ctxt):
# 	lo = ctxt.Source
# 	zPlot_DrawLayout(lo)
	
def zPlot_DrawLayout(lo, showRot=False, showPos=False, showScl=False):
	lo.Clear()
	# lo.Delete()

	lo.AddGroup('Scale')
	lo.AddItem('Scale', 'Enable')
	if showScl:
		lo.AddGroup('Local')
		lo.AddRow()
		lo.AddItem('SclLclX', 'X')
		lo.AddItem('SclLclY', 'Y')
		lo.AddItem('SclLclZ', 'Z')
		lo.AddButton('ToggleAllLclScl', 'All')
		lo.EndRow()
		lo.EndGroup()
		lo.AddGroup('Global')
		lo.AddRow()
		lo.AddItem('SclGlbX', 'X')
		lo.AddItem('SclGlbY', 'Y')
		lo.AddItem('SclGlbZ', 'Z')
		lo.AddButton('ToggleAllGlbScl', 'All')
		lo.EndRow()
		lo.EndGroup()
	lo.EndGroup()

	lo.AddGroup('Rotation')
	lo.AddItem('Rotation', 'Enable')
	if showRot:
		lo.AddGroup('Local')
		lo.AddRow()
		lo.AddItem('RotLclX', 'X')
		lo.AddItem('RotLclY', 'Y')
		lo.AddItem('RotLclZ', 'Z')
		lo.AddButton('ToggleAllLclRot', 'All')
		lo.EndRow()
		lo.EndGroup()
		lo.AddGroup('Global')
		lo.AddRow()
		lo.AddItem('RotGlbX', 'X')
		lo.AddItem('RotGlbY', 'Y')
		lo.AddItem('RotGlbZ', 'Z')
		lo.AddButton('ToggleAllGlbRot', 'All')
		lo.EndRow()
		lo.EndGroup()
	lo.EndGroup()

	lo.AddGroup('Translation')
	lo.AddItem('Translation', 'Enable')
	if showPos:
		lo.AddGroup('Local')
		lo.AddRow()
		lo.AddItem('PosLclX', 'X')
		lo.AddItem('PosLclY', 'Y')
		lo.AddItem('PosLclZ', 'Z')
		lo.AddButton('ToggleAllLclPos', 'All')
		lo.EndRow()
		lo.EndGroup()
		lo.AddGroup('Global')
		lo.AddRow()
		lo.AddItem('PosGlbX', 'X')
		lo.AddItem('PosGlbY', 'Y')
		lo.AddItem('PosGlbZ', 'Z')
		lo.AddButton('ToggleAllGlbPos', 'All')
		lo.EndRow()
		lo.EndGroup()
	lo.EndGroup()
	
	lo.AddItem('Custom')

def zPlot_ToggleAllLclPos_OnClicked():
	ppg = PPG.Inspected(0)
	ppg = dispatch(ppg)

	ppg.PosLclX.Value = 1-ppg.PosLclX.Value
	ppg.PosLclY.Value = 1-ppg.PosLclY.Value
	ppg.PosLclZ.Value = 1-ppg.PosLclZ.Value

def zPlot_ToggleAllGlbPos_OnClicked():
	ppg = PPG.Inspected(0)
	ppg = dispatch(ppg)

	ppg.PosGlbX.Value = 1-ppg.PosGlbX.Value
	ppg.PosGlbY.Value = 1-ppg.PosGlbY.Value
	ppg.PosGlbZ.Value = 1-ppg.PosGlbZ.Value
	
def zPlot_ToggleAllLclRot_OnClicked():
	ppg = PPG.Inspected(0)
	ppg = dispatch(ppg)

	ppg.RotLclX.Value = 1-ppg.RotLclX.Value
	ppg.RotLclY.Value = 1-ppg.RotLclY.Value
	ppg.RotLclZ.Value = 1-ppg.RotLclZ.Value

def zPlot_ToggleAllGlbRot_OnClicked():
	ppg = PPG.Inspected(0)
	ppg = dispatch(ppg)

	ppg.RotGlbX.Value = 1-ppg.RotGlbX.Value
	ppg.RotGlbY.Value = 1-ppg.RotGlbY.Value
	ppg.RotGlbZ.Value = 1-ppg.RotGlbZ.Value
	
def zPlot_ToggleAllLclScl_OnClicked():
	ppg = PPG.Inspected(0)
	ppg = dispatch(ppg)

	ppg.SclLclX.Value = 1-ppg.SclLclX.Value
	ppg.SclLclY.Value = 1-ppg.SclLclY.Value
	ppg.SclLclZ.Value = 1-ppg.SclLclZ.Value

def zPlot_ToggleAllGlbScl_OnClicked():
	ppg = PPG.Inspected(0)
	ppg = dispatch(ppg)

	ppg.SclGlbX.Value = 1-ppg.SclGlbX.Value
	ppg.SclGlbY.Value = 1-ppg.SclGlbY.Value
	ppg.SclGlbZ.Value = 1-ppg.SclGlbZ.Value
	
def zPlot_Scale_OnChanged():
	ppg = PPG.Inspected(0)
	ppg = dispatch(ppg)
	
	# if not ppg.Scale.Value:
	# 	ppg.SclLclX.ReadOnly = True
	# 	ppg.SclLclY.ReadOnly = True
	# 	ppg.SclLclZ.ReadOnly = True
	# 	
	# 	ppg.SclGlbX.ReadOnly = True
	# 	ppg.SclGlbY.ReadOnly = True
	# 	ppg.SclGlbZ.ReadOnly = True
	# 	
	# else:
	# 	ppg.SclLclX.ReadOnly = False
	# 	ppg.SclLclY.ReadOnly = False
	# 	ppg.SclLclZ.ReadOnly = False
	# 	
	# 	ppg.SclGlbX.ReadOnly = False
	# 	ppg.SclGlbY.ReadOnly = False
	# 	ppg.SclGlbZ.ReadOnly = False
	
	# draw the layout #
	zPlot_DrawLayout(
		ppg.PPGLayout, 
		showPos=ppg.Translation.Value, 
		showRot=ppg.Rotation.Value, 
		showScl=ppg.Scale.Value
	)
	PPG.Refresh()

def zPlot_Rotation_OnChanged():
	ppg = PPG.Inspected(0)
	ppg = dispatch(ppg)
	
	# if not ppg.Rotation.Value:
	# 	ppg.RotLclX.ReadOnly = True
	# 	ppg.RotLclY.ReadOnly = True
	# 	ppg.RotLclZ.ReadOnly = True
	# 	
	# 	ppg.RotGlbX.ReadOnly = True
	# 	ppg.RotGlbY.ReadOnly = True
	# 	ppg.RotGlbZ.ReadOnly = True
	# else:
	# 	ppg.RotLclX.ReadOnly = False
	# 	ppg.RotLclY.ReadOnly = False
	# 	ppg.RotLclZ.ReadOnly = False
	# 	
	# 	ppg.RotGlbX.ReadOnly = False
	# 	ppg.RotGlbY.ReadOnly = False
	# 	ppg.RotGlbZ.ReadOnly = False

	# draw the layout #
	zPlot_DrawLayout(
		ppg.PPGLayout, 
		showPos=ppg.Translation.Value, 
		showRot=ppg.Rotation.Value, 
		showScl=ppg.Scale.Value
	)
	PPG.Refresh()

def zPlot_Translation_OnChanged():
	ppg = PPG.Inspected(0)
	ppg = dispatch(ppg)
	
	# if not ppg.Translation.Value:
	# 	ppg.PosLclX.ReadOnly = True
	# 	ppg.PosLclY.ReadOnly = True
	# 	ppg.PosLclZ.ReadOnly = True
	# 	
	# 	ppg.PosGlbX.ReadOnly = True
	# 	ppg.PosGlbY.ReadOnly = True
	# 	ppg.PosGlbZ.ReadOnly = True
	# else:
	# 	ppg.PosLclX.ReadOnly = False
	# 	ppg.PosLclY.ReadOnly = False
	# 	ppg.PosLclZ.ReadOnly = False
	# 	
	# 	ppg.PosGlbX.ReadOnly = False
	# 	ppg.PosGlbY.ReadOnly = False
	# 	ppg.PosGlbZ.ReadOnly = False

	# draw the layout #
	zPlot_DrawLayout(
		ppg.PPGLayout, 
		showPos=ppg.Translation.Value, 
		showRot=ppg.Rotation.Value, 
		showScl=ppg.Scale.Value
	)
	PPG.Refresh()	
	
#-----------------------------------------------------------------------------
# Filter
#-----------------------------------------------------------------------------
def zPlot_Nodes_Match(ctxt):
	# get the object from the input context $
	obj = ctxt.GetAttribute('Input')
	# skip if the item doesn't have a zPlot prop #
	if not obj.Properties('zPlot'): return False
	# return the obj #
	return True


#-----------------------------------------------------------------------------
# Commands
#-----------------------------------------------------------------------------
def zGetPlotString_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	#oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments
	oArgs.AddObjectArgument('model')
	oArgs.Add('includeModelName', c.siArgumentInput, False, c.siBool)

	return True
	
def zGetPlotString_Execute(model, includeModelName):

	# make sure we have a model #
	if not model.type == '#model':
		log('Input argument "%s" is not of type "#model".' % model.FullName, c.siError)
		return False
	# get the filter #
	fltr = xsi.Filters('zPlot_Nodes')
	# get all the items under the model #
	nodes = model.FindChildren('*')
	# filter out the plot nodes #
	plotNodes = fltr.Subset(nodes)
	
	# step through the nodes and get the parameters #
	out = ''
	for node in plotNodes:
		# get the node name #
		nodeName = node.Name
		if includeModelName:
			nodeName = node.FullName
		# get the property #
		prop = dispatch(node.Properties('zPlot'))
		# check trans #
		if prop.Translation.Value:
			if prop.PosLclX.Value: out += '%s.kine.local.posx,' % nodeName
			if prop.PosLclY.Value: out += '%s.kine.local.posy,' % nodeName
			if prop.PosLclZ.Value: out += '%s.kine.local.posz,' % nodeName

			if prop.PosGlbX.Value: out += '%s.kine.global.posx,' % nodeName
			if prop.PosGlbY.Value: out += '%s.kine.global.posy,' % nodeName
			if prop.PosGlbZ.Value: out += '%s.kine.global.posz,' % nodeName
	
		# check rot #
		if prop.Rotation.Value:
			if prop.RotLclX.Value: out += '%s.kine.local.rotx,' % nodeName
			if prop.RotLclY.Value: out += '%s.kine.local.roty,' % nodeName
			if prop.RotLclZ.Value: out += '%s.kine.local.rotz,' % nodeName

			if prop.RotGlbX.Value: out += '%s.kine.global.rotx,' % nodeName
			if prop.RotGlbY.Value: out += '%s.kine.global.roty,' % nodeName
			if prop.RotGlbZ.Value: out += '%s.kine.global.rotz,' % nodeName
	
		# check scale #
		if prop.Scale.Value:
			if prop.SclLclX.Value: out += '%s.kine.local.sclx,' % nodeName
			if prop.SclLclY.Value: out += '%s.kine.local.scly,' % nodeName
			if prop.SclLclZ.Value: out += '%s.kine.local.sclz,' % nodeName

			if prop.SclGlbX.Value: out += '%s.kine.global.sclx,' % nodeName
			if prop.SclGlbY.Value: out += '%s.kine.global.scly,' % nodeName
			if prop.SclGlbZ.Value: out += '%s.kine.global.sclz,' % nodeName
			
		# get the custom field #
		custom = prop.Custom.Value
		if len(custom):
			out += '%s,' % custom
	
	# return the out string #
	if len(out):
		if out[-1] == ',': 
			return out[:-1]
		else:
			return out

#--------------------------------------------------------
	
def zPlotMocapToFile_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	#oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments
	oArgs.AddObjectArgument('model')
	oArgs.Add('filename', c.siArgumentInput, '', c.siString)
	oArgs.Add('actionName', c.siArgumentInput, 'zPlottedAction', c.siString)
	oArgs.Add('start', c.siArgumentInput, 1, c.siUInt2)
	oArgs.Add('end', c.siArgumentInput, 100, c.siUInt2)
	oArgs.Add('step', c.siArgumentInput, 1, c.siUInt2)

	return True
	
def zPlotMocapToFile_Execute(model, filename, actionName, start, end, step):
	# make sure we got a model #
	if not model.type == '#model':
		log('Input argument "%s" is not of type "#model".' % model.FullName, c.siError)
		return False
	# get the plot string #
	plotString = xsi.zGetPlotString(model, True)
	# plot it 
	log(model.Name)
	log(plotString)
	source = xsi.PlotToAction(
		model.Name, 
		plotString, 
		actionName, 
		start, 
		end, 
		step,
		30, 
		2, 
		False, 
		0.01, 
		True
	)
	# set the output type #
	source.storage = 3
	# set the output name #
	if not filename[-5:] == '.eani':
		filename += '.eani'
	source.filename = filename
	# export the file
	source.Offload()
#--------------------------------------------------------

def zAddPlotTags_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	#oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments
	oArgs.AddWithHandler('items', c.siArgHandlerCollection)
	oArgs.Add('show', c.siArgumentInput, True, c.siBool)

	return True
	
def zAddPlotTags_Execute(items, show):
	# track the properties #
	col = dispatch('XSI.Collection')
	# step through the items #
	for item in items:
		log(item)
		# add the property #
		prop = item.AddProperty('zPlot')
		# add it to the collection #
		col.Add(prop)
	# inspect the collection #
	if show:
		xsi.InspectObj(col, None, None, c.siFollow)
		
#--------------------------------------------------------
		
def zAddPlotTagsLocalPosRot_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	#oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments
	oArgs.AddWithHandler('items', c.siArgHandlerCollection)
	oArgs.Add('show', c.siArgumentInput, True, c.siBool)

	return True
	
def zAddPlotTagsLocalPosRot_Execute(items, show):
	# track the properties #
	col = dispatch('XSI.Collection')
	# step through the items #
	for item in items:
		# add the property #
		prop = item.AddProperty('zPlot')
		prop = dispatch(prop)
		# check the local pos and rots #
		prop.Rotation.Value = True
		prop.RotLclX.Value = True
		prop.RotLclY.Value = True
		prop.RotLclZ.Value = True
		prop.Translation.Value = True
		prop.PosLclX.Value = True
		prop.PosLclY.Value = True
		prop.PosLclZ.Value = True
		# add it to the collection #
		col.Add(prop)
	# inspect the collection #
	if show:
		xsi.InspectObj(col, None, None, c.siFollow)
		
#--------------------------------------------------------

def zAddPlotTagsLocalRot_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	#oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments
	oArgs.AddWithHandler('items', c.siArgHandlerCollection)
	oArgs.Add('show', c.siArgumentInput, True, c.siBool)

	return True
	
def zAddPlotTagsLocalRot_Execute(items, show):
	# track the properties #
	col = dispatch('XSI.Collection')
	# step through the items #
	for item in items:
		# add the property #
		prop = item.AddProperty('zPlot')
		prop = dispatch(prop)
		# check the local pos and rots #
		prop.Rotation.Value = True
		prop.RotLclX.Value = True
		prop.RotLclY.Value = True
		prop.RotLclZ.Value = True
		# add it to the collection #
		col.Add(prop)
	# inspect the collection #
	if show:
		xsi.InspectObj(col, None, None, c.siFollow)
		
#--------------------------------------------------------
