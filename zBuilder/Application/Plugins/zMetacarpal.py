"""
zMetacarpal.py

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
alpha = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

null = None
false = 0
true = 1

def XSILoadPlugin(in_reg):
	in_reg.Author = "Andy Buecker"
	in_reg.Name = "zMetacarpal"
	in_reg.Email = "andy@zoogloo.net"
	in_reg.URL = ""
	in_reg.Major = 1
	in_reg.Minor = 1

	in_reg.RegisterCommand('zMetacarpal', 'zMetacarpal')
	
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

class zMetacarpal(object):

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
	uid				= 'f47af905eba6786ae157bb075f8d555f'
	basename		= 'Meta'
	scale			= 1
	
	def __init__(self, sym='left'):
		super(zMetacarpal, self).__init__()
		
		# reset the instance varaibles #
		self._template	= None
		self._rig	  	= None
		
		self.symmetry	= sym
	
	@zProp
	def template():
		'''Template Accessor'''
		def fget(self):
			# create a template if it doesn't exist #
			if not self._template:
				# wrap a new class #
				self._template = win32com.server.util.wrap(zMetacarpal_Template(self))
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
				self._rig = win32com.server.util.wrap(zMetacarpal_Rig(self))
			# return the private var #
			return dispatch(self._rig)
		def fset(self, value):
			raise Exception('Unable to modify rig value.')
		fdel = fset
		return locals()
			
				
class zMetacarpal_Template(object):
	"""docstring for zMetacarpal_Template"""
	
	_inputs_ = [
		'v_root', 
		'v_tip', 
		't_root', 
		't_tip', 
		'defaults'
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

	# define a dictionary of default values (left side)
	v_root   	 = None
	v_tip   	 = None
	
	def __init__(self, parent):
		super(zMetacarpal_Template, self).__init__()
		
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
		# create new vectors #
		self.v_root  = XSIMath.CreateVector3(11.620, 18.348, -0.862)
		self.v_tip   = XSIMath.CreateVector3(13.562, 18.236, -1.342)
		if re.match(r'^right$', self.parent.symmetry, re.I):
			self.v_root.X 	*= -1
			self.v_tip.X 	*= -1
		
		# set the model #
		self.model = xsi.ActiveSceneRoot

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
			xsi.zMapName(self.parent.basename, 'Custom:Container', self.parent.symmetry)
		)
		node_parent.primary_icon.Value = 0
		node_parent.Properties('Visibility').Parameters('viewvis').Value = False
		node_parent.Properties('Visibility').Parameters('rendvis').Value = False
		node_parent.AddProperty('CustomProperty', False, 'zBuilderTemplateItem')
		prop = node_parent.AddProperty('CustomProperty', False, 'zContainer')
		prop = dispatch(prop)
		prop.AddParameter3('ContainerName', c.siString, self.parent.basename)
		prop.AddParameter3('ContainerSym', c.siString, self.parent.symmetry.lower())
		prop.AddParameter3('ContainerUID', c.siString, self.parent.uid)
		
		#---------------------------------------------------------------------
		# draw the nodes #
		node_root 	= node_parent.AddNull(xsi.zMapName('%sRoot' % self.parent.basename, 'Custom:Tmp', self.parent.symmetry))
		node_root.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_root.AddProperty('CustomProperty', False, 'zMetaRoot')

		node_tip	= node_parent.AddNull(xsi.zMapName('%sTip' % self.parent.basename, 'Custom:Tmp', self.parent.symmetry))
		node_tip.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_tip.AddProperty('CustomProperty', False, 'zMetaTip')
		
		#---------------------------------------------------------------------
		# set the positions #
		trans = XSIMath.CreateTransform()
		v_result = XSIMath.CreateVector3()

		# root #
		v_result.Scale(self.parent.scale, self.v_root)
		trans.Translation = v_result
		node_root.Kinematics.Global.Transform = trans

		# tip #
		v_result.Scale(self.parent.scale, self.v_tip)
		trans.Translation = v_result
		node_tip.Kinematics.Global.Transform = trans
		
		#---------------------------------------------------------------------
		# aim the root at the tip #
		cns = node_root.Kinematics.AddConstraint('Direction', node_tip, False)
		cns = dispatch(cns)
		cns.upvct_active.Value = True
		cns.upvct_active.Value = False
		
		#---------------------------------------------------------------------
		# add a visual upvector #
		node_upv						= node_root.AddNull(xsi.zMapName('%sUpv' % self.parent.basename, 'Custom:Tmp', self.parent.symmetry))
		node_upv.primary_icon.Value 	= 0
		node_upv.Properties('Visibility').Parameters('viewvis').Value = False
		node_upv.Properties('Visibility').Parameters('rendvis').Value = False
		node_upv.shadow_icon.Value  	= 10
		node_upv.size.Value				= self.parent.scale
		node_upv.shadow_offsetZ.Value	= node_upv.size.Value
		
		node_upv.shadow_colour_custom	= True
		node_upv.R.Value				= 1
		node_upv.G.Value				= 0.8
		node_upv.B.Value				= 1
		
		# align the arrow to the y direction #
		trans = node_root.Kinematics.Global.Transform
		trans.AddLocalRotation(XSIMath.CreateRotation(XSIMath.DegreesToRadians(-90), 0, 0))
		node_upv.Kinematics.Global.Transform = trans
		
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
				and node.Properties('zContainer').Parameters('ContainerSym').Value == self.parent.symmetry.lower() \
				and node.Properties('zContainer').Parameters('ContainerName').Value == self.parent.basename:
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
			if node.Properties('zMetaRoot'):
				self.t_root			= node.Kinematics.Global.Transform
				self.v_root			= self.t_root.Translation
			elif node.Properties('zMetaTip'):                         
				self.t_tip			= node.Kinematics.Global.Transform
				self.v_tip			= self.t_tip.Translation
		
class zMetacarpal_Rig(object):

	_inputs_ = [
		'controls_parent',  		
		'character_set',   		
		'skeleton_parent',  		
		'deformer_parent',  
		'size_con',	
		'group_deformers',	
		'group_controls',	
		'finger_con',	
		'finger_skel',	
	]
	_outputs_ = [
		'parent',
		'deformers',
		'root_skel',
		'root_con',
		'character_subset',			
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
		super(zMetacarpal_Rig, self).__init__()
		
		# set the instance variables #
		self.parent					= parent

		# set the defaults for the input variables #
		for item in self._inputs_:
			setattr(self, item, None)
			
		# set specific types #
		self.deformers = dispatch('XSI.Collection')
		
		# set the default control size #
		self.size_con = 1
	
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
		
		# setup the symmetry switches #
		left 	= True
		right 	= False
		if re.match(r'^right$', self.parent.symmetry, re.I):
			left 	= False
			right 	= True
		
		#---------------------------------------------------------------------
		# draw the chain #

		# get a vector along the y axis of the root #
		t_up	= XSIMath.CreateTransform()
		t_up.Copy(self.parent.template.t_root)
		t_up.AddLocalTranslation(XSIMath.CreateVector3(0, 1, 0))
		# calculate the plane vector #
		v1		= XSIMath.CreateVector3()
		v2		= XSIMath.CreateVector3()
		v_plane = XSIMath.CreateVector3()
		# get vector from root to tip #
		v1.Sub(self.parent.template.t_root.Translation, self.parent.template.t_tip.Translation)
		# get vector from root to up #
		v2.Sub(self.parent.template.t_root.Translation, t_up.Translation)
		# get the cross product #
		v_plane.Cross(v1, v2)
		
		# draw the skeleton #
		self.root_con = self.controls_parent.Add2DChain(
			self.parent.template.t_root.Translation,
			self.parent.template.t_tip.Translation,
			v_plane,
			c.si2DChainNormalRadian
		)
		
		# rename #
		self.root_con.Name			= xsi.zMapName('%sCon' % (self.parent.basename), 'ChainRoot', self.parent.symmetry)
		self.root_con.Bones(0).Name	= xsi.zMapName(self.parent.basename, 'Control', self.parent.symmetry)
		self.root_con.Effector.Name	= xsi.zMapName('%sCon' % (self.parent.basename), 'ChainEff', self.parent.symmetry)
		
		# format the chain #
		fmt = xsi.zChainFormatter(self.root_con)
		fmt.BoneDisplay = 6
		fmt.BoneSize	= self.size_con * self.parent.scale
		fmt.BoneR		= 0
		fmt.BoneG		= 1
		fmt.BoneB		= 0
		fmt.BoneWireR	= 0
		fmt.BoneWireG	= 1
		fmt.BoneWireB	= 0
		if right:
			fmt.BoneR		= 1
			fmt.BoneG		= 0
			fmt.BoneB		= 0
			fmt.BoneWireR	= 1
			fmt.BoneWireG	= 0
			fmt.BoneWireB	= 0
			
		fmt.RootDisplay = 0
		fmt.RootSize	= self.parent.scale
		fmt.RootR		= 0
		fmt.RootG		= 1
		fmt.RootB		= 0
		fmt.RootWireR	= 0
		fmt.RootWireG	= 1
		fmt.RootWireB	= 0
		if right:
			fmt.RootR		= 1
			fmt.RootG		= 0
			fmt.RootB		= 0
			fmt.RootWireR	= 1
			fmt.RootWireG	= 0
			fmt.RootWireB	= 0
			
		fmt.EffDisplay 	= 0
		fmt.EffSize		= self.parent.scale
		fmt.EffR		= 0
		fmt.EffG		= 1
		fmt.EffB		= 0
		fmt.EffWireR	= 0
		fmt.EffWireG	= 1
		fmt.EffWireB	= 0
		if right:
			fmt.EffR		= 1
			fmt.EffG		= 0
			fmt.EffB		= 0
			fmt.EffWireR	= 1
			fmt.EffWireG	= 0
			fmt.EffWireB	= 0
		
		fmt.EffLastBone	= True
		fmt.Format()
		
		# set neutral pose #
		xsi.SetNeutralPose([self.root_con.Bones(0),
							self.root_con.Effector], c.siSRT, False)

		# set a default key on the rotation of the bones #
		for bone in self.root_con.Bones:
			bone = dispatch(bone)
			bone.Kinematics.Local.RotX.AddFcurve2([0,0], c.siDefaultFCurve)
			bone.Kinematics.Local.RotY.AddFcurve2([0,0], c.siDefaultFCurve)
			bone.Kinematics.Local.RotZ.AddFcurve2([0,0], c.siDefaultFCurve)
			
			# add a transform setup to the con fingers #
			ts = bone.AddProperty('Transform Setup', False)
			ts = dispatch(ts)
			ts.tool.Value = 3
			ts.rotate.Value = 3
			ts.xaxis.Value = True
			ts.yaxis.Value = True
			ts.zaxis.Value = True

		# constrain the control chain to the skeleton parent #
		self.skeleton_parent = dispatch(self.skeleton_parent)
		self.root_con.Kinematics.AddConstraint('Pose', self.skeleton_parent, True)
		
		# reparent the finger fk chain after this one #
		# remove the constraints on the finger root bone #
		self.finger_con = dispatch(self.finger_con)
		for cns in self.finger_con.Kinematics.Constraints:
			xsi.DeleteObj(cns)
			
		self.root_con.Effector.AddChild(self.finger_con)
		
		# add to the control group #
		if self.group_controls:
			self.group_controls.AddMember(self.root_con.Bones)
		
		#---------------------------------------------------------------------
		# add the pick walk and multi select to the fk properties #

		# add the property #
		prop = self.root_con.Bones(0).AddProperty('zPickWalk')
		prop = dispatch(prop)
		
		# add the next (down) con #
		self.finger_con = dispatch(self.finger_con)
		prop.Down.Value = self.finger_con.Bones(0).Name
		# add the previous (up) con to the finger #
		prop_pw = self.finger_con.Bones(0).Properties('zPickWalk')
		if prop_pw:
			prop_pw.Up.Value = self.root_con.Bones(0).Name
			
		#---------------------------------------------------------------------
		# draw the finger skeleton chain #

		# draw the skeleton #
		self.root_skel = self.skeleton_parent.Add2DChain(
			self.parent.template.t_root.Translation,
			self.parent.template.t_tip.Translation,
			v_plane,
			c.si2DChainNormalRadian
		)
		
		# rename #
		self.root_skel.Name				= xsi.zMapName(self.parent.basename, 'ChainRoot', self.parent.symmetry)
		self.root_skel.Bones(0).Name	= xsi.zMapName(self.parent.basename, 'ChainBone', self.parent.symmetry)
		self.root_skel.Effector.Name	= xsi.zMapName(self.parent.basename, 'ChainEff', self.parent.symmetry)
		
		# format the chain #
		xsi.zChainFormatter(self.root_skel).Format()
		
		# set neutral pose #
		xsi.SetNeutralPose([self.root_skel.Bones(0),
							self.root_skel.Effector], c.siSRT, False)

		# reparent the finger chain after this one #
		self.finger_skel = dispatch(self.finger_skel)
		self.root_skel.Effector.AddChild(self.finger_skel)

		#---------------------------------------------------------------------
		# link the skel to the control chain #
		# Note: constraints + bones don't mix, but expressions do! #
		for b in xrange(self.root_skel.Bones.Count):
			self.root_skel.bones(b).Kinematics.Global.Parameters('rotx').AddExpression(
				self.root_con.bones(b).Kinematics.Global.Parameters('rotx').FullName
			) 
			self.root_skel.bones(b).Kinematics.Global.Parameters('roty').AddExpression(
				self.root_con.bones(b).Kinematics.Global.Parameters('roty').FullName
			) 
			self.root_skel.bones(b).Kinematics.Global.Parameters('rotz').AddExpression(
				self.root_con.bones(b).Kinematics.Global.Parameters('rotz').FullName
			) 

		#---------------------------------------------------------------------
		# create a deformer stack #

		for b in xrange(self.root_skel.Bones.Count):
			# finger #
			node_dfm_parent = self.deformer_parent.AddNull(xsi.zMapName(self.parent.basename, 'Custom:DfmSPrnt', self.parent.symmetry))
			node_dfm_shadow = node_dfm_parent.AddNull(xsi.zMapName(self.parent.basename, 'Custom:DfmShdw', self.parent.symmetry))
			node_env 		= node_dfm_shadow.AddNull(xsi.zMapName(self.parent.basename, 'Env', self.parent.symmetry))
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
		
			node_dfm_parent.Kinematics.AddConstraint('Pose', self.root_skel.Bones(b).Parent, False)
			node_dfm_shadow.Kinematics.AddConstraint('Pose', self.root_skel.Bones(b), False)
		
		#---------------------------------------------------------------------
		# add the deformers to the deformers group #
		if self.group_deformers:
			self.group_deformers = dispatch(self.group_deformers)
			self.group_deformers.AddMember(self.deformers)

		#---------------------------------------------------------------------
		# add character sets
		if self.character_set:
			
			# get the subset #
			self.character_set = dispatch(self.character_set)
			upper_set = None
			try:
				upper_set = self.character_set.Get('UpperBody')
			except:                             
				upper_set = self.character_set.AddSubset('UpperBody')
	
			# add the subset #
			self.character_subset = None
			try:
				self.character_subset = self.character_set.Get('%s_%s' % (self.parent.basename, self.parent.symmetry[0].upper()))
			except:                                        
				self.character_subset = self.character_set.AddSubset('%s_%s' % (self.parent.basename, self.parent.symmetry[0].upper()))
			
			# add rotations for each control bone #
			for b in xrange(self.root_con.Bones.Count):
				# add the parameters #
				self.character_subset.AddNodeRot(self.root_con.Bones(b))
		
		# # for setup purposes only #
		# # report the class attributes #
		# for key in self.__dict__:
		# 	log(key)

#-----------------------------------------------------------------------------
# Commands
#-----------------------------------------------------------------------------
def zMetacarpal_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	#oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments
	oArgs.Add('symmetry', c.siArgumentInput, 'left', c.siString)
	return True
	
def zMetacarpal_Execute(symmetry):
	# export the python object #
	import win32com.server
	return win32com.server.util.wrap(
		zMetacarpal(symmetry)
	)
	
