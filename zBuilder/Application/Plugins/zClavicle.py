"""
zClavicle.py

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
	in_reg.Name = "zClavicle"
	in_reg.Email = "andy@zoogloo.net"
	in_reg.URL = ""
	in_reg.Major = 1
	in_reg.Minor = 1

	in_reg.RegisterCommand('zClavicle', 'zClavicle')
	
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

class zClavicle(object):

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
	]
	# define those attrs that are read only #
	_readonly_attrs_ = [
		'rig',
		'template',
	]

	# set the class variables #
	_template 		= None
	_rig 			= None
	uid				= 'ddd0ae7a910f9f4f2d12f47145f15bd3'
	basename		= 'Clavicle'
	scale			= 1
	sym				= None
	
	def __init__(self, sym='left'):
		super(zClavicle, self).__init__()
		
		# reset the instance varaibles #
		self._template 	= None
		self._rig		= None
		
		self.symmetry 	= sym
		self.basename	= 'Clavicle'
	
	@zProp
	def template():
		'''Template Accessor'''
		def fget(self):
			# create a template if it doesn't exist #
			if not self._template:
				# wrap a new class #
				self._template = win32com.server.util.wrap(zClavicle_Template(self))
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
				self._rig = win32com.server.util.wrap(zClavicle_Rig(self))
			# return the private var #
			return dispatch(self._rig)
		def fset(self, value):
			raise Exception('Unable to modify rig value.')
		fdel = fset
		return locals()
			
				
class zClavicle_Template(object):
	"""docstring for zClavicle_Template"""
	
	_inputs_ = [
		'v_clav',
		'v_shoulder', 
		'v_control_center', 
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
		super(zClavicle_Template, self).__init__()
		
		# set the instance variables #
		self.parent			= parent
		self.scale 			= 1
		self.model 			= None
		
		# load the defaults #
		self.LoadDefaultValues()
	
	
	def LoadDefaultValues(self):
		"""
		Sets the default values 
		"""
		self.v_clav				= XSIMath.CreateVector3(0.310, 19.147, 2.004)
		self.v_shoulder			= XSIMath.CreateVector3(1.823, 18.742, -0.171)
		self.v_control_center	= XSIMath.CreateVector3(2.787, 20.304, -0.783)
		if re.match(r'^right$', self.parent.symmetry, re.I):
			self.v_clav.X				*= -1
			self.v_shoulder.X			*= -1
			self.v_control_center.X		*= -1

	def Draw(self):
		"""docstring for Draw"""
		# get the model #
		if not self.model:
			raise Exception('Model attribute for template not specified.')

		# dispatch the model #
		self.model = dispatch(self.model)

		#---------------------------------------------------------------------
		# create a node to hold the template #
		node_parent = self.model.AddNull('Clavicle_%s_Container' % self.parent.symmetry[0].upper())
		node_parent.primary_icon.Value = 0
		node_parent.Properties('Visibility').Parameters('viewvis').Value = False
		node_parent.Properties('Visibility').Parameters('rendvis').Value = False
		node_parent.AddProperty('CustomProperty', False, 'zBuilderTemplateItem')
		prop = node_parent.AddProperty('CustomProperty', False, 'zContainer')
		prop = dispatch(prop)
		prop.AddParameter3('ContainerName', c.siString, 'Clavicle')
		prop.AddParameter3('ContainerSym', c.siString, self.parent.symmetry.lower())
		prop.AddParameter3('ContainerUID', c.siString, self.parent.uid)

		#---------------------------------------------------------------------
		# draw the nodes #
		node_clavicle 	= node_parent.AddNull(xsi.zMapName('Clavicle', 'Custom:Tmp', self.parent.symmetry))
		node_clavicle.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_clavicle.AddProperty('CustomProperty', False, 'zClavicle')

		node_shoulder	= node_parent.AddNull(xsi.zMapName('ClavShoulder', 'Custom:Tmp', self.parent.symmetry))
		node_shoulder.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_shoulder.AddProperty('CustomProperty', False, 'zShoulder')

		node_control	= node_parent.AddNull(xsi.zMapName('ClavShoulderControlCenter', 'Custom:Tmp', self.parent.symmetry))
		node_control.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_control.AddProperty('CustomProperty', False, 'zControl')

		#---------------------------------------------------------------------
		# set the positions #
		trans = XSIMath.CreateTransform()
		v_result = XSIMath.CreateVector3()

		# clavicle #
		v_result.Scale(self.parent.scale, self.v_clav)
		trans.Translation = v_result
		node_clavicle.Kinematics.Global.Transform = trans

		# shoulder #
		v_result.Scale(self.parent.scale, self.v_shoulder)
		trans.Translation = v_result
		node_shoulder.Kinematics.Global.Transform = trans
		
		# control #
		v_result.Scale(self.parent.scale, self.v_control_center)
		trans.Translation = v_result
		node_control.Kinematics.Global.Transform = trans
		
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
				if node.Properties('zContainer').Parameters('ContainerUID').Value == self.parent.uid \
				and node.Properties('zContainer').Parameters('ContainerSym').Value == self.parent.symmetry.lower():
					node_parent = node
					break
		# make sure we have the container #
		if not node_parent:
			raise Exception('Unable to find template container by id: %s and name: %s' % (self.parent.uid, type_name))
		
		#---------------------------------------------------------------------
		# get all the nodes under the container #
		child_nodes = node_parent.FindChildren('*')

		#---------------------------------------------------------------------
		# get the vectors or transform #
		for node in child_nodes:
			if node.Properties('zClavicle'):
				self.v_clav				= node.Kinematics.Global.Transform.Translation
			elif node.Properties('zShoulder'):
				self.v_shoulder			= node.Kinematics.Global.Transform.Translation
			elif node.Properties('zControl'):
				self.v_control_center	= node.Kinematics.Global.Transform.Translation
		
class zClavicle_Rig(object):

	_inputs_ = [
		'controls_parent',  		
		'controls_constraint',  		
		'character_set',   		
		'character_subset',   		
		'skeleton_parent',  		
		'deformer_parent',  
		'size_shoulder_con',	
		'group_deformers',
		'group_controls',
		'fk_mode_con_root',
		'fk_mode_param',
		'rotation_con',
	]
	_outputs_ = [
		'parent',
		'con_clav',
		'root_skel',
		'deformers',
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
		super(zClavicle_Rig, self).__init__()
		
		# set the instance variables #
		self.parent					= parent

		# set the defaults for the input variables #
		for item in self._inputs_:
			setattr(self, item, None)
			
		# set specific types #
		self.deformers = dispatch('XSI.Collection')
		
		# set the size of the shoulder controller #
		self.size_shoulder_con = 1
		
		self.rotation_con			= True
	
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
		#---------------------------------------------------------------------
		# pre conditions
		
		# make sure we have the skeleton_parent #
		if not self.skeleton_parent:
			raise Exception(
				'zLeg.rig.skeleton_parent is not defined.'
			)
		self.skeleton_parent = dispatch(self.skeleton_parent)
		
		# make sure we have the controls_parent #
		if not self.controls_parent:
			raise Exception(
				'zLeg.rig.controls_parent is not defined.'
			)
		self.controls_parent = dispatch(self.controls_parent)
		
		# make sure we have the deformer_parent #
		if not self.deformer_parent:
			raise Exception(
				'zLeg.rig.deformer_parent is not defined.'
			)
		self.deformer_parent = dispatch(self.deformer_parent)
		
		# get the template #
		template = dispatch(self.parent.template)
		
		# setup the self.parent.symmetrymetry switches #
		left 	= True
		right 	= False
		if re.match(r'^right$', self.parent.symmetry, re.I):
			left 	= False
			right 	= True
		
		#---------------------------------------------------------------------
		# draw the clavicle chain #

		# build the plane vector #
		v_plane = XSIMath.CreateVector3(0, 0, 1)
		if right:
			v_plane = XSIMath.CreateVector3(0, 0, -1)
		
		# draw the skeleton #
		self.skeleton_parent = dispatch(self.skeleton_parent)
		self.root_skel = self.skeleton_parent.Add2DChain(
			template.v_clav,
			template.v_shoulder,
			v_plane,
			c.si2DChainNormalRadian
		)
		
		# rename #
		self.root_skel.Name				= xsi.zMapName('Clavicle', 'ChainRoot', 'Mid')
		self.root_skel.Bones(0).Name	= xsi.zMapName('Clavicle', 'ChainBone', 'Mid')
		self.root_skel.Effector.Name	= xsi.zMapName('Clavicle', 'ChainEff', 'Mid')

		# format the chain #
		fmt = xsi.zChainFormatter(self.root_skel)
		fmt.Format()

		#---------------------------------------------------------------------
		# add a con #
		self.con_clav 							= xsi.zCon()
		self.con_clav.type 						= 'text:S'
		self.con_clav.size 						= self.size_shoulder_con * self.parent.scale
		if self.rotation_con:
			self.con_clav.transform.Translation 	= self.root_skel.Kinematics.Global.Transform.Translation
		else:
			self.con_clav.transform.Translation 	= self.root_skel.Effector.Kinematics.Global.Transform.Translation
		self.con_clav.basename 					= 'Shoulder'
		self.con_clav.symmetry 					= self.parent.symmetry
		self.con_clav.parent_node 				= self.controls_parent
		self.con_clav.rotation_order 			= 'zyx'
		self.con_clav.red 						= 0
		self.con_clav.green 					= 1
		self.con_clav.blue 						= 0
		if right:
			self.con_clav.red 						= 1
			self.con_clav.green 					= 0
			self.con_clav.blue 						= 0
		self.con_clav.Draw()
		if self.rotation_con:
			self.con_clav.AddTransformSetupRot('local', False, True, True)
		else:
			self.con_clav.AddTransformSetupPos('local', False, True, True)
		
		# add to the controls group #
		if self.group_controls:
			self.group_controls.AddMember(self.con_clav.node_con)
		
		# offset the controller to it's location #
		v_con = XSIMath.CreateVector3()
		v_con.Sub(template.v_control_center, template.v_clav)
		self.con_clav.Offset(v_con.X, v_con.Y, v_con.Z)
		
		# move the hook node at the effector if this a rotation clav #
		if self.rotation_con:
			self.con_clav.node_hook.Kinematics.Global.Transform = self.root_skel.Kinematics.Global.Transform
			
		# # constrain the controller #
		# if self.rotation_con:
		# 	self.con_clav.node_rest.Kinematics.AddConstraint('Pose', self.controls_constraint, True)
		
		#---------------------------------------------------------------------
		# create a constraint from the rest node to the spine node #
		if self.fk_mode_con_root:
			# constrain the rest node to the 
			cns = self.con_clav.node_rest.Kinematics.AddConstraint('Pose', self.fk_mode_con_root, True);
			cns = dispatch(cns)
			
			# add the expression on the constraint weight to the ik/fk weight #
			cns.blendweight.AddExpression('1 - %s' % self.fk_mode_param.FullName)
		
		#---------------------------------------------------------------------
		# create upvectors oriented skeleton_parent #
		node_clav_upv = self.controls_parent.AddNull(
			xsi.zMapName('Clavicle', 'UpVector', self.parent.symmetry)
		)
		node_clav_upv.primary_icon.Value = 0
		node_clav_upv.Properties('Visibility').Parameters('viewvis').Value = False
		node_clav_upv.Properties('Visibility').Parameters('rendvis').Value = False
		trans = self.root_skel.Bones(0).Kinematics.Global.Transform
		trans.AddLocalTranslation(
			XSIMath.CreateVector3(0, self.root_skel.Bones(0).length.Value, 0)
		)
		node_clav_upv.Kinematics.Global.Transform = trans
		node_clav_upv.Kinematics.AddConstraint('Pose', self.skeleton_parent, True)

		#---------------------------------------------------------------------
		# constrain the chain #
		
		# effector #
		self.root_skel.Effector.Kinematics.AddConstraint('Pose', self.con_clav.node_hook, True)
		
		# up vector #
		xsi.ApplyOp("SkeletonUpVector", "%s;%s" % \
					(self.root_skel.Bones(0), node_clav_upv), 3, 
					c.siPersistentOperation, "", 0)
		
		#---------------------------------------------------------------------
		# create a deformer stack #

		node_dfm_parent = self.deformer_parent.AddNull(xsi.zMapName('Clavicle', 'Custom:DfmPrnt', self.parent.symmetry))
		node_dfm_shadow = node_dfm_parent.AddNull(xsi.zMapName('Clavicle', 'Custom:DfmShdw', self.parent.symmetry))
		node_env 		= node_dfm_shadow.AddNull(xsi.zMapName('Clavicle', 'Env', self.parent.symmetry))
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
		
		node_dfm_parent.Kinematics.AddConstraint('Pose', self.root_skel.Bones(0).Parent, False)
		node_dfm_shadow.Kinematics.AddConstraint('Pose', self.root_skel.Bones(0), False)
		
		#---------------------------------------------------------------------
		# add the deformers to the deformers group #
		if self.group_deformers:
			self.group_deformers = dispatch(self.group_deformers)
			self.group_deformers.AddMember(self.deformers)

		#---------------------------------------------------------------------
		# add character sets
		if self.character_set:
			
			# get the lower subset #
			self.character_set = dispatch(self.character_set)
			upper_set = None
			try:
				upper_set = self.character_set.Get('UpperBody')
			except:                           
				upper_set = self.character_set.AddSubset('UpperBody')
	
			# don't know if we need a subset here, maybe 'arm' #
			self.character_subset = upper_set
			
			# add the parameters #
			self.character_subset.AddNodePosRot(self.con_clav.node_con)
		

#-----------------------------------------------------------------------------
# Commands
#-----------------------------------------------------------------------------
def zClavicle_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oArgs = oCmd.Arguments
	oArgs.Add('symmetry', c.siArgumentInput, 'left', c.siString)
	return True
	
def zClavicle_Execute(symmetry):
	# export the python object #
	import win32com.server
	return win32com.server.util.wrap(
		zClavicle(symmetry)
	)
	
