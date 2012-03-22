"""
zAllFingers.py

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
	in_reg.Name = "zAllFingers"
	in_reg.Email = "andy@zoogloo.net"
	in_reg.URL = ""
	in_reg.Major = 1
	in_reg.Minor = 1

	in_reg.RegisterCommand('zAllFingers', 'zAllFingers')
	
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

class zAllFingers(object):

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
	uid				= 'e1be8bf9c28713442bef0982396b1585'
	basename		= 'Fing'
	scale			= 1
	
	def __init__(self, sym='left'):
		super(zAllFingers, self).__init__()
		
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
				self._template = win32com.server.util.wrap(zAllFingers_Template(self))
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
				self._rig = win32com.server.util.wrap(zAllFingers_Rig(self))
			# return the private var #
			return self._rig
		def fset(self, value):
			raise Exception('Unable to modify rig value.')
		fdel = fset
		return locals()
			
				
class zAllFingers_Template(object):
	"""docstring for zAllFingers_Template"""
	
	_inputs_ = [
		'surface_transform', 
		'joint_transforms', 
		'num_fingers', 
		'num_segments', 
		'surface', 
		'markers',
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

	def __init__(self, parent):
		super(zAllFingers_Template, self).__init__()
		
		# set the instance variables #
		self.parent			= parent
		self.scale 			= 1
		self.model 			= None
		
		# load the defaults #
		self.LoadDefaultValues()
	
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

	def LoadDefaultValues(self):
		"""
		Sets the default values 
		"""
		# set the defaults #
		self.surface_transform	= XSIMath.CreateTransform()
		self.num_fingers		= 4
		self.num_segments		= 3
		
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
		prop.AddParameter3('ContainerNumFingers', c.siUInt2, self.num_fingers)
		prop.AddParameter3('ContainerNumSegments', c.siUInt2, self.num_segments)
		
		#---------------------------------------------------------------------
		# create a nurbs surface guide #
		self.surface = xsi.CreatePrim(
			"Grid", 
			"NurbsSurface", 
			xsi.zMapName('%sGuide' % self.parent.basename, 'Custom:Surf', self.parent.symmetry),
			node_parent
		)
		self.surface.subdivu = self.num_fingers - 1
		self.surface.subdivv = self.num_segments
		
		#---------------------------------------------------------------------
		# create nulls for the home position #

		# create a temporary list to hold all the finger nodes #
		nodes = [None]*self.num_fingers
		for i in xrange(len(nodes)):
			nodes[i] = ['a'] * (self.num_segments+1)
			
		for f in xrange(self.num_fingers):
			# create an organizational node to hold all the fingers manips #
			node_org = node_parent.AddNull(
				xsi.zMapName('%s%d' % (self.parent.basename, (f+1)), 'Branch', self.parent.symmetry)
			)
			node_org.primary_icon.Value = 0
			node_org.Properties('Visibility').Parameters('viewvis').Value = False
			node_org.Properties('Visibility').Parameters('rendvis').Value = False
			
			# step through all the segments #
			for s in xrange(self.num_segments+1):

				# create the home null #
				node_home = node_org.AddNull(
					xsi.zMapName('%s%d' % (self.parent.basename, (f+1)), 'Home', self.parent.symmetry, s, True)
				)

				# add the surface constraint #
				cns = node_home.Kinematics.AddConstraint('Surface', self.surface, False)
				cns = dispatch(cns)
				cns.posu = 1 - (float(f)/float(self.num_fingers-1))
				cns.posv = float(s)/float(self.num_segments)

				# turn off the home null display #
				node_home.primary_icon.Value = 0
				node_home.Properties('Visibility').Parameters('viewvis').Value = False
				node_home.Properties('Visibility').Parameters('rendvis').Value = False

				# create a manipulator #
				node_manip = node_home.AddNull(
					xsi.zMapName('%s%d' % (self.parent.basename, (f+1)), 'Custom:Tmp', self.parent.symmetry, s, True)
				)

				# match the position #
				node_manip.Kinematics.Global.Transform = node_home.Kinematics.Global.Transform

				# create properties #
				node_manip.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
				node_manip.AddProperty('CustomProperty', False, 'zFingAll%d%s' % (f+1, alpha[s]))

				# add the manip to the temp list #
				nodes[f][s] = node_manip
					
		# create a visual cue for the upvector #
		for f in xrange(len(nodes)):
			node_upv = nodes[f][0].parent.parent.AddNull(
				xsi.zMapName('%s%d' % (self.parent.basename, (f+1)), 'UpVector', self.parent.symmetry)
			)
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

			# constrain the direction to the last node #
			cns_upv							= node_upv.Kinematics.AddConstraint('Direction', nodes[f][len(nodes[f])-1], False)
			cns_upv							= dispatch(cns_upv)
			cns_upv.upvct_active.Value 		= True
			cns_upv.UpVectorReference		= nodes[f][1]
			cns_upv.upx						= 0
			cns_upv.upy						= 0
			cns_upv.upz						= 1
			
			# constrain it's position to the first node #
			cns_pos							= node_upv.Kinematics.AddConstraint('Position', nodes[f][0], False)
			
		
		# change the tip icons to spheres #
		for f in xrange(len(nodes)):
			nodes[f][len(nodes[f])-1].primary_icon.Value 	= 2
			nodes[f][len(nodes[f])-1].size.Value 			= 0.5

		# constrain each joint to point at the next (except the tip)#
		for f in xrange(self.num_fingers):
			for s in xrange(self.num_segments):
				nodes[f][s].Kinematics.AddConstraint('Direction', nodes[f][s+1])

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
				if node.Properties('zContainer').Parameters('ContainerUID').Value 	== self.parent.uid \
				and node.Properties('zContainer').Parameters('ContainerSym').Value 	== self.parent.symmetry.lower() \
				and node.Properties('zContainer').Parameters('ContainerName').Value == self.parent.basename:
					node_parent = node
					break
		# make sure we have the container #
		if not node_parent:
			raise Exception('Unable to find template container by id: %s and name: %s' % (self.parent.uid, type_name))
		
		# get the number of fingers and segments
		self.num_fingers 	= node_parent.Properties('zContainer').Parameters('ContainerNumFingers').Value
		self.num_segments	= node_parent.Properties('zContainer').Parameters('ContainerNumSegments').Value
		
		#---------------------------------------------------------------------
		# get all the nodes ending in '_TMP' under the container #
		child_nodes = node_parent.FindChildren('*_Tmp')

		#---------------------------------------------------------------------
		# get the vectors or transform #
		
		# build the empty list for marker transforms #
		self.joint_transforms = [None] * self.num_fingers
		for i in xrange(self.num_fingers):
			self.joint_transforms[i] = [XSIMath.CreateTransform()] * (self.num_segments + 1)
		
		for f in xrange(self.num_fingers):
			for s in xrange(self.num_segments+1):
				for node in child_nodes:
					for prop in node.Properties:
						if re.match(r'^zFing.*%d%s$' % ((f+1), alpha[s]), prop.Name, re.I):
						# if node.Properties('zFingAll%d%s' % ((f+1), alpha[s])):
							# store the transform in the dictionary #
							self.joint_transforms[f][s]  = node.Kinematics.Global.Transform
							# v = self.joint_transforms[f][s].Translation
							# log('-> %s %s %s' % (v.X, v.Y, v.Z))
							break
							
		# make sure we found all the nodes #
		if len(self.joint_transforms) != self.num_fingers or \
		len(self.joint_transforms[0]) != (self.num_segments+1):
			raise Exception('Unable to locate all the template markers.')
		
class zAllFingers_Rig(object):

	_inputs_ = [
		'controls_parent',  		
		'character_set',   		
		'skeleton_parent',  		
		'deformer_parent',  
		'size_finger_con',	
		'group_deformers',	
		'group_controls',	
	]
	_outputs_ = [
		'parent',
		'deformers',
		'root_finger_cons',
		'root_finger_skels',
		'character_subset',			
	]
	# required for COM wrapper #
	_public_methods_ = [
		'LoadDefaultValues',
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
		super(zAllFingers_Rig, self).__init__()
		
		# set the instance variables #
		self.parent					= parent

		# set the defaults for the input variables #
		for item in self._inputs_:
			setattr(self, item, None)
			
		# set specific types #
		self.deformers = dispatch('XSI.Collection')
		
		# set the default control size #
		self.size_finger_con = 1
		
		# load the default values #
		self.LoadDefaultValues()
	
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

	def LoadDefaultValues(self):
		
		self.skeleton_parent = xsi.ActiveSceneRoot
		self.controls_parent = xsi.ActiveSceneRoot
		self.deformer_parent = xsi.ActiveSceneRoot

	def Build(self):
		#---------------------------------------------------------------------
		# pre conditions
		
		# make sure we have the skeleton_parent #
		if not self.skeleton_parent:
			raise Exception(
				'.rig.skeleton_parent is not defined.'
			)
		self.skeleton_parent = dispatch(self.skeleton_parent)
		
		# make sure we have the controls_parent #
		if not self.controls_parent:
			raise Exception(
				'.rig.controls_parent is not defined.'
			)
		self.controls_parent = dispatch(self.controls_parent)
		
		# make sure we have the deformer_parent #
		if not self.deformer_parent:
			raise Exception(
				'.rig.deformer_parent is not defined.'
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
		
		# create a list to hold all the finger roots #
		self.root_finger_cons 	= [None] * template.num_fingers
		self.root_finger_skels 	= [None] * template.num_fingers
		
		for f in xrange(template.num_fingers):

			v_root 	= dispatch(template.joint_transforms[f][0]).Translation
			v_tip 	= dispatch(template.joint_transforms[f][len(template.joint_transforms[f])-1]).Translation
			v_next 	= dispatch(template.joint_transforms[f][1]).Translation

			# calculate a default plane vector #
			v_plane = XSIMath.CreateVector3()
			v1		= XSIMath.CreateVector3()
			v2		= XSIMath.CreateVector3()
			# get vector from root to first joint #
			v1.Sub(v_root, v_next)
			# get vector from root to tip #
			v2.Sub(v_root, v_tip)
			# get the cross product #
			v_plane.Cross(v2, v1)
		
			# draw the skeleton #
			self.root_finger_cons[f] = self.controls_parent.Add2DChain(
				v_root,
				v_next,
				v_plane,
				c.si2DChainNormalRadian
			)

			# rename #
			self.root_finger_cons[f].Name			= xsi.zMapName('%s%sCon' % (self.parent.basename, (f+1)), 'ChainRoot', self.parent.symmetry)
			self.root_finger_cons[f].Bones(0).Name	= xsi.zMapName('%s%s' % (self.parent.basename, (f+1)), 'Control', self.parent.symmetry, 0, True)
			self.root_finger_cons[f].Effector.Name	= xsi.zMapName('%s%sCon' % (self.parent.basename, (f+1)), 'ChainEff', self.parent.symmetry)
			
			# add other bone segments #
			for s in xrange(template.num_segments+1):
				
				# skip over the first to segments
				if s < 2: continue
				
				# get the vector of the next joint #
				v_next_bone = dispatch(template.joint_transforms[f][s]).Translation
				
				# draw the bone #
				self.root_finger_cons[f].AddBone(
					v_next_bone,
					c.siChainBonePin,
					xsi.zMapName('%s%s' % (self.parent.basename, (f+1)), 'Control', self.parent.symmetry, s-1, True)
				)

			# format the chain #
			fmt = xsi.zChainFormatter(self.root_finger_cons[f])
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
			freeze_list = []
			for bone in self.root_finger_cons[f].Bones:
				freeze_list.append(bone)
			freeze_list.append(self.root_finger_cons[f].Effector)
			xsi.SetNeutralPose(freeze_list, c.siSRT, False)

			# set a default key on the rotation of the bones #
			for bone in self.root_finger_cons[f].Bones:
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
			self.root_finger_cons[f].Kinematics.AddConstraint('Pose', self.skeleton_parent, True)

			# add to the controls group #
			if self.group_controls:
				self.group_controls.AddMember(self.root_finger_cons[f].Bones)

			#---------------------------------------------------------------------
			# add the pick walk and multi select to the fk properties #
			last_con 	= None
			last_prop 	= None
			for con in self.root_finger_cons[f].Bones:
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
				prop_multi.Objects.Value = self.root_finger_cons[f].Bones.GetAsText().replace('%s.' % self.root_finger_cons[f].Model.Name, '')

			#---------------------------------------------------------------------
			# draw the finger skeleton chain #

			# draw the skeleton #
			self.root_finger_skels[f] = self.skeleton_parent.Add2DChain(
				v_root,
				v_next,
				v_plane,
				c.si2DChainNormalRadian
			)
			
			# rename #
			self.root_finger_skels[f].Name			= xsi.zMapName('%s%s' % (self.parent.basename, (f+1)), 'ChainRoot', self.parent.symmetry)
			self.root_finger_skels[f].Bones(0).Name	= xsi.zMapName('%s%s' % (self.parent.basename, (f+1)), 'ChainBone', self.parent.symmetry, 0, True)
			self.root_finger_skels[f].Effector.Name	= xsi.zMapName('%s%s' % (self.parent.basename, (f+1)), 'ChainEff', self.parent.symmetry)

			# add another bone #
			# add other bone segments #
			for s in xrange(template.num_segments+1):
				
				# skip over the first to segments
				if s < 2: continue
				
				# get the vector of the next joint #
				v_next_bone = dispatch(template.joint_transforms[f][s]).Translation
				
				# draw the bone #
				self.root_finger_skels[f].AddBone(
					v_next_bone,
					c.siChainBonePin,
					xsi.zMapName('%s%s' % (self.parent.basename, (f+1)), 'ChainBone', self.parent.symmetry, s-1, True)
				)

			# format the chain #
			xsi.zChainFormatter(self.root_finger_skels[f]).Format()

			# set neutral pose #
			freeze_list = []
			for bone in self.root_finger_skels[f].Bones:
				freeze_list.append(bone)
			freeze_list.append(self.root_finger_skels[f].Effector)
			xsi.SetNeutralPose(freeze_list, c.siSRT, False)

			#---------------------------------------------------------------------
			# link the skel to the control chain #
			# Note: constraints + bones don't mix, but expressions do! #
			for b in xrange(self.root_finger_skels[f].Bones.Count):
				self.root_finger_skels[f].bones(b).Kinematics.Global.Parameters('rotx').AddExpression(
					self.root_finger_cons[f].bones(b).Kinematics.Global.Parameters('rotx').FullName
				) 
				self.root_finger_skels[f].bones(b).Kinematics.Global.Parameters('roty').AddExpression(
					self.root_finger_cons[f].bones(b).Kinematics.Global.Parameters('roty').FullName
				) 
				self.root_finger_skels[f].bones(b).Kinematics.Global.Parameters('rotz').AddExpression(
					self.root_finger_cons[f].bones(b).Kinematics.Global.Parameters('rotz').FullName
				) 

			#---------------------------------------------------------------------
			# create a deformer stack #

			for b in xrange(self.root_finger_skels[f].Bones.Count):
				# finger #
				node_dfm_parent = self.deformer_parent.AddNull(xsi.zMapName('%s%s' % (self.parent.basename, (f+1)), 'Custom:DfmPrnt', self.parent.symmetry, b, True))
				node_dfm_shadow = node_dfm_parent.AddNull(xsi.zMapName('%s%s' % (self.parent.basename, (f+1)), 'Custom:DfmShdw', self.parent.symmetry, b, True))
				node_env 		= node_dfm_shadow.AddNull(xsi.zMapName('%s%s' % (self.parent.basename, (f+1)), 'Env', self.parent.symmetry, b, True))
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

				node_dfm_parent.Kinematics.AddConstraint('Pose', self.root_finger_skels[f].Bones(b).Parent, False)
				node_dfm_shadow.Kinematics.AddConstraint('Pose', self.root_finger_skels[f].Bones(b), False)

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
				for b in xrange(self.root_finger_cons[f].Bones.Count):
					# add the parameters #
					self.character_subset.AddNodeRot(self.root_finger_cons[f].Bones(b))

		#---------------------------------------------------------------------
		# add the deformers to the deformers group #
		if self.group_deformers:
			self.group_deformers = dispatch(self.group_deformers)
			self.group_deformers.AddMember(self.deformers)


		# # for setup purposes only #
		# # report the class attributes #
		# for key in self.__dict__:
		# 	log(key)

#-----------------------------------------------------------------------------
# Commands
#-----------------------------------------------------------------------------
def zAllFingers_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	#oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments
	oArgs.Add('symmetry', c.siArgumentInput, 'left', c.siString)
	return True
	
def zAllFingers_Execute(symmetry):
	# export the python object #
	import win32com.server
	return win32com.server.util.wrap(
		zAllFingers(symmetry)
	)
	
