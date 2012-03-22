"""
Module containing all root classes for characters to build on.

Example:

>>> root = xsi.zRoot('ABY')
>>> root.template.model				= xsi.ActiveSceneRoot
>>> root.template.GetFromScene()
>>> root.rig.Build()

Created by andy on 2008-07-22.
Copyright (c) 2008 Zoogloo LLC. All rights reserved.
"""

__version__ = '$Revision: 186 $'
__author__  = '$Author: andy $'
__date__    = '$Date: 2009-02-17 16:35 -0800 $'

import win32com.client
import win32com.server
from win32com.client import constants
from win32com.client import constants as c
from win32com.client.dynamic import Dispatch as dispatch
import re

xsi = Application
log = xsi.logmessage

null = None
false = 0
true = 1

def XSILoadPlugin(in_reg):
	in_reg.Author = "Andy Buecker"
	in_reg.Name = "zRoot"
	in_reg.Email = "andy@zoogloo.net"
	in_reg.URL = ""
	in_reg.Major = 1
	try:
		in_reg.Minor = int(__version__.split(' ')[1])
	except:
		in_reg.Minor = 0

	in_reg.RegisterCommand('zRoot', 'zRoot')
	
	# copyright message #
	msg = '''
#------------------------------------------#
  %s (v.%d.%d)
  Copyright 2008 Zoogloo LLC.
  All rights Reserved.
#------------------------------------------#
	''' % (in_reg.Name, in_reg.Major, in_reg.Minor)
	log(msg)

	return true

def XSIUnloadPlugin(in_reg):
	strPluginName = in_reg.Name
	Application.LogMessage(str(strPluginName) + str(" has been unloaded."))
	return true

#-----------------------------------------------------------------------------
# Classes
#-----------------------------------------------------------------------------

def zProp(function):
	'''
	Easy function decorator for accessing properties.
	
	Usage:
	
	>>> @zProp
	>>> def Connection():
	>>> 	\'''connection\'''
	>>> 	def fget(self):
	>>> 		return self._cnx
	>>>		def fset(self, value):
	>>>			self._cnx = value
	>>>		def fdel(self):
	>>>			raise Exception, "Can't delete attribute 'Connection'"
	>>> 	return locals()
	
	'''
	return property(doc=function.__doc__, **function())

class zRoot(object):
	'''
	
	Example:
	
	>>> root = xsi.zRoot('ABY')
	>>> root.template.model				= xsi.ActiveSceneRoot
	>>> root.template.GetFromScene()
	>>> root.rig.Build()

	'''
	# required for COM wrapper #
	_public_methods_ = [
	]
	# define the output vars here #
	_public_attrs_ = [
		'rig',
		'template',
		'scale',
		'basename',
		'symmetry',
		'digit',
	]
	# define those attrs that are read only #
	_readonly_attrs_ = [
		'rig',
		'template',
	]

	# set the class variables #
	_template 		= None
	_rig 			= None
	uid				= 'aa9133399d406e1cb3c4c34080de87af'
	basename		= 'Root'
	scale			= 1
	prefix			= 'PFX'
	
	def __init__(self, prefix='PFX'):
		'''
		@param prefix: The prefix to use for the model.
		'''
		super(zRoot, self).__init__()
		
		# reset the instance varaibles #
		self._template		= None
		self._rig	  		= None
		self.basename		= 'Root'
		self.scale			= 1
		self.prefix			= prefix
		
	@zProp
	def template():
		'''Template Accessor'''
		def fget(self):
			# create a template if it doesn't exist #
			if not self._template:
				# wrap a new class #
				self._template = win32com.server.util.wrap(zRoot_Template(self))
			return dispatch(self._template)
		def fset(self, value):
			raise Exception('Unable to modify template value')
		fdel = fset
		return locals()
		
	@zProp
	def rig():
		'''Rig accessor'''
		def fget(self):
			# create a rig class if it doesn't exist #
			if not self._rig:
				# wrap a new class #
				self._rig = win32com.server.util.wrap(zRoot_Rig(self))
			# return the private var #
			return dispatch(self._rig)
		def fset(self, value):
			raise Exception('Unable to modify rig value.')
		fdel = fset
		return locals()
			
				
class zRoot_Template(object):
	"""
	Template for laying out the root component.
	
	>>> root = xsi.zRoot('ABY')
	>>> root.template.model				= xsi.ActiveSceneRoot
	>>> root.template.Draw()
	>>> # or if the template is allready in the scene #
	>>> root.template.GetFromScene()
	"""
	
	_inputs_ = [
		'v_center', 
		'v_flight', 
	]
	
	# required for COM wrapper #
	_public_methods_ = [
		'Draw',
		'LoadDefaultValues',
		'GetFromScene',
	]
	# define the output vars here #
	_public_attrs_ = [
		'parent',
		'model',
		'scale',
	]
	_public_attrs_ += _inputs_
	# define those attrs that are read only #
	_readonly_attrs_ = [
		'parent'
	]

	def __init__(self, parent):
		super(zRoot_Template, self).__init__()
		
		# set the instance variables #
		self.parent			= parent
		self.scale 			= 1
		self.model 			= None
		
		# load the defaults #
		self.LoadDefaultValues()
	
	def LoadDefaultValues(self):
		"""
		Loads the default values for the template. 
		"""
		# create new vectors #
		self.v_center	= XSIMath.CreateVector3(0,42.127, -0.398)
		self.v_flight	= XSIMath.CreateVector3(0,46.127, -0.398)
		
		# set the model #
		self.model = xsi.ActiveSceneRoot

	def Draw(self):
		"""
		Draws the component template under the model specified in zRoot.template.model
		"""
		# get the model #
		if not self.model:
			raise Exception('Model attribute for template not specified.')

		# dispatch the model #
		self.model = dispatch(self.model)

		#---------------------------------------------------------------------
		# create a node to hold the template #
		node_parent = self.model.AddNull(
			xsi.zMapName('Root', 'Custom:Container', 'None')
		)
		node_parent.primary_icon.Value = 0
		node_parent.Properties('Visibility').Parameters('viewvis').Value = False
		node_parent.Properties('Visibility').Parameters('rendvis').Value = False
		node_parent.AddProperty('CustomProperty', False, 'zBuilderTemplateItem')
		prop = node_parent.AddProperty('CustomProperty', False, 'zContainer')
		prop = dispatch(prop)
		prop.AddParameter3('ContainerName', c.siString, 'Root')
		prop.AddParameter3('ContainerUID', c.siString, self.parent.uid)
		
		#---------------------------------------------------------------------
		# draw the nodes #
		node_center 	= node_parent.AddNull(xsi.zMapName('Center', 'Custom:Tmp', 'Mid'))
		node_center.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_center.AddProperty('CustomProperty', False, 'zCenter')

		node_center 	= node_parent.AddNull(xsi.zMapName('Flight', 'Custom:Tmp', 'Mid'))
		node_center.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_center.AddProperty('CustomProperty', False, 'zFlight')

		#---------------------------------------------------------------------
		# set the positions #
		trans = XSIMath.CreateTransform()
		v_result = XSIMath.CreateVector3()

		# center #
		v_result.Scale(self.parent.scale, self.v_center)
		trans.Translation = v_result
		node_center.Kinematics.Global.Transform = trans
		
	def GetFromScene(self):
		"""
		Gets the template values from the template model specified in zRoot.template.model
		"""
		
		#---------------------------------------------------------------------
		# make sure the model exists 
		if not self.model:
			raise Exception('Model attribute for template not specified.')
		
		#---------------------------------------------------------------------
		# find the container #
		node_parent = None
		for node in dispatch(self.model).FindChildren('*'):
			if node.Properties('zContainer'):
				# get the container by the id #
				if node.Properties('zContainer').Parameters('ContainerUID').Value == self.parent.uid:
					node_parent = node
					break
		# make sure we have the container #
		if not node_parent:
			raise Exception('Unable to find template container by id: %s' % (self.parent.uid))
		
		#---------------------------------------------------------------------
		# get all the nodes under the container #
		child_nodes = node_parent.FindChildren('*')

		#---------------------------------------------------------------------
		# get the vectors or transform #
		for node in child_nodes:
			if node.Properties('zCenter'):
				self.v_center = node.Kinematics.Global.Transform.Translation
			if node.Properties('zFlight'):
				self.v_flight = node.Kinematics.Global.Transform.Translation
		
class zRoot_Rig(object):
	"""
	Example:

	>>> root = xsi.zRoot('ABY')
	>>> root.template.LoadDefaulValues()
	>>> root.rig.Build()
	
	@cvar size_flight_con: size for the flight controller
	@cvar size_all_con: size for all controller
	
	@cvar node_geom_rig: 		output node for the geometry rig
	@cvar node_geom_render: 	output node for the render geometry
	@cvar node_skeleton:		output node for the skeleton geometry
	@cvar node_lower_body:		output node for the lower body controls
	@cvar node_geom_anim		output node for the animatin geometry
	@cvar node_do_not_touch:	output node for the do not touch hierarchy
	@cvar node_center:			output node for the center node
	@cvar node_upper_body:		output node for the upper body hierarchy
	@cvar node_controls:		output node for the controls hierarchy
	@cvar node_deformers:		output node for the deformers hierarchy
	@cvar group_controls:		output for the controls group
	@cvar group_deformers:		output for the deformer group
	@cvar group_geom_rndr:		output for the geo render group
	@cvar group_geom_anim		output for the geo anim group
	@cvar group_geom_rig:		output for the geo rig group
	@cvar deformers:			output collection for the deformers in this class
	@cvar character_set:		output collection for the character set
	@cvar con_scale:			output zCon for the scale controller
	@cvar con_offset:			output zCon for the offset controller
	@cvar con_flight_path:		output zCon for the flight path controller
	@cvar con_flight:			output zCon for the flight controller
	@cvar con_all:				output zCon for the all controller
	@cvar data:					output node for the data node
	@cvar info:					output property for the info property
	@cvar model:				output model for the character model node
	"""
	
	_inputs_ = [
		'controls_parent',  		
		'character_root',   		
		'skeleton_parent',  		
		'deformer_parent',  
		'size_flight_con',
		'size_all_con',		
	]
	_outputs_ = [
		'parent',
		'node_geom_rig',
		'node_geom_render',
		'node_skeleton',
		'node_lower_body',
		'node_geom_anim',
		'node_do_not_touch',
		'node_center',
		'node_upper_body',
		'node_controls',
		'node_deformers',		
		'group_controls',
		'group_deformers',
		'group_geom_rndr',
		'group_geom_anim',
		'group_geom_rig',
		'deformers',
		'character_set',
		'con_scale',
		'con_offset',
		'con_flight_path',
		'con_flight',
		'con_all',
		'data',
		'info',
		'model',
	]
	# required for COM wrapper #
	_public_methods_ = [
		'Build',
	]
	# define the output vars here #
	_public_attrs_ = [
	]
	_public_attrs_ += _inputs_ + _outputs_
	# define those attrs that are read only #
	_readonly_attrs_ = [
	]
	_readonly_attrs_ += _outputs_

	def __init__(self, parent):
		super(zRoot_Rig, self).__init__()
		
		# set the instance variables #
		self.parent					= parent

		# set the defaults for the input variables #
		for item in self._inputs_:
			setattr(self, item, None)
			
		# set specific types #
		self.deformers = dispatch('XSI.Collection')
		
		# set the default con size #
		self.size_flight_con 	= 8
		self.size_all_con		= 3
	
	# override the attribute setter to dispatch objects when setting #
	def __setattr__(self, name, value):
		# if the name is in the inputs...#
		if name in self._public_attrs_:
			# ... dispatch the value (if we can)#
			try:
				self.__dict__[name] = dispatch(value)
			except:
				self.__dict__[name] = value
		else:
			raise Exception('Unable to locate public attribute "%s"' % (name))
			
	def Build(self):
		'''
		Builds the rig.
		'''

		# create a model #
		self.model = xsi.ActiveSceneRoot.AddModel(None, '%s1' % self.parent.prefix)
		self.model.Properties('Visibility').Parameters('viewvis').Value = False
		
		# create a data null #
		self.data = self.model.AddNull('_DATA_')
		self.data.primary_icon.Value = 0
		self.data.Properties('Visibility').Parameters('viewvis').Value = False
		self.data.Properties('Visibility').Parameters('rendvis').Value = False

		# get the time and build a version #
		import time
		t = time.localtime()
		version = '%2s%02d%02d' % (str(t[0])[-2:], t[1], t[2])
		
		# set the info #
		self.info 				= self.data.AddProperty('zInfo')
		self.info.Version.Value = version
		self.info.Prefix.Value	= self.parent.prefix
		
		# create the default groups on the model #
		self.group_deformers	= self.model.AddGroup(None, xsi.zMapName('Deformers', 'Group', 'None'))
		self.group_controls 	= self.model.AddGroup(None, xsi.zMapName('Controlers', 'Group', 'None'))
		self.group_geom_rndr 	= self.model.AddGroup(None, xsi.zMapName('GeomRndr', 'Group', 'None'))
		self.group_geom_anim 	= self.model.AddGroup(None, xsi.zMapName('GeomAnim', 'Group', 'None'))
		self.group_geom_rig 	= self.model.AddGroup(None, xsi.zMapName('GeomRig', 'Group', 'None'))
		
		# set group selectability #
		self.group_geom_rndr.selectability.Value = 0
		self.group_geom_rig.selectability.Value = 0

		# make the geom lo not renderable #
		self.group_geom_anim.rendvis.Value = 0
		self.group_geom_rig.rendvis.Value = 0
		
		# create a character set #
		self.character_set = xsi.zCharacterSet('CharacterSet', self.model)

		#---------------------------------------------------------------------
		# draw the OFFSET null #
		# 	TODO: add class variable for the OFFSET name
		self.con_offset 				= xsi.zCon()
		self.con_offset.type 			= 'null'
		self.con_offset.size 			= self.parent.scale
		self.con_offset.basename 		= 'Offset'
		self.con_offset.transform 		= self.model.Kinematics.Global.Transform
		self.con_offset.parent_node 	= self.model
		self.con_offset.red 			= 1
		self.con_offset.green 			= 0.5
		self.con_offset.blue 			= 0
		self.con_offset.Draw()
		self.con_offset.AddTransformSetupPos('global')
		
		# turn off the con #
		self.con_offset.node_con.Properties('Visibility').viewvis.Value = False
		
		# add it to the controls group #
		self.group_controls.AddMember(self.con_offset.node_con)
		
		# add to character set #
		stack_set = self.character_set.AddSubset('Stack')
		stack_set.AddNodePosRot(self.con_offset.node_con)
		
		#---------------------------------------------------------------------
		# draw the ALL null #
		# 	TODO: add class variable for the ALL name
		self.con_all 				= xsi.zCon()
		self.con_all.type 			= 'null'
		self.con_all.size 			= self.size_all_con * self.parent.scale
		self.con_all.basename 		= 'All'
		self.con_all.transform 		= self.con_offset.node_hook.Kinematics.Global.Transform
		self.con_all.parent_node 	= self.con_offset.node_hook
		self.con_all.red 			= 1
		self.con_all.green 			= 0.5
		self.con_all.blue 			= 0
		self.con_all.Draw()
		self.con_all.AddTransformSetupPos('local')
		
		# reparent the hook node and remove the old con #
		self.con_all.node_rest.AddChild(self.con_all.node_hook)
		xsi.DeleteObj(self.con_all.node_con)
		
		# draw the text controller #
		self.con_all.node_con = self.con_all.node_rest.AddGeometry(
			'Text', 
			'NurbsCurve', 
			xsi.zMapName('all', 'Control', 'Middle')
		)
		self.con_all.node_con.text = "_RTF_{\\rtf1\\ansi\\deff0{\\fonttbl{\\f0\\fnil\\fprq5\\fcharset0 Arial;}}\r\n\\viewkind4\\uc1\\pard\\qc\\lang1033\\b\\f0\\fs20 %s\\b0\\par\r\n}\r\n" % \
		 	(self.parent.prefix + '1')
		
		# zero the node #
		self.con_all.node_con.Kinematics.Global.Transform = self.con_all.node_rest.Kinematics.Global.Transform
		
		# move it below the character #
		self.con_all.node_con.Kinematics.Global.Parameters('posy').Value = -(self.size_all_con * self.parent.scale) - (2 * self.parent.scale)
		xsi.ResetTransform(self.con_all.node_con, "siCtr", "siTrn", "siXYZ")
		xsi.SetValue('%s.TextToCurveList.fitsize' % self.con_all.node_con.FullName, self.size_all_con * self.parent.scale)

		# add to the controls group #
		self.group_controls.AddMember(self.con_all.node_con)

		# add to character set #
		self.character_set.AddNodePosRot(self.con_all.node_con)

		# change the color of the all node #
		# 	TODO: add class variable for the all wire color
		disp = self.con_all.node_con.AddProperty('Display Property', False)
		disp = dispatch(disp)
		disp.wirecolorr.Value = 1
		disp.wirecolorg.Value = 0.5
		disp.wirecolorb.Value = 0
		
		# put the hook back under the con #
		self.con_all.node_con.AddChild(self.con_all.node_hook)
		
		#---------------------------------------------------------------------
		# add a SCALE controller #
		# 	TODO: add class variable for the scale name
		self.con_scale 					= xsi.zCon()
		self.con_scale.type 			= 'null'
		self.con_scale.size 			= self.parent.scale
		self.con_scale.basename 		= 'Scale'
		self.con_scale.transform 		= self.con_all.node_hook.Kinematics.Global.Transform
		self.con_scale.parent_node 		= self.con_all.node_hook
		self.con_scale.red 				= 1
		self.con_scale.green 			= 0.5
		self.con_scale.blue 			= 0
		self.con_scale.Draw()
		self.con_scale.AddTransformSetupPos('local')

		# turn off the con #
		self.con_scale.node_con.Properties('Visibility').viewvis.Value = False

		# add a default transform to the scale control #
		manip = self.con_scale.node_con.AddProperty('Transform Setup', False)
		manip = dispatch(manip)
		manip.tool.Value = 2
		
		# add to the controls group #
		self.group_controls.AddMember(self.con_scale.node_con)

		# add to character set #
		stack_set.AddNodeScl(self.con_scale.node_con)

		#---------------------------------------------------------------------
		# create a FLIGHTPATH con #
		self.con_flight_path 						= xsi.zCon()
		self.con_flight_path.type 					= 'round_flight'
		self.con_flight_path.size 					= self.size_flight_con * self.parent.scale * 0.8
		self.con_flight_path.basename 				= 'FlightPath'
		self.con_flight_path.transform.Translation	= self.parent.template.v_flight
		self.con_flight_path.parent_node 			= self.con_scale.node_hook
		self.con_flight_path.red 					= 0.1
		self.con_flight_path.green 					= 0.6
		self.con_flight_path.blue 					= 0.5
		self.con_flight_path.Draw()
		self.con_flight_path.AddTransformSetupPos('local')

		#  #
		self.con_flight_path.Scale(self.size_flight_con * self.parent.scale * 0.8 / 4.5, 1, 1)
		self.con_flight_path.Offset(0, 0.25, self.size_flight_con * self.parent.scale * 0.8 / 4.5)
		
		# add to the controls group #
		self.group_controls.AddMember(self.con_flight_path.node_con)

		# add to character set #
		stack_set.AddNodePosRot(self.con_flight_path.node_con)		

		#---------------------------------------------------------------------
		# create a FLIGHT con #
		# 	TODO: pass the con class #
		self.con_flight 						= xsi.zCon()
		self.con_flight.type 					= 'round_flight'
		self.con_flight.size 					= self.size_flight_con * self.parent.scale
		self.con_flight.basename 				= 'Flight'
		self.con_flight.transform.Translation	= self.parent.template.v_flight
		self.con_flight.parent_node 			= self.con_flight_path.node_hook
		self.con_flight.red 					= 0.2
		self.con_flight.green 					= 0.7
		self.con_flight.blue 					= 0.6
		self.con_flight.Draw()
		self.con_flight.AddTransformSetupPos('local')

		#  #
		self.con_flight.Scale(self.size_flight_con * self.parent.scale / 4.5, 1, 1)
		self.con_flight.Offset(0, 0, self.size_flight_con * self.parent.scale / 4.5)
		
		# add to the controls group #
		self.group_controls.AddMember(self.con_flight.node_con)

		# add to character set #
		stack_set.AddNodePosRot(self.con_flight.node_con)		

		#---------------------------------------------------------------------
		# add a visibility toggle for the flight path to the flight con
		prop = self.con_flight.node_con.AddProperty('CustomProperty', False, 'zAnim')
		prop_di = self.con_flight.node_con.AddProperty('CustomProperty', False, 'DisplayInfo_zAnim')
		param = prop.AddParameter3('ShowFlightPathCon', c.siBool, False)
		prop_di.AddProxyParameter(param, None, 'ShowFlightPathCon')
		
		self.con_flight_path.node_con.Properties('Visibility').Parameters('viewvis').AddExpression(
			param
		)
		# add to character set #
		stack_set.AddParams(param)		
		
		#---------------------------------------------------------------------
		# add the CENTER node #
		self.node_center = self.con_flight.node_hook.AddNull(xsi.zMapName('Center', 'Null', 'None'))
		self.node_center.Kinematics.Global.Transform = self.con_flight.node_hook.Kinematics.Global.Transform
		self.node_center.primary_icon.Value = 0
		self.node_center.Properties('Visibility').Parameters('viewvis').Value = False
		self.node_center.Properties('Visibility').Parameters('rendvis').Value = False

		# draw a CONTROLS node #
		self.node_controls = self.node_center.AddNull(xsi.zMapName('Controls', 'Branch', 'None'))
		self.node_controls.primary_icon.Value = 0
		self.node_controls.Properties('Visibility').Parameters('viewvis').Value = False
		self.node_controls.Properties('Visibility').Parameters('rendvis').Value = False

		# add LOWER and UPPER body groups #
		self.node_lower_body = self.node_controls.AddNull(xsi.zMapName('LowerBody', 'Branch', 'None'))
		self.node_lower_body.primary_icon.Value = 0
		self.node_lower_body.Properties('Visibility').Parameters('viewvis').Value = False
		self.node_lower_body.Properties('Visibility').Parameters('rendvis').Value = False

		self.node_upper_body = self.node_controls.AddNull(xsi.zMapName('UpperBody', 'Branch', 'None'))
		self.node_upper_body.primary_icon.Value = 0
		self.node_upper_body.Properties('Visibility').Parameters('viewvis').Value = False
		self.node_upper_body.Properties('Visibility').Parameters('rendvis').Value = False

		# draw a SKELETON node #
		self.node_skeleton = self.node_center.AddNull(xsi.zMapName('Skeleton', 'Branch', 'None'))
		self.node_skeleton.primary_icon.Value = 0
		self.node_skeleton.Properties('Visibility').Parameters('viewvis').Value = False
		self.node_skeleton.Properties('Visibility').Parameters('rendvis').Value = False

		# create a do not touch node #
		self.node_do_not_touch 	= self.model.AddNull(xsi.zMapName('DoNotTouchThis', 'Branch', 'None'))
		self.node_do_not_touch.primary_icon.Value = 0
		self.node_do_not_touch.Properties('Visibility').Parameters('viewvis').Value = False
		self.node_do_not_touch.Properties('Visibility').Parameters('rendvis').Value = False

		# create a do not touch node #
		self.node_deformers	= self.node_do_not_touch.AddNull(xsi.zMapName('Deformers', 'Branch', 'None'))
		self.node_deformers.primary_icon.Value = 0
		self.node_deformers.Properties('Visibility').Parameters('viewvis').Value = False
		self.node_deformers.Properties('Visibility').Parameters('rendvis').Value = False

		# constrain the scale of the do not touch to the scale node #
		self.node_do_not_touch.Kinematics.AddConstraint('Scaling', self.con_scale.node_hook, False)
		
		# create nodes for the geometry #
		self.node_geom_render = self.node_do_not_touch.AddNull(xsi.zMapName('GeomRndr', 'Branch', 'None'))
		self.node_geom_render.primary_icon.Value = 0
		self.node_geom_render.Properties('Visibility').Parameters('viewvis').Value = False
		self.node_geom_render.Properties('Visibility').Parameters('rendvis').Value = False

		self.node_geom_anim = self.node_do_not_touch.AddNull(xsi.zMapName('GeomAnim', 'Branch', 'None'))
		self.node_geom_anim.primary_icon.Value = 0
		self.node_geom_anim.Properties('Visibility').Parameters('viewvis').Value = False
		self.node_geom_anim.Properties('Visibility').Parameters('rendvis').Value = False
		
		self.node_geom_rig = self.node_do_not_touch.AddNull(xsi.zMapName('GeomRig', 'Branch', 'None'))
		self.node_geom_rig.primary_icon.Value = 0
		self.node_geom_rig.Properties('Visibility').Parameters('viewvis').Value = False
		self.node_geom_rig.Properties('Visibility').Parameters('rendvis').Value = False

		# # for setup purposes only #
		# # report the class attributes #
		# for key in self.__dict__:
		# 	log(key)
			
			
			
#-----------------------------------------------------------------------------
# Commands
#-----------------------------------------------------------------------------
def zRoot_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	#oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments
	oArgs.Add('prefix', c.siArgumentInput, 'PFX', c.siString)
	return True
	
def zRoot_Execute(prefix):
	# export the python object #
	import win32com.server
	return win32com.server.util.wrap(
		zRoot(prefix)
	)
	
