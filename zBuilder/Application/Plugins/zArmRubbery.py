"""
zArmRubbery.py

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
	in_reg.Name = "zArmRubbery"
	in_reg.Email = "andy@zoogloo.net"
	in_reg.URL = ""
	in_reg.Major = 1
	in_reg.Minor = 1

	in_reg.RegisterCommand('zArmRubbery', 'zArmRubbery')
	
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

class zArmRubbery(object):

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
	uid				= 'de7bcd10a4d2f171fd1da0e15388adac' # TODO: Might need to change this, right now the same as the regular arm so we can use that template
	basename		= 'Arm'
	scale			= 1
	
	def __init__(self, sym='left'):
		super(zArmRubbery, self).__init__()
		
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
				self._template = win32com.server.util.wrap(zArmRubbery_Template(self))
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
				self._rig = win32com.server.util.wrap(zArmRubbery_Rig(self))
			# return the private var #
			return self._rig
		def fset(self, value):
			raise Exception('Unable to modify rig value.')
		fdel = fset
		return locals()
			
				
class zArmRubbery_Template(object):
	"""docstring for zArmRubbery_Template"""
	
	_inputs_ = [
		'v_shoulder', 
		'v_elbow', 
		'v_wrist', 
		'v_hand', 
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
		super(zArmRubbery_Template, self).__init__()
		
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
		self.v_shoulder   	= XSIMath.CreateVector3(1.823, 18.742, -0.171)
		self.v_elbow      	= XSIMath.CreateVector3(6.705, 18.554, -0.325)
		self.v_wrist   		= XSIMath.CreateVector3(10.762, 18.391, -0.058)
		self.v_hand   		= XSIMath.CreateVector3(14.001, 18.090, -0.058)
		if re.match(r'^right$', self.parent.symmetry, re.I):
			self.v_shoulder.X   	*= -1
			self.v_elbow.X      	*= -1
			self.v_wrist.X   		*= -1
			self.v_hand.X   		*= -1
			
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
		node_parent = self.model.AddNull('Arm_%s_Container' % self.parent.symmetry[0].upper())
		node_parent.primary_icon.Value = 0
		node_parent.Properties('Visibility').Parameters('viewvis').Value = False
		node_parent.Properties('Visibility').Parameters('rendvis').Value = False
		node_parent.AddProperty('CustomProperty', False, 'zBuilderTemplateItem')
		prop = node_parent.AddProperty('CustomProperty', False, 'zContainer')
		prop = dispatch(prop)
		prop.AddParameter3('ContainerName', c.siString, 'Arm')
		prop.AddParameter3('ContainerSym', c.siString, self.parent.symmetry.lower())
		prop.AddParameter3('ContainerUID', c.siString, self.parent.uid)

		#---------------------------------------------------------------------
		# draw the nodes #
		node_shoulder 	= node_parent.AddNull(xsi.zMapName('ArmShoulder', 'Custom:Tmp', self.parent.symmetry))
		node_shoulder.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_shoulder.AddProperty('CustomProperty', False, 'zShoulder')

		node_elbow	= node_parent.AddNull(xsi.zMapName('ArmElbow', 'Custom:Tmp', self.parent.symmetry))
		node_elbow.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_elbow.AddProperty('CustomProperty', False, 'zElbow')

		node_wrist	= node_parent.AddNull(xsi.zMapName('ArmWrist', 'Custom:Tmp', self.parent.symmetry))
		node_wrist.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_wrist.AddProperty('CustomProperty', False, 'zWrist')

		node_hand	= node_parent.AddNull(xsi.zMapName('ArmHand', 'Custom:Tmp', self.parent.symmetry))
		node_hand.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_hand.AddProperty('CustomProperty', False, 'zHand')

		#---------------------------------------------------------------------
		# set the positions #
		trans = XSIMath.CreateTransform()
		v_result = XSIMath.CreateVector3()

		# shoulder #
		v_result.Scale(self.parent.scale, self.v_shoulder)
		trans.Translation = v_result
		node_shoulder.Kinematics.Global.Transform = trans
		
		# elbow #
		v_result.Scale(self.parent.scale, self.v_elbow)
		trans.Translation = v_result
		node_elbow.Kinematics.Global.Transform = trans

		# wrist #
		v_result.Scale(self.parent.scale, self.v_wrist)
		trans.Translation = v_result
		node_wrist.Kinematics.Global.Transform = trans

		# hand #
		v_result.Scale(self.parent.scale, self.v_hand)
		trans.Translation = v_result
		node_hand.Kinematics.Global.Transform = trans

		#---------------------------------------------------------------------
		# add a visual upvector #
		node_upv						= node_parent.AddNull(xsi.zMapName(self.parent.basename, 'Custom:Tmp', self.parent.symmetry))
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
		
		cns_upv							= node_upv.Kinematics.AddConstraint('Direction', node_wrist, False)
		cns_upv							= dispatch(cns_upv)
		cns_upv.upvct_active.Value 		= True
		cns_upv.UpVectorReference		= node_elbow
		cns_upv.upx						= 0
		cns_upv.upy						= 0
		cns_upv.upz						= 1
		
		cns_pos							= node_upv.Kinematics.AddConstraint('Position', node_shoulder, False)
		
	def GetFromScene(self, sym='left'):
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
			if node.Properties('zShoulder'):
				self.v_shoulder		= node.Kinematics.Global.Transform.Translation
			elif node.Properties('zElbow'):
				self.v_elbow		= node.Kinematics.Global.Transform.Translation
			elif node.Properties('zWrist'):
				self.v_wrist		= node.Kinematics.Global.Transform.Translation
			elif node.Properties('zHand'):
				self.v_hand			= node.Kinematics.Global.Transform.Translation
		
class zArmRubbery_Rig(object):

	_inputs_ = [
		'controls_parent',  		
		'character_set',   		
		'skeleton_parent',  		
		'deformer_parent',  		
		'con_body',  		
		'node_world_ref',  
		'size_elbow_con',
		'size_wrist_con',
		'size_hand_con',
		'size_arm_fk_cons',		
		'size_hand_fk_cons',
		'group_deformers',		
		'group_controls',		
		'ribbon_path',		
		'node_do_not_touch',		
	]
	_outputs_ = [
		'parent',
		'character_subset',
		'root_skel_hand',
		'root_skel_arm',
		'root_hand_con',
		'root_arm_con',
		'con_elbow',
		'con_wrist',
		'con_hand',
		'prop_anim',
		'prop_anim_di',
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
		super(zArmRubbery_Rig, self).__init__()
		
		# set the instance variables #
		self.parent					= parent

		# set the defaults for the input variables #
		for item in self._inputs_:
			setattr(self, item, None)
			
		# set specific types #
		self.deformers = dispatch('XSI.Collection')
		
		# set the default controller sizes #
		self.size_elbow_con			= 1
		self.size_wrist_con			= 1
		self.size_hand_con			= 1.25
		self.size_arm_fk_cons		= 2
		self.size_hand_fk_cons		= 2		
		
	# override the attribute setter to dispatch objects when setting #
	def __setattr__(self, name, value):
		# if the name is in the inputs...#
		if name in self._inputs_ or name in self._outputs_:
			# ... dispatch the value (if we can)#
			try:
				self.__dict__[name] = dispatch(value)
			except:
				self.__dict__[name] = value
		else:
			raise Exception('Unable to locate attribute "%s"' % (name))
			
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
		# draw the arm ik chain #
		
		# calculate the plane vector #
		v_plane = XSIMath.CreateVector3()
		v1		= XSIMath.CreateVector3()
		v2		= XSIMath.CreateVector3()
		# get vector from root to ankle #
		v1.Sub(template.v_shoulder, template.v_elbow)
		# get vector from root to knee #
		v2.Sub(template.v_shoulder, template.v_wrist)
		# get the cross product #
		v_plane.Cross(v2, v1)
		
		# draw the skeleton #
		self.root_arm_con = self.controls_parent.Add2DChain(
			template.v_shoulder,
			template.v_elbow,
			v_plane,
			c.si2DChainNormalRadian
		)
		
		# rename #
		self.root_arm_con.Name			= xsi.zMapName('ArmCon', 'ChainRoot', self.parent.symmetry)
		self.root_arm_con.Bones(0).Name	= xsi.zMapName('ArmFk', 'Control', self.parent.symmetry, 1)
		self.root_arm_con.Effector.Name	= xsi.zMapName('ArmCon', 'ChainEff', self.parent.symmetry)
		
		# add another bone #
		self.root_arm_con.AddBone(
			template.v_wrist,
			c.siChainBonePin,
			xsi.zMapName('ArmFk', 'Control', self.parent.symmetry, 2)
		)

		# format the chain #
		fmt = xsi.zChainFormatter(self.root_arm_con)
		fmt.BoneDisplay = 6
		fmt.BoneSize	= self.size_arm_fk_cons * self.parent.scale
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
		xsi.SetNeutralPose([self.root_arm_con.Bones(0),
							self.root_arm_con.Bones(1),
							self.root_arm_con.Effector], c.siSRT, False)

		# set a default key on the rotation of the bones #
		for bone in self.root_arm_con.Bones:
			bone = dispatch(bone)
			bone.Kinematics.Local.RotX.AddFcurve2([0,0], c.siDefaultFCurve)
			bone.Kinematics.Local.RotY.AddFcurve2([0,0], c.siDefaultFCurve)
			bone.Kinematics.Local.RotZ.AddFcurve2([0,0], c.siDefaultFCurve)
			
		# constrain the control chain to the clavicle skeleton #
		self.skeleton_parent = dispatch(self.skeleton_parent)
		self.root_arm_con.Kinematics.AddConstraint('Pose', self.skeleton_parent, True)
		
		# add to the group controls #
		if self.group_controls:
			self.group_controls.AddMember(self.root_arm_con.Bones)
		
		#---------------------------------------------------------------------
		# draw the arm skeleton #
		self.root_skel_arm = self.skeleton_parent.Add2DChain(
			template.v_shoulder,
			template.v_elbow,
			v_plane,
			c.si2DChainNormalRadian
		)
		
		# rename #
		self.root_skel_arm.Name				= xsi.zMapName('Arm', 'ChainRoot', self.parent.symmetry)
		self.root_skel_arm.Bones(0).Name	= xsi.zMapName('Arm', 'ChainBone', self.parent.symmetry, 1)
		self.root_skel_arm.Effector.Name	= xsi.zMapName('Arm', 'ChainEff', self.parent.symmetry)
		
		# add another bone #
		self.root_skel_arm.AddBone(
			template.v_wrist,
			c.siChainBonePin,
			xsi.zMapName('Arm', 'ChainBone', self.parent.symmetry, 2)
		)

		# format the chain #
		xsi.zChainFormatter(self.root_skel_arm).Format()
		
		# set neutral pose #
		xsi.SetNeutralPose([self.root_skel_arm.Bones(0),
							self.root_skel_arm.Bones(1),
							self.root_skel_arm.Effector], c.siSRT, False)
							
		# hook up the skel to the control arm #
		# Note: constraints + bones don't mix, but expressions do! #
		self.root_skel_arm.bones(0).Kinematics.Global.Parameters('rotx').AddExpression(
			self.root_arm_con.bones(0).Kinematics.Global.Parameters('rotx').FullName
		) 
		self.root_skel_arm.bones(0).Kinematics.Global.Parameters('roty').AddExpression(
			self.root_arm_con.bones(0).Kinematics.Global.Parameters('roty').FullName
		) 
		self.root_skel_arm.bones(0).Kinematics.Global.Parameters('rotz').AddExpression(
			self.root_arm_con.bones(0).Kinematics.Global.Parameters('rotz').FullName
		) 

		self.root_skel_arm.bones(1).Kinematics.Global.Parameters('rotx').AddExpression(
			self.root_arm_con.bones(1).Kinematics.Global.Parameters('rotx').FullName
		) 
		self.root_skel_arm.bones(1).Kinematics.Global.Parameters('roty').AddExpression(
			self.root_arm_con.bones(1).Kinematics.Global.Parameters('roty').FullName
		) 
		self.root_skel_arm.bones(1).Kinematics.Global.Parameters('rotz').AddExpression(
			self.root_arm_con.bones(1).Kinematics.Global.Parameters('rotz').FullName
		) 
		
		#---------------------------------------------------------------------
		# draw the hand ik chain #

		# draw the skeleton #
		self.root_hand_con = self.root_arm_con.Effector.Add2DChain(
			template.v_wrist,
			template.v_hand,
			v_plane,
			c.si2DChainNormalRadian
		)
		
		# rename #
		self.root_hand_con.Name				= xsi.zMapName('HandCon', 'ChainRoot', self.parent.symmetry)
		self.root_hand_con.Bones(0).Name	= xsi.zMapName('HandFk', 'Control', self.parent.symmetry, 1)
		self.root_hand_con.Effector.Name	= xsi.zMapName('HandCon', 'ChainEff', self.parent.symmetry)
		
		# format the chain #
		fmt = xsi.zChainFormatter(self.root_hand_con)
		fmt.BoneDisplay = 6
		fmt.BoneSize	= self.size_hand_fk_cons * self.parent.scale
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
		xsi.SetNeutralPose([self.root_arm_con.Bones(0),
							self.root_arm_con.Bones(1),
							self.root_arm_con.Effector], c.siSRT, False)

		# set a default key on the rotation of the bones #
		for bone in self.root_hand_con.Bones:
			bone = dispatch(bone)
			bone.Kinematics.Local.RotX.AddFcurve2([0,0], c.siDefaultFCurve)
			bone.Kinematics.Local.RotY.AddFcurve2([0,0], c.siDefaultFCurve)
			bone.Kinematics.Local.RotZ.AddFcurve2([0,0], c.siDefaultFCurve)
			
		# add to the group controls #
		if self.group_controls:
			self.group_controls.AddMember(self.root_hand_con.Bones)
		
		#---------------------------------------------------------------------
		# draw the hand skeleton #
		self.root_skel_hand = self.root_skel_arm.Effector.Add2DChain(
			template.v_wrist,
			template.v_hand,
			v_plane,
			c.si2DChainNormalRadian
		)
		
		# rename #
		self.root_skel_hand.Name			= xsi.zMapName('Hand', 'ChainRoot', self.parent.symmetry)
		self.root_skel_hand.Bones(0).Name	= xsi.zMapName('Hand', 'ChainBone', self.parent.symmetry, 1)
		self.root_skel_hand.Effector.Name	= xsi.zMapName('Hand', 'ChainEff', self.parent.symmetry)
		
		# format the chain #
		xsi.zChainFormatter(self.root_skel_hand).Format()
		
		# set neutral pose #
		xsi.SetNeutralPose([self.root_skel_hand.Bones(0),
							self.root_skel_hand.Effector], c.siSRT, False)
							
		# hook up the skel to the control arm #
		# Note: constraints + bones don't mix, but expressions do! #
		self.root_skel_hand.bones(0).Kinematics.Global.Parameters('rotx').AddExpression(
			self.root_hand_con.bones(0).Kinematics.Global.Parameters('rotx').FullName
		) 
		self.root_skel_hand.bones(0).Kinematics.Global.Parameters('roty').AddExpression(
			self.root_hand_con.bones(0).Kinematics.Global.Parameters('roty').FullName
		) 
		self.root_skel_hand.bones(0).Kinematics.Global.Parameters('rotz').AddExpression(
			self.root_hand_con.bones(0).Kinematics.Global.Parameters('rotz').FullName
		) 

		#---------------------------------------------------------------------
		# draw the WRIST con

		# redispatch the body con #
		self.con_body = dispatch(self.con_body)

		# create the elbow controller #
		self.con_wrist 							= xsi.zCon()
		self.con_wrist.type 					= '4_pin'
		self.con_wrist.size 					= self.size_wrist_con * self.parent.scale
		self.con_wrist.transform.Translation	= self.root_arm_con.Effector.Kinematics.Global.Transform.Translation
		self.con_wrist.basename 				= 'Wrist'
		self.con_wrist.symmetry 				= self.parent.symmetry
		self.con_wrist.parent_node 				= self.con_body.node_hook
		self.con_wrist.rotation_order 			= 'zyx'
		self.con_wrist.red 						= 0
		self.con_wrist.green 					= 1
		self.con_wrist.blue 					= 0
		if right:
			self.con_wrist.red 					= 1
			self.con_wrist.green 				= 0
			self.con_wrist.blue 				= 0
		self.con_wrist.Draw()
		self.con_wrist.AddTransformSetupPos('local')
		
		# add to the group controls #
		if self.group_controls:
			self.group_controls.AddMember(self.con_wrist.node_con)
		
		# align it to the hand #
		trans = self.root_hand_con.Bones(0).Kinematics.Global.Transform
		trans.AddLocalRotation(
			XSIMath.CreateRotation(0, XSIMath.DegreesToRadians(90), 0)
		)
		self.con_wrist.node_con.Kinematics.Global.Transform = trans
		xsi.ResetTransform(self.con_wrist.node_con, c.siCtr, c.siSRT, c.siXYZ)
		
		# add a default constraint to be relative to the body #
		self.con_wrist.node_rest.Kinematics.AddConstraint('Pose', self.con_body.node_hook, True)
		
		#---------------------------------------------------------------------
		# draw the HAND con

		# create the elbow controller #
		self.con_hand 							= xsi.zCon()
		self.con_hand.type 						= 'sphere'
		self.con_hand.size 						= self.size_hand_con * self.parent.scale
		self.con_hand.transform					= self.root_hand_con.Bones(0).Kinematics.Global.Transform
		self.con_hand.basename 					= 'Hand'
		self.con_hand.symmetry 					= self.parent.symmetry
		self.con_hand.parent_node 				= self.con_wrist.node_hook
		self.con_hand.rotation_order 			= 'zyx'
		self.con_hand.red 						= 0
		self.con_hand.green 					= 1
		self.con_hand.blue 						= 0
		if right:
			self.con_hand.red 					= 1
			self.con_hand.green 				= 0
			self.con_hand.blue 					= 0
		self.con_hand.Draw()
		self.con_hand.AddTransformSetupRot('add')
		
		# add to the group controls #
		if self.group_controls:
			self.group_controls.AddMember(self.con_hand.node_con)
		
		# constrain the con to the arm effector #
		cns_hand_pos = self.con_hand.node_rest.Kinematics.AddConstraint('Position', self.root_arm_con.Effector, True)
		self.con_body = dispatch(self.con_body)
		cns_hand_ori = self.con_hand.node_rest.Kinematics.AddConstraint('Pose', self.con_body.node_hook, True)
		cns_hand_ori = dispatch(cns_hand_ori)
		cns_hand_ori.cnspos.Value = False

		#---------------------------------------------------------------------
		# draw the ELBOW con

		# calculate the elbow position #
		trans = self.root_arm_con.Bones(1).Kinematics.Global.Transform
		# get the middle rotation between the bones #
		quat_1 = self.root_arm_con.Bones(0).Kinematics.Global.Transform.Rotation.Quaternion
		quat_2 = self.root_arm_con.Bones(1).Kinematics.Global.Transform.Rotation.Quaternion
		quat_mid = XSIMath.CreateQuaternion()
		quat_mid.Slerp(quat_1, quat_2, 0.5)
		# put the mid quat in the transform #
		rot = XSIMath.CreateRotation()
		rot.Quaternion = quat_mid
		trans.Rotation = rot
		# move the position out by the length of the arm #
		trans.AddLocalTranslation(
			XSIMath.CreateVector3(0, self.root_arm_con.Bones(0).length.Value, 0)
		)
		# set the default orientation to world 0 #
		trans.Rotation = XSIMath.CreateRotation()

		# create the elbow controller #
		self.con_elbow 							= xsi.zCon()
		self.con_elbow.type 					= 'round_box'
		self.con_elbow.size 					= self.size_elbow_con * self.parent.scale
		self.con_elbow.transform 				= trans
		self.con_elbow.basename 				= 'Elbow'
		self.con_elbow.symmetry 				= self.parent.symmetry
		self.con_elbow.parent_node 				= self.con_body.node_hook
		self.con_elbow.rotation_order 			= 'zyx'
		self.con_elbow.red 						= 0
		self.con_elbow.green 					= 0.8
		self.con_elbow.blue 					= 0
		if right:
			self.con_elbow.red 					= 0.8
			self.con_elbow.green 				= 0
			self.con_elbow.blue 				= 0
		self.con_elbow.Draw()
		self.con_elbow.AddTransformSetupPos('local')

		# add to the group controls #
		if self.group_controls:
			self.group_controls.AddMember(self.con_elbow.node_con)
		
		#---------------------------------------------------------------------
		# constrain the chain #
		
		# arm effector #
		self.root_arm_con.Effector.Kinematics.AddConstraint('Pose', self.con_wrist.node_hook, True)
		
		# hand bone #
		cns_hand_con = self.root_hand_con.Bones(0).Kinematics.AddConstraint('Pose', self.con_hand.node_hook, True)
		cns_hand_con = dispatch(cns_hand_con)
		
		# up vector #
		xsi.ApplyOp("SkeletonUpVector", "%s;%s" % \
					(self.root_arm_con.Bones(0), self.con_elbow.node_hook), 3, 
					c.siPersistentOperation, "", 0)

		#---------------------------------------------------------------------
		# add a transform setup to the fk bones #
		col_bones = dispatch('XSI.Collection')
		col_bones.AddItems(self.root_arm_con.Bones)
		col_bones.AddItems(self.root_hand_con.Bones)
		for bone in col_bones:
			ts = bone.AddProperty('Transform Setup', False)
			ts = dispatch(ts)
			ts.tool.Value = 3
			ts.rotate.Value = 3
			ts.xaxis.Value = True
			ts.yaxis.Value = True
			ts.zaxis.Value = True

		#---------------------------------------------------------------------
		# add ik/fk switch to arm con #
		# create the property #
		self.prop_anim = self.con_wrist.node_con.AddProperty('CustomProperty', False, 'zAnim_%s_%s' % (self.parent.basename, self.parent.symmetry))
		self.prop_anim = dispatch(self.prop_anim)
		
		# add the parameter #
		param_ikfk = self.prop_anim.AddParameter3('FK_IK', c.siFloat, 1.0, 0.0, 1.0)
		
		# hook up the blend ik slider #
		self.root_arm_con.Bones(0).Properties('Kinematic Chain').Parameters('blendik').AddExpression(param_ikfk.FullName)
		
		# hook up the hand constraint blend #
		# cns_hand_ori.blendweight.AddExpression(param_ikfk.FullName)
		cns_hand_con.blendweight.AddExpression(param_ikfk.FullName)
		
		# add a HUD #
		self.prop_anim_di = self.con_wrist.node_con.AddProperty('CustomProperty', False, 'DisplayInfo_zAnim_%s_%s' % (self.parent.basename, self.parent.symmetry))
		self.prop_anim_di.AddProxyParameter(param_ikfk, None, 'FK_IK')
	
		# add proxy's to the other arm controllers #
		col_fk = dispatch('XSI.Collection')
		col_fk.AddItems(self.root_arm_con.Bones)
		col_fk.AddItems(self.root_hand_con.Bones)
		col_fk.Add(self.con_hand.node_con)
		col_fk.Add(self.con_elbow.node_con)
		for item in col_fk:
			prop_anim = item.AddProperty('CustomProperty', False, 'zAnim_%s_%s' % (self.parent.basename, self.parent.symmetry))
			prop_anim.AddProxyParameter(param_ikfk, None, 'FK_IK')

			prop_anim_di = item.AddProperty('CustomProperty', False, 'DisplayInfo_zAnim_%s_%s' % (self.parent.basename, self.parent.symmetry))
			prop_anim_di.AddProxyParameter(param_ikfk, None, 'FK_IK')
		
		
		#---------------------------------------------------------------------
		# link the color of the FK controls to the IK_FK slider #

		# build the fk expression #
		expr_fk_r = 'cond(%s.chain.blendik != 0.0, 0.0, 0.0)'  % self.root_arm_con.Bones(0).FullName
		expr_fk_g = 'cond(%s.chain.blendik != 0.0, 0.25, 1.0)' % self.root_arm_con.Bones(0).FullName
		expr_fk_b = 'cond(%s.chain.blendik != 0.0, 0.0, 0.0)'  % self.root_arm_con.Bones(0).FullName
		if right:
			expr_fk_r = 'cond(%s.chain.blendik != 0.0, 0.25, 1.0)' % self.root_arm_con.Bones(0).FullName
			expr_fk_g = 'cond(%s.chain.blendik != 0.0, 0.0, 0.0)'  % self.root_arm_con.Bones(0).FullName
			expr_fk_b = 'cond(%s.chain.blendik != 0.0, 0.0, 0.0)'  % self.root_arm_con.Bones(0).FullName

		# build the ik expression #
		expr_ik_r = 'cond(%s.chain.blendik != 1.0, 0.0, 0.0)'  % self.root_arm_con.Bones(0).FullName
		expr_ik_g = 'cond(%s.chain.blendik != 1.0, 0.25, 1.0)' % self.root_arm_con.Bones(0).FullName
		expr_ik_b = 'cond(%s.chain.blendik != 1.0, 0.0, 0.0)'  % self.root_arm_con.Bones(0).FullName
		if right:
			expr_ik_r = 'cond(%s.chain.blendik != 1.0, 0.25, 1.0)' % self.root_arm_con.Bones(0).FullName
			expr_ik_g = 'cond(%s.chain.blendik != 1.0, 0.0, 0.0)'  % self.root_arm_con.Bones(0).FullName
			expr_ik_b = 'cond(%s.chain.blendik != 1.0, 0.0, 0.0)'  % self.root_arm_con.Bones(0).FullName

		# add the expression to the fk bones #
		for bone in self.root_arm_con.Bones:
			bone = dispatch(bone)
			bone.R.AddExpression(expr_fk_r)
			bone.G.AddExpression(expr_fk_g)
			bone.B.AddExpression(expr_fk_b)
		self.root_hand_con.Bones(0).R.AddExpression(expr_fk_r)
		self.root_hand_con.Bones(0).G.AddExpression(expr_fk_g)
		self.root_hand_con.Bones(0).B.AddExpression(expr_fk_b)

		# add the expression to the controller #
		disp = self.con_wrist.node_con.AddProperty('Display Property')
		disp = dispatch(disp)
		disp.wirecolorr.AddExpression(expr_ik_r)
		disp.wirecolorg.AddExpression(expr_ik_g)
		disp.wirecolorb.AddExpression(expr_ik_b)

		disp = self.con_hand.node_con.AddProperty('Display Property')
		disp = dispatch(disp)
		disp.wirecolorr.AddExpression(expr_ik_r)
		disp.wirecolorg.AddExpression(expr_ik_g)
		disp.wirecolorb.AddExpression(expr_ik_b)
		
		disp = self.con_elbow.node_con.AddProperty('Display Property')
		disp = dispatch(disp)
		disp.wirecolorr.AddExpression(expr_ik_r)
		disp.wirecolorg.AddExpression(expr_ik_g)
		disp.wirecolorb.AddExpression(expr_ik_b)
		
		#---------------------------------------------------------------------
		# link the visbility on the controls to the ik fk switcher #
		
		# controller #
		self.con_hand.node_con.Properties('Visibility').viewvis.AddExpression(
			'cond(%s.chain.blendik != 0, 1, 0)' % self.root_arm_con.Bones(0).FullName
		)
		self.con_wrist.node_con.Properties('Visibility').viewvis.AddExpression(
			'cond(%s.chain.blendik != 0, 1, 0)' % self.root_arm_con.Bones(0).FullName
		)
		self.con_elbow.node_con.Properties('Visibility').viewvis.AddExpression(
			'cond(%s.chain.blendik != 0, 1, 0)' % self.root_arm_con.Bones(0).FullName
		)
		
		# fk #
		for bone in self.root_arm_con.Bones:
			bone = dispatch(bone)
			bone.Properties('Visibility').viewvis.AddExpression(
				'cond(%s.chain.blendik != 1, 1, 0)' % self.root_arm_con.Bones(0).FullName
			)
			
		self.root_hand_con.Bones(0).Properties('Visibility').viewvis.AddExpression(
			'cond(%s.chain.blendik != 1, 1, 0)' % self.root_arm_con.Bones(0).FullName
		)
			
		#---------------------------------------------------------------------
		# Add constraint to make hand position relative to the body #
		cns_wrist_pos = self.con_wrist.node_rest.Kinematics.AddConstraint('Pose', self.node_world_ref, True)
		cns_wrist_pos = dispatch(cns_wrist_pos)
		
		cns_hand_pose = self.con_hand.node_rest.Kinematics.AddConstraint('Pose', self.node_world_ref, True)
		cns_hand_pose = dispatch(cns_hand_pose)
		cns_hand_pose.cnspos.Value	= False
		
		# add the slider #
		param_link_world = self.prop_anim.AddParameter3('LinkToWorld', c.siFloat, 0.0, 0.0, 1.0)
		cns_wrist_pos.blendweight.AddExpression(param_link_world.FullName)
		cns_hand_pose.blendweight.AddExpression(param_link_world.FullName)
		self.prop_anim_di.AddProxyParameter(param_link_world, None, 'LinkToWorld')
	
		#---------------------------------------------------------------------
		# add arm ribbon
		
		# create a ribbon node under the do not touch #
		ribbon_parent_name = xsi.zMapName('Ribbon', 'Branch', 'None')
		ribbon_parent = self.node_do_not_touch.FindChild(ribbon_parent_name)
		if not ribbon_parent:
			ribbon_parent = self.node_do_not_touch.AddNull(ribbon_parent_name)
		ribbon_parent.primary_icon.Value = 0
		ribbon_parent.Properties('Visibility').Parameters('viewvis').Value = False
		ribbon_parent.Properties('Visibility').Parameters('rendvis').Value = False
		
		# build the start transform #
		trans_start = self.root_skel_arm.Bones(0).Kinematics.Global.Transform
		# trans_start.AddLocalRotation(XSIMath.CreateRotation(0, 0, XSIMath.DegreesToRadians(-90)))

		# build the end transform #
		trans_end 					= XSIMath.CreateTransform()
		trans_end.Copy(trans_start)
		trans_end.Translation 		= self.root_skel_hand.Bones(0).Kinematics.Global.Transform.Translation
		
		# install the ribbon #
		ribbon 						= xsi.zRibbon(self.parent.basename, self.parent.symmetry)
		ribbon.node_start			= self.root_skel_arm
		ribbon.node_end				= self.root_skel_hand.Bones(0)
		ribbon.trans_start			= trans_start
		ribbon.trans_end			= trans_end
		ribbon.parent				= ribbon_parent
		ribbon.model_path			= self.ribbon_path
		ribbon.Install()
		
		# add a node above the node_b to use as an anchor #
		node_anchor = ribbon.node_b.Parent.AddNull(xsi.zMapName(self.parent.basename, 'Custom:Anchor', self.parent.symmetry))
		xsi.zHide(node_anchor)
		node_anchor.Kinematics.Global.Transform = ribbon.node_b.Kinematics.Global.Transform
		node_anchor.AddChild(ribbon.node_b)

		# constrain anchor node to the elbow #
		# node_anchor.Kinematics.AddConstraint('Position', self.root_skel_arm.Bones(1), True)
		node_anchor.Kinematics.AddConstraint('Pose', self.root_skel_arm.Bones(0), True)
		
		# reparent the deformers #
		for item in ribbon.deformers:
			if item.Parent and re.match(r'.+Dfm$', item.Parent.Name):
				self.deformer_parent.AddChild(item.Parent)

		#---------------------------------------------------------------------
		# create a deformer stack #

		# arm1 #
		node_dfm_parent = self.deformer_parent.AddNull(xsi.zMapName('Arm', 'Custom:DfmPrnt', self.parent.symmetry, 1))
		node_dfm_shadow = node_dfm_parent.AddNull(xsi.zMapName('Arm', 'Custom:DfmShdw', self.parent.symmetry, 1))
		node_env 		= node_dfm_shadow.AddNull(xsi.zMapName('Arm', 'Env', self.parent.symmetry, 1))
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
		
		node_dfm_parent.Kinematics.AddConstraint('Pose', self.root_arm_con.Bones(0).Parent, False)
		node_dfm_shadow.Kinematics.AddConstraint('Pose', self.root_arm_con.Bones(0), False)
		
		# arm2 #
		node_dfm_parent = self.deformer_parent.AddNull(xsi.zMapName('Arm', 'Custom:DfmPrnt', self.parent.symmetry, 2))
		node_dfm_shadow = node_dfm_parent.AddNull(xsi.zMapName('Arm', 'Custom:DfmShdw', self.parent.symmetry, 2))
		node_env 		= node_dfm_shadow.AddNull(xsi.zMapName('Arm', 'Env', self.parent.symmetry, 2))
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
		
		node_dfm_parent.Kinematics.AddConstraint('Pose', self.root_arm_con.Bones(1).Parent, False)
		node_dfm_shadow.Kinematics.AddConstraint('Pose', self.root_arm_con.Bones(1), False)
		
		# hand #
		node_dfm_parent = self.deformer_parent.AddNull(xsi.zMapName('Hand', 'Custom:DfmPrnt', self.parent.symmetry, 2))
		node_dfm_shadow = node_dfm_parent.AddNull(xsi.zMapName('Hand', 'Custom:DfmShdw', self.parent.symmetry, 2))
		node_env 		= node_dfm_shadow.AddNull(xsi.zMapName('Hand', 'Env', self.parent.symmetry, 2))
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
		
		node_dfm_parent.Kinematics.AddConstraint('Pose', self.root_hand_con.Bones(0).Parent, False)
		node_dfm_shadow.Kinematics.AddConstraint('Pose', self.root_hand_con.Bones(0), False)
		
		#---------------------------------------------------------------------
		# add the deformers to the deformers group #
		if self.group_deformers:
			self.group_deformers = dispatch(self.group_deformers)
			self.group_deformers.AddMember(self.deformers)
			self.group_deformers.AddMember(ribbon.deformers)

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
	
			# add the leg subset #
			self.character_subset = upper_set.AddSubset(
				xsi.zMapName(self.parent.basename, 'None', self.parent.symmetry)
			)
			
			# add the parameters #
			self.character_subset.AddNodeRot(self.root_arm_con.Bones(0))
			self.character_subset.AddNodeRot(self.root_arm_con.Bones(1))
			self.character_subset.AddNodeRot(self.root_hand_con.Bones(0))
			self.character_subset.AddNodeRot(self.con_hand.node_con)
			self.character_subset.AddNodePos(self.con_wrist.node_con)
			self.character_subset.AddNodePosRot(self.con_elbow.node_con)
			self.character_subset.AddParams(param_ikfk)
			self.character_subset.AddParams(param_link_world)
			
		
		# # for setup purposes only #
		# # report the class attributes #
		# for key in self.__dict__:
		# 	log(key)

			
			
#-----------------------------------------------------------------------------
# Commands
#-----------------------------------------------------------------------------
def zArmRubbery_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	#oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments
	oArgs.Add('symmetry', c.siArgumentInput, 'left', c.siString)
	return True
	
def zArmRubbery_Execute(symmetry):
	# export the python object #
	import win32com.server
	return win32com.server.util.wrap(
		zArmRubbery(symmetry)
	)
	
