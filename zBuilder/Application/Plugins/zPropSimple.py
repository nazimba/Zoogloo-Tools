"""
zPropSimple.py

Created by andy on 2008-07-22.
Copyright (c) 2008 Zoogloo LLC. All rights reserved.
"""

__version__ = '$Revision: 214 $'
__author__  = '$Author: andy $'
__date__    = '$Date: 2009-12-30 00:36 -0800 $'

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
	in_reg.Name = "zPropSimple"
	in_reg.Email = "andy@zoogloo.net"
	in_reg.URL = ""
	in_reg.Major = 1
	in_reg.Minor = 1

	in_reg.RegisterCommand('zPropSimple', 'zPropSimple')
	
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

class zPropSimple(object):

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
	uid				= '4a53318f70539e81eb92960774b98c94'
	basename		= 'PropSimple'
	scale			= 1
	prefix			= 'PFX'
	
	def __init__(self, prefix='PFX'):
		super(zPropSimple, self).__init__()
		
		# reset the instance varaibles #
		self._template		= None
		self._rig	  		= None
		self.basename		= 'PropSimple'
		self.scale			= 1
		self.prefix			= prefix
		
	@zProp
	def template():
		'''Template Accessor'''
		def fget(self):
			# create a template if it doesn't exist #
			if not self._template:
				# wrap a new class #
				self._template = win32com.server.util.wrap(zPropSimple_Template(self))
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
				self._rig = win32com.server.util.wrap(zPropSimple_Rig(self))
			# return the private var #
			return dispatch(self._rig)
		def fset(self, value):
			raise Exception('Unable to modify rig value.')
		fdel = fset
		return locals()
			
				
class zPropSimple_Template(object):
	"""docstring for zPropSimple_Template"""
	
	_inputs_ = [
		'v_start', 
		'v_end', 
		'v_upv', 
		't_root', 
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
		super(zPropSimple_Template, self).__init__()
		
		# set the instance variables #
		self.parent			= parent
		
		# load the defaults #
		self.LoadDefaultValues()
	
	
	def LoadDefaultValues(self):
		"""
		Sets the default values 
		"""
		# create new vectors #
		self.v_start	= XSIMath.CreateVector3(0, 0, 0)
		self.v_end		= XSIMath.CreateVector3(0, 0, 1)
		self.v_up		= XSIMath.CreateVector3(0, 1, 0)
		self.t_root		= XSIMath.CreateTransform()
		
		# set the model #
		self.model = xsi.ActiveSceneRoot

		self.scale 			= 1

	def Draw(self):
		"""docstring for Draw"""
		# get the model #
		if not self.model:
			raise Exception('Model attribute for template not specified.')

		# dispatch the model #
		self.model = dispatch(self.model)

		#---------------------------------------------------------------------
		# create a node to hold the template #
		node_parent = self.model.AddNull(
			xsi.zMapName(self.parent.basename, 'Custom:Container', 'None')
		)
		node_parent.primary_icon.Value = 0
		node_parent.Properties('Visibility').Parameters('viewvis').Value = False
		node_parent.Properties('Visibility').Parameters('rendvis').Value = False
		node_parent.AddProperty('CustomProperty', False, 'zBuilderTemplateItem')
		prop = node_parent.AddProperty('CustomProperty', False, 'zContainer')
		prop = dispatch(prop)
		prop.AddParameter3('ContainerName', c.siString, self.parent.basename)
		prop.AddParameter3('ContainerUID', c.siString, self.parent.uid)
		
		#---------------------------------------------------------------------
		# draw the nodes #
		node_start 	= node_parent.AddNull(xsi.zMapName('%sStart' % self.parent.basename, 'Custom:Tmp', None))
		node_start.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_start.AddProperty('CustomProperty', False, 'z%sStart' % self.parent.basename)

		node_end 	= node_parent.AddNull(xsi.zMapName('%sEnd' % self.parent.basename, 'Custom:Tmp', None))
		node_end.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_end.AddProperty('CustomProperty', False, 'z%sEnd' % self.parent.basename)

		node_up 	= node_parent.AddNull(xsi.zMapName('%sUp' % self.parent.basename, 'Custom:Tmp', None))
		node_up.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_up.AddProperty('CustomProperty', False, 'z%sUp' % self.parent.basename)

		#---------------------------------------------------------------------
		# set the positions #
		trans = XSIMath.CreateTransform()
		v_result = XSIMath.CreateVector3()

		# start #
		v_result.Scale(self.parent.scale, self.v_start)
		trans.Translation = v_result
		node_start.Kinematics.Global.Transform = trans
		
		# end #
		v_result.Scale(self.parent.scale, self.v_end)
		trans.Translation = v_result
		node_end.Kinematics.Global.Transform = trans
		
		# up #
		v_result.Scale(self.parent.scale, self.v_up)
		trans.Translation = v_result
		node_up.Kinematics.Global.Transform = trans
		
		#---------------------------------------------------------------------
		# add the constraints 
		
		cns = node_start.Kinematics.AddConstraint('Direction', node_end, False)
		cns = dispatch(cns)
		cns.UpVectorReference	= node_up
		cns.upvct_active.Value	= True
		
	def GetFromScene(self):
		"""Gets the template values from the template model"""
		
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
				if node.Properties('zContainer').Parameters('ContainerUID').Value == self.parent.uid and \
				node.Properties('zContainer').Parameters('ContainerName').Value == self.parent.basename:
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
			if node.Properties('z%sStart' % self.parent.basename):
				self.v_start 	= node.Kinematics.Global.Transform.Translation
				self.t_root		= node.Kinematics.Global.Transform
			elif node.Properties('z%sEnd' % self.parent.basename):
				self.v_end 		= node.Kinematics.Global.Transform.Translation
			elif node.Properties('z%sUp' % self.parent.basename):
				self.v_up 		= node.Kinematics.Global.Transform.Translation
		
class zPropSimple_Rig(object):

	_inputs_ = [
		'size_handle_con',
		'size_all_con',
	]
	_outputs_ = [
		'parent',
		'node_geom_rig',
		'node_geom_render',
		'node_skeleton',
		'node_geom_anim',
		'node_do_not_touch',
		'node_start',
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
		'con_handle',
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
		super(zPropSimple_Rig, self).__init__()
		
		# set the instance variables #
		self.parent					= parent

		# set the defaults for the input variables #
		for item in self._inputs_:
			setattr(self, item, None)
			
		# set specific types #
		self.deformers = dispatch('XSI.Collection')
		
		# set the default con size #
		self.size_handle_con 	= 1
		self.size_all_con		= 3
	
	def Build(self):

		# create a model #
		self.model = xsi.ActiveSceneRoot.AddModel(None, '%s1' % self.parent.prefix)
		
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
		# create a HANDLE con #
		# 	TODO: pass the con class #
		self.con_handle 						= xsi.zCon()
		self.con_handle.type 					= 'sphere'
		self.con_handle.size 					= self.size_handle_con * self.parent.scale
		self.con_handle.basename 				= 'Handle'
		self.con_handle.transform				= self.parent.template.t_root
		self.con_handle.parent_node 			= self.con_scale.node_hook
		self.con_handle.red 					= 1.0
		self.con_handle.green 					= 0.5
		self.con_handle.blue 					= 0.0
		self.con_handle.Draw()
		self.con_handle.AddTransformSetupPos('local')

		# add to the controls group #
		self.group_controls.AddMember(self.con_handle.node_con)

		# add to character set #
		stack_set.AddNodePosRot(self.con_handle.node_con)		

		#---------------------------------------------------------------------
		# create a do not touch node #
		self.node_do_not_touch 	= self.model.AddNull(xsi.zMapName('DoNotTouchThis', 'Branch', 'None'))
		self.node_do_not_touch.primary_icon.Value = 0
		self.node_do_not_touch.Properties('Visibility').Parameters('viewvis').Value = False
		self.node_do_not_touch.Properties('Visibility').Parameters('rendvis').Value = False

		# create a deformer node #
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
		
		# constrain geo nodes to the controller #
		self.node_geom_render.Kinematics.AddConstraint('Pose', self.con_handle.node_hook, True)
		self.node_geom_anim.Kinematics.AddConstraint('Pose', self.con_handle.node_hook, True)
		self.node_geom_rig.Kinematics.AddConstraint('Pose', self.con_handle.node_hook, True)

		#---------------------------------------------------------------------
		# create a deformer stack #
		node_dfm_parent = self.node_deformers.AddNull(xsi.zMapName('%s' % self.parent.basename, 'Custom:DfmSPrnt', None))
		node_dfm_shadow = node_dfm_parent.AddNull(xsi.zMapName('%s' % self.parent.basename, 'Custom:DfmShdw', None))
		node_env 		= node_dfm_shadow.AddNull(xsi.zMapName('%s' % self.parent.basename, 'Env', None))
		self.deformers.Add(node_env)
	
		node_dfm_parent.primary_icon.Value 	= 0
		node_dfm_parent.Properties('Visibility').Parameters('viewvis').Value = False
		node_dfm_parent.Properties('Visibility').Parameters('rendvis').Value = False
		node_dfm_shadow.primary_icon.Value 	= 0
		node_dfm_shadow.Properties('Visibility').Parameters('viewvis').Value = False
		node_dfm_shadow.Properties('Visibility').Parameters('rendvis').Value = False
		node_env.primary_icon.Value 		= 0
		node_env.Properties('Visibility').Parameters('viewvis').Value = False
		node_env.Properties('Visibility').Parameters('rendvis').Value = False
	
		node_dfm_parent.Kinematics.AddConstraint('Pose', self.con_handle.node_rest, False)
		node_dfm_shadow.Kinematics.AddConstraint('Pose', self.con_handle.node_hook, False)
		
		#---------------------------------------------------------------------
		# add the deformers to the deformers group #
		if self.group_deformers:
			self.group_deformers = dispatch(self.group_deformers)
			self.group_deformers.AddMember(self.deformers)

			
			
#-----------------------------------------------------------------------------
# Commands
#-----------------------------------------------------------------------------
def zPropSimple_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	#oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments
	oArgs.Add('prefix', c.siArgumentInput, 'PFX', c.siString)
	return True
	
def zPropSimple_Execute(prefix):
	# export the python object #
	import win32com.server
	return win32com.server.util.wrap(
		zPropSimple(prefix)
	)
	
