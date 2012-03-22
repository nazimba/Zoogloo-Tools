"""
zAnimalLeg_1_0.py

Created by andy on 2009-03-04.
Copyright (c) 2009 Andy Buecker. All rights reserved.
"""

__version__ = '$Revision: 198 $'
__author__  = '$Author: andy $'
__date__    = '$Date: 2009-03-06 10:14 -0800 $'

import win32com.client
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
	in_reg.Name = "zAnimalLeg_1_0"
	in_reg.Email = "andy@abuecker.com"
	in_reg.URL = ""
	in_reg.Major = 1
	try:
		in_reg.Minor = int(__version__.split(' ')[1])
	except:
		in_reg.Minor = 0


	in_reg.RegisterCommand('zAnimalLeg_1_0', 'zAnimalLeg_1_0')

	# copyright message #
	msg = '''
------------------------------------------
  %s (v.%d.%d)
  Copyright 2009 Zoogloo LLC.
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

class zAnimalLeg(object):

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
	uid				= '8284f9e216d5003fd4523f66eeeb0b43'
	basename		= 'AnimalLeg'
	scale			= 1
	sym				= None
	
	def __init__(self, basename='AnimalLeg', sym='left'):
		super(zAnimalLeg, self).__init__()
		
		# reset the instance varaibles #
		self._template 	= None
		self._rig		= None
		
		self.symmetry 	= sym
		self.basename	= basename
	
	@zProp
	def template():
		'''Template Accessor'''
		def fget(self):
			# create a template if it doesn't exist #
			if not self._template:
				# wrap a new class #
				self._template = win32com.server.util.wrap(zAnimalLeg_Template(self))
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
				self._rig = win32com.server.util.wrap(zAnimalLeg_Rig(self))
			# return the private var #
			return dispatch(self._rig)
		def fset(self, value):
			raise Exception('Unable to modify rig value.')
		fdel = fset
		return locals()
			
				
class zAnimalLeg_Template(object):
	"""docstring for zAnimalLeg_Template"""
	
	_inputs_ = [
		'v_hip',
		'v_knee', 
		'v_hawk', 
		'v_ankle', 
		'v_toe', 
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
		super(zAnimalLeg_Template, self).__init__()
		
		# set the instance variables #
		self.parent			= parent
		self.scale 			= 1
		self.model 			= xsi.ActiveSceneRoot
		
		# load the defaults #
		self.LoadDefaultValues()
	
	
	def LoadDefaultValues(self):
		"""
		Sets the default values 
		"""
		self.v_hip				= XSIMath.CreateVector3(3.2317, 18.829, -0.0303)
		self.v_knee				= XSIMath.CreateVector3(3.2317, 12.542, 4.7761)
		self.v_hawk				= XSIMath.CreateVector3(3.2317, 7.811, -3.4628)
		self.v_ankle			= XSIMath.CreateVector3(3.2317, 2.5095, -0.0658)
		self.v_toe				= XSIMath.CreateVector3(3.2317, 2.2571, 1.8452)
		if re.match(r'^right$', self.parent.symmetry, re.I):
			self.v_hip.X				*= -1
			self.v_knee.X				*= -1
			self.v_hawk.X				*= -1
			self.v_toe.X				*= -1

	def Draw(self):
		"""docstring for Draw"""
		# get the model #
		if not self.model:
			raise Exception('Model attribute for template not specified.')

		# dispatch the model #
		self.model = dispatch(self.model)

		#---------------------------------------------------------------------
		# create a node to hold the template #
		node_parent = self.model.AddNull('%s_%s_Container' % (self.parent.basename, self.parent.symmetry[0].upper()))
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
		node_hip 	= node_parent.AddNull(xsi.zMapName('Hip', 'Custom:Tmp', self.parent.symmetry))
		node_hip.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_hip.AddProperty('CustomProperty', False, 'zAnimalLegHip')

		node_knee	= node_parent.AddNull(xsi.zMapName('Knee', 'Custom:Tmp', self.parent.symmetry))
		node_knee.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_knee.AddProperty('CustomProperty', False, 'zAnimalLegKnee')

		node_hawk	= node_parent.AddNull(xsi.zMapName('Hawk', 'Custom:Tmp', self.parent.symmetry))
		node_hawk.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_hawk.AddProperty('CustomProperty', False, 'zAnimalLegHawk')

		node_ankle	= node_parent.AddNull(xsi.zMapName('Ankle', 'Custom:Tmp', self.parent.symmetry))
		node_ankle.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_ankle.AddProperty('CustomProperty', False, 'zAnimalLegAnkle')

		node_toe	= node_parent.AddNull(xsi.zMapName('Toe', 'Custom:Tmp', self.parent.symmetry))
		node_toe.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_toe.AddProperty('CustomProperty', False, 'zAnimalLegToe')

		#---------------------------------------------------------------------
		# set the positions #
		trans = XSIMath.CreateTransform()
		v_result = XSIMath.CreateVector3()

		# hip #
		v_result.Scale(self.parent.scale, self.v_hip)
		trans.Translation = v_result
		node_hip.Kinematics.Global.Transform = trans

		# knee #
		v_result.Scale(self.parent.scale, self.v_knee)
		trans.Translation = v_result
		node_knee.Kinematics.Global.Transform = trans
		
		# hawk #
		v_result.Scale(self.parent.scale, self.v_hawk)
		trans.Translation = v_result
		node_hawk.Kinematics.Global.Transform = trans
		
		# ankle #
		v_result.Scale(self.parent.scale, self.v_ankle)
		trans.Translation = v_result
		node_ankle.Kinematics.Global.Transform = trans
		
		# ankle #
		v_result.Scale(self.parent.scale, self.v_toe)
		trans.Translation = v_result
		node_toe.Kinematics.Global.Transform = trans
		
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
				and re.match(node.Properties('zContainer').Parameters('ContainerSym').Value, self.parent.symmetry.lower(), re.I) \
				and re.match(node.Properties('zContainer').Parameters('ContainerName').Value, self.parent.basename, re.I):
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
			if node.Properties('zAnimalLegHip'):
				self.v_hip			= node.Kinematics.Global.Transform.Translation
			elif node.Properties('zAnimalLegKnee'):
				self.v_knee			= node.Kinematics.Global.Transform.Translation
			elif node.Properties('zAnimalLegHawk'):
				self.v_hawk			= node.Kinematics.Global.Transform.Translation
			elif node.Properties('zAnimalLegAnkle'):
				self.v_ankle		= node.Kinematics.Global.Transform.Translation
			elif node.Properties('zAnimalLegToe'):
				self.v_toe			= node.Kinematics.Global.Transform.Translation
		
class zAnimalLeg_Rig(object):

	_inputs_ = [
		'controls_parent',  		
		'controls_constraint',  		
		'character_set',   		
		'character_subset',   		
		'skeleton_parent',  		
		'deformer_parent',  
		'size_knee_con',	
		'size_foot_con',	
		'size_ankle_con',	
		'size_leg_fk_con',	
		'size_toe_pivot_con',	
		'group_deformers',
		'group_controls',
		'perc_knee_area',
		'perc_hawk_area',
	]
	_outputs_ = [
		'parent',
		'con_knee',
		'con_foot',
		'con_ankle',
		'con_toe_pivot',
		'root_skel',
		'root_skel_foot',
		'root_con',
		'root_con_foot',
		'root_foot_rev',
		'ik_switch',
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
		super(zAnimalLeg_Rig, self).__init__()
		
		# set the instance variables #
		self.parent					= parent

		# set the defaults for the input variables #
		for item in self._inputs_:
			setattr(self, item, None)
			
		# set specific types #
		self.deformers = dispatch('XSI.Collection')
		
		# set the default sizes #
		self.size_knee_con 		= 1
		self.size_foot_con 		= 1
		self.size_ankle_con		= 1
		self.size_leg_fk_con	= 1
		self.size_toe_pivot_con	= 1
		self.perc_knee_area	 	= 10
		self.perc_hawk_area 	= 10
		
		self.skeleton_parent	= xsi.ActiveSceneRoot
		self.controls_parent	= xsi.ActiveSceneRoot
		self.deformer_parent	= xsi.ActiveSceneRoot
		
	
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
		# draw the leg skeleton
		
		# calculate the plane vector #
		v_plane = XSIMath.CreateVector3()
		v1		= XSIMath.CreateVector3()
		v2		= XSIMath.CreateVector3()
		# get vector from root to ankle #
		v1.Sub(template.v_hip, template.v_ankle)
		# get vector from root to knee #
		v2.Sub(template.v_hip, template.v_knee)
		# get the cross product #
		v_plane.Cross(v1, v2)
		
		# draw the skeleton #
		self.root_skel = self.skeleton_parent.Add2DChain(
			template.v_hip,
			template.v_knee,
			v_plane,
			c.si2DChainNormalRadian
		)
		
		# add the 'shin' bone #
		self.root_skel.AddBone(
			template.v_hawk,
			c.siChainBonePin
		)
		
		# add the hawk bone #
		self.root_skel.AddBone(
			template.v_ankle,
			c.siChainBonePin
		)
	
		# rename the chain #
		self.root_skel.Name 			= xsi.zMapName(self.parent.basename, 'ChainRoot', self.parent.symmetry)
		for b in xrange(self.root_skel.Bones.Count):
			bone 		= self.root_skel.Bones(b)
			bone.Name 	= xsi.zMapName(self.parent.basename, 'ChainBone', self.parent.symmetry, b)
		self.root_skel.effector.Name 	= xsi.zMapName(self.parent.basename, 'ChainEff', self.parent.symmetry)

		#---------------------------------------------------------------------
		# draw the foot chain #

		# calculate the plane vector #
		v_plane_foot = XSIMath.CreateVector3()
		v1		= XSIMath.CreateVector3()
		v2		= XSIMath.CreateVector3(0, 1, 0)
		# get vector from ankle to toe #
		v1.Sub(template.v_toe, template.v_ankle)
		# get the cross product #
		v_plane_foot.Cross(v1, v2)
		
		# draw the skeleton #
		self.root_skel_foot = self.root_skel.effector.Add2DChain(
			template.v_ankle,
			template.v_toe,
			v_plane_foot,
			c.si2DChainNormalRadian
		)
		
		# rename the chain #
		self.root_skel_foot.Name 				= xsi.zMapName('Foot', 'ChainRoot', self.parent.symmetry)
		self.root_skel_foot.Bones(0).Name	 	= xsi.zMapName('Foot', 'ChainBone', self.parent.symmetry)
		self.root_skel_foot.effector.Name 	= xsi.zMapName('Foot', 'ChainEff', self.parent.symmetry)

		#---------------------------------------------------------------------
		# draw a control chain
		
		# draw the skeleton #
		self.root_con = self.controls_parent.Add2DChain(
			template.v_hip,
			template.v_knee,
			v_plane,
			c.si2DChainNormalRadian
		)
		
		# add the 'shin' bone #
		self.root_con.AddBone(
			template.v_hawk,
			c.siChainBonePin
		)
		
		# add the hawk bone #
		self.root_con.AddBone(
			template.v_ankle,
			c.siChainBonePin
		)
		
		# rename the chain #
		self.root_con.Name 			= xsi.zMapName('%sFk' % self.parent.basename, 'ChainRoot', self.parent.symmetry)
		for b in xrange(self.root_con.Bones.Count):
			bone 		= self.root_con.Bones(b)
			bone.Name 	= xsi.zMapName('%sFk' % self.parent.basename, 'Control', self.parent.symmetry, b)
		self.root_con.effector.Name 	= xsi.zMapName('%sFk' % self.parent.basename, 'ChainEff', self.parent.symmetry)
		
		# hook up the skel to the control arm #
		# Note: constraints + bones don't mix, but expressions do! #
		for b in xrange(self.root_skel.Bones.Count):
			bone = self.root_skel.Bones(b)
			bone.Kinematics.Global.Parameters('rotx').AddExpression(
				self.root_con.Bones(b).Kinematics.Global.Parameters('rotx').FullName
			) 
			bone.Kinematics.Global.Parameters('roty').AddExpression(
				self.root_con.Bones(b).Kinematics.Global.Parameters('roty').FullName
			) 
			bone.Kinematics.Global.Parameters('rotz').AddExpression(
				self.root_con.Bones(b).Kinematics.Global.Parameters('rotz').FullName
			) 

		#---------------------------------------------------------------------
		# draw the foot control chain #

		# draw the skeleton #
		self.root_con_foot = self.root_con.effector.Add2DChain(
			template.v_ankle,
			template.v_toe,
			v_plane_foot,
			c.si2DChainNormalRadian
		)
		
		# rename the chain #
		self.root_con_foot.Name 			= xsi.zMapName('FootFk', 'ChainRoot', self.parent.symmetry)
		self.root_con_foot.Bones(0).Name	= xsi.zMapName('FootFk', 'Control', self.parent.symmetry)
		self.root_con_foot.effector.Name 	= xsi.zMapName('FootFk', 'ChainEff', self.parent.symmetry)

		#---------------------------------------------------------------------
		# format the chains #
		xsi.zFormatChainFromPrefs(self.root_skel)
		xsi.zFormatChainFromPrefs(self.root_skel_foot)

		fmt = xsi.zChainFormatter(self.root_con)
		fmt.SetRootColor(0, 1, 0, True)
		fmt.SetBoneColor(0, 1, 0, True)
		fmt.SetEffColor(0, 1, 0, True)
		if right:
			fmt.SetRootColor(1, 0, 0, True)
			fmt.SetBoneColor(1, 0, 0, True)
			fmt.SetEffColor(1, 0, 0, True)
		fmt.RootDisplay = 0
		fmt.BoneDisplay = 6
		fmt.BoneSize	= self.size_leg_fk_con * self.parent.scale
		fmt.EffDisplay 	= 0
		fmt.Format()
		
		fmt = xsi.zChainFormatter(self.root_con_foot)
		fmt.SetRootColor(0, 1, 0, True)
		fmt.SetBoneColor(0, 1, 0, True)
		fmt.SetEffColor(0, 1, 0, True)
		if right:
			fmt.SetRootColor(1, 0, 0, True)
			fmt.SetBoneColor(1, 0, 0, True)
			fmt.SetEffColor(1, 0, 0, True)
		fmt.RootDisplay = 0
		fmt.BoneDisplay = 6
		fmt.BoneSize	= self.size_leg_fk_con * self.parent.scale
		fmt.EffDisplay 	= 0
		fmt.Format()
		
		# set neutral pose #
		xsi.SetNeutralPose([self.root_con.Bones(0),
							self.root_con.Bones(1),
							self.root_con.Bones(2),
							self.root_con.Effector], c.siSRT, False)
		
		xsi.SetNeutralPose([self.root_con_foot.Bones(0),
							self.root_con_foot.Effector], c.siSRT, False)
		
		# set a default key on the rotation of the bones #
		for bone in self.root_con.Bones:
			bone = dispatch(bone)
			bone.Kinematics.Local.RotX.AddFcurve2([0,0], c.siDefaultFCurve)
			bone.Kinematics.Local.RotY.AddFcurve2([0,0], c.siDefaultFCurve)
			bone.Kinematics.Local.RotZ.AddFcurve2([0,0], c.siDefaultFCurve)
			
		for bone in self.root_con_foot.Bones:
			bone = dispatch(bone)
			bone.Kinematics.Local.RotX.AddFcurve2([0,0], c.siDefaultFCurve)
			bone.Kinematics.Local.RotY.AddFcurve2([0,0], c.siDefaultFCurve)
			bone.Kinematics.Local.RotZ.AddFcurve2([0,0], c.siDefaultFCurve)
			
		# add to the group controls #
		if self.group_controls:
			self.group_controls.AddMember(self.root_con.Bones)
			self.group_controls.AddMember(self.root_con_foot.Bones)

		# hook up the skel to the control arm #
		# Note: constraints + bones don't mix, but expressions do! #
		self.root_skel_foot.bones(0).Kinematics.Global.Parameters('rotx').AddExpression(
			self.root_con_foot.bones(0).Kinematics.Global.Parameters('rotx').FullName
		) 
		self.root_skel_foot.bones(0).Kinematics.Global.Parameters('roty').AddExpression(
			self.root_con_foot.bones(0).Kinematics.Global.Parameters('roty').FullName
		) 
		self.root_skel_foot.bones(0).Kinematics.Global.Parameters('rotz').AddExpression(
			self.root_con_foot.bones(0).Kinematics.Global.Parameters('rotz').FullName
		) 


		#---------------------------------------------------------------------
		# draw the controls
		
		# foot con #
		self.con_foot 							= xsi.zCon()
		self.con_foot.type 						= 'sphere'
		self.con_foot.size 						= self.size_foot_con * self.parent.scale
		self.con_foot.transform.Translation 	= self.root_skel.effector.Kinematics.Global.Transform.Translation
		self.con_foot.transform.Rotation 		= XSIMath.CreateRotation(0,XSIMath.DegreesToRadians(-90),0)
		self.con_foot.basename 					= 'Foot'
		self.con_foot.symmetry 					= self.parent.symmetry
		self.con_foot.parent_node 				= self.controls_parent
		self.con_foot.rotation_order 			= 'zxy'
		self.con_foot.red 				   		= 0
		self.con_foot.green 			   		= 1
		self.con_foot.blue 				   		= 0
		if re.match(r'^right$', self.parent.symmetry, re.I):
			self.con_foot.red 					= 1
			self.con_foot.green 				= 0
			self.con_foot.blue 					= 0
		self.con_foot.Draw()
		self.con_foot.AddTransformSetupLast()

		# ankle con #
		self.con_ankle 							= xsi.zCon()
		self.con_ankle.type 					= 'round_box'
		self.con_ankle.size 					= self.size_ankle_con * self.parent.scale
		self.con_ankle.transform.Translation 	= self.root_skel.effector.Kinematics.Global.Transform.Translation
		self.con_ankle.basename 				= 'Ankle'
		self.con_ankle.symmetry 				= self.parent.symmetry
		self.con_ankle.parent_node 				= self.con_foot.node_hook
		if re.match(r'^right$', self.parent.symmetry, re.I):
			self.con_ankle.red 					= 0.8
			self.con_ankle.green 				= 0
			self.con_ankle.blue 				= 0
		else:
			self.con_ankle.red 					= 0
			self.con_ankle.green 				= 0.8
			self.con_ankle.blue 				= 0
		self.con_ankle.Draw()
		self.con_ankle.AddTransformSetupPos('local')
		
		# add to the controls group #
		if self.group_controls:
			self.group_controls.AddMember(self.con_foot.node_con)
			self.group_controls.AddMember(self.con_ankle.node_con)
			
		#---------------------------------------------------------------------
		# create the KNEE orientation nodes #
		
		# create a knee branch #
		knee_branch = self.controls_parent.FindChild(xsi.zMapName('knee', 'Branch', self.parent.symmetry))
		if not knee_branch:
			knee_branch = self.controls_parent.AddNull(xsi.zMapName('knee', 'Branch', self.parent.symmetry))
		knee_branch.primary_icon.Value = 0
		knee_branch.Properties('Visibility').Parameters('viewvis').Value = False
		knee_branch.Properties('Visibility').Parameters('rendvis').Value = False
		
		# create an aim node #
		knee_orient_aim = knee_branch.AddNull(
			xsi.zMapName('KneeOrient', 'Custom:Aim', self.parent.symmetry)
		)
		knee_orient_aim.primary_icon.Value = 0
		knee_orient_aim.Properties('Visibility').Parameters('viewvis').Value = False
		knee_orient_aim.Properties('Visibility').Parameters('rendvis').Value = False
		
		# build the transform for the orientation aim null #
		trans = XSIMath.CreateTransform()
		trans.Translation = template.v_hip
		knee_orient_aim.Kinematics.Global.Transform = trans

		# aim the orientation #
		cns = knee_orient_aim.Kinematics.AddConstraint('Direction', self.con_ankle.node_hook, False)
		cns = dispatch(cns)
		knee_orient_aim.Kinematics.Global.Transform = self.root_skel.Kinematics.Global.Transform
		
		# keep the orientation in the same relative orientation, except the aim vector #
		knee_orient_aim.Kinematics.Local.Parameters('rotx').AddExpression(
			knee_orient_aim.Kinematics.Local.Parameters('rotx').Value
		)
		knee_orient_aim.Kinematics.Local.Parameters('roty').AddExpression(
			knee_orient_aim.Kinematics.Local.Parameters('roty').Value
		)
		knee_orient_aim.Kinematics.Local.Parameters('rotz').AddExpression(
			knee_orient_aim.Kinematics.Local.Parameters('rotz').Value
		)
		
		#.....................................................................
		# NOTE:                                                               
		# The above step doesn't always update correctly.  The rotx           
		# expression isn't necissarly evaluated. This is sometimes noticeable 
		# on undo's.  Just update the frame and the error will correct    
		# itself.                                                             
		#.....................................................................

		# constrain to the chain root #
		knee_orient_aim.Kinematics.AddConstraint('Position', self.root_con, False)

		# create a child twist null #
		knee_twist_rest = knee_orient_aim.AddNull(xsi.zMapName('KneeRigTwist', 'Zero', self.parent.symmetry))
		knee_twist_rest.primary_icon.Value = 0
		knee_twist_rest.Properties('Visibility').Parameters('viewvis').Value = False
		knee_twist_rest.Properties('Visibility').Parameters('rendvis').Value = False
		knee_twist_rest.Kinematics.Global.Transform = knee_orient_aim.Kinematics.Global.Transform
		
		# rotate it 90 in z to get y to point up #
		trans = knee_twist_rest.Kinematics.Global.Transform
		trans.AddLocalRotation(XSIMath.CreateRotation(0, 0, XSIMath.DegreesToRadians(90)))
		knee_twist_rest.Kinematics.Global.Transform = trans
		
		# orient the twister to the foot & position to the leg root #
		trans = self.root_skel.Kinematics.Global.Transform
		trans.Rotation = self.con_foot.node_con.Kinematics.Global.Transform.Rotation
		knee_twist_rest.Kinematics.Global.Transform = trans

		# match the rotation orders #
		knee_twist_rest.Kinematics.Local.Parameters('rotorder').AddExpression(
			self.con_foot.node_con.Kinematics.Local.Parameters('rotorder').FullName
		)

		# create a hook node for the knee twister #
		knee_twist_hook = knee_twist_rest.AddNull(xsi.zMapName('KneeRigTwist', 'Hook', self.parent.symmetry))
		knee_twist_hook.primary_icon.Value = 0
		knee_twist_hook.Properties('Visibility').Parameters('viewvis').Value = False
		knee_twist_hook.Properties('Visibility').Parameters('rendvis').Value = False
		knee_twist_hook.Kinematics.Global.Transform = knee_twist_rest.Kinematics.Global.Transform

		# link an expression to the foot orientation #
		knee_twist_hook.Kinematics.Local.Parameters('roty').AddExpression(
			self.con_foot.node_con.Kinematics.Local.Parameters('roty').FullName
		)

		#---------------------------------------------------------------------
		# create a middle null between the #
		knee_mid = knee_twist_hook.AddNull(xsi.zMapName('KneeRig', 'Custom:Mid', self.parent.symmetry))
		knee_mid.primary_icon.Value = 0
		knee_mid.Properties('Visibility').Parameters('viewvis').Value = False
		knee_mid.Properties('Visibility').Parameters('rendvis').Value = False
		knee_mid.Kinematics.Global.Transform = knee_twist_hook.Kinematics.Global.Transform
		
		# lock the local orientation #
		knee_mid.Kinematics.Local.RotX.AddExpression(0)
		knee_mid.Kinematics.Local.RotY.AddExpression(0)
		knee_mid.Kinematics.Local.RotZ.AddExpression(0)

		# add the 2 point constraint (position only)#
		col = dispatch('XSI.Collection')
		col.Add(self.root_con)
		col.Add(self.con_ankle.node_hook)
		cns = knee_mid.Kinematics.AddConstraint('TwoPoints', col, False)
		cns = dispatch(cns)
		
		# set the constraint options #
		cns.upvct_active.Value 	= False
		cns.tangent.Value 		= False
		
		# set the orientation to the parent (knee twist) #
		trans = knee_mid.Kinematics.Global.Transform 
		trans.Rotation = knee_twist_hook.Kinematics.Global.Transform.Rotation
		knee_mid.Kinematics.Global.Transform = trans

		#---------------------------------------------------------------------
		# calculate the knee controller position #
		trans_knee_con = XSIMath.CreateTransform()

		# set the position #
		trans_knee_con.Translation = self.root_con.Bones(1).Kinematics.Global.Transform.Translation
		
		# get the middle orientation #
		quat_leg1 	= self.root_con.Bones(0).Kinematics.Global.Transform.Rotation.Quaternion
		quat_leg2 	= self.root_con.Bones(1).Kinematics.Global.Transform.Rotation.Quaternion
		quat_mid	= XSIMath.CreateQuaternion()
		quat_mid.Slerp(quat_leg1, quat_leg2, 0.5)
		rot = XSIMath.CreateRotation()
		rot.Quaternion = quat_mid
		trans_knee_con.Rotation = rot
		
		# add the length of the leg joint to the local position in Y #
		trans_knee_con.AddLocalTranslation(
			XSIMath.CreateVector3(
				0, 
				self.root_con.Bones(0).Length.Value, 
				0
			)
		)

		#---------------------------------------------------------------------
		# knee con #
		self.con_knee 						= xsi.zCon()
		self.con_knee.type 					= 'text:K'
		self.con_knee.size 					= self.size_knee_con * self.parent.scale
		self.con_knee.transform 			= trans_knee_con
		self.con_knee.transform.Rotation 	= XSIMath.CreateRotation(0,0,0)
		self.con_knee.basename 				= 'Knee'
		self.con_knee.symmetry 				= self.parent.symmetry
		self.con_knee.parent_node 			= knee_mid
		if re.match(r'^right$', self.parent.symmetry, re.I):
			self.con_knee.red 				= 0.8
			self.con_knee.green 			= 0
			self.con_knee.blue 				= 0
		else:                           	
			self.con_knee.red 				= 0
			self.con_knee.green 			= 0.8
			self.con_knee.blue 				= 0
		self.con_knee.Draw()
		self.con_knee.AddTransformSetupPos('local')

		# add to the controls group #
		if self.group_controls:
			self.group_controls.AddMember(self.con_knee.node_con)
			
		#---------------------------------------------------------------------
		# constrain the chain
		self.root_con.effector.Kinematics.AddConstraint('Pose', self.con_ankle.node_hook, True)
		
		# position constrain the root to the pelvis #
		self.root_con.Kinematics.AddConstraint('Pose', self.skeleton_parent, True)
			
		# constrain the chain up vectors #
		xsi.ApplyOp("SkeletonUpVector", "%s;%s" % \
					(self.root_con.Bones(0), self.con_knee.node_hook), 3, 
					c.siPersistentOperation, "", 0)

		# constrain the foot skel to the foot con #
		# cns_foot = self.root_skel_foot.Bones(0).Kinematics.AddConstraint('Pose', self.con_foot.node_hook, True)
		# cns_foot.Parameters('blendweight').AddExpression(self.root_con.Bones(0).Properties('Kinematic Chain').blendik.FullName)
		
		#---------------------------------------------------------------------
		# add a toe pivot 

		# draw the chain #
		self.root_foot_rev = self.controls_parent.Add2DChain(
			template.v_toe, 
			template.v_ankle, 
			v_plane, 
			c.si2DChainNormalRadian,
			xsi.zMapName('FootRev', 'ChainRoot', self.parent.symmetry)
		)
		self.root_foot_rev.Effector.Name = xsi.zMapName('FootRev', 'ChainEff', self.parent.symmetry)
		self.root_foot_rev.Bones(0).Name = xsi.zMapName('FootRev', 'ChainBone', self.parent.symmetry, 1)
		
		# format the chain #
		fmt = xsi.zChainFormatter(self.root_foot_rev)
		fmt.SetRootColor(0, 1, 0, True)
		fmt.SetBoneColor(0, 1, 0, True)
		fmt.SetEffColor(0, 1, 0, True)
		if right:
			fmt.SetRootColor(1, 0, 0, True)
			fmt.SetBoneColor(1, 0, 0, True)
			fmt.SetEffColor(1, 0, 0, True)
		fmt.RootDisplay = 0
		fmt.BoneSize	= self.parent.scale
		fmt.EffDisplay 	= 0
		fmt.Format()


		#---------------------------------------------------------------------
		# contrain the reverse foot to the controller #
		self.root_foot_rev.Kinematics.AddConstraint('Pose', self.con_foot.node_hook, True)

		# constrain the ankle rest to the reverse foot effector #
		self.con_ankle.node_rest.Kinematics.AddConstraint('Position', self.root_foot_rev.Effector, False)
		
		#---------------------------------------------------------------------
		# add a toe pivot controller
		self.con_toe_pivot 						= xsi.zCon()
		self.con_toe_pivot.type 				= 'rot'
		self.con_toe_pivot.size 				= self.size_toe_pivot_con * self.parent.scale
		self.con_toe_pivot.transform 			= self.root_foot_rev.Kinematics.Global.Transform
		# self.con_toe_pivot.transform.AddLocalRotation(
		# 	XSIMath.CreateRotation(0, 0, XSIMath.DegreesToRadians(180))
		# )
		self.con_toe_pivot.basename 			= 'ToePivot'
		self.con_toe_pivot.symmetry 			= self.parent.symmetry
		self.con_toe_pivot.parent_node 			= self.con_foot.node_hook
		self.con_toe_pivot.rotation_order 		= 'zyx'
		if re.match(r'^right$', self.parent.symmetry, re.I):
			self.con_toe_pivot.red 				= 0.8
			self.con_toe_pivot.green 			= 0
			self.con_toe_pivot.blue 			= 0
		else:                               	
			self.con_toe_pivot.red 				= 0
			self.con_toe_pivot.green 			= 0.8
			self.con_toe_pivot.blue 			= 0
		self.con_toe_pivot.Draw()
		self.con_toe_pivot.AddTransformSetupRot('add', False, False, True) # only z axis
		
		# move the controller points down a bit #
		self.con_toe_pivot.Offset(0, self.parent.scale, 0)
		
		# constrain the reverse foot to the constraint #
		self.root_foot_rev.Bones(0).Kinematics.AddConstraint('Pose', self.con_toe_pivot.node_con, True)

		# add to the control group 
		if self.group_controls:
			self.group_controls.AddMember(self.con_toe_pivot.node_con)
			
		#---------------------------------------------------------------------
		# hook up the foot to the toe pivot #
		
		# create an upvector node on the foot con #
		node_upv = self.con_foot.node_hook.AddNull(
			xsi.zMapName('Foot', 'UpVector', self.parent.symmetry)
		)
		trans = self.con_foot.node_hook.Kinematics.Global.Transform
		trans.AddLocalTranslation(XSIMath.CreateVector3(0,2,0))
		node_upv.Kinematics.Global.Transform = trans
		
		# hide the node #
		xsi.zHide(node_upv)
		
		# aim the foot at the pivot #
		cns_aim = self.root_skel_foot.Bones(0).Kinematics.AddConstraint('Direction', self.con_toe_pivot.node_hook, False)
		cns_aim = dispatch(cns_aim)
		cns_aim.UpVectorReference 	= node_upv
		cns_aim.upvct_active.Value	= True
		
		# add an expression to the aim blendweight #
		cns_aim.Parameters('blendweight').AddExpression(
			self.root_con.Bones(0).Properties('Kinematic Chain').blendik.FullName
		)
		
		#---------------------------------------------------------------------
		# create the animation parameters
		self.prop_anim = self.con_foot.node_con.AddProperty(
			'CustomProperty', False, 'zAnim_Leg_%s' % self.parent.symmetry[0].upper()
		)
		self.prop_anim.AddParameter3('ShowKneeCon', c.siBool, False, None, None, True, False)
		self.prop_anim.AddParameter3('ShowFootCons', c.siBool, False, None, None, True, False)
		self.prop_anim.AddParameter3('ShowToePivot', c.siBool, False, None, None, True, False)
		
		# add display info with proxy parameter #
		self.prop_anim_di = self.con_foot.node_con.AddProperty(
			'CustomProperty', False, 'DisplayInfo_zAnim_Leg_%s' % self.parent.symmetry[0].upper()
		)
		self.prop_anim_di.AddProxyParameter('%s.ShowKneeCon'  % self.prop_anim.Fullname)
		self.prop_anim_di.AddProxyParameter('%s.ShowFootCons' % self.prop_anim.Fullname)
		self.prop_anim_di.AddProxyParameter('%s.ShowToePivot' % self.prop_anim.FullName)

		# hook up the parameters
		self.con_knee.node_con.Properties('Visibility').viewvis.AddExpression(self.prop_anim.ShowKneeCon.FullName)
		self.con_ankle.node_con.Properties('Visibility').viewvis.AddExpression(self.prop_anim.ShowFootCons.FullName)
		self.con_toe_pivot.node_con.Properties('Visibility').viewvis.AddExpression(self.prop_anim.ShowToePivot.FullName)
		
		#---------------------------------------------------------------------
		# add the ik/fk switch
		self.ik_switch = self.prop_anim.AddParameter3('Fk/Ik', c.siFloat, 1, 0, 1, True, False)
		self.prop_anim_di.AddProxyParameter(self.ik_switch)

		# add the expressions #
		self.root_con.Bones(0).Properties('Kinematic Chain').Parameters('blendik').AddExpression(self.ik_switch.FullName)
		self.root_con.Effector.Kinematics.Constraints(0).blendweight.AddExpression(self.ik_switch.FullName)
		
		# add proxy param to fk bones #
		for bone in self.root_con.Bones:
			bone = dispatch(bone)
			di = bone.AddProperty('CustomProperty', False, 'DisplayInfo_zAnim_Leg_%s' % self.parent.symmetry[0].upper())
			di.AddProxyParameter(self.ik_switch, None, 'FK_IK')

		#---------------------------------------------------------------------
		# link the visbility on the controls to the ik fk switcher #
		
		# controller #
		self.con_foot.node_con.Properties('Visibility').viewvis.AddExpression(
			'cond(%s.chain.blendik != 0, 1, 0)' % self.root_con.Bones(0).FullName
		)
		
		# fk #
		for bone in self.root_con.Bones:
			bone = dispatch(bone)
			bone.Properties('Visibility').viewvis.AddExpression(
				'cond(%s.chain.blendik != 1, 1, 0)' % self.root_con.Bones(0).FullName
			)
		
		for bone in self.root_con_foot.Bones:
			bone = dispatch(bone)
			bone.Properties('Visibility').viewvis.AddExpression(
				'cond(%s.chain.blendik != 1, 1, 0)' % self.root_con.Bones(0).FullName
			)
		
		#---------------------------------------------------------------------
		# add character sets
		if self.character_set:
			
			# get the lower subset #
			self.character_set = dispatch(self.character_set)
			lower_set = None
			try:
				lower_set = self.character_set.Get('LowerBody')
			except:                             
				lower_set = self.character_set.AddSubset('LowerBody')
	
			# add the leg subset #
			self.character_subset = lower_set.AddSubset(
				xsi.zMapName(self.parent.basename, 'None', self.parent.symmetry)
			)
			
			# knee con viz #
			self.character_subset.AddParams(
				'%(item)s.ShowKneeCon' % {'item': self.prop_anim.FullName}
			)
			self.character_subset.AddParams(
				'%(item)s.ShowFootCons' % {'item': self.prop_anim.FullName}
			)
			# ik/fk switch #
			self.character_subset.AddParams(self.ik_switch.FullName)
			# fk leg rotations #
			for bone in self.root_con.Bones:
				self.character_subset.AddNodeRot(bone)
			# con pos and rot #
			self.character_subset.AddNodePosRot(self.con_foot.node_con)
			self.character_subset.AddNodePosRot(self.con_knee.node_con)
			self.character_subset.AddNodePosRot(self.con_ankle.node_con)
		
		#---------------------------------------------------------------------
		# create a deformer stack #
		
		# create a deformer stack for the leg bones #
		for b in xrange(self.root_skel.Bones.Count):

			# get the bone #
			bone = self.root_skel.Bones(b)
			
			# create the paarent stack #
			node_dfm_parent = self.deformer_parent.AddNull(xsi.zMapName('%s%s' % (self.parent.basename, b), 'Custom:DfmPrnt', self.parent.symmetry))
			node_dfm_shadow = node_dfm_parent.AddNull(xsi.zMapName('%s%s' % (self.parent.basename, b), 'Custom:DfmShdw', self.parent.symmetry))
			node_env   = node_dfm_shadow.AddNull(xsi.zMapName('%s%s' % (self.parent.basename, b), 'Env', self.parent.symmetry))
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
		
			node_dfm_parent.Kinematics.AddConstraint('Pose', bone.parent, False)
			node_dfm_shadow.Kinematics.AddConstraint('Pose', bone, False)

		# create the deformer stack for the foot #
		node_dfm_parent = self.deformer_parent.AddNull(xsi.zMapName('Foot', 'Custom:DfmPrnt', self.parent.symmetry))
		node_dfm_shadow = node_dfm_parent.AddNull(xsi.zMapName('Foot', 'Custom:DfmShdw', self.parent.symmetry))
		foot_env   = node_dfm_shadow.AddNull(xsi.zMapName('Foot', 'Env', self.parent.symmetry))
		self.deformers.Add(foot_env)
		
		node_dfm_parent.primary_icon.Value 	= 0
		node_dfm_parent.Properties('Visibility').Parameters('viewvis').Value = False
		node_dfm_parent.Properties('Visibility').Parameters('rendvis').Value = False
		node_dfm_shadow.primary_icon.Value 	= 0
		node_dfm_shadow.Properties('Visibility').Parameters('viewvis').Value = False
		node_dfm_shadow.Properties('Visibility').Parameters('rendvis').Value = False
		foot_env.primary_icon.Value			= 0
		foot_env.Properties('Visibility').Parameters('viewvis').Value = False
		foot_env.Properties('Visibility').Parameters('rendvis').Value = False
		
		node_dfm_parent.Kinematics.AddConstraint('Pose', self.root_skel_foot, False)
		node_dfm_shadow.Kinematics.AddConstraint('Pose', self.root_skel_foot.Bones(0), False)
		
		#---------------------------------------------------------------------
		# add the deformers to the deformers group #
		if self.group_deformers:
			self.group_deformers = dispatch(self.group_deformers)
			self.group_deformers.AddMember(self.deformers)
			
#-----------------------------------------------------------------------------
# Commands
#-----------------------------------------------------------------------------
def zAnimalLeg_1_0_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oArgs = oCmd.Arguments
	oArgs.Add('basename', c.siArgumentInput, 'AnimalLeg', c.siString)
	oArgs.Add('symmetry', c.siArgumentInput, 'left', c.siString)
	return True
	
def zAnimalLeg_1_0_Execute(basename, symmetry):
	# export the python object #
	import win32com.server
	return win32com.server.util.wrap(
		zAnimalLeg(basename, symmetry)
	)
	
