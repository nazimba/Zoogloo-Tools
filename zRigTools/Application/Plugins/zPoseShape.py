"""
zPoseShapeTools.py
"""

__version__ = '$Revision: 11 $'
__author__  = '$Author: andy $'
__date__    = '$Date: 2008-07-21 15:20 -0700 $'

import win32com.client
from win32com.client import constants
from win32com.client import constants as c
from win32com.client.dynamic import Dispatch as dispatch
import xml.dom.minidom as dom
import time
import os
import re
import glob
import zipfile
import shutil

xsi = Application
log = xsi.logmessage

null = None
false = 0
true = 1

def XSILoadPlugin(in_reg):
	in_reg.Author = "Andy Buecker"
	in_reg.Name = "zPoseShape"
	in_reg.Email = "andy@zoogloo.net"
	in_reg.URL = ""
	try:
		in_reg.Major = int(__version__.split(' ')[1])
	except:
		in_reg.Major = 1
	in_reg.Minor = 0

	in_reg.RegisterProperty('zPoseShapeExportGUI')
	in_reg.RegisterProperty('zPoseShapeImportGUI')
	in_reg.RegisterProperty('zPoseShapeTransferGeoGUI')
	in_reg.RegisterProperty('zPoseShapeMirrorGUI')

	in_reg.RegisterCommand('zPoseShapeExport', 'zPoseShapeExport')
	in_reg.RegisterCommand('zPoseShapeExportGUI', 'zPoseShapeExportGUI')
	in_reg.RegisterCommand('zPoseShapeImport', 'zPoseShapeImport')
	in_reg.RegisterCommand('zPoseShapeImportGUI', 'zPoseShapeImportGUI')
	
	in_reg.RegisterCommand('zPoseShapeUpdateContents', 'zPoseShapeUpdateContents')
	in_reg.RegisterCommand('zPoseShapeImportDirectory', 'zPoseShapeImportDirectory')
	
	in_reg.RegisterCommand('zPoseShapeContents', 'zPoseShapeContents')

	in_reg.RegisterCommand('zPoseShapeDelete', 'zPoseShapeDelete')
	in_reg.RegisterCommand('zPoseShapeTransferGeo', 'zPoseShapeTransferGeo')
	in_reg.RegisterCommand('zPoseShapeTransferGeoGUI', 'zPoseShapeTransferGeoGUI')
	in_reg.RegisterCommand('zPoseShapeMirror', 'zPoseShapeMirror')
	in_reg.RegisterCommand('zPoseShapeMirrorGUI', 'zPoseShapeMirrorGUI')

	in_reg.RegisterMenu(c.siMenuTbAnimateDeformShapeID, 'zPoseShapeToolsMenu', False)
	
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
def zPoseShapeToolsMenu_Init(ctxt):
	menu = ctxt.Source
	
	item = menu.AddCommandItem('zPoseShapeImportGUI', 'zPoseShapeImportGUI')
	item.Name = '(z) PoseShape Import'
	item = menu.AddCommandItem('zPoseShapeExportGUI', 'zPoseShapeExportGUI')
	item.Name = '(z) PoseShape Export'
	item = menu.AddCommandItem('zPoseShapeTransferGeoGUI', 'zPoseShapeTransferGeoGUI')
	item.Name = '(z) PoseShape Transfer Geo'
	item = menu.AddCommandItem('zPoseShapeMirrorGUI', 'zPoseShapeMirrorGUI')
	item.Name = '(z) PoseShape Mirror'

#-----------------------------------------------------------------------------
# Properties
#-----------------------------------------------------------------------------
def zPoseShapeExportGUI_Define(ctxt):
	prop = ctxt.Source
	
	prop.AddParameter3("Path", c.siString, xsi.ActiveProject.Path)
	prop.AddParameter3("ShapeName", c.siString, '')
	prop.AddParameter3("Objects", c.siString, '')
	prop.AddParameter3("NodeReference", c.siString, '')
	prop.AddParameter3("Zip", c.siBool, True, None, None, False)
	prop.AddParameter3("Overwrite", c.siBool, True, None, None, False)

def zPoseShapeExportGUI_OnInit():
	prop = PPG.Inspected(0)
	
	# if no objects are in the property, update the object list #
	if not prop.Objects.Value and xsi.Selection.Count:
		prop.Objects.Value = xsi.Selection.GetAsText()
	
def zPoseShapeExportGUI_DefineLayout(ctxt):
	lo = ctxt.Source
	lo.Clear()

	lo.AddGroup('(z) PoseShape Export Menu')
	
	lo.AddGroup()
	lo.AddItem('ShapeName')
	lo.AddRow()
	lo.AddItem('Path')
	lo.AddButton('PickPath', 'Pick')
	lo.EndRow()
	lo.EndGroup()
	
	lo.AddGroup()
	lo.AddItem('Objects')
	lo.AddRow()
	lo.AddSpacer()
	lo.AddButton('Update', 'Use Selection')
	lo.EndRow()
	lo.AddItem('NodeReference', 'Reference Node')
	lo.AddRow()
	lo.AddSpacer()
	lo.AddButton('UpdateNode', 'Use Selection')
	lo.EndRow()
	lo.EndGroup()

	lo.AddGroup('Options')
	lo.AddItem('Overwrite')
	lo.AddItem('Zip')
	lo.EndGroup()

	lo.AddRow()
	lo.AddButton('Close', 'Close')
	lo.AddSpacer()
	lo.AddButton('Export', 'Export')
	lo.EndRow()
	
	lo.EndGroup()
	
def zPoseShapeExportGUI_Update_OnClicked():
	'''Updates the object list with the current selection'''
	prop = PPG.Inspected(0)
	if xsi.Selection.Count:
		prop.Objects.Value = xsi.Selection.GetAsText()
		
def zPoseShapeExportGUI_UpdateNode_OnClicked():
	'''Updates the object list with the current selection'''
	prop = PPG.Inspected(0)
	if xsi.Selection.Count:
		prop.NodeReference.Value = xsi.Selection(0)		
		
def zPoseShapeExportGUI_PickPath_OnClicked():
	# get the ppg #
	prop = PPG.Inspected(0)
	prop = dispatch(prop)

	# get the current path #
	path_current = xsi.ActiveProject.Path
	if prop.Path.Value:
		path_current = prop.Path.Value 
	
	# folder picker #
	folder = XSIUIToolkit.PickFolder(path_current, 'Pick folder for zPoseShape...')
	if folder:
		prop.Path.Value = folder
		
def zPoseShapeExportGUI_Export_OnClicked():
	'''Scrapes the info from the GUI and call zPoseShapeExport'''
	prop = PPG.Inspected(0)
	
	# make sure there is a shapename #
	if not prop.ShapeName.Value:
		log('No Shape Name specified.', c.siError)
		return False
		
	# make sure the path exists #
	if not prop.Path.Value:
		log('No Path specified.', c.siError)
		return False
		
	if not os.path.exists(prop.Path.Value):
		log('Path "%s" doesn\'t exist on disk.' % prop.Path.Value, c.siError)
		return False
		
	# build the shape path #
	filename = prop.Path.Value + os.sep + prop.ShapeName.Value
	
	# get the objects #
	objects = dispatch('XSI.Collection')
	objects.SetAsText(prop.Objects.Value)
	if not objects.Count:
		log('No objects selected.', c.siError)
		return False
	
	# write out the shape #
	xsi.zPoseShapeExport(objects, filename, prop.NodeReference.Value, prop.Overwrite.Value, prop.Zip.Value)
	
	# close the ppg #
	# PPG.Close()

def zPoseShapeExportGUI_Close_OnClicked():
	# close the ppg #
	PPG.Close()	
	

#-----------------------------------------------------------------------------

def zPoseShapeTransferGeoGUI_Define(ctxt):
	prop = ctxt.Source

	# model, dir_pose_shape, path_pose_rest, node_reference	
	prop.AddParameter3("OldModel", c.siString, '')
	prop.AddParameter3("NewModel", c.siString, '')
	prop.AddParameter3("OldPoseShape", c.siString, '')
	prop.AddParameter3("NewPoseShape", c.siString, '')
	prop.AddParameter3("ObjClusters", c.siBool, True, None, None, False)
	
def zPoseShapeTransferGeoGUI_DefineLayout(ctxt):
	lo = ctxt.Source
	lo.Clear()	

	lo.AddGroup('(z) PoseShape Transfer Geo Menu')
	
	lo.AddGroup('Old Pose Shape')

	lo.AddRow()
	lo.AddItem('OldPoseShape', "Old Pose Shape Path")
	lo.AddButton('PickOldPoseShape', 'Pick')
	lo.EndRow()

	lo.AddRow()
	lo.AddItem('OldModel', 'Old Model')
	lo.AddButton('OldModel', 'Use Selection')
	lo.EndRow()
	
	lo.AddGroup('Note:')
	lo.AddStaticText('The old model must work with the old pose shape.')
	lo.EndGroup()

	lo.EndGroup()
	

	lo.AddGroup('New Pose Shape')

	lo.AddRow()
	lo.AddItem('NewPoseShape', "New Pose Shape Path")
	lo.AddButton('PickNewPoseShape', 'Pick')
	lo.EndRow()

	lo.AddRow()
	lo.AddItem('NewModel', 'New Model')
	lo.AddButton('NewModel', 'Use Selection')
	lo.EndRow()

	lo.AddGroup('Note:')
	lo.AddStaticText('The new model has the geometry to transfer the old pose to.')
	lo.EndGroup()

	lo.EndGroup()
	
	lo.AddRow()
	lo.AddButton('Close', 'Close')
	lo.AddSpacer()
	lo.AddButton('Transfer', 'Transfer')
	lo.EndRow()
	
	lo.EndGroup()	
	
	lo.AddTab('Options')
	lo.AddGroup('Options')
	lo.AddItem('ObjClusters', 'Import Multiple Obj\'s as Clusters')
	lo.EndGroup()
	
	

def zPoseShapeTransferGeoGUI_PickOldPoseShape_OnClicked():
	# get the ppg #
	prop = PPG.Inspected(0)
	prop = dispatch(prop)

	# get the current path #
	path_current = xsi.ActiveProject.Path
	if prop.OldPoseShape.Value:
		path_current = prop.OldPoseShape.Value 
	
	# folder picker #
	folder = XSIUIToolkit.PickFolder(path_current, 'Pick zPoseShape (.zpshp) folder...')
	if folder:
		prop.OldPoseShape.Value = folder
		
def zPoseShapeTransferGeoGUI_PickNewPoseShape_OnClicked():
	# get the ppg #
	prop = PPG.Inspected(0)
	prop = dispatch(prop)

	# get the current path #
	path_current = xsi.ActiveProject.Path
	if prop.NewPoseShape.Value:
		path_current = prop.NewPoseShape.Value 
	
	# folder picker #
	folder = XSIUIToolkit.PickFolder(path_current, 'Pick zPoseShape (.zpshp) folder...')
	if folder:
		prop.NewPoseShape.Value = folder
		
def zPoseShapeTransferGeoGUI_OldModel_OnClicked():
	# get the ppg #
	prop = PPG.Inspected(0)
	prop = dispatch(prop)
	
	# get the model #
	if xsi.selection(0).Type == '#model':
		prop.OldModel.Value = xsi.selection(0)
	else:
		prop.OldModel.Value = xsi.selection(0).Model
	
def zPoseShapeTransferGeoGUI_NewModel_OnClicked():
	# get the ppg #
	prop = PPG.Inspected(0)
	prop = dispatch(prop)
	
	# get the model #
	if xsi.selection(0).Type == '#model':
		prop.NewModel.Value = xsi.selection(0)
	else:
		prop.NewModel.Value = xsi.selection(0).Model
	
def zPoseShapeTransferGeoGUI_Close_OnClicked():
	PPG.Close()
	
def zPoseShapeTransferGeoGUI_Transfer_OnClicked():
	# get the ppg #
	prop = PPG.Inspected(0)
	prop = dispatch(prop)
	
	# get the variables #
	new_model			= prop.NewModel.Value
	old_model			= prop.OldModel.Value
	dir_pose_shape		= prop.OldPoseShape.Value
	dir_new_shape		= prop.NewPoseShape.Value
	obj_cluster_mode	= int(prop.ObjClusters.Value)
	
	# import the obj #
	xsi.zPoseShapeTransferGeo(
		old_model, 
		new_model, 
		dir_pose_shape, 
		dir_new_shape, 
		obj_cluster_mode
	)
	
#-----------------------------------------------------------------------------

def zPoseShapeMirrorGUI_Define(ctxt):
	prop = ctxt.Source

	# model, dir_pose_shape, path_pose_rest, node_reference	
	prop.AddParameter3("TargetModel", c.siString, '')
	prop.AddParameter3("PoseShape", c.siString, '')
	prop.AddParameter3("NewPoseShape", c.siString, '')
	prop.AddParameter3("MirroredPose", c.siString, '')
	prop.AddParameter3("FromString", c.siString, '_L')
	prop.AddParameter3("ToString", c.siString, '_R')
	prop.AddParameter3("ObjClusters", c.siBool, True, None, None, False)
	
def zPoseShapeMirrorGUI_DefineLayout(ctxt):
	lo = ctxt.Source
	lo.Clear()	

	lo.AddGroup('(z) PoseShape Mirror Menu')
	
	lo.AddGroup('Pose Shape')

	lo.AddRow()
	lo.AddItem('PoseShape', "Pose Shape Path")
	lo.AddButton('PickPoseShape', 'Pick')
	lo.EndRow()

	lo.AddRow()
	lo.AddItem('NewPoseShape', "New Pose Shape Path")
	lo.AddButton('PickNewPoseShape', 'Pick')
	lo.EndRow()

	lo.AddRow()
	lo.AddItem('MirroredPose', "MirroredPose")
	lo.AddButton('PickMirrorPose', 'Pick')
	lo.EndRow()

	lo.AddRow()
	lo.AddItem('TargetModel', 'Model')
	lo.AddButton('UpdateModel', 'Use Selection')
	lo.EndRow()
	
	lo.EndGroup()
	
	lo.AddGroup('Symmetry String')
	lo.AddRow()
	lo.AddItem('FromString', 'From')
	lo.AddItem('ToString', 'To')
	lo.EndRow()
	lo.EndGroup()
	
	lo.AddRow()
	lo.AddButton('Close', 'Close')
	lo.AddSpacer()
	lo.AddButton('Mirror', 'Mirror')
	lo.EndRow()
	
	lo.EndGroup()	

	lo.AddTab('Options')
	lo.AddGroup('Options')
	lo.AddItem('ObjClusters', 'Import Multiple Obj\'s as Clusters')
	lo.EndGroup()
	
def zPoseShapeMirrorGUI_UpdateModel_OnClicked():
	# get the ppg #
	prop = PPG.Inspected(0)
	prop = dispatch(prop)
	
	# get the model #
	if xsi.selection(0).Type == '#model':
		prop.TargetModel.Value = xsi.selection(0)
	else:    
		prop.TargetModel.Value = xsi.selection(0).Model
	
def zPoseShapeMirrorGUI_PickPoseShape_OnClicked():
	# get the ppg #
	prop = PPG.Inspected(0)
	prop = dispatch(prop)

	# get the current path #
	path_current = xsi.ActiveProject.Path
	if prop.PoseShape.Value:
		path_current = prop.PoseShape.Value 
	
	# folder picker #
	folder = XSIUIToolkit.PickFolder(path_current, 'Pick zPoseShape (.zpshp) folder...')
	if folder:
		prop.PoseShape.Value = folder
		
def zPoseShapeMirrorGUI_PickNewPoseShape_OnClicked():
	# get the ppg #
	prop = PPG.Inspected(0)
	prop = dispatch(prop)

	# get the current path #
	path_current = xsi.ActiveProject.Path
	if prop.NewPoseShape.Value:
		path_current = prop.NewPoseShape.Value 
	
	# folder picker #
	folder = XSIUIToolkit.PickFolder(path_current, 'Pick zPoseShape (.zpshp) folder...')
	if folder:
		prop.NewPoseShape.Value = folder
		
def zPoseShapeMirrorGUI_PickMirrorPose_OnClicked():
	# get the ppg #
	prop = PPG.Inspected(0)
	prop = dispatch(prop)
	
	# get the initial directories #
	init_dir	= xsi.ActiveProject.Path
	init_file	= ''
	if prop.MirroredPose.Value:
		init_dir  = os.path.dirname(prop.MirroredPose.Value)
		init_file = os.path.basename(prop.MirroredPose.Value)

	# get a file browser #
	fb = XSIUIToolkit.FileBrowser
	fb.DialogTitle 		= "Select the Mirrored Pose..."
	fb.InitialDirectory = init_dir
	fb.FileBaseName 	= init_file
	fb.Filter 			= "Zoogloo Pose Shape (*.xml)|*.xml|All Files (*.*)|*.*||"
	fb.ShowOpen()
	
	# get the filename #
	if not fb.FilePathName:
		return False
	
	# set the value #
	prop.MirroredPose.Value = fb.FilePathName
	
def zPoseShapeMirrorGUI_Mirror_OnClicked():
	# get the ppg #
	prop = PPG.Inspected(0)
	prop = dispatch(prop)
	
	# get the variables #
	target_model		= prop.TargetModel.Value
	dir_pose_shape		= prop.PoseShape.Value
	dir_new_shape		= prop.NewPoseShape.Value
	mirror_pose			= prop.MirroredPose.Value
	from_string			= prop.FromString.Value
	to_string			= prop.ToString.Value
	obj_cluster_mode	= int(prop.ObjClusters.Value)
	
	# import the obj #
	xsi.zPoseShapeMirror(
		target_model,	
		dir_pose_shape,	
		dir_new_shape,	
		mirror_pose,		
		obj_cluster_mode
	)
	
#-----------------------------------------------------------------------------

def zPoseShapeImportGUI_Define(ctxt):
	prop = ctxt.Source

	# model, dir_pose_shape, path_pose_rest, node_reference	
	prop.AddParameter3("TargetModel", c.siString, '')
	prop.AddParameter3("PoseShape", c.siString, '')
	prop.AddParameter3("RestPose", c.siString, '')
	prop.AddParameter3("UseReferenceFromContents", c.siBool, True, None, None, False)
	prop.AddParameter3("NodeReference", c.siString, '', None, None, False, True)
	prop.AddParameter3("ObjClusters", c.siBool, True, None, None, False)
	
def zPoseShapeImportGUI_DefineLayout(ctxt):
	lo = ctxt.Source
	lo.Clear()	
	
	lo.AddGroup('(z) PoseShape Import Menu')
	
	lo.AddGroup('Pose Shape')

	lo.AddRow()
	lo.AddItem('PoseShape', "Pose Shape Path")
	lo.AddButton('PickPoseShape', 'Pick')
	lo.EndRow()

	lo.AddRow()
	lo.AddItem('RestPose', 'Rest Pose')
	lo.AddButton('PickRestPath', 'Pick')
	lo.EndRow()
	
	lo.AddRow()
	lo.AddItem('TargetModel', 'Model')
	lo.AddButton('UpdateModel', 'Use Selection')
	lo.EndRow()
	lo.EndGroup()
	
	lo.AddRow()
	lo.AddButton('Close', 'Close')
	lo.AddSpacer()
	item = lo.AddButton('Import', 'Import')
	# item.SetAttribute(c.siUIButtonDisable, True)
	lo.EndRow()
	
	lo.EndGroup()
	
	lo.AddTab('Options')
	
	lo.AddGroup('Hook Ups')
	lo.AddItem('UseReferenceFromContents', 'Reference From Contents.xml')
	lo.AddGroup('(temporarily disabled)')
	lo.AddRow()
	lo.AddItem('NodeReference', 'Reference Node')
	item = lo.AddButton('UpdateNode', 'Use Selection')
	item.SetAttribute(c.siUIButtonDisable, True)
	lo.EndRow()
	lo.EndGroup()
	lo.EndGroup()
	
	lo.AddGroup('Options')
	lo.AddItem('ObjClusters', 'Import Multiple Obj\'s as Clusters')
	lo.EndGroup()
	
	
		
def zPoseShapeImportGUI_PickPoseShape_OnClicked():
	# get the ppg #
	prop = PPG.Inspected(0)
	prop = dispatch(prop)

	# get the current path #
	path_current = xsi.ActiveProject.Path
	if prop.PoseShape.Value:
		path_current = prop.PoseShape.Value 
	
	# folder picker #
	folder = XSIUIToolkit.PickFolder(path_current, 'Pick zPoseShape (.zpshp) folder...')
	if folder:
		prop.PoseShape.Value = folder
		
	# update the gui #
	UpdateShapeImportGUI(prop)

	# update from the xml file #
	UpdateShapeImportFromXML(prop)
	
def zPoseShapeImportGUI_PickRestPath_OnClicked():
	# get the ppg #
	prop = PPG.Inspected(0)
	prop = dispatch(prop)
	
	# get the initial directories #
	init_dir	= xsi.ActiveProject.Path
	init_file	= ''
	if prop.RestPose.Value:
		init_dir  = os.path.dirname(prop.RestPose.Value)
		init_file = os.path.basename(prop.RestPose.Value)

	# get a file browser #
	fb = XSIUIToolkit.FileBrowser
	fb.DialogTitle 		= "Select the Rest Pose..."
	fb.InitialDirectory = init_dir
	fb.FileBaseName 	= init_file
	fb.Filter 			= "Zoogloo Pose Shape (*.xml)|*.xml|All Files (*.*)|*.*||"
	fb.ShowOpen()
	
	# get the filename #
	if not fb.FilePathName:
		return False
	
	# set the value #
	prop.RestPose.Value = fb.FilePathName
	
	# read the contents xml #
	UpdateShapeImportFromXML(prop)
	
def UpdateShapeImportFromXML(prop):
	# get the path #
	path_pose = prop.PoseShape.Value
	if not path_pose:
		return
	if not os.path.exists(path_pose):
		log('Path doesn\'t exist: %s' % path_pose, c.siError)
		return
	
	# get the contents file #
	xml_contents = path_pose + os.sep + 'contents.xml'
	if not os.path.exists(xml_contents):
		log('Unable to find "contents.xml" in: %s' % path_pose, c.siError)
		return
		
	# parse the xml #
	xml = dom.parse(xml_contents)
	doc = xml.documentElement
	
	# get the model #
	xml_root = xml.getElementsByTagName('zPoseShape')[0]
	model_name = xml_root.getAttribute('model')
	
	# find the model in the scene #
	model = xsi.ActiveSceneRoot.FindChild(model_name)
	if model:
		prop.TargetModel.Value = model.Name
		
	# get the reference node #
	xml_tfm = xml.getElementsByTagName('transform')
	node_name = None
	if len(xml_tfm):
		node_name = xml_tfm[0].getAttribute('name')
		
	# find the model in the scene #
	if node_name:
		log(node_name)
		node_reference = model.FindChild(node_name)
		if node_reference:
			prop.NodeReference.Value = node_reference.FullName

def zPoseShapeImportGUI_PoseShape_OnChanged():
	# get the ppg #
	prop = PPG.Inspected(0)
	prop = dispatch(prop)
	
	# update the gui #
	UpdateShapeImportGUI(prop)

	# update from the xml file #
	UpdateShapeImportFromXML(prop)

def zPoseShapeImportGUI_TargetModel_OnChanged():
	# get the ppg #
	prop = PPG.Inspected(0)
	prop = dispatch(prop)
	
	# update the gui #
	UpdateShapeImportGUI(prop)
		
def zPoseShapeImportGUI_NodeReference_OnChanged():
	# get the ppg #
	prop = PPG.Inspected(0)
	prop = dispatch(prop)
	
	# update the gui #
	UpdateShapeImportGUI(prop)
		
def zPoseShapeImportGUI_UpdateModel_OnClicked():
	# get the ppg #
	prop = PPG.Inspected(0)
	prop = dispatch(prop)
	
	# get the model #
	if xsi.selection(0).Type == '#model':
		prop.TargetModel.Value = xsi.selection(0)
	else:
		prop.TargetModel.Value = xsi.selection(0).Model
	
	# update the gui #
	UpdateShapeImportGUI(prop)
	
def zPoseShapeImportGUI_UpdateNode_OnClicked():
	# get the ppg #
	prop = PPG.Inspected(0)
	prop = dispatch(prop)
	
	# get the model #
	prop.NodeReference.Value = xsi.selection(0)
	
	# update the gui #
	UpdateShapeImportGUI(prop)
	
def zPoseShapeImportGUI_Import_OnClicked():
	# get the ppg #
	prop = PPG.Inspected(0)
	prop = dispatch(prop)
	
	# get the variables #
	model 				= prop.TargetModel.Value
	dir_pose_shape		= prop.PoseShape.Value
	path_pose_rest		= prop.RestPose.Value
	refs_from_contents	= prop.NodeReference.Value
	node_reference		= prop.NodeReference.Value
	obj_cluster_mode	= int(prop.ObjClusters.Value)
	
	# import the obj #
	xsi.zPoseShapeImport(
		model, 
		dir_pose_shape, 
		path_pose_rest, 
		refs_from_contents, 
		node_reference, 
		obj_cluster_mode
	)
	
	# close the ppg #
	PPG.Close()	

def zPoseShapeImportGUI_Close_OnClicked():
	# close the ppg #
	PPG.Close()	
	
def UpdateShapeImportGUI(prop):
# 	# get the current path #
# 	path_current = prop.Path.Value
# 	if not path_current:
# 		log('No Path specified.', c.siWarning)
# 		return False
# 	if not os.path.exists(path_current):
# 		log('Unable to find path %s.' % path_current, c.siWarning)
# 		return False
# 		
# 	# get the contents #
# 	xml_contents = path_current + os.sep + 'contents.xml'
# 	if not os.path.exists(xml_contents):
# 		log('Unable to locate contents.xml in "%s".' % path_current, c.siError)
# 		return False
# 		
# 	# parse contents #
# 	xml = dom.parse(xml_contents)
# 	doc = xml.documentElement
# 	
# 	# get the objects #
# 	list_objs = []
# 	xml_objects = xml.getElementsByTagName('obj')
# 	for xml_obj in xml_objects:
# 		list_objs.append(xml_obj.getAttribute('name'))
# 	prop.Objects.Value = ', '.join(list_objs)
# 	
# 	# get the pose #
# 	xml_pose_name = xml.getElementsByTagName('pose')[0]
# 	name_pose = xml_pose_name.getAttribute('file')
# 	prop.PoseName.Value = name_pose
# 	
# 	# get the name #
# 	xml_pose_shape = xml.getElementsByTagName('zPoseShape')[0]
# 	name_pose_shape = xml_pose_shape.getAttribute('name')
# 	log('Pose Name: %s' % name_pose_shape)
# 	if not name_pose_shape:
# 		name_pose_shape = name_pose.split('.')[0]
# 	prop.ShapeName.Value = name_pose_shape
# 	
# 	# check for the same number of obj files #
# 	path_originals 	= path_current + os.sep + 'objs_original'
# 	path_fixed	 	= path_current + os.sep + 'objs_fixed'
# 	objs_original 	= glob.glob('%s/*.obj' % path_originals)
# 	objs_fixed 		= glob.glob('%s/*.obj' % path_fixed)
# 	log('%s/obj_original/*.obj' % path_current)
# 	log(`objs_original`)
# 	prop.ObjsOriginal.Value = ', '.join(objs_original).replace(path_originals + os.sep, '')
# 	prop.ObjsFixed.Value 	= ', '.join(objs_fixed).replace(path_fixed + os.sep, '')
# 	prop.ObjsOriginalCount.Value = len(objs_original)
# 	prop.ObjsFixedCount.Value = len(objs_fixed)
# 	
# 	
	# if we have all the parameters we need turn on the load button #
	lo = prop.PPGLayout
	button_load = lo.Item('Import')
	if prop.PoseShape.Value \
	and prop.TargetModel.Value:
	# and prop.NodeReference.Value:
		button_load.SetAttribute(c.siUIButtonDisable, False)
	else:
		button_load.SetAttribute(c.siUIButtonDisable, True)
		
	try:
		PPG.Refresh()
	except:
		pass
	
	
		
#-----------------------------------------------------------------------------
# Commands
#-----------------------------------------------------------------------------
def zPoseShapeExportGUI_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	#oCmd.SetFlag(constants.siNoLogging,false)

	# oArgs = oCmd.Arguments
	# oArgs.Add('filename', c.siArgumentInput, xsi.ActiveProject.Path, c.siString)
	# oArgs.Add('overwrite', c.siArgumentInput, False, c.siBool)
	# oArgs.AddWithHandler('objects', c.siArgHandlerCollection)

	return True
	
def zPoseShapeExportGUI_Execute():
	
	# create the menu on the scene root if it doesn't exist #
	prop = xsi.ActiveSceneRoot.Properties('zPoseShapeExportGUI')
	if not prop:
		prop = xsi.ActiveSceneRoot.AddProperty('zPoseShapeExportGUI')
	prop = dispatch(prop)
	
	# show the GUI #
	xsi.InspectObj(prop, '', '', c.siLockAndForceNew, False)

#-----------------------------------------------------------------------------

def zPoseShapeImportGUI_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	#oCmd.SetFlag(constants.siNoLogging,false)

	# oArgs = oCmd.Arguments
	# oArgs.Add('filename', c.siArgumentInput, xsi.ActiveProject.Path, c.siString)
	# oArgs.Add('overwrite', c.siArgumentInput, False, c.siBool)
	# oArgs.AddWithHandler('objects', c.siArgHandlerCollection)

	return True
	
def zPoseShapeImportGUI_Execute():
	'''
	Only supports polymeshes for now.
	'''
	
	# create the menu on the scene root if it doesn't exist #
	prop = xsi.ActiveSceneRoot.Properties('zPoseShapeImportGUI')
	if not prop:
		prop = xsi.ActiveSceneRoot.AddProperty('zPoseShapeImportGUI')
	prop = dispatch(prop)
	
	# show the GUI #
	xsi.InspectObj(prop, '', '', c.siLockAndForceNew, False)
	
	# update the gui #
	UpdateShapeImportGUI(prop)

#-----------------------------------------------------------------------------

def zPoseShapeExport_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	#oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments
	oArgs.AddWithHandler('objects', c.siArgHandlerCollection)
	oArgs.Add('filename', c.siArgumentInput, xsi.ActiveProject.Path, c.siString)
	oArgs.Add('node_reference', c.siArgumentInput, '', c.siString)
	oArgs.Add('overwrite', c.siArgumentInput, False, c.siBool)
	oArgs.Add('Zip', c.siArgumentInput, False, c.siBool)

	return True
	
def zPoseShapeExport_Execute(objects, filename, node_reference, overwrite, Zip):
	'''
	Only supports polymeshes for now.
	'''
	
	# step through all the objects and filter out meshes #
	meshes = dispatch('XSI.Collection')
	for obj in objects:
		# skip over non meshes #
		if obj.Type != 'polymsh':
			log('Skipping (%s)%s.' % (obj.Type, obj.FullName), c.siWarning)
			continue
		# add the to the meshes collection #
		meshes.Add(obj)
		
	# make sure we have something #
	if not meshes.Count:
		log('Nothing to export.', c.siError)
		return
		
	# add the extension to the filename #
	if not re.match(r'.*\.zpshp$', filename):
		filename += '.zpshp'
		
	# make the directory if it doesn't exist #
	if not os.path.exists(filename):
		try:
			os.mkdir(filename)
		except:
			log('Unable to create directory: %s' % filename, c.siError)
			return
	else:
		if not os.path.isdir(filename):
			log('Export path "%s" is a file not a directory.' % filename, c.siError)
			return
		elif not overwrite:
			log('Path "%s" exists and "overwrite" argument is not enabled.' % filename, c.siError)
			return
			
	# add an objs folder #
	path_objs_orig = filename + os.sep + 'objs_original'
	if not os.path.exists(path_objs_orig):
		os.mkdir(path_objs_orig)

	path_objs_fixed = filename + os.sep + 'objs_fixed'
	if not os.path.exists(path_objs_fixed):
		os.mkdir(path_objs_fixed)
	
	# get just the name #
	name_only = os.path.basename(filename).replace('.zpshp', '')
	
	# create a contents xml file #
	impl = dom.getDOMImplementation()
	docType = impl.createDocumentType('zPoseShape', '-//Zoogloo//zPoseShape 1.0//EN' , 'http://zoogloo.net/dtds/zPoseShape-1.0.dtd')
	doc = impl.createDocument(None, "zPoseShape", None)
	top = doc.documentElement
	
	# set the date #
	top.setAttribute('date', time.asctime())
	# set the version from the plugin #
	plugin = xsi.Plugins('zPoseShape')
	top.setAttribute('version', '%d.%d' % (plugin.Major, plugin.Minor))
	# set the username #
	if os.name == 'nt':
		import win32api
		user=win32api.GetUserName()
	if os.name == 'posix':
		user = os.environ['USER']
	top.setAttribute('author', user)
	top.setAttribute('model', objects(0).Model.Name)
	top.setAttribute('name', name_only)

	# create an obj's element #
	xml_objs = doc.createElement('objs')
	top.appendChild(xml_objs)
	
	# step through the geometry #
	for mesh in meshes:
		
		# export the selected as obj files #
		xsi.Selection.Clear()
		xsi.Selection.SetAsText(mesh)
		file_obj = path_objs_orig + os.sep + name_only +'.' + mesh.Name + '.obj'
		xsi.ObjExport(file_obj, 0, "", "", "", "", "", "", "", "", 0, 0, 0, 0, 0)

		# create an objs key in the plist #
		xml_obj = doc.createElement('obj')
		xml_objs.appendChild(xml_obj)
		xml_obj.setAttribute('file', os.path.basename(file_obj))
		xml_obj.setAttribute('type', mesh.Type)
		xml_obj.setAttribute('name', mesh.Name)
		xml_obj.setAttribute('points', str(mesh.ActivePrimitive.Geometry.Points.Count))

		# add it to the plist #
		# xml_geo = doc.createElement('geometry')
		# xml_objs.appendChild(xml_geo)
		# xml_geo.setAttribute('type', mesh.Type)
		# xml_geo.setAttribute('name', mesh.Name)

	# export a pose #
	char_model = meshes(0).model
	char_set = char_model.Properties('CharacterSet')
	if not char_set:
		log('Unable to find %s.CharacterSet' % char_model, c.siError)
		return False
	pose_name = '%s.zpose.xml' % name_only
	pose_path = filename + os.sep + pose_name
	xsi.zSaveCharacterPose(char_set, pose_path, True)
	
	# write the pose to xml #
	xml_pose = doc.createElement('pose')
	top.appendChild(xml_pose)
	xml_pose.setAttribute('file', pose_name)
	
	# save the transform reference node #
	node_reference = xsi.ActiveSceneRoot.FindChild(node_reference)
	xml_tfrm = doc.createElement('transform')
	top.appendChild(xml_tfrm)
	xml_tfrm.setAttribute('name', node_reference.Name)
	
	# store the global matrix #
	xml_mtx = doc.createElement('matrix')
	xml_mtx.setAttribute('space', 'global')
	xml_tfrm.appendChild(xml_mtx)
	mtx = node_reference.Kinematics.Global.Transform.Matrix4
	for r in xrange(4):
		for c in xrange(4):
			xml_value = doc.createElement('field')
			xml_mtx.appendChild(xml_value)
			xml_value.setAttribute('row', str(r))
			xml_value.setAttribute('col', str(c))
			xml_value.setAttribute('value', str(mtx.Value(r,c)))
	
	# write it to disk #
	file_xml = filename + os.sep + 'contents.xml'
	fh = open(file_xml, 'w')
	fh.write('<?xml version="1.0" encoding="utf-8"?>\n')
	docType.writexml(fh, indent='', addindent='\t', newl='\n')
	top.writexml(fh, indent='', addindent='\t', newl='\n')
	fh.close()
	
	# zip it up #
	if Zip:
		# create a handle to a zip file #
		zipname = filename + '.zip'
		z = zipfile.ZipFile(zipname, 'w', zipfile.ZIP_DEFLATED)
		
		# create a function to walk the directories #
		def zip_dir(zip, dir, files):
			
			for file in files:
				full_path = '%s/%s' % (dir, file)
				if os.path.isfile(full_path):
					# log('File: %s' % full_path)
					archive_name = os.path.basename(filename) + '/' + full_path.replace(filename, '')
					# log('Archive: %s' % archive_name)
					z.write(full_path, str(archive_name))
			
		# walk the directory #
		os.path.walk(filename, zip_dir, z)
		
		# close the zip file #
		z.close()
		
	# select all the meshes #
	xsi.selection.Clear()
	xsi.selection.SetAsText(meshes.GetAsText())
	
#-----------------------------------------------------------------------------

def zPoseShapeImport_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	#oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments
	oArgs.AddObjectArgument('model')
	oArgs.Add('dir_pose_shape', c.siArgumentInput, '', c.siString)
	oArgs.Add('path_pose_rest', c.siArgumentInput, '', c.siString)
	oArgs.Add('refs_from_contents', c.siArgumentInput, 1, c.siUInt2)
	oArgs.AddWithHandler('node_reference', c.siArgHandlerCollection)
	oArgs.Add('obj_cluster_mode', c.siArgumentInput, 1, c.siUInt2)

	return True
	
def zPoseShapeImport_Execute(
	model, 
	dir_pose_shape, 
	path_pose_rest, 
	refs_from_contents, 
	node_reference, 
	obj_cluster_mode):
	
	# make sure the file exists #
	if not os.path.exists(dir_pose_shape):
		log('Unable to locate path: %s' % dir_pose_shape, c.siError)
		return None
		
	# make sure the model exists and is a model #
	if model.type != '#model':
		log('Model argument "%s" not a model' % model, c.siError)
		return False

	# get the contents #
	ps = xsi.zPoseShapeContents(dir_pose_shape)
	ps.Load()
		
	# check for the same number of obj files #
	path_originals 	= dir_pose_shape + os.sep + 'objs_original'
	path_fixed	 	= dir_pose_shape + os.sep + 'objs_fixed'
	objs_original 	= glob.glob('%s/*.obj' % path_originals)
	objs_fixed 		= glob.glob('%s/*.obj' % path_fixed)
	# Note: This is here because maya need to NOT export multiple objects in the same obj
	# file or else they scramble the point ids
	if len(objs_original) != len(objs_fixed):
		log('Number of obj files don\'t match.  %d original != %d fixed.' \
		% (len(objs_original), len(objs_fixed)), c.siError)
		return False

	# get the pose #
	file_pose = ps.pose.file
	
	# make sure the pose files exists #
	path_pose = dir_pose_shape + os.sep + file_pose
	if not os.path.exists(path_pose):
		log('Unable to locate pose "%s".' % path_pose, c.siError)
		return False
		
	# get the pose shape name #
	name_pose_shape = os.path.basename(dir_pose_shape).split('.')[0]

	# import the new obj's #
	geom_imported = []
	for obj_file in objs_fixed:
		geom_import = xsi.ObjImport(obj_file, 1-obj_cluster_mode, 0, 1, 1, 0, 1)
		if geom_import.Count > 1:
			log('Obj file %s contains multiple objs.  Not expecting this.  Could cause errors.' % obj_file, c.siWarning)
		geom_imported.append(geom_import(0))
		log('Imported: %s' % geom_import(0))
	
	# load the rest pose #
	if path_pose_rest:
		# load it twice incase we are setting switches that may come after setting transforms #
		log('Loding Rest Pose: %s' % path_pose_rest)
		xsi.zLoadCharacterPose(model, path_pose_rest)
		xsi.zLoadCharacterPose(model, path_pose_rest)
	else:
		# reset the actor to rest position #
		log('No rest pose given.  Trying to reset the actor...', c.siWarning)
		log('If results are unsuccessful, pass a rest pose.', c.siWarning)
		model_geom_all = model.FindChildren('', '', [c.siMeshFamily, c.siNurbsSurfaceMeshFamily])
		for geo in model_geom_all:
			if geo.Envelopes.Count:
				log('Reset actor with geo %s' % geo)
				reset = False
				try:
					xsi.ResetActor(geo, False)
					reset = True
				except:
					log('Unable to reset actor with "%s"' % geo, c.siWarning)
					log('Trying other geometry...', c.siWarning)
					continue
			
				# if successful, break the loop #
				if reset: break
	
	# create a dictionary to store the point arrays at the rest poses #
	dict_geom_rest = {}

	# try to fix the names if they don't match #
	map_geom = {}
	for geom in geom_imported:
		geom_target = model.FindChild(geom.Name)
		if geom_target:
			# add it to the mapping dictionary #
			map_geom[geom_target.Name] = {
				'fixed': geom,
				'original': geom_target
			}
			
			# store the position array at rest #
			dict_geom_rest[geom_target.Name] = {
				'position_array': geom_target.ActivePrimitive.Geometry.Points.PositionArray
			}
			
		else:
			log('Unable to find corresponding target for import shape: %s' % geom, c.siWarning)
			log('Trying other methods...', c.siWarning)
			# get the point count on the imported obj #
			point_count = geom.ActivePrimitive.Geometry.Points.Count
			# get all the geometry in the model scene #
			model_geom_all = model.FindChildren('', '', [c.siMeshFamily, c.siNurbsSurfaceMeshFamily])
			# step through the geo looking for matching point count #
			geom_match = []
			for model_geom in model_geom_all:
				if model_geom.ActivePrimitive.Geometry.Points.Count == point_count:
					geom_match.append(model_geom)
			# skip geo if we couldn't find a point count match #
			if len(geom_match) == 0:
				log('Unable to find any matching geometry for %s' % geom, c.siError)
				xsi.DeleteObj(geom)
				break
			# report if we have more than one match #
			if len(geom_match) > 1:
				log('Found multiple matches for %s by point count.' % geom, c.siWarning)
				for item in geom_match:
					log('  - %s' % item, c.siWarning)
				log('Using the first item.  If this is incorrect', c.siWarning)
				log('rename the incoming obj to match the target geometry name.', c.siWarning)
			
			# add it to the mapping dictionary #
			log('...Using target geometry: %s' % geom_match[0], c.siWarning)
			map_geom[geom_match[0].Name] = {
				'fixed': geom,
				'original': geom_match[0]
			} 
			
			# store the position array at rest #
			dict_geom_rest[geom_match[0].Name] = {
				'position_array': geom_match[0].ActivePrimitive.Geometry.Points.PositionArray
			}

	# load the pose #
	# load it twice incase we are setting switches that may come after setting transforms #
	log('Loding Shape Pose: %s' % path_pose)
	xsi.zLoadCharacterPose(model, path_pose)
	xsi.zLoadCharacterPose(model, path_pose)
	
	# create a dictionary to hold the deformers transformation cache #
	mtx_transform_cache 	= {}
	
	# initialize a progress bar #
	pb = XSIUIToolkit.ProgressBar
	pb.Step = 1
	pb.Caption = 'Calculting itterations....'
	if xsi.Interactive: pb.Visible = True

	# calculate the max itterations #
	for geo_name in map_geom.keys():
		geo_original 	= map_geom.get(geo_name).get('original')
		# set the maximum #
		pb.Maximum += geo_original.ActivePrimitive.Geometry.Points.Count
		
	# create a pose shape reference prop under the model #
	prop_ps = model.Properties('zPoseShapes')
	if not prop_ps:
		prop_ps = model.AddProperty('CustomProperty', False, 'zPoseShapes')
	prop_ps = dispatch(prop_ps)

	# create a subprop for blends #
	prop_blends = None
	for nested in prop_ps.NestedObjects:
		if re.match(r'^zBlenders$', nested.Name, re.I): prop_blends = nested
	if not prop_blends:
		# prop_blends = prop_ps.AddProperty('CustomProperty', False, 'zBlenders')
		# can't use the OM to add nested properties
		prop_blends = xsi.AddProp('Custom_parameter_list', prop_ps, c.siDefaultPropagation, 'zBlenders')[1](0)

	# create a subprop pose shape property #
	prop_shapes = None
	for nested in prop_ps.NestedObjects:
		if re.match(r'^zPShapes$', nested.Name, re.I): prop_shapes = nested
	if not prop_shapes:
		# prop_blends = prop_ps.AddProperty('CustomProperty', False, 'zBlenders')
		# can't use the OM to add nested properties
		prop_shapes = xsi.AddProp('Custom_parameter_list', prop_ps, c.siDefaultPropagation, 'zPShapes')[1](0)

	# create a subprop for info #
	prop_info = None
	for nested in prop_ps.NestedObjects:
		if re.match(r'^zPShapeInfo$', nested.Name, re.I): prop_info = nested
	if not prop_info:
		# prop_blends = prop_ps.AddProperty('CustomProperty', False, 'zBlenders')
		# can't use the OM to add nested properties
		prop_info = xsi.AddProp('Custom_parameter_list', prop_ps, c.siDefaultPropagation, 'zPShapeInfo')[1](0)

	# create a subprop for this shapes info #
	prop_shape_info = None
	for nested in prop_info.NestedObjects:
		if re.match(r'^zPShapeInfo$', nested.Name, re.I): 
			prop_shape_info = nested
			log('Whoops... found info for this shape all ready at: %s' % prop_shape_info.FullName, c.siError)
			return prop_shape_info
	if not prop_shape_info:
		# prop_blends = prop_ps.AddProperty('CustomProperty', False, 'zBlenders')
		# can't use the OM to add nested properties
		prop_shape_info = xsi.AddProp('Custom_parameter_list', prop_info, c.siDefaultPropagation, name_pose_shape)[1](0)
		
	# add parameters to info node #
	prop_shape_info.AddParameter3('FileName', c.siString, dir_pose_shape)

	# create a collection to hold all the shape keys #
	col_shapekeys = dispatch('XSI.Collection')
	
	# create a collection to hold the new shape params #
	col_shape_params = dispatch('XSI.Collection')

	# step through the mapped geometry#
	for geo_name in map_geom.keys():

		# set the caption #
		pb.Caption = 'Calculating pose offset for: %s' % geo_name
		
		# get the geometry #
		geo_fixed 		= map_geom.get(geo_name).get('fixed')
		geo_original 	= map_geom.get(geo_name).get('original')
		
		# get the points #
		points_fixed 		= geo_fixed.ActivePrimitive.Geometry.Points
		points_original 	= geo_original.ActivePrimitive.Geometry.Points

		# make sure they match #
		if points_fixed.Count != points_original.Count:
			log('Point Counts don\'t match.', c.siError)
			log('Fixed(%d) != Original(%d).' % (points_fixed.Count, points_original.Count), c.siError)
			log('Skipping.', c.siError)
			continue
		
		# create an array to hold the delta vectors #
		pa_delta = [[0.0]*points_fixed.Count, [0.0]*points_fixed.Count, [0.0]*points_fixed.Count]
		
		# get the point arrays (use the duplicate geom)#
		pa_fixed 		= points_fixed.PositionArray
		pa_original	 	= points_original.PositionArray
		
		# get the envelope and weights #
		env 		= geo_original.Envelopes(0)
		env_weights = env.Weights
		
		# get the global position of the original geometry #
		v_geom_orig 	= geo_original.Kinematics.Global.Transform.Translation
		v_geom_fixed 	= geo_fixed.Kinematics.Global.Transform.Translation
		
		# step through the points #
		v_fixed			= XSIMath.CreateVector3()
		v_original		= XSIMath.CreateVector3()
		v_original_rest	= XSIMath.CreateVector3()
		v_delta  		= XSIMath.CreateVector3()
		for p in xrange(len(pa_fixed[0])):
			
			# inrement the progress bar #
			pb.Increment()
			
			# catch cancel pressed #
			if pb.CancelPressed:
				log('Cancelled.', c.siWarning)
				return

			# build the vectors #
			v_fixed.X = pa_fixed[0][p]
			v_fixed.Y = pa_fixed[1][p]
			v_fixed.Z = pa_fixed[2][p]

			v_original.X = pa_original[0][p]
			v_original.Y = pa_original[1][p]
			v_original.Z = pa_original[2][p]

			pa_original_rest = dict_geom_rest.get(geo_original.Name).get('position_array')
			v_original_rest.X = pa_original_rest[0][p]
			v_original_rest.Y = pa_original_rest[1][p]
			v_original_rest.Z = pa_original_rest[2][p]
			
			# subtract the vectors #
			v_delta.Sub(v_fixed, v_original)

			# if the point is greater than the threshold it's moved #
			if v_delta.Length() > 0.001:
				# log('Delta [%d] <%0.2f, %0.2f, %0.2f>' % (i, v_delta.X, v_delta.Y, v_delta.Z))
			
				# create a matrix to hold the sum of the weighted matrices #
				mtx_sigma = XSIMath.CreateMatrix4(
					0.0, 0.0, 0.0, 0.0,
					0.0, 0.0, 0.0, 0.0,
					0.0, 0.0, 0.0, 0.0,
					0.0, 0.0, 0.0, 0.0
				)
				
				# copy the fixed vector #
				v_env = XSIMath.CreateVector3()
				v_env.Copy(v_fixed)
				
				# put the point in global space #
				v_env.AddInPlace(v_geom_fixed)

				# get the deformers for the vertex #
				for d in xrange(len(env_weights[p])):
					
					# Vorig = Venv / (Mbind^-1 * Mcur) * w

					# only process weights greater than 0 #
					weight = env_weights[p][d]/100.0
					if not weight > 0: continue
				
					deformer = env.Deformers(d)
					# log('Deformer: %s' % deformer)
					
					# calculate the transformation matrix from the bind pose 
					# and the current pose 
					# 	Mresult = Mbind^-1 * Mcurrent
					# get the static kinestate matrix (bind pose) #
					trans_static 	= XSIMath.CreateTransform()
					static_kine		= deformer.Properties('Static KineState')
					static_kine		= dispatch(static_kine)
					trans_static.Translation = XSIMath.CreateVector3(
						static_kine.posx.Value,
						static_kine.posy.Value,
						static_kine.posz.Value
					)
					trans_static.Scaling = XSIMath.CreateVector3(
						static_kine.sclx.Value,
						static_kine.scly.Value,
						static_kine.sclz.Value
					)
					trans_static.Rotation = XSIMath.CreateRotation(
						XSIMath.DegreesToRadians(static_kine.orix.Value),
						XSIMath.DegreesToRadians(static_kine.oriy.Value),
						XSIMath.DegreesToRadians(static_kine.oriz.Value)
					)
					mtx_static = trans_static.Matrix4

					# get the current matrix #
					mtx_current = deformer.Kinematics.Global.Transform.Matrix4
				
					# create the transformation matrix #
					mtx_transform = XSIMath.CreateMatrix4()
					
					# calculate the transform from the deformed to the static #
					mtx_transform.Invert(mtx_static)  		# invert the matrix
					mtx_transform.MulInPlace(mtx_current) 	# multiply by the current matrix
					
					# mutliply the matrix by the weight #
					mtx_transform.Set(
						mtx_transform.Value(0,0) * weight, mtx_transform.Value(0,1) * weight, mtx_transform.Value(0,2) * weight, mtx_transform.Value(0,3) * weight, 
						mtx_transform.Value(1,0) * weight, mtx_transform.Value(1,1) * weight, mtx_transform.Value(1,2) * weight, mtx_transform.Value(1,3) * weight, 
						mtx_transform.Value(2,0) * weight, mtx_transform.Value(2,1) * weight, mtx_transform.Value(2,2) * weight, mtx_transform.Value(2,3) * weight, 
						mtx_transform.Value(3,0) * weight, mtx_transform.Value(3,1) * weight, mtx_transform.Value(3,2) * weight, mtx_transform.Value(3,3) * weight
					)
					
					# add it to the sigma matrix #
					mtx_sigma.Set(
						mtx_transform.Value(0,0) + mtx_sigma.Value(0,0), mtx_transform.Value(0,1) + mtx_sigma.Value(0,1), mtx_transform.Value(0,2) + mtx_sigma.Value(0,2), mtx_transform.Value(0,3) + mtx_sigma.Value(0,3), 
						mtx_transform.Value(1,0) + mtx_sigma.Value(1,0), mtx_transform.Value(1,1) + mtx_sigma.Value(1,1), mtx_transform.Value(1,2) + mtx_sigma.Value(1,2), mtx_transform.Value(1,3) + mtx_sigma.Value(1,3), 
						mtx_transform.Value(2,0) + mtx_sigma.Value(2,0), mtx_transform.Value(2,1) + mtx_sigma.Value(2,1), mtx_transform.Value(2,2) + mtx_sigma.Value(2,2), mtx_transform.Value(2,3) + mtx_sigma.Value(2,3), 
						mtx_transform.Value(3,0) + mtx_sigma.Value(3,0), mtx_transform.Value(3,1) + mtx_sigma.Value(3,1), mtx_transform.Value(3,2) + mtx_sigma.Value(3,2), mtx_transform.Value(3,3) + mtx_sigma.Value(3,3)
					)
					
				# invert the sigma matrix #
				mtx_sigma.InvertInPlace()
				
				# calculate the original vector #
				v_orig = XSIMath.CreateVector3()
				v_orig.Copy(v_env)
				
				# multiply the env vector by the inverse
				v_orig.MulByMatrix4InPlace(mtx_sigma)
				
				# put point back in local space #
				v_orig.SubInPlace(v_geom_fixed)
				
				# calculate the delta from the source #
				v_delta_from_orig = XSIMath.CreateVector3()
				# v_delta_from_orig.Sub(v_original_rest, v_orig)
				v_delta_from_orig.Sub(v_orig, v_original_rest)
				
				# add the delta vector to the delta point array #
				pa_delta[0][p] = v_delta_from_orig.X
				pa_delta[1][p] = v_delta_from_orig.Y
				pa_delta[2][p] = v_delta_from_orig.Z
				
		# store a shape key #
		unique_shape_name = name_pose_shape + '__' + geo_original.name
		shape_key = xsi.StoreShapeKey(geo_original, unique_shape_name, c.siShapeObjectReferenceMode, "", "", "", c.siShapeContentSecondaryShape, True)
		
		# make sure the parent (cluster) name is 'zPoseShapes' #
		if shape_key.Parent.Name != 'zPoseShapes':
			shape_key.Parent.Name = 'zPoseShapes'
		
		# renaming the cluster group doesn't rename the source target, so let's go do it #
		for source in model.Sources:
			# skip over non shapes #
			if source.Type != 'ShapeAction': continue
			# find by shape key name #
			if source.Name == shape_key.Name:
				for item in source.SourceItems:
					# rename the target #
					item.Target = shape_key.Parent.FullName
			
		# set the delta data #
		shape_key.Elements.Array = pa_delta
		
		# store the shape key in the info #
		prop_shape_info.AddParameter3('ShapeKey', c.siString, shape_key.FullName)
		
		# remove the geo fixed #
		xsi.DeleteObj(geo_fixed)
		
		# add it to the shape collection #
		col_shapekeys.Add(shape_key)
		
		# apply the shape key #
		clip = xsi.ApplyShapeKey(shape_key, '', '', 1, '', 5, '', 2)
		log('Clip FullName: %s' % clip.FullName)
		
		# add a parameter of the shape to the property #
		# param_shape = prop_pshape.AddParameter3(name_pose_shape, c.siFloat, 0, -1000, 1000)
		param_shape = prop_shapes.Parameters(name_pose_shape)
		if not param_shape:
			param_shape = prop_shapes.AddParameter2(name_pose_shape, c.siFloat, 0, -1000, 1000, 0, 1, c.siClassifUnknown, c.siAnimatable+c.siPersistable)

		# add the parameter to a collection #
		col_shape_params.Add(param_shape)

		# link it with an expression #
		# log(clip.Weight.Value)
		clip.Weight.AddExpression(param_shape)
		
	# apply vectors from contents.xml #
	if (refs_from_contents and len(ps.vectors.children)):

		log('Applying vectors from contents.xml:')

		# create a temporary collection to hold the props 
		col_temp = dispatch('XSI.Collection')

		# step through the vectors #
		for vector in ps.vectors.children:
			log('Applying vector weight to "%s"' % vector.node)
			node = model.FindChild(vector.node)
			
			# add the vector weight nodes #
			axis_int = 0
			if re.match(r'^x$', vector.axis, re.I): axis_int = 0
			elif re.match(r'^y$', vector.axis, re.I): axis_int = 1
			elif re.match(r'^z$', vector.axis, re.I): axis_int = 2
			prop_vw = xsi.zApplyVectorWeight(node, axis_int, 'zVW_%s_%s' % (name_pose_shape, vector.axis))

			# add it to the temp collection #
			col_temp.Add(prop_vw)
			
			# add it to the info #
			prop_shape_info.AddParameter3('Vector', c.siString, prop_vw.FullName)
		
		# blend the weights #
		log('Appling Blend weight to "%s" for "%s"' % (prop_blends, col_temp.GetAsText()))
		log(prop_blends.Type)
		prop_blend = xsi.zApplyBlendWeights(col_temp, prop_blends, 'zBlend_%s' % name_pose_shape)

		# add it to the info #
		prop_shape_info.AddParameter3('Blend', c.siString, prop_blend.FullName)

		# we are in the target position, so let's store the vector #
		for prop in col_temp:
			xsi.zSetVectorWeightFromCurrentPose(prop, True)
			xsi.zSetVectorWeightFromCurrentPose(prop, True)

		# load the rest pose to store the rest vectors #
		xsi.zLoadCharacterPose(model, path_pose_rest)
		xsi.zLoadCharacterPose(model, path_pose_rest)
	
		# set the rest vector #
		for prop in col_temp:
			xsi.zSetVectorWeightFromCurrentPose(prop, False)
			xsi.zSetVectorWeightFromCurrentPose(prop, False)

		# load the target pose again #
		xsi.zLoadCharacterPose(model, path_pose)
		xsi.zLoadCharacterPose(model, path_pose)
	
		# link the values to the shapes #
		log('Linking to blend weight node: %s' % prop_blend)
		for param in col_shape_params:
			param.AddExpression(prop_blend.weight.FullName)

	# apply vectors from command line #
	if (not refs_from_contents and node_reference.Count):
		
		log('Applying vectors from commandline override: "%s"' % node_reference.GetAsText())

		# create a temporary collection to hold the props 
		col_temp = dispatch('XSI.Collection')

		# step through the reference nodes #
		for node in node_reference:
			# add the vector weight nodes #
			prop_vw_x = xsi.zApplyVectorWeight(node, 0, 'zVW_%s_X' % name_pose_shape)
			prop_vw_y = xsi.zApplyVectorWeight(node, 1, 'zVW_%s_Y' % name_pose_shape)

			# add it to the temp collection #
			col_temp.Add(prop_vw_x)
			col_temp.Add(prop_vw_y)

			# add it to the info #
			prop_shape_info.AddParameter3('Vector', c.siString, prop_vw_x.FullName)
			prop_shape_info.AddParameter3('Vector', c.siString, prop_vw_y.FullName)
		
		# blend the weights #
		prop_blend = xsi.zApplyBlendWeights(col_temp, node, 'zVW_%s_Blend' % name_pose_shape)	

		# add it to the info #
		prop_shape_info.AddParameter3('Blend', c.siString, prop_blend.FullName)

		# we are in the target position, so let's store the vector #
		for prop in col_temp:
			xsi.zSetVectorWeightFromCurrentPose(prop, True)
			xsi.zSetVectorWeightFromCurrentPose(prop, True)

		# load the rest pose to store the rest vectors #
		xsi.zLoadCharacterPose(model, path_pose_rest)
		xsi.zLoadCharacterPose(model, path_pose_rest)

		# set the rest vector #
		for prop in col_temp:
			xsi.zSetVectorWeightFromCurrentPose(prop, False)
			xsi.zSetVectorWeightFromCurrentPose(prop, False)

		# load the target pose again #
		xsi.zLoadCharacterPose(model, path_pose)
		xsi.zLoadCharacterPose(model, path_pose)

		# link the values to the shapes #
		for param in col_shape_params:
			param.AddExpression(prop_blend.weight.FullName)
	
		
	# apply driven keys #
	if ps.driven:
		
		# add the expression #
		for param in col_shape_params:
			expr_str = 'l_fcv( %s.%s.kine.local.%s )' % (model.Name, ps.driven.node, ps.driven.channel)
			log(expr_str)
			expr = param.AddExpression(expr_str)
			# add the keys to the fcurve #
			fcurve = expr.Parameters('l_fcv').Source
			fcurve = dispatch(fcurve)
			# set the curve interpolation #
			if ps.driven.curve == 'linear':
				fcurve.Interpolation = c.siLinearInterpolation
			elif ps.driven.curve == 'spline':
				fcurve.Interpolation = c.siCubicInterpolation
			elif ps.driven.curve == 'constant':
				fcurve.Interpolation = c.siConstantInterpolation
			# add the keys #
			for key in ps.driven.keys:
				fcurve.AddKey(key.value, key.weight)
				
			# add it to the info #
			prop_shape_info.AddParameter3('Driven', c.siString, param.FullName)

	# return the shape keys #
	return col_shapekeys

#-----------------------------------------------------------------------------

def zPoseShapeUpdateContents_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	#oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments
	oArgs.AddObjectArgument('model')
	oArgs.Add('dir_pose_shape', c.siArgumentInput, '', c.siString)
	oArgs.Add('backup', c.siArgumentInput, True, c.siBool)
	# oArgs.Add('path_contents', c.siArgumentInput, '', c.siString)
	# oArgs.AddObjectArgument('node_reference')
	# oArgs.Add('obj_cluster_mode', c.siArgumentInput, 1, c.siUInt2)

	return True
	
def zPoseShapeUpdateContents_Execute(model, dir_pose_shape, backup):
	'''
	Updates the corresponding contents.xml file from the given shape.
	'''
	
	# make sure the file exists #
	if not os.path.exists(dir_pose_shape):
		log('Unable to locate path: %s' % dir_pose_shape, c.siError)
		return None
		
	# make sure the model exists and is a model #
	if model.type != '#model':
		log('Model argument "%s" not a model' % model, c.siError)
		return False

	# backup #
	if backup:
		shutil.copyfile(
			dir_pose_shape + os.sep + 'contents.xml',
			dir_pose_shape + os.sep + 'contents.xml.backup',
		)

	# get the shape name #
	shape_name = os.path.basename(dir_pose_shape).split('.')[0]
	
	# get the contents #
	ps = xsi.zPoseShapeContents(dir_pose_shape)
	# load the contents from disk #
	ps.Load()
	# update the info #
	ps.UpdateInfo()
	ps.info.model = model.name
	
	# find the pose shape property #
	prop_pose_shapes = model.Properties('zPoseShapes')
	if not prop_pose_shapes:
		log('Unable to find "zPoseShapes" property on "%s"' % (model), c.siWarning)
		return False
	
	# find the zPShapes prop #
	prop_poses = None
	for nested in prop_pose_shapes.NestedObjects:
		if re.match(r'^zPShapes$', nested.Name):
			prop_poses = nested
			break
	if not prop_poses:
		log('Unable to find "zPShapes" on "%s"' % (prop_pose_shapes.FullName), c.siError)
		return False
		
	# get the shape infos #
	prop_info = None
	for nested in prop_pose_shapes.NestedObjects:
		if re.match(r'^zPShapeInfo$', nested.Name):
			prop_info = nested
			break
	if not prop_info:
		log('Unable to find "zPShapeInfo" on "%s"' % (prop_pose_shapes.FullName), c.siError)
		return False
	
	# get this shape's info #
	prop_shape_info = None
	for nested in prop_info.NestedObjects:
		if re.match(r'^%s$' % shape_name, nested.Name):
			prop_shape_info = nested
			break
	if not prop_shape_info:
		log('Unable to find "%s" on "%s"' % (shape_name, prop_info.FullName), c.siError)
		return False
	
	# clear the vectors and driven keys #
	ps.vectors.Clear()
	ps.RemoveDriven()
	
	# step through all the parameters #
	for param in prop_shape_info.Parameters:
		# catch driven keys #
		if re.match(r'^Driven.*$', param.Name, re.I):
			log('Driven key: %s' % param.Name)
			
			# get the driving object #
			driven_key = None
			try:
				driven_key = xsi.Dictionary.GetObject(param.Value)
			except:
				log('Unable to find driving parameter "%s"' % param.Value, c.siError)
				log('Might need to update value at "%s"' % param.FullName, c.siError)
				return False
				
			# get the fcurve #
			fcurve = driven_key.Source
			fcurve = dispatch(fcurve)
			
			# get the curve type #
			curve_type = 'linear'
			if fcurve.Interpolation == 1:
				curve_type = 'constant'
			elif fcurve.Interpolation == 2:
				curve_type = 'linear'
			elif fcurve.Interpolation == 3:
				curve_type = 'spline'
				
			# add the driven key element #
			expr_str = expr_str.replace('l_fcv( ', '').replace(' )', '')
			driven = ps.AddDriven()
			driven.curve 	= curve_type
			driven.node		= expr_str.split('.')[1]
			driven.channel 	= expr_str.split('.')[-1]
			
			# add the keys #
			for key in fcurve.Keys:
				k = driven.AddKey()
				k.value 	= key.Time
				k.weight 	= key.Value
				
		# catch vector weights #
		elif re.match(r'^Vector.*$', param.Name, re.I):
			log('Vector Weight: %s' % param.Value)

			# get the driving object #
			vector_prop = None
			try:
				vector_prop = xsi.Dictionary.GetObject(param.Value)
			except:
				log('Unable to find vector prop "%s"' % param.Value, c.siError)
				log('Might need to update value at "%s"' % param.FullName, c.siError)
				return False
				
			# create a new vector in the xml file and set values #
			vector = ps.vectors.Add()
			axis_str = 'X'
			if vector_prop.Axis.Value == 1:
				axis_str = 'Y'
			elif vector_prop.Axis.Value == 2:
				axis_str = 'Z'
			vector.axis 		= axis_str
			vector.clamp 		= vector_prop.Clamp.Value
			vector.invert 		= vector_prop.Invert.Value
			vector.manips 		= vector_prop.DirectManips.Value
			vector.node 		= vector_prop.Parent3DObject.Name
			vector.scale 		= vector_prop.Scale.Value
			vector.visualize 	= vector_prop.Visualize.Value
			# rest vector #
			vector.rest.x		= vector_prop.RestVectorX.Value
			vector.rest.y		= vector_prop.RestVectorY.Value
			vector.rest.z		= vector_prop.RestVectorZ.Value
			# target vector #
			vector.target.x		= vector_prop.TargetVectorX.Value
			vector.target.y		= vector_prop.TargetVectorY.Value
			vector.target.z		= vector_prop.TargetVectorZ.Value

	# save the new contents file #
	ps.Save()
			
	return
	
	# # step through the geom #
	# for obj in ps.objs.children:
	# 	# find the geometry #
	# 	xsi_geom = model.FindChild(obj.name, '', [c.siMeshFamily,c.siNurbsSurfaceMeshFamily])
	# 	if not xsi_geom:
	# 		log('Unable to locate geom "%s".  Skipping update.' % obj.name, c.siError)
	# 		return False
	# step through the parameters #
	for param in prop_poses.Parameters:
		# find the corresponding shape #
		if re.match(r'%s' % ps.pose_name, param.Name):
			# get the expression #
			if not param.Source.Type != 'expression':
				log('Unable to locate driving vector object for shape "%s"' % ps.pose_name, c.siError)
				return False
			expr = param.Source
			expr_str = expr.Parameters('Definition').Value
			
			# clear the xml vectors #
			ps.vectors.Clear()
			# clear out the driven #
			ps.RemoveDriven()

			# catch driven keys #
			driven_key = expr.Parameters('l_fcv')
			if driven_key:
				# get the fcurve #
				fcurve = driven_key.Source
				fcurve = dispatch(fcurve)
				
				# get the curve type #
				curve_type = 'linear'
				if fcurve.Interpolation == 1:
					curve_type = 'constant'
				elif fcurve.Interpolation == 2:
					curve_type = 'linear'
				elif fcurve.Interpolation == 3:
					curve_type = 'spline'
					
				# add the driven key element #
				expr_str = expr_str.replace('l_fcv( ', '').replace(' )', '')
				driven = ps.AddDriven()
				driven.curve 	= curve_type
				driven.node		= expr_str.split('.')[1]
				driven.channel 	= expr_str.split('.')[-1]
				
				# add the keys #
				for key in fcurve.Keys:
					k = driven.AddKey()
					k.value 	= key.Time
					k.weight 	= key.Value
					
				# save the xml file #
				ps.Save()
				# all good, lets get out of here #
				return
			
			# get the driving object #
			log(expr_str)
			splits = expr_str.split('.')
			vector_obj_name = '%s.%s' % (splits[0], splits[1])
			vector_obj = model.FindChild(vector_obj_name)
			# get the properties #
			for prop in vector_obj.Properties:
				if re.match(r'.+%s.+' % ps.pose_name, prop.Name, re.I):
					# skip the blend nodes #
					if re.match(r'.+_Blend$', prop.Name, re.I): continue
					# create a new vector in the xml file and set values #
					vector = ps.vectors.Add()
					axis_str = 'X'
					if prop.Axis.Value == 1:
						axis_str = 'Y'
					elif prop.Axis.Value == 2:
						axis_str = 'Z'
					vector.axis 		= axis_str
					vector.clamp 		= prop.Clamp.Value
					vector.invert 		= prop.Invert.Value
					vector.manips 		= prop.DirectManips.Value
					vector.node 		= vector_obj.Name
					vector.scale 		= prop.Scale.Value
					vector.visualize 	= prop.Visualize.Value
					# rest vector #
					vector.rest.x		= prop.RestVectorX.Value
					vector.rest.y		= prop.RestVectorY.Value
					vector.rest.z		= prop.RestVectorZ.Value
					# target vector #
					vector.target.x		= prop.TargetVectorX.Value
					vector.target.y		= prop.TargetVectorY.Value
					vector.target.z		= prop.TargetVectorZ.Value
			# we found the vector object, so let's get out of here #
			ps.Save()
			return
							
#-----------------------------------------------------------------------------

def zPoseShapeContents_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	# oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments
	oArgs.Add("dir_pose_shape", c.siArgumentInput, '', c.siString)

	return True

def zPoseShapeContents_Execute(dir_pose_shape):
	# export the python object #
	import win32com.server
	# from zPoseShapeContents import zPoseShapeContents
	import zPoseShapeContents
	reload(zPoseShapeContents)
	return win32com.server.util.wrap(
		zPoseShapeContents.zPoseShapeContents(dir_pose_shape)
	)
		
#-----------------------------------------------------------------------------

def zPoseShapeImportDirectory_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	#oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments
	oArgs.AddObjectArgument('model')
	oArgs.Add('dir_pose_shape', c.siArgumentInput, '', c.siString)
	oArgs.Add('path_pose_rest', c.siArgumentInput, '', c.siString)
	oArgs.Add('obj_cluster_mode', c.siArgumentInput, 1, c.siUInt2)

	return True
	
def zPoseShapeImportDirectory_Execute(model, directory, path_pose_rest, obj_cluster_mode):
	'''
	Imports all the pose shapes (.zpshp) in a given directory.
	'''
	all_zpshp = glob.glob(directory + os.sep + '*.zpshp')
	for zpshp in all_zpshp:
		xsi.zPoseShapeImport(model, zpshp, path_pose_rest, None, None, obj_cluster_mode)

#-----------------------------------------------------------------------------

def zPoseShapeDelete_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	# oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments
	oArgs.AddObjectArgument("model")
	oArgs.Add("pose_name", c.siArgumentInput, '', c.siString)

	return True

def zPoseShapeDelete_Execute(model, pose_name):
	
	# find the zPoseShapes property on the model #
	prop_pshapes = model.Properties('zPoseShapes')
	if not prop_pshapes:
		log('Unable to find "zPoseShapes" property on model "%s"' % model.FullName, c.siError)
		return -1
		
	# find the zPoseShapeInfo #
	prop_info = None
	for prop in prop_pshapes.NestedObjects:
		if re.match(r'^zPShapeInfo$', prop.Name, re.I): prop_info = prop
	if not prop_info:
		log('Unable to find "zPShapeInfo" property on "%s"' % prop_pshapes.FullName, c.siError)
		return -1
		
	# find the zPoseShapes #
	prop_shapes = None
	for prop in prop_pshapes.NestedObjects:
		if re.match(r'^zPShapes$', prop.Name, re.I): prop_shapes = prop
	if not prop_info:
		log('Unable to find "zPShapes" property on "%s"' % prop_pshapes.FullName, c.siError)
		return -1
		
	# find the zPoseShapeInfo."PoseShapeName" #
	prop_shape_info = None
	for prop in prop_info.NestedObjects:
		if re.match(r'^%s$' % pose_name, prop.Name, re.I): prop_shape_info = prop
	if not prop_shape_info:
		log('Unable to find "%s" property on "%s"' % (pose_name, prop_info.FullName), c.siError)
		return -1
		
	# create a collection for deleting #
	col_del = dispatch('XSI.Collection')
	
	# add the properties #
	col_del.Add(prop_shape_info)
	
	# reomve the slider on zPShapes #
	for param in prop_shapes.Parameters:
		if re.match(r'^%s$' % pose_name, param.Name, re.I):
			prop_shapes.RemoveParameter(param)
			break

	# step through the parameters on the info node #
	for param in prop_shape_info.Parameters:

		# remove the blends #
		if re.match(r'^Blend', param.Name, re.I):
			try:
				om_blend = xsi.Dictionary.GetObject(param.Value)
				col_del.Add(om_blend)
			except:
				log('Unable to find blend: %s' % param.Value)
		
		# catch vector weights #
		if re.match(r'^Vector', param.Name, re.I):
			try:
				om_vector = xsi.Dictionary.GetObject(param.Value)
				col_del.Add(om_vector)
			except:
				log('Unable to find vector weight: %s' % param.Value)
			
		# catch shape keys #
		if re.match(r'^ShapeKey', param.Name, re.I):
			try:
				om_shapekey = xsi.Dictionary.GetObject(param.Value)
				col_del.Add(om_shapekey)
			except:
				log('Unable to find shape key: %s' % param.Value)
			
		
	# delete #
	log('Deleting:')
	for item in col_del:
		log('  - %s' % item.FullName)
	xsi.DeleteObj(col_del)
	
	# return success #
	return 1
		
	
#-----------------------------------------------------------------------------

def zPoseShapeTransferGeo_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	# oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments
	oArgs.AddObjectArgument("model_old_geo")
	oArgs.AddObjectArgument("model_new_geo")
	oArgs.Add("dir_pose_shape", c.siArgumentInput, '', c.siString)
	oArgs.Add("dir_new_pose", c.siArgumentInput, '', c.siString)
	oArgs.Add("overwrite", c.siArgumentInput, False, c.siBool)
	oArgs.Add("obj_cluster_mode", c.siArgumentInput, 1, c.siUInt2)

	return True

def zPoseShapeTransferGeo_Execute(model_old_geo, model_new_geo, dir_pose_shape, dir_new_pose, overwrite, obj_cluster_mode):
	
	# make sure the file exists #
	if not os.path.exists(dir_pose_shape):
		log('Unable to locate path: %s' % dir_pose_shape, c.siError)
		return None
		
	# make sure the models exists and are models #
	if model_old_geo.type != '#model':
		log('Model argument "%s" not a model' % model_old_geo, c.siError)
		return False
	if model_new_geo.type != '#model':
		log('Model argument "%s" not a model' % model_old_geo, c.siError)
		return False

	# get the contents #
	ps = xsi.zPoseShapeContents(dir_pose_shape)
	ps.Load()
		
	# check for the same number of obj files #
	path_originals 	= dir_pose_shape + os.sep + 'objs_original'
	path_fixed	 	= dir_pose_shape + os.sep + 'objs_fixed'
	objs_original 	= glob.glob('%s/*.obj' % path_originals)
	objs_fixed 		= glob.glob('%s/*.obj' % path_fixed)
	# Note: This is here because maya need to NOT export multiple objects in the same obj
	# file or else they scramble the point ids
	if len(objs_original) != len(objs_fixed):
		log('Number of obj files don\'t match.  %d original != %d fixed.' \
		% (len(objs_original), len(objs_fixed)), c.siError)
		return False

	# get the pose #
	file_pose = ps.pose.file
	
	# make sure the pose files exists #
	path_pose = dir_pose_shape + os.sep + file_pose
	if not os.path.exists(path_pose):
		log('Unable to locate pose "%s".' % path_pose, c.siError)
		return False
		
	# get the pose shape name #
	name_pose_shape = os.path.basename(dir_pose_shape).split('.')[0]

	# import the new obj's #
	geom_imported = []
	for obj_file in objs_fixed:
		geom_import = xsi.ObjImport(obj_file, 1-obj_cluster_mode, 0, 1, 1, 0, 1)
		if geom_import.Count > 1:
			log('Obj file %s contains multiple objs.  Not expecting this.  Could cause errors.' % obj_file, c.siWarning)
		geom_imported.append(geom_import(0))
		log('Imported: %s' % geom_import(0))
		
	# find corresponding geo #
	# map_geom_new = {}
	# map_geom_old = {}
	map_geom = {}
	for geom_import in geom_imported:
		
		# process the new geometry #
		geom_target_new = model_new_geo.FindChild(geom_import.Name)

		# find the old geom #
		geom_target_old = model_old_geo.FindChild(geom_import.Name)

		# get all the geometry in the new model #
		all_new_geom = model_new_geo.FindChildren('', '', [c.siMeshFamily, c.siNurbsSurfaceMeshFamily])

		# get all the geometry in the new model #
		all_old_geom = model_old_geo.FindChildren('', '', [c.siMeshFamily, c.siNurbsSurfaceMeshFamily])

		# did we find new geometry by name #
		if geom_target_new:
			# add it to the mapping dictionary #
			map_geom[geom_import.Name] = {
				'imported': 	geom_import,
				'new': 			geom_target_new
			}
		else:
			# try and find it by cluster names #
			for cluster in geom_import.ActivePrimitive.Geometry.Clusters:
				if cluster.type == 'poly':
					# step through all the new geom #
					for new_geom in all_new_geom:
						# match by the cluster name #
						if re.match(cluster.Name, new_geom.Name, re.I) or \
						re.match(new_geom.Name, cluster.Name, re.I):
							log('Found corresponding geom by cluster for %s -> %s' % (geom_import.FullName, new_geom.FullName))
							map_geom[geom_import.Name] = {
								'imported': 	geom_import,
								'new': 			new_geom
							}
							# on to the next piece #
							break

		# we should have a key from the new geom, if not, we can't do anything #
		if not geom_import.Name in map_geom.keys():
			log('Unable to locate new geometry for %s in %s' % (geom_import.FullName, model_new_geo), c.siError)
			return False

		# did we find old geometry by name #
		if geom_target_old:
			# add it to the mapping dictionary #
			map_geom[geom_import.Name]['old'] = geom_target_old
		else:
			# try and find it by cluster names (similar to above)#
			for cluster in geom_import.ActivePrimitive.Geometry.Clusters:
				if cluster.type == 'poly':
					# step through all the new geom #
					for old_geom in all_old_geom:
						# match by the cluster name #
						if re.match(cluster.Name, old_geom.Name, re.I) or \
						re.match(old_geom.Name, cluster.Name, re.I):
							log('Found corresponding geom by cluster for %s -> %s' % (geom_import.FullName, old_geom.FullName))
							map_geom[geom_import.Name]['old'] = old_geom
							# on to the next piece #
							break

	if not len(map_geom.keys()):
		log('Unable to map poseshape geom to the new geom')
		return False
		
	# create the new pose shape directory #
	if os.path.exists(dir_new_pose):
		if not overwrite:
			log('Pose shape "%s" all ready exists and "overwrite" is not turned on' % dir_new_pose, c.siError)
			return False
		else:
			shutil.rmtree(dir_new_pose)
	
	# copy the old pose shape #
	shutil.copytree(dir_pose_shape, dir_new_pose)
	
	# remove the fixed geometry #
	path_fixed_new = dir_new_pose + os.sep + "objs_fixed"
	for item in os.listdir(path_fixed_new):
		os.unlink(path_fixed_new + os.sep + item)
		
	# update the header info #
	ps = xsi.zPoseShapeContents(dir_new_pose)
	ps.Load()
	ps.UpdateInfo()
	ps.Save()
	
	# create a collection to hold all the items to delete at the end #
	col_del = dispatch('XSI.Collection')
	
	# step through the mapped geom #
	for key in map_geom.keys():
		geom_old 		= map_geom.get(key).get('old')
		geom_new 		= map_geom.get(key).get('new')
		geom_imported   = map_geom.get(key).get('imported')
		
		log('geom_old: %s' % geom_old)
		log('geom_new: %s' % geom_new)
		log('geom_imported: %s' % geom_imported)
		
		# add imported geom to del col #
		col_del.Add(geom_imported)

		# apply the shapes to the original model #
		unique_shape_name = name_pose_shape + '__' + geom_old.name
		# shape_key = xsi.StoreShapeKey(geom_old, unique_shape_name, c.siShapeObjectReferenceMode, "", "", "", c.siShapeContentSecondaryShape, True)
		log('Adding imported obj "%s" as shape to old geom "%s".' % (geom_imported, geom_old))
		shape_key = xsi.SelectShapeKey(geom_old, geom_imported, c.siShapeObjectReferenceMode, False, False)(0)
		
		# log('Shape Key: %s' % shape_key)
		col_del.Add(shape_key)
		
		# apply the shape key #
		clip = xsi.ApplyShapeKey(shape_key, '', '', 1, '', 5, '', 2)
		col_del.Add(clip)

		# set the value to 0 #
		clip.Weight.Value = 0
	
		# apply the gator op #
		log('Gatoring "%s" to "%s"' % (geom_new.FullName, geom_old.FullName))
		gator = xsi.ApplyGenOp(
			"Gator", 
			"", 
			"%s;%s" % (geom_new.FullName, geom_old.FullName), 
			3, 
			"siPersistentOperation", 
			"siKeepGenOpInputs", 
			""
		)(0)
		log('Gator: %s' % gator)
		col_del.Add(gator)
		
		# gator the shapes to the new geom model #
		shape_key_new = xsi.TransferClusterPropertiesAcrossGenOp(
			gator,
			geom_new, 
			shape_key, 
			name_pose_shape + '__' + geom_new.name, 
		)
		col_del.Add(shape_key_new)
		log('New Shape Key: %s' % shape_key_new)
		log('New Shape Key Group Name: %s' % shape_key_new.ShapeGroupName)
		
		# freeze the gator op #
		xsi.FreezeObj(gator)
		
		# apply and turn on the shape #
		clip = xsi.ApplyShapeKey(shape_key_new, '', '', 1, '', 5, '', 2)
		col_del.Add(clip)
		clip.Weight.Value = 1
		
		# export the obj #
		file_obj = path_fixed_new + os.sep + geom_new.Name + ".obj"
		xsi.Selection.Clear()
		xsi.Selection.Add(geom_new)
		xsi.ObjExport(file_obj, 0, "", "", "", "", "", "", "", "", 0, 0, 0, 0, 0)
		xsi.Selection.Clear()
		log('Exported update obj for "%s" to "%s"' % (geom_new.Name, file_obj))
		

	# cleanup #
	log("Cleaning and Deleting: ")
	for item in col_del:
		log('  - %s' % item)
	xsi.DeleteObj(col_del)

	return True
	
#-----------------------------------------------------------------------------

def zPoseShapeTransferGeoGUI_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	#oCmd.SetFlag(constants.siNoLogging,false)

	return True
	
def zPoseShapeTransferGeoGUI_Execute():
	
	# create the menu on the scene root if it doesn't exist #
	prop = xsi.ActiveSceneRoot.Properties('zPoseShapeTransferGeoGUI')
	if not prop:
		prop = xsi.ActiveSceneRoot.AddProperty('zPoseShapeTransferGeoGUI')
	prop = dispatch(prop)
	
	# show the GUI #
	xsi.InspectObj(prop, '', '', c.siLockAndForceNew, False)

#-----------------------------------------------------------------------------

def zPoseShapeMirrorGUI_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	#oCmd.SetFlag(constants.siNoLogging,false)

	return True
	
def zPoseShapeMirrorGUI_Execute():
	
	# create the menu on the scene root if it doesn't exist #
	prop = xsi.ActiveSceneRoot.Properties('zPoseShapeMirrorGUI')
	if not prop:
		prop = xsi.ActiveSceneRoot.AddProperty('zPoseShapeMirrorGUI')
	prop = dispatch(prop)
	
	# show the GUI #
	xsi.InspectObj(prop, '', '', c.siLockAndForceNew, False)

#-----------------------------------------------------------------------------

def zPoseShapeMirror_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	#oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments
	oArgs.AddObjectArgument('target_model')
	oArgs.Add('dir_pose_shape', c.siArgumentInput, '', c.siString)	
	oArgs.Add('dir_new_shape', c.siArgumentInput, '', c.siString)	
	oArgs.Add('mirror_pose', c.siArgumentInput, '', c.siString)	
	oArgs.Add('from_string', c.siArgumentInput, 'L', c.siString)	
	oArgs.Add('to_string', c.siArgumentInput, 'R', c.siString)	
	oArgs.Add('obj_cluster_mode', c.siArgumentInput, True, c.siBool)
	
	return True
	
def zPoseShapeMirror_Execute(
	target_model,	
	dir_pose_shape,	
	dir_new_shape,	
	mirror_pose,		
	obj_cluster_mode
):
	
	# create the menu on the scene root if it doesn't exist #
	prop = xsi.ActiveSceneRoot.Properties('zPoseShapeTransferGeoGUI')
	if not prop:
		prop = xsi.ActiveSceneRoot.AddProperty('zPoseShapeTransferGeoGUI')
	prop = dispatch(prop)
	
	# show the GUI #
	xsi.InspectObj(prop, '', '', c.siLockAndForceNew, False)
	
	
	
	