"""
zPoser.py

Requires environment variable "ZPOSER_PATH".
Requires elementtree: http://effbot.org/zone/element-index.htm

Created by Andy Buecker on 2008-04-09.
Copyright (c) 2008 Zoogloo LLC. All rights reserved.
"""

__version__ = '$Revision: 12 $'
__author__  = '$Author: andy $'
__date__    = '$Date: 2008-07-21 16:02 -0700 $'

import win32com.client
from win32com.client import constants
from win32com.client import constants as c
from win32com.client import Dispatch as dispatch
import xml.dom.minidom as dom
import os
import time
import re

xsi = Application
log = xsi.logmessage

null = None
false = 0
true = 1

class zTailError(Exception): pass

def XSILoadPlugin(in_reg):
	in_reg.Author = 'Andy Buecker'
	in_reg.Name = "zPoser"
	in_reg.Email = ""
	in_reg.URL = ""
	try:
		in_reg.Major = int(__version__.split(' ')[1])
	except:
		in_reg.Major = 1
	in_reg.Minor = 0

	in_reg.RegisterProperty('zPoserSaveGUI')
	in_reg.RegisterProperty('zPoserLoadGUI')
	in_reg.RegisterProperty('zLoadCharacterPoseGUI')
	in_reg.RegisterProperty('zSaveCharacterPoseGUI')
	
	in_reg.RegisterCommand("zPoserLoadGUI")
	in_reg.RegisterCommand("zPoserSaveGUI")
	in_reg.RegisterCommand("zPoserSave")
	in_reg.RegisterCommand("zPoserLoad")

	in_reg.RegisterCommand("zSaveCharacterPose")
	in_reg.RegisterCommand("zSaveCharacterPoseGUI")
	in_reg.RegisterCommand("zLoadCharacterPose")
	in_reg.RegisterCommand("zLoadCharacterPoseGUI")
	
	in_reg.RegisterMenu(c.siMenuTbAnimateActionsStoreID, 'zPoserSaveMenu', False)
	in_reg.RegisterMenu(c.siMenuTbAnimateActionsApplyID, 'zPoserLoadMenu', False)

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
	
	
def zPoserSaveMenu_Init(ctxt):
	menu = ctxt.Source
	
	item = menu.AddCommandItem('zSaveCharacterPoseGUI', 'zSaveCharacterPoseGUI')
	item.Name = '(z) Save Character Pose'
	item = menu.AddCommandItem('zPoserSaveGUI', 'zPoserSaveGUI')
	item.Name = '(z) Save Pose (from Env)'
	
def zPoserLoadMenu_Init(ctxt):
	menu = ctxt.Source
	
	item = menu.AddCommandItem('zLoadCharacterPoseGUI', 'zLoadCharacterPoseGUI')
	item.Name = '(z) Load Character Pose'
	item = menu.AddCommandItem('zPoserLoadGUI', 'zPoserLoadGUI')
	item.Name = '(z) Load Pose (from Env)'
	
def zPoserSaveGUI_Define(ctxt):
	
	prop = ctxt.Source
	
	prop.AddParameter3("PosePath", c.siString, os.environ['ZPOSER_PATH'], 1, 20, False, True)
	prop.AddParameter3("PoseName", c.siString, '')

	prop.AddParameter3("CharacterSet", c.siBool, False)
	prop.AddParameter3("SetName", c.siString, '')

	prop.AddParameter3("Space", c.siString, 'Local')
	
	prop.AddParameter3("Scale", c.siBool, False, None, None, False, False)
	sx = prop.AddParameter3("SclX", c.siBool, True, None, None, False, True)
	sy = prop.AddParameter3("SclY", c.siBool, True, None, None, False, True)
	sz = prop.AddParameter3("SclZ", c.siBool, True, None, None, False, True)
	
	prop.AddParameter3("Rotation", c.siBool, False, None, None, False, False)
	rx = prop.AddParameter3("RotX", c.siBool, True, None, None, False, True)
	ry = prop.AddParameter3("RotY", c.siBool, True, None, None, False, True)
	rz = prop.AddParameter3("RotZ", c.siBool, True, None, None, False, True)
	
	prop.AddParameter3("Translation", c.siBool, False, None, None, False, False)
	tx = prop.AddParameter3("PosX", c.siBool, True, None, None, False, True)
	ty = prop.AddParameter3("PosY", c.siBool, True, None, None, False, True)
	tz = prop.AddParameter3("PosZ", c.siBool, True, None, None, False, True)
	
	prop.AddParameter3("Image", c.siString, '')
	
	return True

def zPoserSaveGUI_OnInit():
	prop = PPG.Inspected(0)
	node = prop.Parent3DObject
	
	# set the character set value if we don't have one #
	if not prop.SetName.Value:
		# step through all the models #
		for model in xsi.ActiveSceneRoot.Models:
			# step through all the properties #
			for prp in model.Properties:
				if prp.type == 'customparamset':
					import re
					if re.match(r'.*set.*', prp.Name, re.I):
						prop.SetName.Value = prp.FullName
	
def zPoserSaveGUI_DefineLayout(ctxt):
	lo = ctxt.Source
	zPoserGUI_DrawLayout(lo)
	
def zPoserGUI_DrawLayout(lo, showRot=False, showPos=False, showScl=False):
	lo.Clear()

	lo.AddGroup('Zoogloo - Save Pose')

	lo.AddGroup('Location')
	lo.AddItem('PoseName', 'Pose Name')
	lo.AddStaticText('Note:\r\nPoses can have a relaitve path before the name:\r\n  Char/Part/PoseName')
	lo.EndGroup()
	
	lo.AddGroup('Sets')
	lo.AddItem('CharacterSet', 'Use Character Set')
	lo.AddRow()
	lo.AddItem('SetName', 'SetName')
	lo.AddButton('PickSet', 'Pick')
	lo.EndRow()
	lo.EndGroup()
	
	lo.AddGroup('Channels')

	lo.AddEnumControl('Space', ['Local', 'kine.local', 'Global', 'kine.global'], 'Coordinate Space')
	
	lo.AddGroup('Scale')
	lo.AddItem('Scale')
	if showScl:
		lo.AddRow()
		lo.AddItem('SclX', 'X')
		lo.AddItem('SclY', 'Y')
		lo.AddItem('SclZ', 'Z')
		lo.EndRow()
	lo.EndGroup()

	lo.AddGroup('Rotation')
	lo.AddItem('Rotation')
	if showRot:
		log('ShowRot')
		lo.AddRow()
		lo.AddItem('RotX', 'X')
		lo.AddItem('RotY', 'Y')
		lo.AddItem('RotZ', 'Z')
		lo.EndRow()
	lo.EndGroup()

	lo.AddGroup('Translation')
	lo.AddItem('Translation')
	if showPos:
		lo.AddRow()
		lo.AddItem('PosX', 'X')
		lo.AddItem('PosY', 'Y')
		lo.AddItem('PosZ', 'Z')
		lo.EndRow()
	lo.EndGroup()
	
	lo.EndGroup()
	
	lo.AddGroup('Reference Image (optional)')
	lo.AddRow()
	lo.AddItem('Image', 'Image Location')
	lo.AddButton('PickImage', '...')
	lo.EndRow()
	lo.EndGroup()
	
	lo.EndGroup()

	lo.AddGroup('Output Path')
	item = lo.AddItem('PosePath')
	item.SetAttribute(c.siUINoLabel, True)
	lo.AddStaticText('Note:\r\n  The output path is set with \r\n  environment variable:  ZPOSER_PATH')
	lo.EndGroup()

	lo.AddRow()
	lo.AddButton('Close', 'Close Window')
	lo.AddSpacer()
	lo.AddButton('Save', 'Save Pose')
	lo.EndRow()

def zPoserSaveGUI_PickSet_OnClicked():
	prop = PPG.Inspected(0)
	prop = dispatch(prop)
	
	picker = xsi.PickElement(c.siPropertyFilter, 'Pick Character Set')
	if not picker[0]:
		log('Cancelled.')
		return False
	
	# set the value #
	prop.SetName.Value = picker[2].FullName

def zPoserSaveGUI_Scale_OnChanged():
	ppg = PPG.Inspected(0)
	ppg = dispatch(ppg)
	
	if not ppg.Scale.Value:
		ppg.SclX.ReadOnly = True
		ppg.SclY.ReadOnly = True
		ppg.SclZ.ReadOnly = True
		
	else:
		ppg.SclX.ReadOnly = False
		ppg.SclY.ReadOnly = False
		ppg.SclZ.ReadOnly = False
	
	# draw the layout #
	zPoserGUI_DrawLayout(
		ppg.PPGLayout, 
		showPos=ppg.Translation.Value, 
		showRot=ppg.Rotation.Value, 
		showScl=ppg.Scale.Value
	)
	PPG.Refresh()

def zPoserSaveGUI_Rotation_OnChanged():
	ppg = PPG.Inspected(0)
	ppg = dispatch(ppg)
	
	if not ppg.Rotation.Value:
		ppg.RotX.ReadOnly = True
		ppg.RotY.ReadOnly = True
		ppg.RotZ.ReadOnly = True
	else:
		ppg.RotX.ReadOnly = False
		ppg.RotY.ReadOnly = False
		ppg.RotZ.ReadOnly = False

	# draw the layout #
	zPoserGUI_DrawLayout(
		ppg.PPGLayout, 
		showPos=ppg.Translation.Value, 
		showRot=ppg.Rotation.Value, 
		showScl=ppg.Scale.Value
	)
	PPG.Refresh()

def zPoserSaveGUI_Translation_OnChanged():
	ppg = PPG.Inspected(0)
	ppg = dispatch(ppg)
	
	if not ppg.Translation.Value:
		ppg.PosX.ReadOnly = True
		ppg.PosY.ReadOnly = True
		ppg.PosZ.ReadOnly = True
	else:
		ppg.PosX.ReadOnly = False
		ppg.PosY.ReadOnly = False
		ppg.PosZ.ReadOnly = False

	# draw the layout #
	zPoserGUI_DrawLayout(
		ppg.PPGLayout, 
		showPos=ppg.Translation.Value, 
		showRot=ppg.Rotation.Value, 
		showScl=ppg.Scale.Value
	)
	PPG.Refresh()

def zPoserSaveGUI_Close_OnClicked():
	PPG.Close()

def zPoserSaveGUI_Save_OnClicked():
	ppg = PPG.Inspected(0)
	
	# save #
	xsi.zPoserSave()
	
	# clear the name #
	ppg.PoseName.Value = ''
	
def zPoserSaveGUI_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	# oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments

	return True

def zPoserSaveGUI_Execute():
	# get the ui #
	prop = xsi.ActiveSceneRoot.Properties('zPoserSaveGUI')
	if not prop:
		prop = xsi.ActiveSceneRoot.AddProperty('zPoserSaveGUI')
	# display the property #
	xsi.Inspectobj(prop, '', None, c.siLock)

#-----------------------------------------------------------------------------

def zSaveCharacterPoseGUI_Define(ctxt):
	
	prop = ctxt.Source
	
	prop.AddParameter3("PosePath", c.siString, xsi.ActiveProject.Path)
	prop.AddParameter3("PoseName", c.siString, '')

	prop.AddParameter3("CharacterSet", c.siString, '')
	
	prop.AddParameter3("Overwrite", c.siBool, False)

	return True

def zSaveCharacterPoseGUI_OnInit():
	prop = PPG.Inspected(0)
	node = prop.Parent3DObject
	
	# set the character set value if we don't have one #
	if not prop.CharacterSet.Value:
		# step through all the models #
		for model in xsi.ActiveSceneRoot.Models:
			# step through all the properties #
			for prp in model.Properties:
				if prp.type == 'customparamset':
					import re
					if re.match(r'.*set.*', prp.Name, re.I):
						prop.CharacterSet.Value = prp.FullName
	
def zSaveCharacterPoseGUI_DefineLayout(ctxt):
	lo = ctxt.Source
	lo.Clear()

	lo.AddGroup('Zoogloo - Save Character Pose')

	lo.AddGroup('Location')
	lo.AddItem('PoseName', 'Pose Name')
	lo.AddRow()
	lo.AddItem('PosePath', 'Pose Path')
	lo.AddButton('PickPath', '...')
	lo.EndRow()
	lo.EndGroup()
	
	lo.AddGroup('Sets')
	lo.AddRow()
	lo.AddItem('CharacterSet', 'Character Set')
	lo.AddButton('PickSet', 'Pick')
	lo.EndRow()
	lo.EndGroup()
	
	lo.AddGroup('Options')
	lo.AddItem('Overwrite')
	lo.EndGroup()
	
	lo.AddRow()
	lo.AddButton('Close', 'Close Window')
	lo.AddSpacer()
	lo.AddButton('Save', 'Save Pose')
	lo.EndRow()

def zSaveCharacterPoseGUI_PickPath_OnClicked():
	# get the ppg #
	prop = PPG.Inspected(0)
	prop = dispatch(prop)

	# get the current path #
	path_current = xsi.ActiveProject.Path
	if prop.PosePath.Value:
		path_current = prop.PosePath.Value 
	
	# folder picker #
	folder = XSIUIToolkit.PickFolder(path_current, 'Pick Output folder...')
	if folder:
		prop.PosePath.Value = folder
		
def zSaveCharacterPoseGUI_PickSet_OnClicked():
	prop = PPG.Inspected(0)
	prop = dispatch(prop)
	
	picker = xsi.PickElement(c.siPropertyFilter, 'Pick Character Set')
	if not picker[0]:
		log('Cancelled.')
		return False
	
	# set the value #
	prop.CharacterSet.Value = picker[2].FullName

def zSaveCharacterPoseGUI_Close_OnClicked():
	PPG.Close()

def zSaveCharacterPoseGUI_Save_OnClicked():
	prop = PPG.Inspected(0)
	
	# save #
	xsi.zSaveCharacterPose(
		prop.CharacterSet.Value, 
		prop.PosePath.Value + os.sep + prop.PoseName.Value, 
		prop.Overwrite.Value
	)
	
	# clear the name #
	prop.PoseName.Value = ''
	
def zSaveCharacterPoseGUI_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	# oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments

	return True

def zSaveCharacterPoseGUI_Execute():
	# get the ui #
	prop = xsi.ActiveSceneRoot.Properties('zSaveCharacterPoseGUI')
	if not prop:
		prop = xsi.ActiveSceneRoot.AddProperty('zSaveCharacterPoseGUI')
	# display the property #
	xsi.Inspectobj(prop, '', None, c.siLock)

#-----------------------------------------------------------------------------

def zLoadCharacterPose_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	# oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments
	oArgs.AddObjectArgument('model')
	oArgs.Add('path_pose', c.siArgumentInput, 'zPose', c.siString)

	return True

def zLoadCharacterPose_Execute(model, path_pose):

	# get the model #
	if not model:
		model = xsi.ActiveSceneRoot
	elif xsi.ClassName(model) == 'X3DObject':
		model = model.model
	elif model.type != '#model':
		log('Unrecognized model argument: %s' % model, c.siError)
		return False
	
	# read in the xml file #
	xml = dom.parse(path_pose)
	doc = xml.documentElement
	objects = xml.getElementsByTagName('object')
	for obj in objects:

		# get the object #
		nodeName = obj.getAttribute('name')
		node = model.FindChild(nodeName)
		if not node:
			log('Unable to locate node: %s.%s' % (model.Name, nodeName), c.siWarning)
			continue

		# step through the channels #
		channels = obj.getElementsByTagName('channel')
		for chnl in channels:
			if re.match( 'kine.local', chnl.getAttribute('owner'), re.I):
				node.Kinematics.Local.Parameters(chnl.getAttribute('name')).Value = \
					float(chnl.getAttribute('value'))
			elif re.match( 'kine.global', chnl.getAttribute('owner'), re.I):
				node.Kinematics.Global.Parameters(chnl.getAttribute('name')).Value = \
					float(chnl.getAttribute('value'))
			else:
				# cast the proper value #
				value = None
				try:
					value = float(chnl.getAttribute('value'))
				except:
					if chnl.getAttribute('value') == 'False':
						value = False
					elif chnl.getAttribute('value') == 'True':
						value = True
					else:
						value = chnl.getAttribute('value')
				
				# set the value #
				try:
					xsi.SetValue('%s.%s.%s' % \
						(
							node.FullName, 
							chnl.getAttribute('owner'), 
							chnl.getAttribute('name')
						),
						value
					)
				except:
					log('Unable to set %s.%s.%s = %s' % \
						(
							node.FullName, 
							chnl.getAttribute('owner'), 
							chnl.getAttribute('name'),
							value
						),
						c.siError
					)

#-----------------------------------------------------------------------------

def zSaveCharacterPose_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	# oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments
	oArgs.AddObjectArgument('char_set')
	oArgs.Add('path_pose', c.siArgumentInput, 'zPose', c.siString)
	oArgs.Add('overwrite', c.siArgumentInput, False, c.siBool)

	return True

def zSaveCharacterPose_Execute(char_set, path_pose, overwrite):
	
	# make sure the path ends in ".zpose.xml"
	if not re.match(r'.+\.zpose\.xml$', path_pose, re.I):
		path_pose += '.zpose.xml'
	
	# if the pose exists, overwrite #	
	if os.path.exists(path_pose) and not overwrite:
		log('Pose "%s" all ready exists.  Enable the overwrite attribute to continue.' % path_pose, c.siError)
		return
		
	# build the path to the pose if it doesn't exist #
	name_only = os.path.basename(path_pose)
	path_only = os.path.dirname(path_pose)
	if not os.path.exists(path_only):
		log('Making directory: %s' % path_only)
		os.mkdir(path_only)

	# create an xml doc #
	impl = dom.getDOMImplementation()
	docType = impl.createDocumentType('zPoser', '-//Zoogloo LLC//zPoser//EN' , 'http://portal.zoogloo.net/dtds/zPoser.dtd')
	doc = impl.createDocument(None, "zPoser", None)
	top = doc.documentElement
	top.setAttribute('name', os.path.basename(name_only))
	top.setAttribute('date', time.asctime())
	
	# TODO: make sure we have a characters set #
	if char_set.Type != 'customparamset':
		log('Unable to verify %s as a character set.', c.siError)
		return False
	
	# process character set
	cset = char_set

	# step through the set #
	all_params = []
	def walkProp(Prop):
		# get the nested properties #
		nested = Prop.NestedObjects
		# skip if there is nothing there #
		if not nested.Count: return
		# step through the nested items #
		for item in nested:
			# catch the properties #
			if item.type == 'customparamset':
				prop = dispatch(item)
				log('SubSet: %s' % prop.FullName, c.siVerbose)
				# walk through the prop #
				walkProp(prop)
			else:
				# add to the keyable parameters list #
				all_params.append(item.MasterParameter)

	# walk the character set #
	walkProp(cset)
	log('Params in CharSet: %d' % len(all_params), c.siVerbose)
		
	# create a dictionary of objects #
	obj_dict = {}
	
	# step through the parameters #
	for param in all_params:
		# log('%s : %s' % (param.MasterParameter, param.Value))
		# master_param =  param.MasterParameter
		obj = param.Parent3DObject
		
		# see if the object exists in the ob dictionary #
		if not obj.Name in obj_dict.keys():
			
			# create an object item in the xml file #
			xml_obj = doc.createElement('object')
			top.appendChild(xml_obj)
			xml_obj.setAttribute('name', obj.Name)

			# add the xml to the object dictionary #
			obj_dict[obj.Name] = xml_obj
		
		# get the owner name #
		splits = param.FullName.split('.')[2:-1]
		owner = '.'.join(splits)
			
		# add the param #
		xml_obj = obj_dict.get(obj.Name)
		xml_chnl = doc.createElement('channel')
		xml_obj.appendChild(xml_chnl)
		xml_chnl.setAttribute('name', param.ScriptName)
		xml_chnl.setAttribute('owner', owner)
		xml_chnl.setAttribute('value', str(param.Value))
			
	# write it to disk #
	fh = open(path_pose, 'w')
	fh.write('<?xml version="1.0" encoding="utf-8"?>\n')
	docType.writexml(fh, indent='', addindent='\t', newl='\n')
	top.writexml(fh, indent='', addindent='\t', newl='\n')
	fh.close()
			
#-----------------------------------------------------------------------------

def zPoserSave_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	# oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments

	return True

def zPoserSave_Execute():
	
	# get the property #
	prop = xsi.ActiveSceneRoot.Properties('zPoserSaveGUI')
	if not prop:
		log('Uable to locate property "zPoserSaveGUI" on Scene_Root.', c.siError)
		return False

	# make sure we have a pose name #
	if not prop.PoseName.Value:
		log('Missing a pose name.', c.siError)
		return False

	# make sure the path exists
	if not os.path.exists(prop.PosePath.Value):
		log('Unable to find path: %s' % prop.PosePath.Value, c.siError)
		return False
		
	# replace all slashes in poseName to os specific slashes #	
	poseName = prop.PoseName.Value
	poseName = poseName.replace('\\', os.sep)
	poseName = poseName.replace('/', os.sep)
	
	# build the path to the pose if it doesn't exist #
	posePath = prop.PosePath.Value + os.sep + poseName + '.xml'
	poseDir = os.path.dirname(posePath)
	if not os.path.exists(poseDir):
		log('Making directory: %s' % poseDir)
		os.mkdir(poseDir)

	# create an xml doc #
	impl = dom.getDOMImplementation()
	docType = impl.createDocumentType('zPoser', '-//Zoogloo LLC//zPoser//EN' , 'http://portal.zoogloo.net/dtds/zPoser.dtd')
	doc = impl.createDocument(None, "zPoser", None)
	top = doc.documentElement
	top.setAttribute('name', os.path.basename(poseName))
	top.setAttribute('image', prop.Image.Value)
	top.setAttribute('date', time.asctime())
	
	# process character set
	if prop.CharacterSet.Value and prop.SetName.Value:
		
		# get the character set #
		col = dispatch('XSI.Collection')
		col.SetAsText(prop.SetName.Value)
		cset = col(0)

		# step through the set #
		all_params = []
		def walkProp(Prop):
			# get the nested properties #
			nested = Prop.NestedObjects
			# skip if there is nothing there #
			if not nested.Count: return
			# step through the nested items #
			for item in nested:
				# catch the properties #
				if item.type == 'customparamset':
					prop = dispatch(item)
					log('SubSet: %s' % prop.FullName, c.siVerbose)
					# walk through the prop #
					walkProp(prop)
				else:
					# add to the keyable parameters list #
					all_params.append(item.MasterParameter)

		# walk the character set #
		walkProp(cset)
		log('Params in CharSet: %d' % len(all_params), c.siVerbose)
			
		# create a dictionary of objects #
		obj_dict = {}
		
		# step through the parameters #
		for param in all_params:
			# log('%s : %s' % (param.MasterParameter, param.Value))
			# master_param =  param.MasterParameter
			obj = param.Parent3DObject
			
			# see if the object exists in the ob dictionary #
			if not obj.Name in obj_dict.keys():
				
				# create an object item in the xml file #
				xml_obj = doc.createElement('object')
				top.appendChild(xml_obj)
				xml_obj.setAttribute('name', obj.Name)

				# add the xml to the object dictionary #
				obj_dict[obj.Name] = xml_obj
			
			# get the owner name #
			splits = param.FullName.split('.')[2:-1]
			owner = '.'.join(splits)
				
			# add the param #
			xml_obj = obj_dict.get(obj.Name)
			xml_chnl = doc.createElement('channel')
			xml_obj.appendChild(xml_chnl)
			xml_chnl.setAttribute('name', param.ScriptName)
			xml_chnl.setAttribute('owner', owner)
			xml_chnl.setAttribute('value', str(param.Value))
			
	# store the other parameters #			
	if prop.Scale.Value or prop.Rotation.Value or prop.Translation.Value:
	
		# step through the objects #
		for item in xsi.selection:
		
			# create an object item in the xml file #
			obj = doc.createElement('object')
			top.appendChild(obj)
			obj.setAttribute('name', item.Name)

			# get the coordinate space #
			# owner = None
			# if prop.Space.Value == 'Local':
			# 	owner = 'kine.local'
			# elif prop.Space.Value == 'Global':
			# 	owner = 'kine.global'

			# get the owner name #
			splits = param.FullName.split('.')[2:-1]
			owner = '.'.join(splits)
				
			# step through the channels #
			if prop.Scale.Value:
				if prop.SclX.Value:
					chnl = doc.createElement('channel')
					obj.appendChild(chnl)
					chnl.setAttribute('owner', prop.Space.Value)
					chnl.setAttribute('name', 'sclx')
					chnl.setAttribute('value', str(space.sclx.Value))
				if prop.SclY.Value:
					chnl = doc.createElement('channel')
					obj.appendChild(chnl)
					chnl.setAttribute('owner', prop.Space.Value)
					chnl.setAttribute('name', 'scly')
					chnl.setAttribute('value', str(space.scly.Value))
				if prop.SclZ.Value:
					chnl = doc.createElement('channel')
					obj.appendChild(chnl)
					chnl.setAttribute('owner', prop.Space.Value)
					chnl.setAttribute('name', 'sclz')
					chnl.setAttribute('value', str(space.sclz.Value))
		
			if prop.Rotation.Value:
				if prop.RotX.Value:
					chnl = doc.createElement('channel')
					obj.appendChild(chnl)
					chnl.setAttribute('owner', prop.Space.Value)
					chnl.setAttribute('name', 'rotx')
					chnl.setAttribute('value', str(space.rotx.Value))
				if prop.RotY.Value:
					chnl = doc.createElement('channel')
					obj.appendChild(chnl)
					chnl.setAttribute('owner', prop.Space.Value)
					chnl.setAttribute('name', 'roty')
					chnl.setAttribute('value', str(space.roty.Value))
				if prop.RotZ.Value:
					chnl = doc.createElement('channel')
					obj.appendChild(chnl)
					chnl.setAttribute('owner', prop.Space.Value)
					chnl.setAttribute('name', 'rotz')
					chnl.setAttribute('value', str(space.rotz.Value))
		
			if prop.Translation.Value:
				if prop.PosX.Value:
					chnl = doc.createElement('channel')
					obj.appendChild(chnl)
					chnl.setAttribute('owner', prop.Space.Value)
					chnl.setAttribute('name', 'posx')
					chnl.setAttribute('value', str(space.posx.Value))
				if prop.PosY.Value:
					chnl = doc.createElement('channel')
					obj.appendChild(chnl)
					chnl.setAttribute('owner', prop.Space.Value)
					chnl.setAttribute('name', 'posy')
					chnl.setAttribute('value', str(space.posy.Value))
				if prop.PosZ.Value:
					chnl = doc.createElement('channel')
					obj.appendChild(chnl)
					chnl.setAttribute('owner', prop.Space.Value)
					chnl.setAttribute('name', 'posz')
					chnl.setAttribute('value', str(space.posz.Value))
		
	# write it to disk #
	fh = open(posePath, 'w')
	fh.write('<?xml version="1.0" encoding="utf-8"?>\n')
	docType.writexml(fh, indent='', addindent='\t', newl='\n')
	top.writexml(fh, indent='', addindent='\t', newl='\n')
	fh.close()

#-----------------------------------------------------------------------------

def zLoadCharacterPoseGUI_Define(ctxt):
	prop = ctxt.Source
	
	prop.AddParameter3("PosePath", c.siString, '')
	prop.AddParameter3("ModelName", c.siString, 'Scene_Root')
	prop.AddParameter3("PoseName", c.siString, '')

	
def zLoadCharacterPoseGUI_DefineLayout(ctxt):
	lo = ctxt.Source
	lo.Clear()

	lo.AddGroup('Zoogloo - Load Character Pose')

	lo.AddGroup('Location')
	lo.AddRow()
	lo.AddItem('PosePath', 'Pose Path')
	lo.AddButton('PickPath', '...')
	lo.EndRow()
	lo.AddRow()
	lo.AddItem('ModelName')
	lo.AddButton('UpdateModel', 'Update From Selection')
	lo.EndRow()
	lo.EndGroup()
	
	lo.AddRow()
	lo.AddButton('Close', 'Close Window')
	lo.AddSpacer()
	lo.AddButton('Load', 'Load Pose')
	lo.EndRow()

def zLoadCharacterPoseGUI_PickPath_OnClicked():
	# get the ppg #
	prop = PPG.Inspected(0)
	prop = dispatch(prop)

	# get the initial directories #
	init_dir	= xsi.ActiveProject.Path
	init_file	= ''
	if prop.PosePath.Value:
		init_dir  = os.path.dirname(prop.PosePath.Value)
		init_file = os.path.basename(prop.PosePath.Value)

	# get a file browser #
	fb = XSIUIToolkit.FileBrowser
	fb.DialogTitle 		= "Select the Pose (.zpose.xml)..."
	fb.InitialDirectory = init_dir
	fb.FileBaseName 	= init_file
	fb.Filter 			= "Zoogloo Pose Shape (*.xml)|*.xml|All Files (*.*)|*.*||"
	fb.ShowOpen()
	
	# get the filename #
	if not fb.FilePathName:
		return False
	
	# set the value #
	prop.PosePath.Value = fb.FilePathName
	
def zLoadCharacterPoseGUI_UpdateModel_OnClicked():
	ppg = PPG.Inspected(0)
	ppg = dispatch(ppg)
	
	# get the model from the selection #
	if not xsi.selection.Count:
		log('Nothing selected.', c.siError)
		return False
		
	if xsi.selection(0).type == '#model':
		ppg.ModelName.Value = xsi.selection(0).Name
	else:
		ppg.ModelName.Value = xsi.selection(0).Model.Name
		
def zLoadCharacterPoseGUI_Close_OnClicked():
	PPG.Close()

def zLoadCharacterPoseGUI_Load_OnClicked():
	ppg = PPG.Inspected(0)
	
	# get the model from the string #
	model = None
	if ppg.ModelName.Value == 'Scene_Root':
		model = xsi.ActiveSceneRoot
	else:
		model = xsi.ActiveSceneRoot.FindChild(ppg.ModelName.Value, c.siModelType)
		if not model:
			log('Unable to find model: %s' % ppg.ModelName.Value, c.siError)
			return False
			
	# load #
	xsi.zLoadCharacterPose(model, ppg.PosePath.Value)

def zLoadCharacterPoseGUI_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	# oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments

	return True
	
def zLoadCharacterPoseGUI_Execute():
	# get the ui #
	prop = xsi.ActiveSceneRoot.Properties('zLoadCharacterPoseGUI')
	if not prop:
		prop = xsi.ActiveSceneRoot.AddProperty('zLoadCharacterPoseGUI')
	# display the property #
	xsi.Inspectobj(prop, '', None, c.siLock)
		
#-----------------------------------------------------------------------------

def zPoserLoadGUI_Define(ctxt):
	prop = ctxt.Source
	
	prop.AddParameter3("PosePath", c.siString, os.environ['ZPOSER_PATH'], 1, 20, False, True)
	prop.AddParameter3("ModelName", c.siString, 'Scene_Root', 1, 20, False, True)
	prop.AddParameter3("PoseName", c.siString, '')

	
def zPoserLoadGUI_DefineLayout(ctxt):
	lo = ctxt.Source
	lo.Clear()

	lo.AddGroup('Zoogloo - Load Pose')

	lo.AddGroup('Location')
	lo.AddItem('PoseName', 'Pose Name')
	lo.AddRow()
	lo.AddItem('ModelName')
	lo.AddButton('UpdateModel', 'Update From Selection')
	lo.EndRow()
	lo.EndGroup()
	
	lo.EndGroup()
	
	lo.AddGroup('Input Path')
	item = lo.AddItem('PosePath')
	item.SetAttribute(c.siUINoLabel, True)
	lo.AddStaticText('Note:\r\n  The output path is set with \r\n  environment variable:  ZPOSER_PATH')
	lo.EndGroup()

	lo.AddRow()
	lo.AddButton('Close', 'Close Window')
	lo.AddSpacer()
	lo.AddButton('Load', 'Load Pose')
	lo.EndRow()


def zPoserLoadGUI_UpdateModel_OnClicked():
	ppg = PPG.Inspected(0)
	ppg = dispatch(ppg)
	
	# get the model from the selection #
	if not xsi.selection.Count:
		log('Nothing selected.', c.siError)
		return False
		
	if xsi.selection(0).type == '#model':
		ppg.ModelName.Value = xsi.selection(0).Name
	else:
		ppg.ModelName.Value = xsi.selection(0).Model.Name
		
def zPoserLoadGUI_Close_OnClicked():
	PPG.Close()

def zPoserLoadGUI_Load_OnClicked():
	ppg = PPG.Inspected(0)
	
	# get the model from the string #
	model = None
	if ppg.ModelName.Value == 'Scene_Root':
		model = xsi.ActiveSceneRoot
	else:
		model = xsi.ActiveSceneRoot.FindChild(ppg.ModelName.Value, c.siModelType)
		if not model:
			log('Unable to find model: %s' % ppg.ModelName.Value, c.siError)
			return False
			
	# load #
	xsi.zPoserLoad(ppg.PoseName.Value, model)

def zPoserLoadGUI_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	# oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments

	return True
	
def zPoserLoadGUI_Execute():
	# get the ui #
	prop = xsi.ActiveSceneRoot.Properties('zPoserLoadGUI')
	if not prop:
		prop = xsi.ActiveSceneRoot.AddProperty('zPoserLoadGUI')
	# display the property #
	xsi.Inspectobj(prop, '', None, c.siLock)
	
def zPoserLoad_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	# oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments
	oArgs.Add('poseName', c.siArgumentInput, '', c.siString)
	oArgs.AddObjectArgument('model')

	return True
	
def zPoserLoad_Execute(poseName, model):
	
	# get the environment variable #
	if not os.environ.has_key('ZPOSER_PATH'):
		log('Unable to find environment variable "ZPOSER_PATH".', c.siError)
		return False
	path = os.environ['ZPOSER_PATH']	
	
	# make sure the env path exists #
	if not os.path.exists(path):
		log('"ZPOSER_PATH" doesn\'t exist: %s' % path, c.siError)
		return False
	
	# replace all slashes in poseName to os specific slashes #	
	poseName = poseName.replace('\\', os.sep)
	poseName = poseName.replace('/', os.sep)
	
	# make sure the pose exists #
	posePath = path + os.sep + poseName + '.xml'
	if not os.path.exists(posePath):
		log('Unable to find pose "%s" in ZPOSER_PATH' % poseName, c.siError)
		return False
		
	# get the model #
	if not model:
		model = xsi.ActiveSceneRoot
	elif xsi.ClassName(model) == 'X3DObject':
		model = model.model
	elif model.type != '#model':
		log('Unrecognized model argument: %s' % model, c.siError)
		return False
	
	# read in the xml file #
	# fh = open(posePath, 'r')
	xml = dom.parse(posePath)
	doc = xml.documentElement
	objects = xml.getElementsByTagName('object')
	for obj in objects:

		# get the object #
		nodeName = obj.getAttribute('name')
		node = model.FindChild(nodeName)
		if not node:
			log('Unable to locate node: %s.%s' % (model.Name, nodeName), c.siWarning)
			continue

		# step through the channels #
		channels = obj.getElementsByTagName('channel')
		for chnl in channels:
			if re.match( 'kine.local', chnl.getAttribute('owner'), re.I):
				node.Kinematics.Local.Parameters(chnl.getAttribute('name')).Value = \
					float(chnl.getAttribute('value'))
			elif re.match( 'kine.global', chnl.getAttribute('owner'), re.I):
				node.Kinematics.Global.Parameters(chnl.getAttribute('name')).Value = \
					float(chnl.getAttribute('value'))
			else:
				# cast the proper value #
				value = None
				try:
					value = float(chnl.getAttribute('value'))
				except:
					if chnl.getAttribute('value') == 'False':
						value = False
					elif chnl.getAttribute('value') == 'True':
						value = True
					else:
						value = chnl.getAttribute('value')
				
				# set the value #
				try:
					xsi.SetValue('%s.%s.%s' % \
						(
							node.FullName, 
							chnl.getAttribute('owner'), 
							chnl.getAttribute('name')
						),
						value
					)
				except:
					log('Unable to set %s.%s.%s = %s' % \
						(
							node.FullName, 
							chnl.getAttribute('owner'), 
							chnl.getAttribute('name'),
							value
						),
						c.siError
					)


