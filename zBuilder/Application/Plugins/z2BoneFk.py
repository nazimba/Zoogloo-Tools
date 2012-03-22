"""
A 2 Bone Fk system.

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

temp_null = None
false = 0
true = 1

def XSILoadPlugin(in_reg):
	in_reg.Author = "Andy Buecker"
	in_reg.Name = "z2BoneFk"
	in_reg.Email = "andy@zoogloo.net"
	in_reg.URL = ""
	in_reg.Major = 1
	in_reg.Minor = 0

	in_reg.RegisterCommand('z2BoneFk', 'z2BoneFk')
	
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

#-----------------------------------------------------------------------------
# Classes
#-----------------------------------------------------------------------------

class z2BoneFk(object):
	'''
	XSI Class for building a 2 Bone Fk System.
	
	:IVariables:
		rig
		template
	
	'''
	# required for COM wrapper #
	_inputs_ = [
		'scale',
		'basename',
		'symmetry',
	]
	
	_outputs_ = [
		'rig',
		'template',
	]
	
	_public_methods_ = [
	]

	# define the output vars here #
	_public_attrs_ = []
	_public_attrs_ += _inputs_
	_public_attrs_ += _outputs_

	# define those attrs that are read only #
	_readonly_attrs_ = []
	_readonly_attrs_ += _outputs_

	# set the class variables #
	_template 		= None
	_rig 			= None
	uid				= 'dccf3648e3ef9b973c81a65c3f6b453c'
	basename		= '2BoneFk'
	scale			= 1
	
	def __init__(self, sym='left'):
		'''
		:Parameters:
		      sym : string
		        The symmetry name for the object.
		'''
		super(z2BoneFk, self).__init__()
		
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
				self._template = win32com.server.util.wrap(z2BoneFk_Template(self))
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
				self._rig = win32com.server.util.wrap(z2BoneFk_Rig(self))
			# return the private var #
			return dispatch(self._rig)
		def fset(self, value):
			raise Exception('Unable to modify rig value.')
		fdel = fset
		return locals()
			
				
class z2BoneFk_Template(object):
	"""docstring for z2BoneFk_Template"""
	
	_inputs_ = [
		'v_root', 
		'v_joint1', 
		'v_tip', 
		'defaults',
		'model',
		'scale',
		'use_transforms',
		't_root', 
		't_joint1', 
		't_tip', 
	]
	_outputs_ = [
		'parent',
	]
	
	# required for COM wrapper #
	_public_methods_ = [
		'Draw',
		'LoadDefaultValues',
		'GetFromScene',
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
		super(z2BoneFk_Template, self).__init__()
		
		# set the instance variables #
		self.parent			= parent
		
		# load the defaults #
		self.LoadDefaultValues()
	
	def LoadDefaultValues(self):
		"""
		Sets the default values 
		"""
		# create new vectors #
		self.v_root   	 	= XSIMath.CreateVector3(0, 0, 0)
		self.v_joint1 		= XSIMath.CreateVector3(0, 0.1, 1)
		self.v_tip   	 	= XSIMath.CreateVector3(0, 0, 2)

		# create new transforms #
		self.t_root   	 	= XSIMath.CreateTransform()
		self.t_joint1 		= XSIMath.CreateTransform()
		self.t_tip   	 	= XSIMath.CreateTransform()
		
		self.t_root.Translation 	= self.v_root  
		self.t_joint1.Translation 	= self.v_joint1
		self.t_tip.Translation 		= self.v_tip   

		if re.match(r'^right$', self.parent.symmetry, re.I):
			# symmetrize #
			self.v_root.X       *= -1
			self.v_joint1.X   	*= -1
			self.v_tip.X        *= -1
			
		# set the model #
		self.model 			= xsi.ActiveSceneRoot
		
		self.scale 			= 1
		self.use_transforms = False

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
			xsi.zMapName(
				'%s' % self.parent.basename,
				'Custom:Container', 
				self.parent.symmetry
			)
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
		node_root 	= node_parent.AddNull(
			xsi.zMapName(
				'%sRoot' % self.parent.basename, 
				'Custom:Tmp', 
				self.parent.symmetry
			)
		)
		node_root.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_root.AddProperty('CustomProperty', False, 'z%sRoot' % self.parent.basename)

		node_joint1	= node_parent.AddNull(
			xsi.zMapName(
				'%sJoint1' % self.parent.basename, 
				'Custom:Tmp', 
				self.parent.symmetry
			)
		)
		node_joint1.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_joint1.AddProperty('CustomProperty', False, 'z%sJoint1' % self.parent.basename)

		node_tip	= node_parent.AddNull(
			xsi.zMapName(
				'%sTip' % self.parent.basename, 
				'Custom:Tmp', 
				self.parent.symmetry
			)
		)
		node_tip.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_tip.AddProperty('CustomProperty', False, 'z%sTip' % self.parent.basename)
		
		#---------------------------------------------------------------------
		# set the positions #
		trans 		= XSIMath.CreateTransform()
		v_result 	= XSIMath.CreateVector3()
		
		v_result.Scale(self.parent.scale, self.v_root)
		trans.Translation = v_result
		node_root.Kinematics.Global.Transform = trans
		
		v_result.Scale(self.parent.scale, self.v_joint1)
		trans.Translation = v_result
		node_joint1.Kinematics.Global.Transform = trans

		v_result.Scale(self.parent.scale, self.v_tip)
		trans.Translation = v_result
		node_tip.Kinematics.Global.Transform = trans
		
		#---------------------------------------------------------------------
		# set the default orientations #
		cns = node_root.Kinematics.AddConstraint('Direction', node_joint1, False)
		cns = dispatch(cns)

		cns = node_joint1.Kinematics.AddConstraint('Direction', node_tip, False)
		cns = dispatch(cns)

		trans = node_tip.Kinematics.Global.Transform
		trans.Rotation = node_joint1.Kinematics.Global.Transform.Rotation
		node_tip.Kinematics.Global.Transform = trans
		
		#---------------------------------------------------------------------
		# add a visual upvector #
		node_upv						= node_parent.AddNull(xsi.zMapName('%sUpv' % self.parent.basename, 'Custom:Tmp', self.parent.symmetry))
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
		
		cns_upv							= node_upv.Kinematics.AddConstraint('Direction', node_tip, False)
		cns_upv							= dispatch(cns_upv)
		cns_upv.upvct_active.Value 		= True
		cns_upv.UpVectorReference		= node_joint1
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

			if node.Properties('z%sRoot' % self.parent.basename):
				self.v_root			= node.Kinematics.Global.Transform.Translation
				self.t_root			= node.Kinematics.Global.Transform
				
			elif node.Properties('z%sJoint1' % self.parent.basename):
				self.v_joint1		= node.Kinematics.Global.Transform.Translation
				self.t_joint1 		= node.Kinematics.Global.Transform
				
			elif node.Properties('z%sTip' % self.parent.basename):
				self.v_tip			= node.Kinematics.Global.Transform.Translation
				self.t_tip			= node.Kinematics.Global.Transform
				

				
		
class z2BoneFk_Rig(object):
	_inputs_ = [
		'controls_parent',  		
		# 'controls_constraint',  		
		'character_set',   		
		'skeleton_parent',  		
		'deformer_parent',  
		'size_finger_con',	
		'group_deformers',	
		'group_controls',	
		'inc_alpha',	
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
		super(z2BoneFk_Rig, self).__init__()
		
		# set the instance variables #
		self.parent					= parent

		# set the defaults for the input variables #
		for item in self._inputs_:
			setattr(self, item, None)
			
		# set specific types #
		self.deformers  = dispatch('XSI.Collection')
		self.inc_alpha	= True
		
		# set the default control size #
		self.size_finger_con = 1
	
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
		# draw the finger control chain #

		# calculate a default plane vector #
		v_plane = XSIMath.CreateVector3()
		v1		= XSIMath.CreateVector3()
		v2		= XSIMath.CreateVector3()
		# get vector from root to ankle #
		v1.Sub(template.v_root, template.v_joint1)
		# get vector from root to knee #
		v2.Sub(template.v_root, template.v_tip)
		# get the cross product #
		v_plane.Cross(v2, v1)
		
		# draw the skeleton #
		self.root_con = self.controls_parent.Add2DChain(
			template.v_root,
			template.v_joint1,
			v_plane,
			c.si2DChainNormalRadian
		)
		
		# rename #
		self.root_con.Name			= xsi.zMapName('%sCon' % self.parent.basename, 'ChainRoot', self.parent.symmetry)
		self.root_con.Bones(0).Name	= xsi.zMapName('%s' % self.parent.basename, 'Control', self.parent.symmetry, 0, self.inc_alpha)
		self.root_con.Effector.Name	= xsi.zMapName('%sCon' % self.parent.basename, 'ChainEff', self.parent.symmetry)
		
		# add another bone #
		self.root_con.AddBone(
			template.v_tip,
			c.siChainBonePin,
			xsi.zMapName('%s' % self.parent.basename, 'Control', self.parent.symmetry, 1, self.inc_alpha)
		)

		# force the control chain to fk #
		self.root_con.Bones(0).Properties('Kinematic Chain').Parameters('blendik').Value = 0

		# align the transforms if applicable #
		#  NOTE: This is a very hacky process.  For some reason, matching the kine.glocal.rotations through
		#        the object model produce incorrect result.  This gets past it all.
		#  TODO: Convert the fk structure over to a temp_null setup.  Since the bones are giving ius troubles,
		#        no need to cary the extra overhead.
		temp_null = xsi.ActiveSceneRoot.AddNull('TempWingNull')  # hack
		if self.parent.template.use_transforms:

			temp_null.Kinematics.Global.Transform = self.parent.template.t_root
			xsi.MatchTransform(self.root_con, temp_null, c.siRot, False)

			temp_null.Kinematics.Global.Transform = self.parent.template.t_root
			xsi.MatchTransform(self.root_con.Bones(0), temp_null, c.siRot, False)

			temp_null.Kinematics.Global.Transform = self.parent.template.t_joint1
			xsi.MatchTransform(self.root_con.Bones(1), temp_null, c.siRot, False)
			
			temp_null.Kinematics.Global.Transform = self.parent.template.t_tip
			xsi.MatchTransform(self.root_con.Effector, temp_null, c.siRot, False)
			
		# clean up the temp null #
		xsi.DeleteObj(temp_null)
		
		# format the chain #
		fmt = xsi.zChainFormatter(self.root_con)
		fmt.BoneDisplay = 6
		fmt.BoneSize	= self.size_finger_con * self.parent.scale
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
							self.root_con.Bones(1),
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
		
		# add to the controls group #
		if self.group_controls:
			self.group_controls.AddMember(self.root_con.Bones)
							
		#---------------------------------------------------------------------
		# add the pick walk and multi select to the fk properties #
		last_con 	= None
		last_prop 	= None
		for con in self.root_con.Bones:
			# add the property #
			prop = con.AddProperty('zPickWalk')
			prop = dispatch(prop)
			# add the previous (up) con #
			if last_con: prop.Up.Value = last_con.Name
			# add the next (down) con #
			if last_prop: last_prop.Down.Value = con.Name
			# set the last con #
			last_con = con
			# set the last prop #
			last_prop = prop

			# add the zMultiSelect #
			prop_multi = con.AddProperty('zMultiSelect')
			prop_multi = dispatch(prop_multi)
			prop_multi.Objects.Value = self.root_con.Bones.GetAsText().replace('%s.' % self.root_con.Model.Name, '')
			# prop_multi.Objects.Value = self.root_con.Bones.GetAsText()
			
		#---------------------------------------------------------------------
		# draw the skeleton chain #

		# draw the skeleton #
		self.root_skel = self.skeleton_parent.Add2DChain(
			template.v_root,
			template.v_joint1,
			v_plane,
			c.si2DChainNormalRadian
		)
		
		# rename #
		self.root_skel.Name				= xsi.zMapName('%s' % self.parent.basename, 'ChainRoot', self.parent.symmetry)
		self.root_skel.Bones(0).Name	= xsi.zMapName('%s' % self.parent.basename, 'ChainBone', self.parent.symmetry, 0, self.inc_alpha)
		self.root_skel.Effector.Name	= xsi.zMapName('%s' % self.parent.basename, 'ChainEff', self.parent.symmetry)
		
		# add another bone #
		self.root_skel.AddBone(
			template.v_tip,
			c.siChainBonePin,
			xsi.zMapName('%s' % self.parent.basename, 'ChainBone', self.parent.symmetry, 1, self.inc_alpha)
		)

		# format the chain #
		xsi.zChainFormatter(self.root_skel).Format()
		
		# set neutral pose #
		xsi.SetNeutralPose([self.root_skel.Bones(0),
							self.root_skel.Bones(1),
							self.root_skel.Effector], c.siSRT, False)
							
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
			node_dfm_parent = self.deformer_parent.AddNull(xsi.zMapName('%s' % self.parent.basename, 'Custom:DfmPrnt', self.parent.symmetry, b, self.inc_alpha))
			node_dfm_shadow = node_dfm_parent.AddNull(xsi.zMapName('%s' % self.parent.basename, 'Custom:DfmShdw', self.parent.symmetry, b, self.inc_alpha))
			node_env 		= node_dfm_shadow.AddNull(xsi.zMapName('%s' % self.parent.basename, 'Env', self.parent.symmetry, b, self.inc_alpha))
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
def z2BoneFk_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	#oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments
	oArgs.Add('symmetry', c.siArgumentInput, 'left', c.siString)
	return True
	
def z2BoneFk_Execute(symmetry):
	# export the python object #
	import win32com.server
	return win32com.server.util.wrap(
		z2BoneFk(symmetry)
	)


