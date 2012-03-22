"""
zPelvis.py

Created by andy on 2008-07-22.
Copyright (c) 2008 Zoogloo LLC. All rights reserved.
"""

__version__ = '$Revision: 232 $'
__author__  = '$Author: andy $'
__date__    = '$Date: 2010-03-28 10:41 -0700 $'

import win32com.client
import win32com.server
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
	in_reg.Name = "zPelvis"
	in_reg.Email = "andy@zoogloo.net"
	in_reg.URL = ""
	in_reg.Major = 1
	in_reg.Minor = 1

	in_reg.RegisterProperty('zPelvis')

	in_reg.RegisterCommand('zPelvis', 'zPelvis')

	in_reg.RegisterMenu(c.siMenuTbAnimateActionsStoreID, 'zPelvisMenu', False)
	
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

class zPelvis(object):
	'''
	# get a new pelvis instance #
	pelvis = xsi.zPelvis()
	
	# set the model to use for the template #
	pelvis.template.model = xsi_template_model
	
	# draw the template #
	pelvis.template.Draw()
	
	# build the rig from the template #
	pelvis.rig.model = xsi_rig_model
	pelvis.rig.Build()
	'''
	# required for COM wrapper #
	_public_methods_ = [
	]
	# define the output vars here #
	_public_attrs_ = [
		'rig',
		'template',
		'scale',
	]
	# define those attrs that are read only #
	_readonly_attrs_ = []

	# set the class variables #
	uid				= 'a80bc57992c6de7c48e2b31bfa8d02ea'
	
	def __init__(self):
		super(zPelvis, self).__init__()
		
		# reset the instance varaibles #
		self._template 		= None
		self._rig		 	= None
		self.scale			= 1
		self.basename		= 'Pelvis'
	
	@zProp
	def template():
		'''Template Accessor'''
		def fget(self):
			# create a template if it doesn't exist #
			if not self._template:
				# wrap a new class #
				self._template = dispatch(win32com.server.util.wrap(zPelvis_Template(self)))
			return self._template
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
				self._rig = dispatch(win32com.server.util.wrap(zPelvis_Rig(self)))
			# return the private var #
			return self._rig
		def fset(self, value):
			raise Exception('Unable to modify rig value.')
		fdel = fset
		return locals()
			
				
class zPelvis_Template(object):
	"""docstring for zPelvis_Template"""
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
		'v_root',
		'v_target',
		'v_upv',
	]
	# define those attrs that are read only #
	_readonly_attrs_ = [
		'parent'
	]

	def __init__(self, parent):
		super(zPelvis_Template, self).__init__()
		
		# set the instance variables #
		self.parent		= parent
		
		# load the defaul values #
		self.LoadDefaultValues()
	
	def LoadDefaultValues(self):
		"""Sets the default values for the template"""
		self.v_root 	= XSIMath.CreateVector3(-0.000, 12.945, 0.172)
		self.v_target 	= XSIMath.CreateVector3(0.000, 11.530, 2.040)
		self.v_upv 		= XSIMath.CreateVector3(-0.000, 13.945, 0.172)
		
		# setup the default model #
		self.model		= xsi.ActiveSceneRoot
			
	def Draw(self):
		"""docstring for Draw"""
		# get the model #
		if not self.model:
			raise Exception('Model attribute for template not specified.')
		
		# dispatch the model #
		self.model = dispatch(self.model)
		
		#---------------------------------------------------------------------
		# create a node to hold the template #
		node_parent = self.model.AddNull('Pelvis_Container')
		node_parent.primary_icon.Value = 0
		node_parent.Properties('Visibility').Parameters('viewvis').Value = False
		node_parent.Properties('Visibility').Parameters('rendvis').Value = False
		node_parent.AddProperty('CustomProperty', False, 'zBuilderTemplateItem')
		prop = node_parent.AddProperty('CustomProperty', False, 'zContainer')
		prop = dispatch(prop)
		prop.AddParameter3('ContainerName', c.siString, 'Pelvis')
		prop.AddParameter3('ContainerUID', c.siString, self.parent.uid)
			
		# draw the nodes #
		node_root 	= node_parent.AddNull('Pelvis_Root')
		node_eff 	= node_root.AddNull('Pelvis_Target')
		node_upv 	= node_root.AddNull('Pelvis_Upv')
		
		# tag the nodes #
		node_root.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_root.AddProperty('CustomProperty', False, 'zPelvisRoot')

		node_eff.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_eff.AddProperty('CustomProperty', False, 'zPelvisTarget')

		node_upv.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_upv.AddProperty('CustomProperty', False, 'zPelvisUpv')
		
		#---------------------------------------------------------------------
		# set the positions #
		trans = XSIMath.CreateTransform()
		v_result = XSIMath.CreateVector3()
		
		# root #
		v_result.Scale(self.parent.scale, self.v_root)
		trans.Translation = v_result
		node_root.Kinematics.Global.Transform = trans
		
		# eff #
		v_result.Scale(self.parent.scale, self.v_target)
		trans.Translation = v_result
		node_eff.Kinematics.Global.Transform = trans
		
		# upv #
		v_result.Add(self.v_root, self.v_upv)
		v_result.ScaleInPlace(self.parent.scale)
		trans.Translation = v_result
		node_upv.Kinematics.Global.Transform = trans
		
	def GetFromScene(self):
		"""Gets the template values from the template model"""
		
		#---------------------------------------------------------------------
		# make sure the model exists 
		log(self.model)
		if not self.model:
			raise Exception('Model attribute for template not specified.')
		
		#---------------------------------------------------------------------
		# find the container #
		node_parent = None
		for node in dispatch(self.model).FindChildren('*'):
			if node.Properties('zContainer'):
				if node.Properties('zContainer').Parameters('ContainerUID').Value == self.parent.uid:
					node_parent = node
					break
		# make sure we have the container #
		if not node_parent:
			raise Exception('Unable to find pelvis template container by id: %s' % self.parent.uid)
		
		#---------------------------------------------------------------------
		# get all the nodes under the container #
		child_nodes = node_parent.FindChildren('*')

		#---------------------------------------------------------------------
		# get the vectors #
		for node in child_nodes:
			if node.Properties('zPelvisRoot'):
				self.v_root = node.Kinematics.Global.Transform.Translation
			elif node.Properties('zPelvisTarget'):
				self.v_target = node.Kinematics.Global.Transform.Translation
			elif node.Properties('zPelvisUpv'):
				self.v_upv = node.Kinematics.Global.Transform.Translation
		
class zPelvis_Rig(object):
	"""
	Class for drawing a pelvis.
	
	
	@ivar parent: zPelvis class
	@type parent: L{zPelvis}
	@ivar skeleton_parent: Node to use as the parent of the skeleton nodes.
	@type skeleton_parent: X3DObject
	@ivar controls_parent: Node to use for the parent of the control nodes.
	@type controls_parent: X3DObject
	@ivar deformer_parent: Node to use for the parent of the deformer nodes.
	@type deformer_parent: X3DObject
	@ivar character_root: Reference to the character root node.
	@type character_root: zCharacterRoot
	@ivar con_body: I{Output} Body controller node..
	@ivar con_hips: I{Output} Hip controller node.
	@ivar root_pelvis: I{Output} Chain drawn for the hips.
	@ivar node_env: I{Output} Deformer node used for enveloping.
	@ivar character_subset: I{Output} Character set for the pelvis component.
	"""
	# required for COM wrapper #
	_public_methods_ = [
		'Build',
	]
	# define the output vars here #
	_public_attrs_ = [
		'parent',
		'skeleton_parent',
		'controls_parent',
		'deformer_parent',
		'deformer_parent',
		'size_body_con',
		'size_hips_con',
		'hips_y_offset',
		'group_deformers',
		'group_controls',
		'deformers',

		'con_body',
		'con_hips',
		'root_pelvis',
		'node_env',
		'character_subset',
		'character_set',
		'unlock_hip_translation',
	]
	# define those attrs that are read only #
	_readonly_attrs_ = [
		'parent',
		'con_body',
		'con_hips',
		'root_pelvis',
		'node_env',
		'character_subset',
	]

	
	def __init__(self, parent):
		super(zPelvis_Rig, self).__init__()
		# set the instance variables #
		self.parent				= parent
		self.skeleton_parent 	= None
		self.controls_parent 	= None
		self.deformer_parent 	= None
		self.con_body	   		= None
		self.con_hips	   		= None
		self.root_pelvis  		= None
		self.group_deformers	= None
		self.unlock_hip_translation = False
		
		self.deformers			= dispatch('XSI.Collection')
		
		# set the default con size #
		self.size_body_con		= 10
		self.size_hips_con		= 8
		self.hips_y_offset		= -0.25
	
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
		"""Builds the rig from the template values"""
		#---------------------------------------------------------------------
		# pre conditions
		
		# make sure we have the skeleton_parent #
		if not self.skeleton_parent:
			raise Exception(
				'zPelvis.rig.skeleton_parent is not defined.'
			)
		self.skeleton_parent = dispatch(self.skeleton_parent)
		
		# make sure we have the controls_parent #
		if not self.controls_parent:
			raise Exception(
				'zPelvis.rig.controls_parent is not defined.'
			)
		self.controls_parent = dispatch(self.controls_parent)
		
		# make sure we have the deformer_parent #
		if not self.deformer_parent:
			raise Exception(
				'zPelvis.rig.deformer_parent is not defined.'
			)
		self.deformer_parent = dispatch(self.deformer_parent)
		
		# make sure we have the template values #
		template = self.parent.template
		template = dispatch(template)
		if not template.v_root or not template.v_target or not template.v_upv:
			raise Exception(
				'Missing one or more template paramters.  Try using zPelvis.template.LoadDefaultValues()'
			)
			
		#---------------------------------------------------------------------
		# draw the rig
		
		# calculate the plane vector #
		v_plane = XSIMath.CreateVector3()
		v1		= XSIMath.CreateVector3()
		v2		= XSIMath.CreateVector3()
		# get vector from root to target #
		v1.Sub(template.v_root, template.v_target)
		# get vector from root to upv #
		v2.Sub(template.v_root, template.v_upv)
		# get the cross product #
		v_plane.Cross(v1, v2)
		
		# draw the skeleton #
		chain_root = self.skeleton_parent.Add2DChain(
			template.v_root,
			template.v_target,
			v_plane,
			c.si2DChainNormalRadian
		)
		
		# # rename #
		chain_root.Name 			= xsi.zMapName(self.parent.basename, 'ChainRoot', 'M')
		chain_root.Bones(0).Name 	= xsi.zMapName(self.parent.basename, 'ChainBone', 'M')
		chain_root.effector.Name 	= xsi.zMapName(self.parent.basename, 'ChainEff', 'M')
		
		# put the effector under the bone #
		chain_root.Bones(0).AddChild(chain_root.effector)
		
		# align the chain root #
		trans = chain_root.Bones(0).Kinematics.Global.Transform
		chain_root.Kinematics.Global.Transform = chain_root.Bones(0).Kinematics.Global.Transform
		chain_root.Bones(0).Kinematics.Global.Transform = trans
		
		#---------------------------------------------------------------------
		# draw the controls
		
		# body con #
		con_body 						= xsi.zCon()
		con_body.type 					= 'pointy_circle'
		con_body.size 					= self.size_body_con * self.parent.scale
		con_body.transform.Translation 	= chain_root.Kinematics.Global.Transform.Translation
		con_body.transform.Rotation 	= XSIMath.CreateRotation(0,XSIMath.DegreesToRadians(-90),0)
		con_body.basename 				= 'Body'
		con_body.parent_node 			= self.controls_parent
		con_body.red 					= 1
		con_body.green 					= 1
		con_body.blue 					= 0
		con_body.rotation_order			= 'zxy'
		con_body.Draw()
		con_body.AddTransformSetupLast()
		
		# hips con #
		con_hips 						= xsi.zCon()
		con_hips.type 					= 'pointy_circle'
		con_hips.size 					= self.size_hips_con * self.parent.scale
		con_hips.transform.Translation 	= chain_root.Kinematics.Global.Transform.Translation
		con_hips.transform.Rotation 	= XSIMath.CreateRotation(0,XSIMath.DegreesToRadians(-90),0)
		con_hips.basename 				= 'Hips'
		con_hips.parent_node 			= con_body.node_hook
		con_hips.red 					= 0.75
		con_hips.green 					= 0.75
		con_hips.blue 					= 0
		con_hips.rotation_order			= 'zxy'
		con_hips.Draw()
		con_hips.AddTransformSetupRot('add')
		
		# offset the hips con #
		con_hips.Offset(0, self.hips_y_offset, 0)
		
		# lock the hip position #
		if not self.unlock_hip_translation:
			con_hips.node_con.Kinematics.Local.PosX.AddExpression(0)
			con_hips.node_con.Kinematics.Local.PosY.AddExpression(0)
			con_hips.node_con.Kinematics.Local.PosZ.AddExpression(0)
		
		#---------------------------------------------------------------------
		# add cons to group #
		if self.group_controls:
			self.group_controls.AddMember(con_body.node_con)
			self.group_controls.AddMember(con_hips.node_con)
		
		#---------------------------------------------------------------------
		# constrain the chain
		chain_root.Kinematics.AddConstraint('Pose', con_body.node_hook, True)

		cns = chain_root.Bones(0).Kinematics.AddConstraint('Pose', con_hips.node_hook, True)
		cns = dispatch(cns)
		cns.cnspos.Value = False
		
		#---------------------------------------------------------------------
		# create a deformer stack #
		node_dfm_parent = self.deformer_parent.AddNull(xsi.zMapName(self.parent.basename, 'Custom:DfmPrnt', 'M'))
		node_dfm_shadow = node_dfm_parent.AddNull(xsi.zMapName(self.parent.basename, 'Custom:DfmShdw', 'M'))
		self.node_env   = node_dfm_shadow.AddNull(xsi.zMapName(self.parent.basename, 'Env', 'M'))
		self.deformers.Add(self.node_env)
		
		# turn off the null #
		node_dfm_parent.primary_icon.Value = 0
		node_dfm_parent.Properties('Visibility').Parameters('viewvis').Value = False
		node_dfm_parent.Properties('Visibility').Parameters('rendvis').Value = False
		node_dfm_shadow.primary_icon.Value = 0
		node_dfm_shadow.Properties('Visibility').Parameters('viewvis').Value = False
		node_dfm_shadow.Properties('Visibility').Parameters('rendvis').Value = False
		self.node_env.primary_icon.Value = 0
		self.node_env.Properties('Visibility').Parameters('viewvis').Value = False
		self.node_env.Properties('Visibility').Parameters('rendvis').Value = False
		
		# align the nodes #
		node_dfm_parent.Kinematics.AddConstraint('Pose', chain_root, False)
		node_dfm_shadow.Kinematics.AddConstraint('Pose', chain_root.Bones(0), False)
		
		#---------------------------------------------------------------------
		# add the deformers to the deformers group #
		if self.group_deformers:
			self.group_deformers = dispatch(self.group_deformers)
			self.group_deformers.AddMember(self.deformers)
		
		#---------------------------------------------------------------------
		# add character sets
		if self.character_set:
			self.character_set = dispatch(self.character_set)
			self.character_subset = self.character_set.AddSubset('LowerBody')
			self.character_subset.AddNodePosRot(con_body.node_con)
			self.character_subset.AddNodeRot(con_hips.node_con)
		
		#---------------------------------------------------------------------
		# format the chain colors
		fmt = xsi.zChainFormatter(chain_root)
		fmt.Format()
		
		#---------------------------------------------------------------------
		# expose the references 
		self.root_pelvis	= chain_root
		self.con_body 		= con_body
		self.con_hips 		= con_hips
		
	
#-----------------------------------------------------------------------------
# Commands
#-----------------------------------------------------------------------------
def zPelvis_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	#oCmd.SetFlag(constants.siNoLogging,false)

	#oArgs = oCmd.Arguments
	#oArgs.Add('arg', c.siArgumentInput, '', c.siString)
	#oArgs.AddObjectArgument('model')

	return True
	
def zPelvis_Execute():
	# export the python object #
	import win32com.server
	return win32com.server.util.wrap(
		zPelvis()
	)
	
