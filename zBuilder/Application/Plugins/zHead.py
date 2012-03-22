"""
zHead.py

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
	in_reg.Name = "zHead"
	in_reg.Email = "andy@zoogloo.net"
	in_reg.URL = ""
	in_reg.Major = 1
	in_reg.Minor = 1

	in_reg.RegisterCommand('zHead', 'zHead')
	
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

class zHead(object):

	# required for COM wrapper #
	_public_methods_ = [
	]
	# define the output vars here #
	_public_attrs_ = [
		'rig',
		'template',
		'scale',
		'basename',
	]
	# define those attrs that are read only #
	_readonly_attrs_ = [
		'rig',
		'template',
	]

	# set the class variables #
	_template 		= None
	_rig 			= None
	uid				= '037f628285c295e12e5c0e683fc947ad'
	basename		= 'Head'
	scale			= 1
	
	def __init__(self):
		super(zHead, self).__init__()
		
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
				self._template = dispatch(win32com.server.util.wrap(zHead_Template(self)))
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
				self._rig = dispatch(win32com.server.util.wrap(zHead_Rig(self)))
			# return the private var #
			return self._rig
		def fset(self, value):
			raise Exception('Unable to modify rig value.')
		fdel = fset
		return locals()
			
				
class zHead_Template(object):
	"""docstring for zHead_Template"""
	
	_inputs_ = [
		'v_head_base',
		'v_head_top', 
		'v_jaw',   
		'v_chin',	   
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
		super(zHead_Template, self).__init__()
		
		# set the instance variables #
		self.parent			= parent
		self.scale 			= 1
		self.model 			= None
		
		# self.v_head_base	= XSIMath.CreateVector3()
		# self.v_head_top		= XSIMath.CreateVector3()
		# self.v_jaw			= XSIMath.CreateVector3()
		# self.v_chin			= XSIMath.CreateVector3()
		# self.v_eye_l		= XSIMath.CreateVector3()
		# self.v_eye_r		= XSIMath.CreateVector3()
		# self.v_eye_aim		= XSIMath.CreateVector3()
		
		self.LoadDefaultValues()
	
	def LoadDefaultValues(self):
		"""
		Sets the default values 
		"""
		self.v_head_base			= XSIMath.CreateVector3(0.000, 23.250, 0.534)
		self.v_head_top				= XSIMath.CreateVector3(0.000, 29.840, 0.534)
		self.v_jaw					= XSIMath.CreateVector3(0.000, 23.184, 2.166)   
		self.v_chin					= XSIMath.CreateVector3(0.000, 20.772, 3.993)
		self.v_eye_aim				= XSIMath.CreateVector3(0.000, 26.922, 30.000)

		self.t_eye_l				= XSIMath.CreateTransform()
		self.t_eye_l.Translation 	= XSIMath.CreateVector3(-1.452, 26.877, 4.350)
		self.t_eye_l.Rotation 		= XSIMath.CreateRotation(0, XSIMath.DegreesToRadians(-90), 0)

		self.t_eye_r				= XSIMath.CreateTransform()
		self.t_eye_r.Translation 	= XSIMath.CreateVector3(1.452, 26.877, 4.350)
		self.t_eye_r.Rotation 		= XSIMath.CreateRotation(0, XSIMath.DegreesToRadians(-90), 0)


	def Draw(self):
		"""docstring for Draw"""
		# get the model #
		if not self.model:
			raise Exception('Model attribute for template not specified.')
		
		# dispatch the model #
		self.model = dispatch(self.model)
		
		#---------------------------------------------------------------------
		# create a node to hold the template #
		node_parent = self.model.AddNull('Head_Container')
		node_parent.primary_icon.Value = 0
		node_parent.Properties('Visibility').Parameters('viewvis').Value = False
		node_parent.Properties('Visibility').Parameters('rendvis').Value = False
		node_parent.AddProperty('CustomProperty', False, 'zBuilderTemplateItem')
		prop = node_parent.AddProperty('CustomProperty', False, 'zContainer')
		prop = dispatch(prop)
		prop.AddParameter3('ContainerName', c.siString, 'Head')
		prop.AddParameter3('ContainerUID', c.siString, self.parent.uid)
			
		#---------------------------------------------------------------------
		# draw the nodes #
		node_head_base 	= node_parent.AddNull(xsi.zMapName('HeadBase', 'Custom:Tmp', 'Mid'))
		node_head_base.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_head_base.AddProperty('CustomProperty', False, 'zHeadBase')

		node_head_top 	= node_parent.AddNull(xsi.zMapName('HeadTop', 'Custom:Tmp', 'Mid'))
		node_head_top.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_head_top.AddProperty('CustomProperty', False, 'zHeadTop')
		
		node_jaw 		= node_parent.AddNull(xsi.zMapName('Jaw', 'Custom:Tmp', 'Mid'))
		node_jaw.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_jaw.AddProperty('CustomProperty', False, 'zJaw')

		node_chin 		= node_parent.AddNull(xsi.zMapName('Chin', 'Custom:Tmp', 'Mid'))
		node_chin.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_chin.AddProperty('CustomProperty', False, 'zChin')
		
		node_eye_l 		= node_parent.AddNull(xsi.zMapName('Eye', 'Custom:Tmp', 'Left'))
		node_eye_l.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_eye_l.AddProperty('CustomProperty', False, 'zEyeL')
		
		node_eye_r 		= node_parent.AddNull(xsi.zMapName('Eye', 'Custom:Tmp', 'Right'))
		node_eye_r.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_eye_r.AddProperty('CustomProperty', False, 'zEyeR')
		
		node_eye_aim	= node_parent.AddNull(xsi.zMapName('EyeAim', 'Custom:Tmp', 'Mid'))
		node_eye_aim.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_eye_aim.AddProperty('CustomProperty', False, 'zEyeAim')
		

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
		
		# jaw #
		v_result.Scale(self.parent.scale, self.v_jaw)
		trans.Translation = v_result
		node_jaw.Kinematics.Global.Transform = trans

		# chin #
		v_result.Scale(self.parent.scale, self.v_chin)
		trans.Translation = v_result
		node_chin.Kinematics.Global.Transform = trans

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
		set_zHeadBase	= False
		set_zHeadTop	= False
		set_zJaw		= False
		set_zChin		= False
		set_zEyeAim		= False
		set_zEyeL		= False
		set_zEyeR		= False
		for node in child_nodes:
			if node.Properties('zHeadBase'):
				self.v_head_base	= node.Kinematics.Global.Transform.Translation
				set_zHeadBase 		= True
			elif node.Properties('zHeadTop'):
				self.v_head_top		= node.Kinematics.Global.Transform.Translation
				set_zHeadTop 		= True
			elif node.Properties('zJaw'):
				self.v_jaw			= node.Kinematics.Global.Transform.Translation
				set_zJaw 			= True
			elif node.Properties('zChin'):
				self.v_chin			= node.Kinematics.Global.Transform.Translation
				set_zChin 			= True
			elif node.Properties('zEyeAim'):
				self.v_eye_aim		= node.Kinematics.Global.Transform.Translation
				set_zEyeAim 		= True
			elif node.Properties('zEyeL'):
				self.t_eye_l		= node.Kinematics.Global.Transform
				set_zEyeL 			= True
			elif node.Properties('zEyeR'):
				self.t_eye_r		= node.Kinematics.Global.Transform
				set_zEyeR	 		= True
		if not set_zHeadBase or not set_zHeadTop or not set_zJaw or not set_zChin \
		or not set_zEyeAim or not set_zEyeL or not set_zEyeR:
			raise Exception(
				'Was unable to set all template parameters from the scene.'
			)
		
class zHead_Rig(object):

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
		'group_deformers',
		'group_controls',
		'con_head',
		'build_jaw',
		'build_eyes',
	]
	_outputs_ = [
		'parent',
		'character_subset',
		'deformers',
		'root_head',
		'root_jaw',
		'root_eye_l',
		'root_eye_r',
		'con_jaw',
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
		super(zHead_Rig, self).__init__()
		
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
		
		self.build_jaw			= True
		self.build_eyes			= True
	
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
		
		#---------------------------------------------------------------------
		# draw the head chain #

		# calculate the plane vector #
		v_plane = XSIMath.CreateVector3()
		v1		= XSIMath.CreateVector3()
		v2		= XSIMath.CreateVector3()
		# get vector from root to ankle #
		v1.Sub(template.v_head_base, template.v_head_top)
		# get vector from root to knee #
		v2.Sub(template.v_head_base, template.v_jaw)
		# get the cross product #
		v_plane.Cross(v2, v1)
		
		# draw the skeleton #
		self.skeleton_parent = dispatch(self.skeleton_parent)
		self.root_head = self.skeleton_parent.Add2DChain(
			template.v_head_base,
			template.v_head_top,
			v_plane,
			c.si2DChainNormalRadian
		)
		
		# rename #
		self.root_head.Name				= xsi.zMapName('Head', 'ChainRoot', 'Mid')
		self.root_head.Bones(0).Name	= xsi.zMapName('Head', 'ChainBone', 'Mid')
		self.root_head.Effector.Name	= xsi.zMapName('Head', 'ChainEff', 'Mid')

		# format the chain #
		fmt = xsi.zChainFormatter(self.root_head)
		fmt.Format()
		
		#---------------------------------------------------------------------
		# add a con #
		if not self.con_head:
			self.con_head 							= xsi.zCon()
			self.con_head.type 						= 'sphere'
			self.con_head.size 						= self.size_head_con * self.parent.scale
			self.con_head.transform.Translation 	= self.root_head.Kinematics.Global.Transform.Translation
			self.con_head.transform.Rotation 		= XSIMath.CreateRotation(0,XSIMath.DegreesToRadians(-90),0)
			self.con_head.basename 					= 'Head'
			self.con_head.symmetry 					= 'Mid'
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
		v_half.Sub(template.v_head_top, template.v_head_base)
		# v_half.ScaleInPlace(0.5)
		v_half.ScaleInPlace(0.35)
		self.con_head.Offset(v_half.Z, v_half.Y, v_half.X)

		#---------------------------------------------------------------------
		# setup the contraints on the head con #
		
		# # have the controller follow the neck effector's position #
		self.root_neck = dispatch(self.root_neck)

		# keep head controller oriented with the body con #
		self.con_body = dispatch(self.con_body)
		cns = self.con_head.node_rest.Kinematics.AddConstraint('Pose', self.con_body.node_hook, True)
		cns = dispatch(cns)
		cns.cnspos.Value = False

		# constraint to orient the head to the world #
		cns_head_world = self.con_head.node_rest.Kinematics.AddConstraint('Pose', self.node_world_ref, True)
		cns_head_world = dispatch(cns_head_world)
		cns_head_world.cnspos.Value = False
		cns_head_world.blendweight.Value = 0
		
		# add head orientation sliders to the head con #
		prop_anim = self.con_head.node_con.Properties('zAnim')
		if not prop_anim:
			prop_anim = self.con_head.node_con.AddProperty('CustomProperty', False, 'zAnim')
		orient_world = prop_anim.AddParameter3('OrientToWorld', c.siFloat, 0, 0, 1, True)
		cns_head_world.blendweight.AddExpression(orient_world)

		# hook up the blend on the orient to spine #
		orient_spine = prop_anim.AddParameter3('OrientToSpine', c.siFloat, 0, 0, 1, True)
		constraints = self.con_head.node_rest.Kinematics.Constraints
		if constraints.Count >= 2:
			log(constraints(0).Constraining(0))
			constraints(0).blendweight.AddExpression('1 - %s' % orient_spine.FullName)
		else:
			# build the contraint #
			pass
		
		# add the HUD #
		prop_anim_di = self.con_head.node_con.Properties('DisplayInfo_zAnim')
		if not prop_anim_di:
			prop_anim_di = self.con_head.node_con.AddProperty('CustomProperty', False, 'DisplayInfo_zAnim')
		prop_anim_di.AddProxyParameter(orient_spine, None, 'OrientToSpine')
		prop_anim_di.AddProxyParameter(orient_world, None, 'OrientToWorld')
	
		#---------------------------------------------------------------------
		# hook up the head bone to the head con #
		self.root_head.Bones(0).Kinematics.AddConstraint('Pose', self.con_head.node_hook, True)
		
		#---------------------------------------------------------------------
		# draw the JAW
		if self.build_jaw:
			
			# draw the skeleton #
			self.root_jaw = self.root_head.Effector.Add2DChain(
				template.v_jaw,
				template.v_chin,
				v_plane,
				c.si2DChainNormalRadian
			)
		
			# rename #
			self.root_jaw.Name			= xsi.zMapName('Jaw', 'ChainRoot', 'Mid')
			self.root_jaw.Bones(0).Name	= xsi.zMapName('Jaw', 'ChainBone', 'Mid')
			self.root_jaw.Effector.Name	= xsi.zMapName('Jaw', 'ChainEff', 'Mid')

			# format the chain #
			fmt = xsi.zChainFormatter(self.root_jaw)
			fmt.Format()
		
			#---------------------------------------------------------------------
			# add a con #
			self.con_jaw 							= xsi.zCon()
			self.con_jaw.type 						= 'sphere'
			self.con_jaw.size 						= self.size_jaw_con * self.parent.scale
			self.con_jaw.transform 					= self.root_jaw.Bones(0).Kinematics.Global.Transform
			self.con_jaw.basename 					= 'Jaw'
			self.con_jaw.symmetry 					= 'Mid'
			self.con_jaw.parent_node 				= self.con_head.node_hook
			self.con_jaw.rotation_order 			= 'zyx'
			self.con_jaw.red 						= 0.75
			self.con_jaw.green 						= 0.75
			self.con_jaw.blue 						= 0
			self.con_jaw.Draw()
			self.con_jaw.AddTransformSetupRot()
		
			# offset to the chin #
			self.con_jaw.Offset(self.root_jaw.Bones(0).Length.Value, 0, 0)
		
			# add it to the controls group #
			if self.group_controls: self.group_controls.AddMember(self.con_jaw.node_con)
		
			#---------------------------------------------------------------------
			# hook up the jaw bone #
	
			# constrain the jaw effector to the jaw con #
			self.root_jaw.Bones(0).Kinematics.AddConstraint('Pose', self.con_jaw.node_hook, True)
	
		#---------------------------------------------------------------------
		# draw the EYES
		if self.build_eyes:
		
			trans = XSIMath.CreateTransform()

			# calculate the eye effector position #
			trans.Copy(template.t_eye_l)
			trans.AddLocalTranslation(XSIMath.CreateVector3(self.parent.scale, 0, 0))
			v_eye_eff_l = trans.Translation

			trans.Copy(template.t_eye_r)
			trans.AddLocalTranslation(XSIMath.CreateVector3(self.parent.scale, 0, 0))
			v_eye_eff_r = trans.Translation
		
			# get the eye root #
			v_eye_root_l = template.t_eye_l.Translation
			v_eye_root_r = template.t_eye_r.Translation
		
		
			# draw the skeletons #
			self.root_eye_l = self.root_head.Effector.Add2DChain(
				v_eye_root_l,
				v_eye_eff_l,
				XSIMath.CreateVector3(0, 0, 1),
				c.si2DChainNormalRadian
			)
		
			self.root_eye_r = self.root_head.Effector.Add2DChain(
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
			self.con_eye_aim.transform.Translation		= template.v_eye_aim
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
			v_eye_root_aim_l.Sub(template.v_eye_aim, v_eye_root_l)
			v_eye_aim_l = XSIMath.CreateVector3(0, 0, v_eye_root_aim_l.Z)  # use the z component only #
			v_eye_aim_l.AddInPlace(v_eye_root_l)
		
			v_eye_root_aim_r = XSIMath.CreateVector3()
			v_eye_root_aim_r.Sub(template.v_eye_aim, v_eye_root_r)
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
			# add the constraint from the eyes to the world (all_null) #

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

		# jaw #
		if self.build_jaw:
			node_dfm_parent = self.deformer_parent.AddNull(xsi.zMapName('Jaw', 'Custom:DfmPrnt', 'Mid'))
			node_dfm_shadow = node_dfm_parent.AddNull(xsi.zMapName('Jaw', 'Custom:DfmShdw', 'Mid'))
			node_env 		= node_dfm_shadow.AddNull(xsi.zMapName('Jaw', 'Env', 'Mid'))
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
		
			node_dfm_parent.Kinematics.AddConstraint('Pose', self.root_jaw.Bones(0).Parent, False)
			node_dfm_shadow.Kinematics.AddConstraint('Pose', self.root_jaw.Bones(0), False)
		
		# eye left #
		if self.build_eyes:
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
		if self.build_eyes:
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
			self.character_subset.AddNodeRot(self.con_head.node_con)
			if self.build_jaw:
				self.character_subset.AddNodeRot(self.con_jaw.node_con)
			self.character_subset.AddParams(orient_spine)
			self.character_subset.AddParams(orient_world)
			if self.build_eyes:
				self.character_subset.AddNodePosRot(self.con_eye_aim.node_con)
			self.character_subset.AddParams(param_to_world)
		
		# # for setup purposes only #
		# # report the class attributes #
		# for key in self.__dict__:
		# 	log(key)

#-----------------------------------------------------------------------------
# Commands
#-----------------------------------------------------------------------------
def zHead_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	#oCmd.SetFlag(constants.siNoLogging,false)

	#oArgs = oCmd.Arguments
	#oArgs.Add('arg', c.siArgumentInput, '', c.siString)
	#oArgs.AddObjectArgument('model')

	return True
	
def zHead_Execute():
	# export the python object #
	import win32com.server
	return win32com.server.util.wrap(
		zHead()
	)
	
