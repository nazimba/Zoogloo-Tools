"""
zHeadPuppet.py

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

xsi = Application
log = xsi.logmessage

null = None
false = 0
true = 1

def XSILoadPlugin(in_reg):
	in_reg.Author = "Andy Buecker"
	in_reg.Name = "zHeadPuppet"
	in_reg.Email = "andy@zoogloo.net"
	in_reg.URL = ""
	in_reg.Major = 1
	in_reg.Minor = 1

	in_reg.RegisterCommand('zHeadPuppet', 'zHeadPuppet')
	
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

class zHeadPuppet(object):

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
	uid				= 'e49e2ace36317f33a46e61b274e76c3a'
	basename		= 'HeadPuppet'
	scale			= 1
	symmetry		= 'middle'
	
	def __init__(self):
		super(zHeadPuppet, self).__init__()
		
		# reset the instance varaibles #
		_template 		= None
		_rig		 	= None
	
	@zProp
	def template():
		'''Template Accessor'''
		def fget(self):
			# create a template if it doesn't exist #
			if not self._template:
				# wrap a new class #
				self._template = dispatch(win32com.server.util.wrap(zHeadPuppet_Template(self)))
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
				self._rig = dispatch(win32com.server.util.wrap(zHeadPuppet_Rig(self)))
			# return the private var #
			return self._rig
		def fset(self, value):
			raise Exception('Unable to modify rig value.')
		fdel = fset
		return locals()
			
				
class zHeadPuppet_Template(object):
	"""docstring for zHeadPuppet_Template"""
	
	_inputs_ = [
		'v_head_base',
		'v_head_top', 
		'v_face',   
		'v_lip_upper',	   
		'v_mouth',	   
		'v_lip_lower',	   
		'v_cheek_l',	   
		'v_cheek_r',	   
		'v_eye_aim',  
		't_eye_l',	   
		't_eye_r',
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
		super(zHeadPuppet_Template, self).__init__()
		
		# set the instance variables #
		self.parent			= parent
		
		self.LoadDefaultValues()
	
	def LoadDefaultValues(self):
		"""
		Sets the default values 
		"""
		self.v_head_base			= XSIMath.CreateVector3(0.000, 23.250, 0.534)
		self.v_head_top				= XSIMath.CreateVector3(0.000, 29.840, 0.534)
		self.v_face					= XSIMath.CreateVector3(0.000, 26.024, 2.323)   
		self.v_lip_lower			= XSIMath.CreateVector3(0.000, 21.822, 4.518)
		self.v_lip_upper			= XSIMath.CreateVector3(0.000, 24.133, 4.885)
		self.v_mouth				= XSIMath.CreateVector3(0.000, 23.292, 2.786)
		self.v_cheek_l				= XSIMath.CreateVector3(2.743, 24.143, 2.424)
		self.v_cheek_r				= XSIMath.CreateVector3(-2.743, 24.143, 2.424)
		self.v_eye_aim				= XSIMath.CreateVector3(0.000, 26.922, 30.000)

		self.t_eye_l				= XSIMath.CreateTransform()
		self.t_eye_l.Translation 	= XSIMath.CreateVector3(1.452, 26.877, 4.350)
		self.t_eye_l.Rotation 		= XSIMath.CreateRotation(0, XSIMath.DegreesToRadians(-90), 0)

		self.t_eye_r				= XSIMath.CreateTransform()
		self.t_eye_r.Translation 	= XSIMath.CreateVector3(-1.452, 26.877, 4.350)
		self.t_eye_r.Rotation 		= XSIMath.CreateRotation(0, XSIMath.DegreesToRadians(-90), 0)

		self.scale 					= 1
		self.model 					= xsi.ActiveSceneRoot
		

	def Draw(self):
		"""docstring for Draw"""
		# get the model #
		if not self.model:
			raise Exception('Model attribute for template not specified.')
		
		# dispatch the model #
		self.model = dispatch(self.model)
		
		#---------------------------------------------------------------------
		# create a node to hold the template #
		node_parent = self.model.AddNull(xsi.zMapName(self.parent.basename, 'Custom:Container', self.parent.symmetry))
		node_parent.primary_icon.Value = 0
		node_parent.AddProperty('CustomProperty', False, 'zBuilderTemplateItem')
		prop = node_parent.AddProperty('CustomProperty', False, 'zContainer')
		prop = dispatch(prop)
		prop.AddParameter3('ContainerName', c.siString, self.parent.basename)
		prop.AddParameter3('ContainerUID', c.siString, self.parent.uid)
			
		#---------------------------------------------------------------------
		# draw the nodes #
		node_head_base 	= node_parent.AddNull(xsi.zMapName('HeadBase', 'Custom:Tmp', self.parent.symmetry))
		node_head_base.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_head_base.AddProperty('CustomProperty', False, 'zHeadPuppetBase')

		node_head_top 	= node_head_base.AddNull(xsi.zMapName('HeadTop', 'Custom:Tmp', self.parent.symmetry))
		node_head_top.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_head_top.AddProperty('CustomProperty', False, 'zHeadPuppetTop')
		
		node_face 		= node_head_base.AddNull(xsi.zMapName('Face', 'Custom:Tmp', self.parent.symmetry))
		node_face.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_face.AddProperty('CustomProperty', False, 'zHeadPuppetFace')

		node_lip_upper 		= node_head_base.AddNull(xsi.zMapName('LipUpper', 'Custom:Tmp', self.parent.symmetry))
		node_lip_upper.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_lip_upper.AddProperty('CustomProperty', False, 'zHeadPuppetLipUpper')

		node_mouth 		= node_head_base.AddNull(xsi.zMapName('Mouth', 'Custom:Tmp', self.parent.symmetry))
		node_mouth.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_mouth.AddProperty('CustomProperty', False, 'zHeadPuppetMouth')

		node_lip_lower 		= node_head_base.AddNull(xsi.zMapName('LipLower', 'Custom:Tmp', self.parent.symmetry))
		node_lip_lower.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_lip_lower.AddProperty('CustomProperty', False, 'zHeadPuppetLipLower')
		
		node_cheek_l 		= node_head_base.AddNull(xsi.zMapName('Cheek', 'Custom:Tmp', 'left'))
		node_cheek_l.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_cheek_l.AddProperty('CustomProperty', False, 'zHeadPuppetCheekL')

		node_cheek_r 		= node_head_base.AddNull(xsi.zMapName('Cheek', 'Custom:Tmp', 'right'))
		node_cheek_r.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_cheek_r.AddProperty('CustomProperty', False, 'zHeadPuppetCheekR')
		
		node_eye_l 		= node_head_base.AddNull(xsi.zMapName('Eye', 'Custom:Tmp', 'left'))
		node_eye_l.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_eye_l.AddProperty('CustomProperty', False, 'zHeadPuppetEyeL')
		
		node_eye_r 		= node_head_base.AddNull(xsi.zMapName('Eye', 'Custom:Tmp', 'right'))
		node_eye_r.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_eye_r.AddProperty('CustomProperty', False, 'zHeadPuppetEyeR')
		
		node_eye_aim	= node_head_base.AddNull(xsi.zMapName('EyeAim', 'Custom:Tmp', self.parent.symmetry))
		node_eye_aim.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_eye_aim.AddProperty('CustomProperty', False, 'zHeadPuppetEyeAim')
		

		#---------------------------------------------------------------------
		# set the positions #
		trans = XSIMath.CreateTransform()
		v_result = XSIMath.CreateVector3()
		
		# head base #
		v_result.Scale(self.parent.scale, self.v_head_base)
		trans.Translation = v_result
		node_head_base.Kinematics.Global.Transform = trans
		
		# head top #
		v_result.Scale(self.parent.scale, self.v_head_top)
		trans.Translation = v_result
		node_head_top.Kinematics.Global.Transform = trans
		
		# face #
		v_result.Scale(self.parent.scale, self.v_face)
		trans.Translation = v_result
		node_face.Kinematics.Global.Transform = trans

		# lip_upper #
		v_result.Scale(self.parent.scale, self.v_lip_upper)
		trans.Translation = v_result
		node_lip_upper.Kinematics.Global.Transform = trans

		# mouth #
		v_result.Scale(self.parent.scale, self.v_mouth)
		trans.Translation = v_result
		node_mouth.Kinematics.Global.Transform = trans

		# lip_lower #
		v_result.Scale(self.parent.scale, self.v_lip_lower)
		trans.Translation = v_result
		node_lip_lower.Kinematics.Global.Transform = trans

		# eye left #
		v_result.Scale(self.parent.scale, self.t_eye_l.Translation)
		self.t_eye_l.Translation = v_result
		node_eye_l.Kinematics.Global.Transform = self.t_eye_l
		
		# eye right #
		v_result.Scale(self.parent.scale, self.t_eye_r.Translation)
		self.t_eye_r.Translation = v_result
		node_eye_r.Kinematics.Global.Transform = self.t_eye_r
		
		# eye aim #
		v_result.Scale(self.parent.scale, self.v_eye_aim)
		trans.Translation = v_result
		node_eye_aim.Kinematics.Global.Transform = trans
		
		# keep the eye aim the same height as the eyes #
		node_eye_aim.Kinematics.Global.PosY.AddExpression(
			'(%s.kine.global.posy + %s.kine.global.posy) / 2' % (node_eye_l.FullName, node_eye_r.FullName)
		)
		
		# add default symmetry constraint #
		xsi.zApplySymConstraint(node_eye_r, node_eye_l)
		xsi.zApplySymConstraint(node_cheek_r, node_cheek_l)
		
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
			if node.Properties('zHeadPuppetBase'):
				self.v_head_base	= node.Kinematics.Global.Transform.Translation
			elif node.Properties('zHeadPuppetTop'):
				self.v_head_top		= node.Kinematics.Global.Transform.Translation
			elif node.Properties('zHeadPuppetFace'):
				self.v_face			= node.Kinematics.Global.Transform.Translation
			elif node.Properties('zHeadPuppetLipUpper'):
				self.v_lip_upper	= node.Kinematics.Global.Transform.Translation
			elif node.Properties('zHeadPuppetMouth'):
				self.v_mouth		= node.Kinematics.Global.Transform.Translation
			elif node.Properties('zHeadPuppetLipLower'):
				self.v_lip_lower	= node.Kinematics.Global.Transform.Translation
			elif node.Properties('zHeadPuppetCheekL'):
				self.v_cheek_l		= node.Kinematics.Global.Transform.Translation
			elif node.Properties('zHeadPuppetCheekR'):
				self.v_cheek_r		= node.Kinematics.Global.Transform.Translation
			elif node.Properties('zHeadPuppetEyeAim'):
				self.v_eye_aim		= node.Kinematics.Global.Transform.Translation
			elif node.Properties('zHeadPuppetEyeL'):
				self.t_eye_l		= node.Kinematics.Global.Transform
			elif node.Properties('zHeadPuppetEyeR'):
				self.t_eye_r		= node.Kinematics.Global.Transform
		
class zHeadPuppet_Rig(object):

	_inputs_ = [
		'controls_parent',  		
		'character_set',   		
		'skeleton_parent',  		
		'param_twist_neck', 		
		'param_twist_spine',		
		'root_neck',       		
		'node_world_ref',   		
		'deformer_parent',  		
		'con_body',         		
		'size_head_con',
		'size_eye_aim_con',
		'size_jaw_con',
		'size_cheek_con',
		'group_deformers',
		'group_controls',
		'con_head',
		'keys_head',
		'keys_jaw',
		'keys_mouth',
		'keys_face',
	]
	_outputs_ = [
		'parent',
		'character_subset',
		'deformers',
		'root_head',
		'root_mouth',
		'root_eye_l',
		'root_eye_r',
		'con_face',
		'con_mouth',
		'con_jaw',
		'con_cheek_l',
		'con_cheek_r',
		'con_eye_aim',
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
		super(zHeadPuppet_Rig, self).__init__()
		
		# set the instance variables #
		self.parent					= parent

		# set the defaults for the input variables #
		for item in self._inputs_:
			setattr(self, item, None)
			
		# set specific types #
		self.deformers 	= dispatch('XSI.Collection')

		# set the default controller size #
		self.size_head_con 		= 5
		self.size_eye_aim_con	= 1
		self.size_jaw_con		= 0.5
		self.size_cheek_con		= 0.5
	
		# defaults #
		self.controls_parent	= xsi.ActiveSceneRoot  		
		self.skeleton_parent	= xsi.ActiveSceneRoot  		
		self.root_neck			= xsi.ActiveSceneRoot  		
		self.deformer_parent	= xsi.ActiveSceneRoot
		
		# default driven keys #
		self.keys_head = [
			[-1, -3],
			[1, 3]
		]
		self.keys_face = [
			[-1, -4],
			[1, 4]
		]
		self.keys_mouth = [
			[-1, -40],
			[1, 40]
		]
		self.keys_jaw = [
			[-1, 64],
			[1, -64]
		]
		

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
		# draw the head chain #

		# calculate the plane vector #
		v_plane = XSIMath.CreateVector3()
		v1		= XSIMath.CreateVector3()
		v2		= XSIMath.CreateVector3()
		# get vector from root to ankle #
		v1.Sub(self.parent.template.v_head_base, self.parent.template.v_head_top)
		# get vector from root to knee #
		v2.Sub(self.parent.template.v_head_base, self.parent.template.v_lip_lower)
		# get the cross product #
		v_plane.Cross(v2, v1)
		
		# draw the skeleton #
		self.skeleton_parent = dispatch(self.skeleton_parent)
		self.root_head = self.skeleton_parent.Add2DChain(
			self.parent.template.v_head_base,
			self.parent.template.v_head_top,
			v_plane,
			c.si2DChainNormalRadian
		)
		
		# rename #
		self.root_head.Name				= xsi.zMapName('Head', 'ChainRoot', self.parent.symmetry)
		self.root_head.Bones(0).Name	= xsi.zMapName('Head', 'ChainBone', self.parent.symmetry)
		self.root_head.Effector.Name	= xsi.zMapName('Head', 'ChainEff',  self.parent.symmetry)

		# format the chain #
		fmt = xsi.zChainFormatter(self.root_head)
		fmt.Format()
		
		# set the joint to fk #
		self.root_head.Bones(0).Properties('Kinematic Chain').Parameters('blendik').Value = 0
		
		# align the root #
		trans = self.root_head.Bones(0).Kinematics.Global.Transform
		self.root_head.Kinematics.Global.Transform 			= trans
		self.root_head.Bones(0).Kinematics.Global.Transform = trans
		
		# set the neutral pose on the bones #
		xsi.SetNeutralPose([self.root_head.Bones(0),
							self.root_head.Effector], c.siRot, False)
							
		#---------------------------------------------------------------------
		# add a con #
		if not self.con_head:
			self.con_head 							= xsi.zCon()
			self.con_head.type 						= 'hemi'
			self.con_head.size 						= self.size_head_con * self.parent.scale
			self.con_head.transform.Translation 	= self.root_head.Kinematics.Global.Transform.Translation
			self.con_head.transform.Rotation 		= XSIMath.CreateRotation(0,XSIMath.DegreesToRadians(-90),0)
			self.con_head.basename 					= 'Head'
			self.con_head.symmetry 					= self.parent.symmetry
			self.con_head.parent_node 				= self.controls_parent
			self.con_head.rotation_order 			= 'zyx'
			self.con_head.red 						= 1
			self.con_head.green 					= 1
			self.con_head.blue 						= 0
			self.con_head.Draw()
			self.con_head.AddTransformSetupRot()
			
			# add it to the controls group #
			if self.group_controls: self.group_controls.AddMember(self.con_head.node_con)
			
		self.con_head = dispatch(self.con_head)
		
		# offset the controller halfway up the head joint #
		v_half = XSIMath.CreateVector3()
		v_half.Sub(self.parent.template.v_head_top, self.parent.template.v_head_base)
		v_half.ScaleInPlace(0.35)
		self.con_head.Offset(v_half.Z, v_half.Y, v_half.X)

		# add a node for hooking up the mouth open slider #
		node_util_head = self.con_head.node_con.AddNull(xsi.zMapName('Head', 'Custom:Util', self.parent.symmetry))
		node_util_head.Properties('Visibility').Parameters('viewvis').Value = 0
		node_util_head.Properties('Visibility').Parameters('rendvis').Value = 0
		node_util_head.Kinematics.Global.Transform = self.con_head.node_con.Kinematics.Global.Transform
		node_util_head.AddChild(self.con_head.node_hook)
		
		#---------------------------------------------------------------------
		# create an animation ppg #
		prop_anim = self.con_head.node_con.Properties('zAnim')
		if not prop_anim:
			prop_anim = self.con_head.node_con.AddProperty('CustomProperty', False, 'zAnim')
		prop_anim_di = self.con_head.node_con.Properties('DisplayInfo_zAnim')
		if not prop_anim_di:
			prop_anim_di = self.con_head.node_con.AddProperty('CustomProperty', False, 'DisplayInfo_zAnim')

		#---------------------------------------------------------------------
		# setup the contraints on the head con #
		
		#  have the controller follow the neck effector's position #
		if self.root_neck:
			self.root_neck = dispatch(self.root_neck)

		# keep head controller oriented with the body con #
		if self.con_body:
			self.con_body = dispatch(self.con_body)
			cns = self.con_head.node_rest.Kinematics.AddConstraint('Pose', self.con_body.node_hook, True)
			cns = dispatch(cns)
			cns.cnspos.Value = False

		# constraint to orient the head to the world #
		if self.node_world_ref:
			cns_head_world = self.con_head.node_rest.Kinematics.AddConstraint('Pose', self.node_world_ref, True)
			cns_head_world = dispatch(cns_head_world)
			cns_head_world.cnspos.Value = False
			cns_head_world.blendweight.Value = 0
		
			# add head orientation sliders to the head con #
			orient_world = prop_anim.AddParameter3('OrientToWorld', c.siFloat, 0, 0, 1, True)
			cns_head_world.blendweight.AddExpression(orient_world)

			# hook up the blend on the orient to spine #
			orient_spine = prop_anim.AddParameter3('OrientToSpine', c.siFloat, 0, 0, 1, True)
			constraints = self.con_head.node_rest.Kinematics.Constraints
			if constraints.Count >= 2:
				constraints(0).blendweight.AddExpression('1 - %s' % orient_spine.FullName)
			else:
				# build the contraint #
				pass
		
			# add the HUD #
			prop_anim_di.AddProxyParameter(orient_spine, None, 'OrientToSpine')
			prop_anim_di.AddProxyParameter(orient_world, None, 'OrientToWorld')
		
		#---------------------------------------------------------------------
		# hook up the head bone to the head con #
		self.root_head.Bones(0).Kinematics.AddConstraint('Pose', self.con_head.node_hook, True)
		
		#---------------------------------------------------------------------
		# draw the mouth

		# draw the skeleton #
		self.root_mouth = self.root_head.Effector.Add2DChain(
			self.parent.template.v_face,
			self.parent.template.v_lip_upper,
			v_plane,
			c.si2DChainNormalRadian
		)
		
		# rename #
		self.root_mouth.Name			= xsi.zMapName('PuppetMouth', 'ChainRoot', self.parent.symmetry)
		self.root_mouth.Bones(0).Name	= xsi.zMapName('PuppetMouth', 'ChainBone', self.parent.symmetry, 1)
		self.root_mouth.Effector.Name	= xsi.zMapName('PuppetMouth', 'ChainEff',  self.parent.symmetry)

		# add upper mouth bone #
		self.root_mouth.AddBone(
			self.parent.template.v_mouth, 
			c.siChainBonePin,
			xsi.zMapName('PuppetMouth', 'ChainBone', self.parent.symmetry, 2)
		)

		self.root_mouth.AddBone(
			self.parent.template.v_lip_lower, 
			c.siChainBonePin,
			xsi.zMapName('PuppetMouth', 'ChainBone', self.parent.symmetry, 3)
		)

		# format the chain #
		fmt = xsi.zChainFormatter(self.root_mouth)
		fmt.Format()
		
		# set chain to fk only #
		self.root_mouth.Bones(0).Properties('Kinematic Chain').Parameters('blendik').Value = 0
		
		# set the neutral pose on the bones #
		xsi.SetNeutralPose([self.root_mouth.Bones(0),
							self.root_mouth.Bones(1),
							self.root_mouth.Bones(2),
							self.root_mouth.Effector], c.siSRT, False)

		#---------------------------------------------------------------------
		# add a mouth con #
		self.con_face 							= xsi.zCon()
		self.con_face.type 						= 'sphere'
		self.con_face.size 						= 1
		self.con_face.transform 				= self.root_mouth.Bones(0).Kinematics.Global.Transform
		self.con_face.basename 					= 'Face'
		self.con_face.symmetry 					= self.parent.symmetry
		self.con_face.parent_node 				= self.con_head.node_hook
		self.con_face.rotation_order 			= 'zyx'
		self.con_face.red 						= 0.7
		self.con_face.green 					= 0.7
		self.con_face.blue 						= 0
		self.con_face.Draw()
		self.con_face.AddTransformSetupRot()
		
		# add it to the controls group #
		if self.group_controls: self.group_controls.AddMember(self.con_face.node_con)
		
		# hide this controller.  don't really plan on using it for now #
		self.con_face.node_con.Properties('Visibility').Parameters('viewvis').Value = 0
		self.con_face.node_con.Properties('Visibility').Parameters('rendvis').Value = 0
		
		# add a node for hooking up the mouth open slider #
		node_util_face = self.con_face.node_rest.AddNull(xsi.zMapName('Face', 'Custom:Util', self.parent.symmetry))
		node_util_face.Properties('Visibility').Parameters('viewvis').Value = 0
		node_util_face.Properties('Visibility').Parameters('rendvis').Value = 0
		node_util_face.Kinematics.Global.Transform = self.con_face.node_con.Kinematics.Global.Transform
		node_util_face.AddChild(self.con_face.node_con)
		
		# pose constrain it to the head #
		cns = self.con_face.node_rest.Kinematics.AddConstraint('Pose', self.root_head.Bones(0), True)
		cns = dispatch(cns)
		cns.cnsori.Value = False
		
		#---------------------------------------------------------------------
		# hook up the face bone #
		self.root_mouth.Bones(0).Kinematics.AddConstraint('Pose', self.con_face.node_hook, True)
		
		#---------------------------------------------------------------------
		# add a mouth con #
		self.con_mouth 							= xsi.zCon()
		self.con_mouth.type 					= 'sphere'
		self.con_mouth.size 					= 1
		self.con_mouth.transform 				= self.root_mouth.Bones(1).Kinematics.Global.Transform
		self.con_mouth.basename 				= 'Mouth'
		self.con_mouth.symmetry 				= self.parent.symmetry
		self.con_mouth.parent_node 				= self.con_face.node_hook
		self.con_mouth.rotation_order 			= 'zyx'
		self.con_mouth.red 						= 0.7
		self.con_mouth.green 					= 0.7
		self.con_mouth.blue 					= 0
		self.con_mouth.Draw()
		self.con_mouth.AddTransformSetupRot()
		
		# add it to the controls group #
		if self.group_controls: self.group_controls.AddMember(self.con_mouth.node_con)
		
		# hide this controller.  don't really plan on using it for now #
		self.con_mouth.node_con.Properties('Visibility').Parameters('viewvis').Value = 0
		self.con_mouth.node_con.Properties('Visibility').Parameters('rendvis').Value = 0
		
		# add a node for hooking up the mouth open slider #
		node_util_mouth = self.con_mouth.node_rest.AddNull(xsi.zMapName('Mouth', 'Custom:Util', self.parent.symmetry))
		node_util_mouth.Properties('Visibility').Parameters('viewvis').Value = 0
		node_util_mouth.Properties('Visibility').Parameters('rendvis').Value = 0
		node_util_mouth.Kinematics.Global.Transform = self.con_mouth.node_con.Kinematics.Global.Transform
		node_util_mouth.AddChild(self.con_mouth.node_con)
		
		#---------------------------------------------------------------------
		# hook up the mouth bone #
		self.root_mouth.Bones(1).Kinematics.AddConstraint('Pose', self.con_mouth.node_hook, True)
		
		#---------------------------------------------------------------------
		# add a jaw con #
		self.con_jaw 							= xsi.zCon()
		self.con_jaw.type 						= 'sphere'
		self.con_jaw.size 						= self.size_jaw_con * self.parent.scale
		self.con_jaw.transform 					= self.root_mouth.Bones(2).Kinematics.Global.Transform
		self.con_jaw.basename 					= 'Jaw'
		self.con_jaw.symmetry 					= self.parent.symmetry
		self.con_jaw.parent_node 				= self.con_mouth.node_hook
		self.con_jaw.rotation_order 			= 'zyx'
		self.con_jaw.red 						= 0.7
		self.con_jaw.green 						= 0.7
		self.con_jaw.blue 						= 0
		self.con_jaw.Draw()
		self.con_jaw.AddTransformSetupRot()
		
		# offset to the lip_lower #
		self.con_jaw.Offset(self.root_mouth.Bones(2).Length.Value, 0, 0)
		
		# add it to the controls group #
		if self.group_controls: self.group_controls.AddMember(self.con_jaw.node_con)
		
		# add a node for hooking up the mouth open slider #
		node_util_jaw = self.con_jaw.node_rest.AddNull(xsi.zMapName('Jaw', 'Custom:Util', self.parent.symmetry))
		node_util_jaw.Properties('Visibility').Parameters('viewvis').Value = 0
		node_util_jaw.Properties('Visibility').Parameters('rendvis').Value = 0
		node_util_jaw.Kinematics.Global.Transform = self.con_jaw.node_con.Kinematics.Global.Transform
		node_util_jaw.AddChild(self.con_jaw.node_con)
		
		#---------------------------------------------------------------------
		# hook up the jaw bone #
		self.root_mouth.Bones(2).Kinematics.AddConstraint('Pose', self.con_jaw.node_hook, True)

		#---------------------------------------------------------------------
		# create a node to hold a weight multiplier for the puppet mouth slider effect on the head #
		prop_anim_head_util = node_util_head.AddProperty('CustomProperty', False, 'zAnim')
		param_mouth_weight = prop_anim_head_util.AddParameter3('Mouth_Head_Weight', c.siFloat, 1, 0, 1)
		param_mouth_driven = prop_anim_head_util.AddParameter3('DrivenKey', c.siFloat, 0, -1000000, 1000000)
		
		# proxy it to the head con ppg #
		prop_anim.AddProxyParameter(param_mouth_weight, None, 'Mouth_Head_Weight')
		# prop_anim_di.AddProxyParameter(param_mouth_weight, None, 'Mouth_Head_Weight')

		#---------------------------------------------------------------------
		# create an animation ppg #
		prop_anim_mouth 	= self.con_jaw.node_con.AddProperty('CustomProperty', False, 'zAnim')
		prop_anim_mouth_di 	= self.con_jaw.node_con.AddProperty('CustomProperty', False, 'DisplayInfo_zAnim')

		# get the current frame rate #
		rate = xsi.GetValue('PlayControl.Rate')
		
		# add a slider to open/close the mouth #
		slider_mouth = prop_anim_mouth.AddParameter3('Mouth', c.siFloat, 0, -1, 1)
		prop_anim_mouth_di.AddProxyParameter(slider_mouth, '', 'Mouth')
		# add the proxy parameter to the head con #
		prop_anim.AddProxyParameter(slider_mouth, '', 'Mouth')
		prop_anim_di.AddProxyParameter(slider_mouth, '', 'Mouth')
		
		# link the z rotations #
		node_util_head.Kinematics.Local.RotZ.AddExpression( # link the node to the driven key * weight #
			'%s * %s' % (param_mouth_driven.FullName, param_mouth_weight.FullName)
		) 
		expr = param_mouth_driven.AddExpression('l_fcv(%s)' % slider_mouth.FullName)
		expr = dispatch(expr)
		fcurve = expr.Parameters('l_fcv').Source
		# set the interpolation and extrapolation #
		fcurve.Interpolation = c.siLinearInterpolation
		fcurve.Extrapolation = c.siLinearExtrapolation
		# add a default key #
		fcurve.AddKey(0, 0)
		# add the outer limits keys #
		for keys in self.keys_head:
			fcurve.AddKey(keys[0], keys[1])
		
		expr = node_util_face.Kinematics.Local.RotZ.AddExpression('l_fcv(%s)' % slider_mouth.FullName)
		expr = dispatch(expr)
		fcurve = expr.Parameters('l_fcv').Source
		# set the interpolation and extrapolation #
		fcurve.Interpolation = c.siLinearInterpolation
		fcurve.Extrapolation = c.siLinearExtrapolation
		# add a default key #
		fcurve.AddKey(0, 0)
		# add the outer limits keys #
		for keys in self.keys_face:
			fcurve.AddKey(keys[0], keys[1])

		expr = node_util_mouth.Kinematics.Local.RotZ.AddExpression('l_fcv(%s)' % slider_mouth.FullName)
		expr = dispatch(expr)
		fcurve = expr.Parameters('l_fcv').Source
		# set the interpolation and extrapolation #
		fcurve.Interpolation = c.siLinearInterpolation
		fcurve.Extrapolation = c.siLinearExtrapolation
		# add a default key #
		fcurve.AddKey(0, 0)
		# add the outer limits keys #
		for keys in self.keys_mouth:
			fcurve.AddKey(keys[0], keys[1])

		expr = node_util_jaw.Kinematics.Local.RotZ.AddExpression('l_fcv(%s)' % slider_mouth.FullName)
		expr = dispatch(expr)
		fcurve = expr.Parameters('l_fcv').Source
		# set the interpolation and extrapolation #
		fcurve.Interpolation = c.siLinearInterpolation
		fcurve.Extrapolation = c.siLinearExtrapolation
		# add a default key #
		fcurve.AddKey(0, 0)
		# add the outer limits keys #
		for keys in self.keys_jaw:
			fcurve.AddKey(keys[0], keys[1])

		#---------------------------------------------------------------------
		# cheek cons 
		node_cheek_cons	= self.con_jaw.node_hook.AddNull(xsi.zMapName('Cheeks', 'Branch', 'None'))
		trans = self.con_jaw.node_con.Kinematics.Global.Transform
		trans.Rotation = self.con_head.node_con.Kinematics.Global.Transform.Rotation
		node_cheek_cons.Kinematics.Global.Transform = trans
		node_cheek_cons.Properties('Visibility').Parameters('viewvis').Value = 0
		node_cheek_cons.Properties('Visibility').Parameters('rendvis').Value = 0
		
		self.con_cheek_l 							= xsi.zCon()
		self.con_cheek_l.type 						= 'round_box'
		self.con_cheek_l.size 						= self.size_cheek_con * self.parent.scale
		self.con_cheek_l.transform					= self.con_head.node_con.Kinematics.Global.Transform
		self.con_cheek_l.transform.Translation		= self.parent.template.v_cheek_l
		self.con_cheek_l.basename 					= 'Cheek'
		self.con_cheek_l.symmetry 					= 'left'
		self.con_cheek_l.parent_node 				= node_cheek_cons
		self.con_cheek_l.rotation_order 			= 'zyx'
		self.con_cheek_l.red 						= 0
		self.con_cheek_l.green 						= 0.7
		self.con_cheek_l.blue 						= 0
		self.con_cheek_l.Draw()
		self.con_cheek_l.AddTransformSetupPos()
		
		# add it to the controls group #
		if self.group_controls: self.group_controls.AddMember(self.con_cheek_l.node_con)

		# add an expression half of the jaw rotation #
		expr = self.con_cheek_l.node_rest.Kinematics.Local.RotZ.AddExpression('%s.kine.local.rotz * -0.5' % self.root_mouth.Bones(2).FullName)
		
		self.con_cheek_r 							= xsi.zCon()
		self.con_cheek_r.type 						= 'round_box'
		self.con_cheek_r.size 						= self.size_cheek_con * self.parent.scale
		self.con_cheek_r.transform					= self.con_head.node_con.Kinematics.Global.Transform
		self.con_cheek_r.transform.Translation		= self.parent.template.v_cheek_r
		self.con_cheek_r.basename 					= 'Cheek'
		self.con_cheek_r.symmetry 					= 'right'
		self.con_cheek_r.parent_node 				= node_cheek_cons
		self.con_cheek_r.rotation_order 			= 'zyx'
		self.con_cheek_r.red 						= 0.7
		self.con_cheek_r.green 						= 0
		self.con_cheek_r.blue 						= 0
		self.con_cheek_r.Draw()
		self.con_cheek_r.AddTransformSetupPos()
		
		# add it to the controls group #
		if self.group_controls: self.group_controls.AddMember(self.con_cheek_r.node_con)

		# add an expression half of the jaw rotation #
		expr = self.con_cheek_r.node_rest.Kinematics.Local.RotZ.AddExpression('%s.kine.local.rotz * -0.5' % self.root_mouth.Bones(2).FullName)
		
		#---------------------------------------------------------------------
		# draw the EYES
		
		trans = XSIMath.CreateTransform()

		# calculate the eye effector position #
		trans.Copy(self.parent.template.t_eye_l)
		trans.AddLocalTranslation(XSIMath.CreateVector3(self.parent.scale, 0, 0))
		v_eye_eff_l = trans.Translation

		trans.Copy(self.parent.template.t_eye_r)
		trans.AddLocalTranslation(XSIMath.CreateVector3(self.parent.scale, 0, 0))
		v_eye_eff_r = trans.Translation
		
		# get the eye root #
		v_eye_root_l = self.parent.template.t_eye_l.Translation
		v_eye_root_r = self.parent.template.t_eye_r.Translation
		
		
		# draw the skeletons #
		self.root_eye_l = self.root_mouth.Bones(0).Add2DChain(
			v_eye_root_l,
			v_eye_eff_l,
			XSIMath.CreateVector3(0, 0, 1),
			c.si2DChainNormalRadian
		)
		
		self.root_eye_r = self.root_mouth.Bones(0).Add2DChain(
			v_eye_root_r,
			v_eye_eff_r,
			XSIMath.CreateVector3(0, 0, 1),
			c.si2DChainNormalRadian
		)
		
		# rename #
		self.root_eye_l.Name			= xsi.zMapName('Eye', 'ChainRoot', 'Left')
		self.root_eye_l.Bones(0).Name	= xsi.zMapName('Eye', 'ChainBone', 'Left')
		self.root_eye_l.Effector.Name	= xsi.zMapName('Eye', 'ChainEff',  'Left')

		self.root_eye_r.Name			= xsi.zMapName('Eye', 'ChainRoot', 'Right')
		self.root_eye_r.Bones(0).Name	= xsi.zMapName('Eye', 'ChainBone', 'Right')
		self.root_eye_r.Effector.Name	= xsi.zMapName('Eye', 'ChainEff',  'Right')

		# format the chain #
		xsi.zChainFormatter(self.root_eye_l).Format()
		xsi.zChainFormatter(self.root_eye_r).Format()
		
		#---------------------------------------------------------------------
		# create a eye aim con #
		self.con_eye_aim 							= xsi.zCon()
		self.con_eye_aim.type 						= 'round_box'
		self.con_eye_aim.size 						= self.size_eye_aim_con * self.parent.scale
		self.con_eye_aim.transform.Translation		= self.parent.template.v_eye_aim
		self.con_eye_aim.basename 					= 'EyeAim'
		self.con_eye_aim.symmetry 					= 'Mid'
		self.con_eye_aim.parent_node 				= self.con_head.node_hook
		self.con_eye_aim.rotation_order 			= 'zyx'
		self.con_eye_aim.red 						= 1
		self.con_eye_aim.green 						= 1
		self.con_eye_aim.blue 						= 0
		self.con_eye_aim.Draw()
		self.con_eye_aim.AddTransformSetupRot()
		
		# add it to the controls group #
		if self.group_controls: self.group_controls.AddMember(self.con_eye_aim.node_con)

		# get the eye projected to the con #
		v_eye_root_aim_l = XSIMath.CreateVector3()
		v_eye_root_aim_l.Sub(self.parent.template.v_eye_aim, v_eye_root_l)
		v_eye_aim_l = XSIMath.CreateVector3(0, 0, v_eye_root_aim_l.Z)  # use the z component only #
		v_eye_aim_l.AddInPlace(v_eye_root_l)
		
		v_eye_root_aim_r = XSIMath.CreateVector3()
		v_eye_root_aim_r.Sub(self.parent.template.v_eye_aim, v_eye_root_r)
		v_eye_aim_r = XSIMath.CreateVector3(0, 0, v_eye_root_aim_r.Z)  # use the z component only #
		v_eye_aim_r.AddInPlace(v_eye_root_r)

		# create a node to aim at (could be used for convergence and divergence)#
		node_eye_aim_l = self.con_eye_aim.node_hook.AddNull(
			xsi.zMapName('Eye', 'Custom:Aim', 'Left')
		)
		node_eye_aim_l.primary_icon.Value = 0
		node_eye_aim_l.Properties('Visibility').Parameters('viewvis').Value = False
		node_eye_aim_l.Properties('Visibility').Parameters('rendvis').Value = False
		trans = node_eye_aim_l.Kinematics.Global.Transform
		trans.Translation = v_eye_aim_l
		node_eye_aim_l.Kinematics.Global.Transform = trans
		
		node_eye_aim_r = self.con_eye_aim.node_hook.AddNull(
			xsi.zMapName('Eye', 'Custom:Aim', 'Right')
		)
		node_eye_aim_r.primary_icon.Value = 0
		node_eye_aim_r.Properties('Visibility').Parameters('viewvis').Value = False
		node_eye_aim_r.Properties('Visibility').Parameters('rendvis').Value = False
		trans = node_eye_aim_r.Kinematics.Global.Transform
		trans.Translation = v_eye_aim_r
		node_eye_aim_r.Kinematics.Global.Transform = trans

		# add up vectors to the eyes #
		node_eye_upv_l = node_eye_aim_l.AddNull(xsi.zMapName('Eye', 'UpVector', 'Left'))
		node_eye_upv_l.primary_icon.Value = 0
		node_eye_upv_l.Properties('Visibility').Parameters('viewvis').Value = False
		node_eye_upv_l.Properties('Visibility').Parameters('rendvis').Value = False
		trans = node_eye_aim_l.Kinematics.Global.Transform
		trans.AddLocalTranslation(XSIMath.CreateVector3(0, self.parent.scale, 0))
		node_eye_upv_l.Kinematics.Global.Transform = trans
		
		node_eye_upv_r = node_eye_aim_r.AddNull(xsi.zMapName('Eye', 'UpVector', 'Right'))
		node_eye_upv_r.primary_icon.Value = 0
		node_eye_upv_r.Properties('Visibility').Parameters('viewvis').Value = False
		node_eye_upv_r.Properties('Visibility').Parameters('rendvis').Value = False
		trans = node_eye_aim_r.Kinematics.Global.Transform
		trans.AddLocalTranslation(XSIMath.CreateVector3(0, self.parent.scale, 0))
		node_eye_upv_r.Kinematics.Global.Transform = trans

		# aim the eyes at the con #
		cns_eye_l = self.root_eye_l.Bones(0).Kinematics.AddConstraint('Direction', node_eye_aim_l, False)
		cns_eye_l = dispatch(cns_eye_l)
		cns_eye_l.upvct_active.Value = True
		cns_eye_l.UpVectorReference = node_eye_upv_l

		cns_eye_r = self.root_eye_r.Bones(0).Kinematics.AddConstraint('Direction', node_eye_aim_r, False)
		cns_eye_r = dispatch(cns_eye_r)
		cns_eye_r.upvct_active.Value = True
		cns_eye_r.UpVectorReference = node_eye_upv_r
		
		#---------------------------------------------------------------------
		# create a individual eye aim controls #
		con_eye_aim_l 							= xsi.zCon()
		con_eye_aim_l.type 						= 'circle'
		con_eye_aim_l.size 						= self.size_eye_aim_con * self.parent.scale * 0.5
		con_eye_aim_l.transform					= node_eye_aim_l.Kinematics.Global.Transform
		con_eye_aim_l.basename 					= 'EyeAim'
		con_eye_aim_l.symmetry 					= 'left'
		con_eye_aim_l.parent_node 				= self.con_eye_aim.node_hook
		con_eye_aim_l.rotation_order 			= 'zyx'
		con_eye_aim_l.red 						= 0
		con_eye_aim_l.green 					= 1
		con_eye_aim_l.blue 						= 0
		con_eye_aim_l.Draw()
		con_eye_aim_l.Rotate(90, 0, 0)
		con_eye_aim_l.AddTransformSetupPos()
		
		con_eye_aim_r 							= xsi.zCon()
		con_eye_aim_r.type 						= 'circle'
		con_eye_aim_r.size 						= self.size_eye_aim_con * self.parent.scale * 0.5
		con_eye_aim_r.transform					= node_eye_aim_r.Kinematics.Global.Transform
		con_eye_aim_r.basename 					= 'EyeAim'
		con_eye_aim_r.symmetry 					= 'right'
		con_eye_aim_r.parent_node 				= self.con_eye_aim.node_hook
		con_eye_aim_r.rotation_order 			= 'zyx'
		con_eye_aim_r.red 						= 1
		con_eye_aim_r.green 					= 0
		con_eye_aim_r.blue 						= 0
		con_eye_aim_r.Draw()
		con_eye_aim_r.Rotate(90, 0, 0)
		con_eye_aim_r.AddTransformSetupPos()
		
		# constrain the aim nodes to the hookd #
		node_eye_aim_l.Kinematics.AddConstraint('Pose', con_eye_aim_l.node_hook, True)
		node_eye_aim_r.Kinematics.AddConstraint('Pose', con_eye_aim_r.node_hook, True)
		
		#---------------------------------------------------------------------
		# add the constraint from the eyes to the world (all_null) #
		prop_anim_eye = None
		if self.node_world_ref:

			# set a default constraint #
			self.con_eye_aim.node_rest.Kinematics.AddConstraint('Pose', self.con_eye_aim.node_rest.Parent, True)

			# set a constraint to the world #
			cns = self.con_eye_aim.node_rest.Kinematics.AddConstraint('Pose', self.node_world_ref, True)
			cns	= dispatch(cns)
		
			# create the ppg #
			prop_anim_eye 		= self.con_eye_aim.node_con.AddProperty('CustomProperty', False, 'zAnim')
			param_to_world 		= prop_anim_eye.AddParameter3('RelativeToWorld', c.siFloat, 0, 0, 1)
			prop_anim_eye_di 	= self.con_eye_aim.node_con.AddProperty('CustomProperty', False, 'DisplayInfo_zAnim')
			prop_anim_eye_di.AddProxyParameter(param_to_world, None, 'RelativeToWorld')
		
			# hook up the sliders #
			cns.blendweight.AddExpression(param_to_world.FullName)
		
		#---------------------------------------------------------------------
		# create a visibility slider on the eye con #
		param_show_eye_cons = prop_anim_eye.AddParameter3('ShowIndividualCons', c.siBool, False)
		prop_anim_eye_di.AddProxyParameter(param_show_eye_cons, None, 'ShowIndividualCons')
		
		con_eye_aim_l.node_con.Properties('Visibility').Parameters('viewvis').AddExpression(
			param_show_eye_cons
		)
		con_eye_aim_r.node_con.Properties('Visibility').Parameters('viewvis').AddExpression(
			param_show_eye_cons
		)

		#---------------------------------------------------------------------
		# create a deformer stack #

		# head #
		node_dfm_parent = self.deformer_parent.AddNull(xsi.zMapName('Head', 'Custom:DfmPrnt', 'Mid'))
		node_dfm_shadow = node_dfm_parent.AddNull(xsi.zMapName('Head', 'Custom:DfmShdw', 'Mid'))
		node_env 		= node_dfm_shadow.AddNull(xsi.zMapName('Head', 'Env', 'Mid'))
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
		
		node_dfm_parent.Kinematics.AddConstraint('Pose', self.root_head.Bones(0).Parent, False)
		node_dfm_shadow.Kinematics.AddConstraint('Pose', self.root_head.Bones(0), False)

		# eye left #
		node_dfm_parent = self.deformer_parent.AddNull(xsi.zMapName('Eye', 'Custom:DfmPrnt', 'Left'))
		node_dfm_shadow = node_dfm_parent.AddNull(xsi.zMapName('Eye', 'Custom:DfmShdw', 'Left'))
		node_env 		= node_dfm_shadow.AddNull(xsi.zMapName('Eye', 'Env', 'Left'))
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
		
		node_dfm_parent.Kinematics.AddConstraint('Pose', self.root_eye_l.Bones(0).Parent, False)
		node_dfm_shadow.Kinematics.AddConstraint('Pose', self.root_eye_l.Bones(0), False)
		
		# eye right #
		node_dfm_parent = self.deformer_parent.AddNull(xsi.zMapName('Eye', 'Custom:DfmPrnt', 'Right'))
		node_dfm_shadow = node_dfm_parent.AddNull(xsi.zMapName('Eye', 'Custom:DfmShdw', 'Right'))
		node_env 		= node_dfm_shadow.AddNull(xsi.zMapName('Eye', 'Env', 'Right'))
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
		
		node_dfm_parent.Kinematics.AddConstraint('Pose', self.root_eye_r.Bones(0).Parent, False)
		node_dfm_shadow.Kinematics.AddConstraint('Pose', self.root_eye_r.Bones(0), False)
		
		
		# mouth #
		for b in xrange(self.root_mouth.Bones.Count):
			node_dfm_parent = self.deformer_parent.AddNull(xsi.zMapName('PuppetMouth%s' % (b+1), 'Custom:DfmPrnt', self.parent.symmetry))
			node_dfm_shadow = node_dfm_parent.AddNull(xsi.zMapName('PuppetMouth%s' % (b+1), 'Custom:DfmShdw', self.parent.symmetry))
			node_env 		= node_dfm_shadow.AddNull(xsi.zMapName('PuppetMouth%s' % (b+1), 'Env', self.parent.symmetry))
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
		
			node_dfm_parent.Kinematics.AddConstraint('Pose', self.root_mouth.Bones(b).Parent, False)
			node_dfm_shadow.Kinematics.AddConstraint('Pose', self.root_mouth.Bones(b), False)
		
		# cheeck left #
		node_dfm_parent = self.deformer_parent.AddNull(xsi.zMapName('Cheek', 'Custom:DfmPrnt', 'left'))
		node_dfm_shadow = node_dfm_parent.AddNull(xsi.zMapName('Cheek', 'Custom:DfmShdw', 'left'))
		node_env 		= node_dfm_shadow.AddNull(xsi.zMapName('Cheek', 'Env', 'left'))
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
		
		node_dfm_parent.Kinematics.AddConstraint('Pose', self.con_cheek_l.node_con.Parent, False)
		node_dfm_shadow.Kinematics.AddConstraint('Pose', self.con_cheek_l.node_con, False)

		# cheeck right #
		node_dfm_parent = self.deformer_parent.AddNull(xsi.zMapName('Cheek', 'Custom:DfmPrnt', 'Right'))
		node_dfm_shadow = node_dfm_parent.AddNull(xsi.zMapName('Cheek', 'Custom:DfmShdw', 'Right'))
		node_env 		= node_dfm_shadow.AddNull(xsi.zMapName('Cheek', 'Env', 'Right'))
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
		
		node_dfm_parent.Kinematics.AddConstraint('Pose', self.con_cheek_r.node_con.Parent, False)
		node_dfm_shadow.Kinematics.AddConstraint('Pose', self.con_cheek_r.node_con, False)
		
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
	
			# add the leg subset #
			self.character_subset = upper_set.AddSubset(
				xsi.zMapName('Head', 'None', 'Middle')
			)
			
			# add the parameters #
			self.character_subset.AddNodePosRot(self.con_head.node_con)
			self.character_subset.AddNodeRot(self.con_face.node_con)
			self.character_subset.AddNodeRot(self.con_mouth.node_con)
			self.character_subset.AddNodeRot(self.con_jaw.node_con)
			self.character_subset.AddNodePosRot(self.con_cheek_l.node_con)
			self.character_subset.AddNodePosRot(self.con_cheek_r.node_con)
			self.character_subset.AddParams(slider_mouth)
			self.character_subset.AddParams(orient_spine)
			self.character_subset.AddParams(orient_world)
			self.character_subset.AddParams(param_mouth_weight)
			self.character_subset.AddNodePosRot(self.con_eye_aim.node_con)
			self.character_subset.AddNodePosRot(con_eye_aim_l.node_con)
			self.character_subset.AddNodePosRot(con_eye_aim_r.node_con)
			self.character_subset.AddParams(param_show_eye_cons)
			self.character_subset.AddParams(param_to_world)
		
#-----------------------------------------------------------------------------
# Commands
#-----------------------------------------------------------------------------
def zHeadPuppet_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	#oCmd.SetFlag(constants.siNoLogging,false)

	#oArgs = oCmd.Arguments
	#oArgs.Add('arg', c.siArgumentInput, '', c.siString)
	#oArgs.AddObjectArgument('model')

	return True
	
def zHeadPuppet_Execute():
	# export the python object #
	import win32com.server
	return win32com.server.util.wrap(
		zHeadPuppet()
	)
	
