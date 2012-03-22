"""
zLeg.py

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
	in_reg.Name = "zLeg"
	in_reg.Email = "andy@zoogloo.net"
	in_reg.URL = ""
	in_reg.Major = 1
	in_reg.Minor = 1

	in_reg.RegisterProperty('zLeg')

	in_reg.RegisterCommand('zLeg', 'zLeg')

	in_reg.RegisterMenu(c.siMenuTbAnimateActionsStoreID, 'zLegMenu', False)
	
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

class zLeg(object):
	'''
	# get a new pelvis instance #
	pelvis = xsi.zLeg()
	
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
		'symmetry',
	]
	# define those attrs that are read only #
	_readonly_attrs_ = []

	# set the class variables #
	_template 		= None
	_rig 			= None
	uid				= '64df5ba9764a18e9094e9d5da2f843aa'
	basename		= 'Leg'
	scale			= 1
	
	def __init__(self, symmetry='left'):
		super(zLeg, self).__init__()
		
		# reset the instance varaibles #
		self._template 		= None
		self._rig		 	= None
		
		self.scale			= 1
		self.basename		= 'Leg'
		self.symmetry		= symmetry
	
	@zProp
	def template():
		'''Template Accessor'''
		def fget(self):
			# create a template if it doesn't exist #
			if not self._template:
				# wrap a new class #
				self._template = dispatch(win32com.server.util.wrap(zLeg_Template(self)))
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
				self._rig = dispatch(win32com.server.util.wrap(zLeg_Rig(self)))
			# return the private var #
			return self._rig
		def fset(self, value):
			raise Exception('Unable to modify rig value.')
		fdel = fset
		return locals()
			
				
class zLeg_Template(object):
	"""docstring for zLeg_Template"""
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
		'v_root',
		'v_knee',
		'v_ankle',
	]    
	# defv_toe  ine those attrs that are read only #
	_readonly_attrs_ = [
		'parent'
	]

	# set the class variables #
	parent		= None
	model 		= None

	def __init__(self, parent):
		super(zLeg_Template, self).__init__()
		
		# set the instance variables #
		self.parent		= parent
		self.model 		= None
		
		# set the default value #
		self.LoadDefaultValues()
		
	
	def LoadDefaultValues(self):
		"""Sets the default values for the template"""
		self.v_root 	= XSIMath.CreateVector3(1.839, 12.151, 0.196)
		self.v_knee 	= XSIMath.CreateVector3(2.414, 7.474, 0.866)
		self.v_ankle	= XSIMath.CreateVector3(2.580, 3.454, 0.216)
		if re.match(r'^right$', self.parent.symmetry, re.I):
			self.v_root.X 	*= -1
			self.v_knee.X 	*= -1
			self.v_ankle.X	*= -1
		
		# set the default model for the template space #
		self.model = xsi.ActiveSceneRoot
			
	def Draw(self):
		"""docstring for Draw"""
		
		# get the model #
		if not self.model:
			raise Exception('Model attribute for template not specified.')
		
		# dispatch the model #
		self.model = dispatch(self.model)
		
		# get the defaults if the vectors aren't defined #
		if not self.v_root or not self.v_knee or not self.v_ankle:
			self.LoadDefaultValues(sym)
		
		#---------------------------------------------------------------------
		# create a node to hold the template #
		node_parent = self.model.AddNull('Leg_%s_Container' % self.parent.symmetry[0].upper())
		node_parent.primary_icon.Value = 0
		node_parent.Properties('Visibility').Parameters('viewvis').Value = False
		node_parent.Properties('Visibility').Parameters('rendvis').Value = False
		node_parent.AddProperty('CustomProperty', False, 'zBuilderTemplateItem')
		prop = node_parent.AddProperty('CustomProperty', False, 'zContainer')
		prop = dispatch(prop)
		prop.AddParameter3('ContainerName', c.siString, 'Leg')
		prop.AddParameter3('ContainerSym', c.siString, self.parent.symmetry)
		prop.AddParameter3('ContainerUID', c.siString, self.parent.uid)
			
		# draw the nodes #
		node_root 	= node_parent.AddNull(xsi.zMapName('LegRoot', 'Custom:Tmp', self.parent.symmetry))
		node_knee 	= node_parent.AddNull(xsi.zMapName('LegKnee', 'Custom:Tmp', self.parent.symmetry))
		node_ankle 	= node_parent.AddNull(xsi.zMapName('LegAnkle', 'Custom:Tmp', self.parent.symmetry))
		
		# tag the nodes #
		node_root.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_root.AddProperty('CustomProperty', False, 'zLegRoot')

		node_knee.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_knee.AddProperty('CustomProperty', False, 'zLegKnee')

		node_ankle.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_ankle.AddProperty('CustomProperty', False, 'zLegAnkle')
		
		#---------------------------------------------------------------------
		# set the positions #
		trans = XSIMath.CreateTransform()
		v_result = XSIMath.CreateVector3()
		
		# root #
		v_result.Scale(self.parent.scale, self.v_root)
		trans.Translation = v_result
		node_root.Kinematics.Global.Transform = trans
		
		# knee #
		v_result.Scale(self.parent.scale, self.v_knee)
		trans.Translation = v_result
		node_knee.Kinematics.Global.Transform = trans
		
		# ankle #
		v_result.Scale(self.parent.scale, self.v_ankle)
		trans.Translation = v_result
		node_ankle.Kinematics.Global.Transform = trans
		
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
		
		cns_upv							= node_upv.Kinematics.AddConstraint('Direction', node_ankle, False)
		cns_upv							= dispatch(cns_upv)
		cns_upv.upvct_active.Value 		= True
		cns_upv.UpVectorReference		= node_knee
		cns_upv.upx						= 0
		cns_upv.upy						= 0
		cns_upv.upz						= 1
		
		cns_pos							= node_upv.Kinematics.AddConstraint('Position', node_root, False)

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
				if node.Properties('zContainer').Parameters('ContainerUID').Value  == self.parent.uid \
				and node.Properties('zContainer').Parameters('ContainerSym').Value == self.parent.symmetry:
					node_parent = node
					break
		# make sure we have the container #
		if not node_parent:
			raise Exception('Unable to find leg template container by id: %s' % self.parent.uid)
		
		#---------------------------------------------------------------------
		# get all the nodes under the container #
		child_nodes = node_parent.FindChildren('*')

		#---------------------------------------------------------------------
		# get the vectors #
		set_zLegRoot		= False
		set_zLegKnee		= False
		set_zLegAnkle		= False
		for node in child_nodes:
			if node.Properties('zLegRoot'):
				self.v_root 	= node.Kinematics.Global.Transform.Translation
				set_zLegRoot	= True
			elif node.Properties('zLegKnee'):
				self.v_knee 	= node.Kinematics.Global.Transform.Translation
				set_zLegKnee	= True
			elif node.Properties('zLegAnkle'):
				self.v_ankle 	= node.Kinematics.Global.Transform.Translation
				set_zLegAnkle	= True
		
		# see if all the variables are set #		
		for varname in locals().keys():
			if re.match(r'^set_.+', varname):
				if not locals().get(varname):
					raise Exception(
						'Unable to set "%s" template value from scene.' % varname
					)
		
class zLeg_Rig(object):
	"""
	Class for drawing a Leg.
	"""
	# required for COM wrapper #
	_public_methods_ = [
		'Build',
	]
	# define the output vars here #
	_public_attrs_ = [
		# ins #
		'parent',	   
		'skeleton_parent',
		'controls_parent',
		'deformer_parent',
		'root_pelvis',	   
		'character_set',	
		'size_foot_con',
		'size_knee_con',
		'size_ankle_con',
		'size_fk_cons',
		'group_deformers',
		'group_controls',
		   
		# outs #
	    'con_knee',	 
	    'con_foot',	 
	    'con_ankle',	 
	    'ik_switch',	 
	    'prop_anim',	 
	    'prop_anim_di', 
	    'character_subset',
		'root_leg',	
		'root_leg_con',
		'deformers',	
	]
	# define those attrs that are read only #
	_readonly_attrs_ = [
		'parent',
	    'con_knee',	 
	    'con_foot',	 
	    'con_ankle',	 
	    'ik_switch',	 
	    'prop_anim',	 
	    'prop_anim_di', 
	    'character_subset',
		'root_leg',	
		'root_leg_con',
		'deformers',	
	]

	def __init__(self, parent):
		super(zLeg_Rig, self).__init__()
		# set the instance variables #
		self.parent				= parent
		self.skeleton_parent 	= None
		self.controls_parent 	= None
		self.deformer_parent 	= None
		self.root_pelvis		= None
		self.character_set		= None
		self.group_deformers	= None

		# outputs #
		self.con_knee	   		= None
		self.con_foot	   		= None
		self.con_ankle	   		= None
		self.ik_switch	   		= None
		self.prop_anim	   		= None
		self.prop_anim_di  		= None
		self.character_subset	= None
		self.root_leg			= None
		self.root_leg_con		= None
		self.deformers			= dispatch('XSI.Collection')
		
		self.size_foot_con		= 3
		self.size_knee_con		= 1
		self.size_ankle_con		= 1
		self.size_fk_cons		= 2.5
		
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
		
		# make sure we have the template values #
		template = self.parent.template
		template = dispatch(template)
		if not template.v_root or not template.v_knee or not template.v_ankle:
			raise Exception(
				'Missing one or more template paramters.  Try using zLeg.template.LoadDefaultValues()'
			)
			
		#---------------------------------------------------------------------
		# draw the leg skeleton
		
		# calculate the plane vector #
		v_plane = XSIMath.CreateVector3()
		v1		= XSIMath.CreateVector3()
		v2		= XSIMath.CreateVector3()
		# get vector from root to ankle #
		v1.Sub(template.v_root, template.v_ankle)
		# get vector from root to knee #
		v2.Sub(template.v_root, template.v_knee)
		# get the cross product #
		v_plane.Cross(v1, v2)
		
		# draw the skeleton #
		self.root_pelvis = dispatch(self.root_pelvis)
		self.root_leg = self.root_pelvis.Effector.Add2DChain(
			template.v_root,
			template.v_knee,
			v_plane,
			c.si2DChainNormalRadian
		)
		
		# rename #
		self.root_leg.Name 				= xsi.zMapName(self.parent.basename, 'ChainRoot', self.parent.symmetry)
		self.root_leg.Bones(0).Name 	= xsi.zMapName(self.parent.basename, 'ChainBone', self.parent.symmetry, 1)
		self.root_leg.effector.Name 	= xsi.zMapName(self.parent.basename, 'ChainEff', self.parent.symmetry)
		
		# draw the shin #
		self.root_leg.AddBone(
			template.v_ankle,
			c.siChainBonePin,
			xsi.zMapName(self.parent.basename, 'ChainBone', self.parent.symmetry, 2)
		)
		
		# put the effector under the last bone #
		self.root_leg.Bones(1).AddChild(self.root_leg.effector)
		
		# align the chain root #
		trans =self.root_leg.Bones(0).Kinematics.Global.Transform
		self.root_leg.Kinematics.Global.Transform =self.root_leg.Bones(0).Kinematics.Global.Transform
		self.root_leg.Bones(0).Kinematics.Global.Transform = trans
		
		# format the chain colors
		fmt = xsi.zChainFormatter(self.root_leg)
		fmt.Format()
		
		#---------------------------------------------------------------------
		# draw the control chain
		
		# draw the skeleton #
		self.root_leg_con = self.controls_parent.Add2DChain(
			template.v_root,
			template.v_knee,
			v_plane,
			c.si2DChainNormalRadian
		)
		
		# rename #
		self.root_leg_con.Name 				= xsi.zMapName('%sFk' % self.parent.basename, 'ChainRoot', self.parent.symmetry)
		self.root_leg_con.Bones(0).Name 	= xsi.zMapName('%sFk' % self.parent.basename, 'Control', self.parent.symmetry, 1)
		self.root_leg_con.Effector.Name 	= xsi.zMapName('%sFk' % self.parent.basename, 'ChainEff', self.parent.symmetry)
		
		# draw the shin #
		self.root_leg_con.AddBone(
			template.v_ankle,
			c.siChainBonePin,
			xsi.zMapName('%sFk' % self.parent.basename, 'Control', self.parent.symmetry, 2)
		)
		
		# put the effector under the bone #
		self.root_leg_con.Bones(1).AddChild(self.root_leg_con.Effector)
		
		# align the chain root #
		trans = self.root_leg_con.Bones(0).Kinematics.Global.Transform
		self.root_leg_con.Kinematics.Global.Transform = self.root_leg_con.Bones(0).Kinematics.Global.Transform
		self.root_leg_con.Bones(0).Kinematics.Global.Transform = trans
		
		# format the bones #
		fmt = xsi.zChainFormatter(self.root_leg_con)
		if re.match(r'^left$', self.parent.symmetry, re.I):
			fmt.BoneDisplay = 6
			fmt.BoneSize	= self.size_fk_cons * self.parent.scale
			fmt.BoneR		= 0
			fmt.BoneG		= 1
			fmt.BoneB		= 0
			fmt.BoneWireR	= 0
			fmt.BoneWireG	= 1
			fmt.BoneWireB	= 0
			
			fmt.RootDisplay = 0
			fmt.RootSize	= self.parent.scale
			fmt.RootR		= 0
			fmt.RootG		= 1
			fmt.RootB		= 0
			fmt.RootWireR	= 0
			fmt.RootWireG	= 1
			fmt.RootWireB	= 0

			fmt.EffDisplay 	= 0
			fmt.EffSize		= self.parent.scale
			fmt.EffR		= 0
			fmt.EffG		= 1
			fmt.EffB		= 0
			fmt.EffWireR	= 0
			fmt.EffWireG	= 1
			fmt.EffWireB	= 0
			
			fmt.EffLastBone	= True
		else:                                                
			fmt.BoneDisplay = 6
			fmt.BoneSize	= self.size_fk_cons * self.parent.scale
			fmt.BoneR		= 1
			fmt.BoneG		= 0
			fmt.BoneB		= 0
			fmt.BoneWireR	= 1
			fmt.BoneWireG	= 0
			fmt.BoneWireB	= 0
			
			fmt.RootDisplay = 0
			fmt.RootSize	= self.parent.scale
			fmt.RootR		= 1
			fmt.RootG		= 0
			fmt.RootB		= 0
			fmt.RootWireR	= 1
			fmt.RootWireG	= 0
			fmt.RootWireB	= 0

			fmt.EffDisplay 	= 0
			fmt.EffSize		= self.parent.scale
			fmt.EffR		= 1
			fmt.EffG		= 0
			fmt.EffB		= 0
			fmt.EffWireR	= 1
			fmt.EffWireG	= 0
			fmt.EffWireB	= 0
			
			fmt.EffLastBone	= True

		fmt.Format()
		
		# add to the controls group #
		if self.group_controls:
			self.group_controls.AddMember(self.root_leg_con.Bones)
		
		#---------------------------------------------------------------------
		# constrain the skeleton root to the controll root #
		self.root_leg.Kinematics.AddConstraint('Pose', self.root_leg_con, True)

		# Note: constraints + bones don't mix, but expressions do! #
		# thigh bone #
		self.root_leg.bones(0).Kinematics.Global.Parameters('rotx').AddExpression(
			self.root_leg_con.bones(0).Kinematics.Global.Parameters('rotx').FullName
		) 
		self.root_leg.bones(0).Kinematics.Global.Parameters('roty').AddExpression(
			self.root_leg_con.bones(0).Kinematics.Global.Parameters('roty').FullName
		) 
		self.root_leg.bones(0).Kinematics.Global.Parameters('rotz').AddExpression(
			self.root_leg_con.bones(0).Kinematics.Global.Parameters('rotz').FullName
		) 

		# calf bone #
		self.root_leg.bones(1).Kinematics.Global.Parameters('rotx').AddExpression(
			self.root_leg_con.bones(1).Kinematics.Global.Parameters('rotx').FullName
		) 
		self.root_leg.bones(1).Kinematics.Global.Parameters('roty').AddExpression(
			self.root_leg_con.bones(1).Kinematics.Global.Parameters('roty').FullName
		) 
		self.root_leg.bones(1).Kinematics.Global.Parameters('rotz').AddExpression(
			self.root_leg_con.bones(1).Kinematics.Global.Parameters('rotz').FullName
		) 


		#---------------------------------------------------------------------
		# set neutral pose on leg joints

		# skeleton leg #
		for bone in self.root_leg.Bones:
			bone = dispatch(bone)
			# set the neutral pose #
			xsi.SetNeutralPose(bone, c.siSRT, False)
			
		# control leg #
		for bone in self.root_leg_con.Bones:
			bone = dispatch(bone)
			# set the neutral pose #
			xsi.SetNeutralPose(bone, c.siSRT, False)
			# key the rotations so they have something to blend back to initially #
			bone.Kinematics.Local.Parameters('rotx').AddFcurve2([0,0], c.siDefaultFCurve) 
			bone.Kinematics.Local.Parameters('roty').AddFcurve2([0,0], c.siDefaultFCurve) 
			bone.Kinematics.Local.Parameters('rotz').AddFcurve2([0,0], c.siDefaultFCurve)

		#---------------------------------------------------------------------
		# add transform setups to the leg 
		
		# thigh #
		self.root_leg_con.Bones(0).Kinematics.Local.RotX.AddFcurve2([0,0], c.siDefaultFCurve)
		self.root_leg_con.Bones(0).Kinematics.Local.RotY.AddFcurve2([0,0], c.siDefaultFCurve)
		self.root_leg_con.Bones(0).Kinematics.Local.RotZ.AddFcurve2([0,0], c.siDefaultFCurve)
		
		# add a transform setup to the con fingers #
		ts = self.root_leg_con.Bones(0).AddProperty('Transform Setup', False)
		ts = dispatch(ts)
		ts.tool.Value = 3
		ts.rotate.Value = 3
		ts.xaxis.Value = True
		ts.yaxis.Value = True
		ts.zaxis.Value = True
		
		# calf #
		self.root_leg_con.Bones(1).Kinematics.Local.RotX.AddFcurve2([0,0], c.siDefaultFCurve)
		self.root_leg_con.Bones(1).Kinematics.Local.RotY.AddFcurve2([0,0], c.siDefaultFCurve)
		self.root_leg_con.Bones(1).Kinematics.Local.RotZ.AddFcurve2([0,0], c.siDefaultFCurve)
		
		# add a transform setup to the con fingers #
		ts = self.root_leg_con.Bones(1).AddProperty('Transform Setup', False)
		ts = dispatch(ts)
		ts.tool.Value = 3
		ts.rotate.Value = 3
		ts.xaxis.Value = False
		ts.yaxis.Value = False
		ts.zaxis.Value = True
		
		#---------------------------------------------------------------------
		# draw the controls
		
		# foot con #
		self.con_foot 							= xsi.zCon()
		self.con_foot.type 						= 'sphere'
		self.con_foot.size 						= self.size_foot_con * self.parent.scale
		# self.con_foot.transform				 	= self.root_leg.effector.Kinematics.Global.Transform
		self.con_foot.transform.Translation 	= self.root_leg.effector.Kinematics.Global.Transform.Translation
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
		# self.con_ankle.transform			 	= self.root_leg.effector.Kinematics.Global.Transform
		self.con_ankle.transform.Translation 	= self.root_leg.effector.Kinematics.Global.Transform.Translation
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
		# knee_orient_aim.size.Value = 7

		# build the transform for the orientation aim null #
		trans = XSIMath.CreateTransform()
		trans.Translation = template.v_root
		# trans.Rotation =self.root_leg.Bones(0).Kinematics.Local.Transform.Rotation
		knee_orient_aim.Kinematics.Global.Transform = trans

		# aim the orientation #
		cns = knee_orient_aim.Kinematics.AddConstraint('Direction', self.con_ankle.node_hook, False)
		cns = dispatch(cns)
		knee_orient_aim.Kinematics.Global.Transform = self.root_leg.Kinematics.Global.Transform
		
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
		knee_orient_aim.Kinematics.AddConstraint('Position', self.root_leg_con, False)

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
		trans = self.root_leg.Kinematics.Global.Transform
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
		col.Add(self.root_leg_con)
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
		trans_knee_con.Translation = self.root_leg_con.Bones(1).Kinematics.Global.Transform.Translation
		
		# get the middle orientation #
		quat_leg1 	= self.root_leg_con.Bones(0).Kinematics.Global.Transform.Rotation.Quaternion
		quat_leg2 	= self.root_leg_con.Bones(1).Kinematics.Global.Transform.Rotation.Quaternion
		quat_mid	= XSIMath.CreateQuaternion()
		quat_mid.Slerp(quat_leg1, quat_leg2, 0.5)
		rot = XSIMath.CreateRotation()
		rot.Quaternion = quat_mid
		trans_knee_con.Rotation = rot
		
		# add the length of the leg joint to the local position in Y #
		trans_knee_con.AddLocalTranslation(
			XSIMath.CreateVector3(
				0, 
				self.root_leg_con.Bones(0).Length.Value, 
				0
			)
		)

		#---------------------------------------------------------------------
		# knee con #
		self.con_knee 						= xsi.zCon()
		self.con_knee.type 					= 'text:K'
		self.con_knee.size 					= self.size_knee_con
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
		self.root_leg_con.effector.Kinematics.AddConstraint('Pose', self.con_ankle.node_hook, True)
		
		# position constrain the root to the pelvis #
		if self.root_pelvis.Bones(0):
			self.root_leg_con.Kinematics.AddConstraint('Pose', self.root_pelvis.Bones(0), True)
			
		# constrain the chain up vectors #
		xsi.ApplyOp("SkeletonUpVector", "%s;%s" % \
					(self.root_leg_con.Bones(0), self.con_knee.node_hook), 3, 
					c.siPersistentOperation, "", 0)

		#---------------------------------------------------------------------
		# create the animation parameters
		self.prop_anim = self.con_foot.node_con.AddProperty(
			'CustomProperty', False, 'zAnim_Leg_%s' % self.parent.symmetry[0].upper()
		)
		self.prop_anim.AddParameter3('ShowKneeCon', c.siBool, False, None, None, True, False)
		self.prop_anim.AddParameter3('ShowFootCons', c.siBool, False, None, None, True, False)
		
		# add display info with proxy parameter #
		self.prop_anim_di = self.con_foot.node_con.AddProperty(
			'CustomProperty', False, 'DisplayInfo_zAnim_Leg_%s' % self.parent.symmetry[0].upper()
		)
		self.prop_anim_di.AddProxyParameter('%s.ShowKneeCon'  % self.prop_anim.Fullname)
		self.prop_anim_di.AddProxyParameter('%s.ShowFootCons' % self.prop_anim.Fullname)

		# hook up the parameters
		self.con_knee.node_con.Properties('Visibility').viewvis.AddExpression(self.prop_anim.ShowKneeCon.FullName)
		self.con_ankle.node_con.Properties('Visibility').viewvis.AddExpression(self.prop_anim.ShowFootCons.FullName)
		
		#---------------------------------------------------------------------
		# add the ik/fk switch
		self.ik_switch = self.prop_anim.AddParameter3('Fk/Ik', c.siFloat, 1, 0, 1, True, False)
		self.prop_anim_di.AddProxyParameter(self.ik_switch)

		# add the expressions #
		self.root_leg_con.Bones(0).Properties('Kinematic Chain').blendik.AddExpression(self.ik_switch.FullName)
		self.root_leg_con.Effector.Kinematics.Constraints(0).blendweight.AddExpression(self.ik_switch.FullName)
		
		# add proxy param to fk bones #
		for bone in self.root_leg_con.Bones:
			bone = dispatch(bone)
			di = bone.AddProperty('CustomProperty', False, 'DisplayInfo_zAnim_Leg_%s' % self.parent.symmetry[0].upper())
			di.AddProxyParameter(self.ik_switch, None, 'FK_IK')

		#---------------------------------------------------------------------
		# link the color of the FK controls to the IK_FK slider #

		# build the fk expression #
		expr_fk_r = ''
		expr_fk_g = ''
		expr_fk_b = ''
		if re.match(r'^left$', self.parent.symmetry, re.I):
			expr_fk_r = 'cond(%s.chain.blendik != 0.0, 0.0, 0.0)'  % self.root_leg_con.Bones(0).FullName
			expr_fk_g = 'cond(%s.chain.blendik != 0.0, 0.25, 1.0)' % self.root_leg_con.Bones(0).FullName
			expr_fk_b = 'cond(%s.chain.blendik != 0.0, 0.0, 0.0)'  % self.root_leg_con.Bones(0).FullName
		else:
			expr_fk_r = 'cond(%s.chain.blendik != 0.0, 0.25, 1.0)' % self.root_leg_con.Bones(0).FullName
			expr_fk_g = 'cond(%s.chain.blendik != 0.0, 0.0, 0.0)'  % self.root_leg_con.Bones(0).FullName
			expr_fk_b = 'cond(%s.chain.blendik != 0.0, 0.0, 0.0)'  % self.root_leg_con.Bones(0).FullName

		# build the ik expression #
		expr_ik_r = ''
		expr_ik_g = ''
		expr_ik_b = ''
		if re.match(r'^left$', self.parent.symmetry, re.I):
			expr_ik_r = 'cond(%s.chain.blendik != 1.0, 0.0, 0.0)'  % self.root_leg_con.Bones(0).FullName
			expr_ik_g = 'cond(%s.chain.blendik != 1.0, 0.25, 1.0)' % self.root_leg_con.Bones(0).FullName
			expr_ik_b = 'cond(%s.chain.blendik != 1.0, 0.0, 0.0)'  % self.root_leg_con.Bones(0).FullName
		else:
			expr_ik_r = 'cond(%s.chain.blendik != 1.0, 0.25, 1.0)' % self.root_leg_con.Bones(0).FullName
			expr_ik_g = 'cond(%s.chain.blendik != 1.0, 0.0, 0.0)'  % self.root_leg_con.Bones(0).FullName
			expr_ik_b = 'cond(%s.chain.blendik != 1.0, 0.0, 0.0)'  % self.root_leg_con.Bones(0).FullName

		# add the expression to the fk bones #
		for bone in self.root_leg_con.Bones:
			bone = dispatch(bone)
			bone.R.AddExpression(expr_fk_r)
			bone.G.AddExpression(expr_fk_g)
			bone.B.AddExpression(expr_fk_b)

		# add the expression to the controller #
		disp = self.con_foot.node_con.AddProperty('Display Property')
		disp = dispatch(disp)
		disp.wirecolorr.AddExpression(expr_ik_r)
		disp.wirecolorg.AddExpression(expr_ik_g)
		disp.wirecolorb.AddExpression(expr_ik_b)
		
		#---------------------------------------------------------------------
		# link the visbility on the controls to the ik fk switcher #
		
		# controller #
		self.con_foot.node_con.Properties('Visibility').viewvis.AddExpression(
			'cond(%s.chain.blendik != 0, 1, 0)' % self.root_leg_con.Bones(0).FullName
		)
		
		# fk #
		for bone in self.root_leg_con.Bones:
			bone = dispatch(bone)
			bone.Properties('Visibility').viewvis.AddExpression(
				'cond(%s.chain.blendik != 1, 1, 0)' % self.root_leg_con.Bones(0).FullName
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
			self.character_subset.AddNodeRot(self.root_leg_con.Bones(0))
			self.character_subset.AddNodeRot(self.root_leg_con.Bones(1))
			# con pos and rot #
			self.character_subset.AddNodePosRot(self.con_foot.node_con)
			self.character_subset.AddNodePosRot(self.con_knee.node_con)
			self.character_subset.AddNodePosRot(self.con_ankle.node_con)
		
		#---------------------------------------------------------------------
		# create a deformer stack #
		
		# create the deformer stack #
		node_dfm_parent = self.deformer_parent.AddNull(xsi.zMapName('%s1' % self.parent.basename, 'Custom:DfmPrnt', self.parent.symmetry))
		node_dfm_shadow = node_dfm_parent.AddNull(xsi.zMapName('%s1' % self.parent.basename, 'Custom:DfmShdw', self.parent.symmetry))
		leg1_env   = node_dfm_shadow.AddNull(xsi.zMapName('%s1' % self.parent.basename, 'Env', self.parent.symmetry))
		self.deformers.Add(leg1_env)
		
		node_dfm_parent.primary_icon.Value 	= 0
		node_dfm_parent.Properties('Visibility').Parameters('viewvis').Value = False
		node_dfm_parent.Properties('Visibility').Parameters('rendvis').Value = False
		node_dfm_shadow.primary_icon.Value 	= 0
		node_dfm_shadow.Properties('Visibility').Parameters('viewvis').Value = False
		node_dfm_shadow.Properties('Visibility').Parameters('rendvis').Value = False
		leg1_env.primary_icon.Value 		= 0
		leg1_env.Properties('Visibility').Parameters('viewvis').Value = False
		leg1_env.Properties('Visibility').Parameters('rendvis').Value = False
		
		node_dfm_parent.Kinematics.AddConstraint('Pose',self.root_leg, False)
		node_dfm_shadow.Kinematics.AddConstraint('Pose',self.root_leg.Bones(0), False)

		# create the deformer stack #
		node_dfm_parent = self.deformer_parent.AddNull(xsi.zMapName('%s2' % self.parent.basename, 'Custom:DfmPrnt', self.parent.symmetry))
		node_dfm_shadow = node_dfm_parent.AddNull(xsi.zMapName('%s2' % self.parent.basename, 'Custom:DfmShdw', self.parent.symmetry))
		leg2_env   = node_dfm_shadow.AddNull(xsi.zMapName('%s2' % self.parent.basename, 'Env', self.parent.symmetry))
		self.deformers.Add(leg2_env)
		
		node_dfm_parent.primary_icon.Value 	= 0
		node_dfm_parent.Properties('Visibility').Parameters('viewvis').Value = False
		node_dfm_parent.Properties('Visibility').Parameters('rendvis').Value = False
		node_dfm_shadow.primary_icon.Value 	= 0
		node_dfm_shadow.Properties('Visibility').Parameters('viewvis').Value = False
		node_dfm_shadow.Properties('Visibility').Parameters('rendvis').Value = False
		leg2_env.primary_icon.Value			= 0
		leg2_env.Properties('Visibility').Parameters('viewvis').Value = False
		leg2_env.Properties('Visibility').Parameters('rendvis').Value = False
		
		node_dfm_parent.Kinematics.AddConstraint('Pose',self.root_leg, False)
		node_dfm_shadow.Kinematics.AddConstraint('Pose',self.root_leg.Bones(1), False)
		
		#---------------------------------------------------------------------
		# add the deformers to the deformers group #
		if self.group_deformers:
			self.group_deformers = dispatch(self.group_deformers)
			self.group_deformers.AddMember(self.deformers)

#-----------------------------------------------------------------------------
# Commands
#-----------------------------------------------------------------------------
def zLeg_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	#oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments
	oArgs.Add('symmetry', c.siArgumentInput, 'left', c.siString)
	# oArgs.AddObjectArgument('model')

	return True
	
def zLeg_Execute(symmetry):
	# export the python object #
	import win32com.server
	return win32com.server.util.wrap(
		zLeg(symmetry)
	)
	
