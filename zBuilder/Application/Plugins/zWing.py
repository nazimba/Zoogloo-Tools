"""
zWing.py

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

alpha = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

xsi = Application
log = xsi.logmessage

null = None
false = 0
true = 1

def XSILoadPlugin(in_reg):
	in_reg.Author = "Andy Buecker"
	in_reg.Name = "zWing"
	in_reg.Email = "andy@zoogloo.net"
	in_reg.URL = ""
	in_reg.Major = 1
	in_reg.Minor = 0

	in_reg.RegisterCommand('zWing', 'zWing')
	
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

class zWing(object):

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
		'span_segments',
		'sub_spans',
	]
	# define those attrs that are read only #
	_readonly_attrs_ = [
		'rig',
		'template',
	]

	# set the class variables #
	_template 		= None
	_rig 			= None
	uid				= 'efa574cffe1c3e29d9de8d4ac78ca0f3'
	basename		= 'Wing'
	scale			= 1
	
	def __init__(self, sym='left'):
		super(zWing, self).__init__()
		
		# reset the instance varaibles #
		self._template	= None
		self._rig	  	= None
		
		self.symmetry		= sym
		self.span_segments	= 2
		self.sub_spans		= [2, 2, 1]
	
	@zProp
	def template():
		'''Template Accessor'''
		def fget(self):
			# create a template if it doesn't exist #
			if not self._template:
				# wrap a new class #
				self._template = win32com.server.util.wrap(zWing_Template(self))
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
				self._rig = win32com.server.util.wrap(zWing_Rig(self))
			# return the private var #
			return self._rig
		def fset(self, value):
			raise Exception('Unable to modify rig value.')
		fdel = fset
		return locals()
			
				
class zWing_Template(object):
	"""docstring for zWing_Template"""
	
	_inputs_ = [
		'v_shoulder', 
		'v_elbow', 
		'v_wrist', 
		'v_hand', 
		'v_spans',
		'v_subspans',
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
		super(zWing_Template, self).__init__()
		
		# set defaults to None #
		for item in self._public_attrs_:
			setattr(self, item, None)
		
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
		self.v_shoulder   	= XSIMath.CreateVector3(1.823, 0.000, -0.171)
		self.v_elbow      	= XSIMath.CreateVector3(8.065, 0.000, -1.082)
		self.v_wrist   		= XSIMath.CreateVector3(14.081, 0.000, -0.058)
		self.v_hand   		= XSIMath.CreateVector3(16.308, 0.000, -2.689)
		
		# set the model #
		self.model = xsi.ActiveSceneRoot

		# roots are the same as the aboce joints #
		v_span_roots = [
			XSIMath.CreateVector3(1.823, 0.000, -0.171),
			XSIMath.CreateVector3(8.065, 0.000, -1.082),
			XSIMath.CreateVector3(14.081, 0.000, -0.058),
			XSIMath.CreateVector3(14.081, 0.000, -0.058)
		]

		# a list of all the tips #
		v_span_tips = [
			XSIMath.CreateVector3(1.823, 0.000, -8.426),
			XSIMath.CreateVector3(8.065, 0.000, -11.245),
			XSIMath.CreateVector3(14.081, 0.000, -7.158),
			XSIMath.CreateVector3(18.669, 0.000, -5.477)
		]
	
		# generate a list of the span vectors #
		self.v_spans	= [None]*4
		for i in xrange(4):
			spans = []
			# set the root #
			spans.append(v_span_roots[i])
			# genrate the segments #
			# TODO: generate the span segments vectors from the number of span segments #
			log('Span Segments: %s' % self.parent.span_segments)
			for s in xrange(self.parent.span_segments-1):
				log('%s/%s' % (s+1, self.parent.span_segments))
				v = XSIMath.CreateVector3()
				v.Sub(v_span_tips[i], v_span_roots[i]) 			# get the vector from root to tip
				v.ScaleInPlace(float(s+1)/float(self.parent.span_segments))		# scale it by the current percentage
				v.AddInPlace(v_span_roots[i])							# add it to the root vector
				spans.append(v)												# append it to the list
			# set the tip #
			spans.append(v_span_tips[i])
			# add the spans list to the class vector spans list #
			self.v_spans[i] = spans
		
		# symmetrize #
		if re.match(r'^right$', self.parent.symmetry, re.I):
			self.v_shoulder.X   	*= -1
			self.v_elbow.X      	*= -1
			self.v_wrist.X   		*= -1
			self.v_hand.X   		*= -1
			
			for item in self.v_spans:
				for v in item:
					v.X				*= -1

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
		node_shoulder 	= node_parent.AddNull(xsi.zMapName('WingShoulder', 'Custom:Tmp', self.parent.symmetry))
		node_shoulder.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_shoulder.AddProperty('CustomProperty', False, 'zWingShoulder')
		node_shoulder.primary_icon.Value = 4
		node_shoulder.shadow_icon.Value = 1

		node_elbow	= node_parent.AddNull(xsi.zMapName('WingElbow', 'Custom:Tmp', self.parent.symmetry))
		node_elbow.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_elbow.AddProperty('CustomProperty', False, 'zWingElbow')
		node_elbow.primary_icon.Value = 4
		node_elbow.shadow_icon.Value = 1

		node_wrist	= node_parent.AddNull(xsi.zMapName('WingWrist', 'Custom:Tmp', self.parent.symmetry))
		node_wrist.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_wrist.AddProperty('CustomProperty', False, 'zWingWrist')
		node_wrist.primary_icon.Value = 4
		node_wrist.shadow_icon.Value = 1

		node_hand	= node_parent.AddNull(xsi.zMapName('WingHand', 'Custom:Tmp', self.parent.symmetry))
		node_hand.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_hand.AddProperty('CustomProperty', False, 'zWingHand')
		node_hand.primary_icon.Value = 4
		node_hand.shadow_icon.Value = 1

		#---------------------------------------------------------------------
		# add a visual upvector #
		node_upv						= node_parent.AddNull(xsi.zMapName(self.parent.basename, 'Custom:Tmp', self.parent.symmetry))
		node_upv.primary_icon.Value 	= 0
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

		#---------------------------------------------------------------------
		# create orientation nodes 
		node_orients = [None] * 4
		node_orients[0] = node_parent.AddNull(xsi.zMapName('WingSpan1', 'Custom:Orient', self.parent.symmetry))
		node_orients[0].Kinematics.AddConstraint('Position', node_shoulder, False)
		node_orients[0].Kinematics.AddConstraint('Orientation', node_upv, False)
		node_orients[0].Kinematics.AddConstraint('Direction', node_elbow, False)
		
		node_orients[1] = node_orients[0].AddNull(xsi.zMapName('WingSpan2', 'Custom:Orient', self.parent.symmetry))
		node_orients[1].Kinematics.AddConstraint('Position', node_elbow, False)
		node_orients[1].Kinematics.AddConstraint('Orientation', node_upv, False)
		node_orients[1].Kinematics.AddConstraint('Direction', node_wrist, False)

		node_orients[2] = node_orients[1].AddNull(xsi.zMapName('WingSpan3', 'Custom:Orient', self.parent.symmetry))
		node_orients[2].Kinematics.AddConstraint('Position', node_wrist, False)
		node_orients[2].Kinematics.AddConstraint('Orientation', node_upv, False)
		node_orients[2].Kinematics.AddConstraint('Direction', node_hand, False)

		node_orients[3] = node_orients[2].AddNull(xsi.zMapName('WingSpan4', 'Custom:Orient', self.parent.symmetry))
		node_orients[3].Kinematics.AddConstraint('Position', node_wrist, False)
		node_orients[3].Kinematics.AddConstraint('Orientation', node_upv, False)
		node_orients[3].Kinematics.AddConstraint('Direction', node_hand, False)
		
		for node in node_orients:
			node.Properties('Visibility').Parameters('viewvis').Value = 0
			node.Properties('Visibility').Parameters('rendvis').Value = 0

		#---------------------------------------------------------------------
		# create middler nodes 
		node_mids = [None] * 4
		node_mids[0] = node_orients[0].AddNull(xsi.zMapName('WingSpan1', 'Custom:Mdlr', self.parent.symmetry))

		node_mids[1] = node_orients[1].AddNull(xsi.zMapName('WingSpan2', 'Custom:Mdlr', self.parent.symmetry))
		node_mids[1].Kinematics.Local.RotY.AddExpression('%s.kine.local.roty * -0.5' % node_orients[1].FullName)

		node_mids[2] = node_orients[2].AddNull(xsi.zMapName('WingSpan3', 'Custom:Mdlr', self.parent.symmetry))
		node_mids[2].Kinematics.Local.RotY.AddExpression('%s.kine.local.roty * -0.5' % node_orients[2].FullName)

		node_mids[3] = node_orients[3].AddNull(xsi.zMapName('WingSpan4', 'Custom:Mdlr', self.parent.symmetry))

		for node in node_mids:
			node.Properties('Visibility').Parameters('viewvis').Value = 0
			node.Properties('Visibility').Parameters('rendvis').Value = 0
			
		#---------------------------------------------------------------------
		# create a root node for each span #
		node_span_roots = [None] * 4
		node_span_roots[0] = node_mids[0].AddNull(xsi.zMapName('WingSpan1', 'Custom:Root', self.parent.symmetry))
		node_span_roots[1] = node_mids[1].AddNull(xsi.zMapName('WingSpan2', 'Custom:Root', self.parent.symmetry))
		node_span_roots[2] = node_mids[2].AddNull(xsi.zMapName('WingSpan3', 'Custom:Root', self.parent.symmetry))
		node_span_roots[3] = node_mids[3].AddNull(xsi.zMapName('WingSpan4', 'Custom:Root', self.parent.symmetry))
		for node in node_span_roots:
			node.primary_icon.Value = 5
			node.size.Value 		= 2
		
		# create a list to hold the span nodes #
		node_spans	= [None]*4
		for i in xrange(4):
			node_spans[i] = [None] * (self.parent.span_segments+1)
		
		# create the span nodes #
		for i in xrange(4):
			for s in xrange(self.parent.span_segments+1):
				node = node_span_roots[i].AddNull(xsi.zMapName('WingSpan%d' % (i+1), 'Custom:Tmp', self.parent.symmetry, s, True))
				node.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
				node.AddProperty('CustomProperty', False, 'zWingSpan%d%s' % ((i+1), alpha[s]))
				
				# add them to the list #
				node_spans[i][s] = node
		
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

		# set the span nodes #
		for i in xrange(4):
			for s in xrange(self.parent.span_segments+1):
				# get the node from the spans list #
				node = node_spans[i][s]
				# set the position #
				v_result.Scale(self.parent.scale, self.v_spans[i][s])
				trans.Translation = v_result
				node.Kinematics.Global.Transform = trans
				

		
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
			if node.Properties('zWingShoulder'):
				self.v_shoulder		= node.Kinematics.Global.Transform.Translation
			elif node.Properties('zWingElbow'):
				self.v_elbow		= node.Kinematics.Global.Transform.Translation
			elif node.Properties('zWingWrist'):
				self.v_wrist		= node.Kinematics.Global.Transform.Translation
			elif node.Properties('zWingHand'):
				self.v_hand			= node.Kinematics.Global.Transform.Translation
				
		# set the span nodes #
		for i in xrange(4):
			for s in xrange(self.parent.span_segments+1):
				# get the node from the spans list #
				for node in child_nodes:
					if node.Properties('zWingSpan%d%s' % ((i+1), alpha[s])):
						self.v_spans[i][s] = node.Kinematics.Global.Transform.Translation
						break
		
		
class zWing_Rig(object):

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
		'size_span_cons',
		'group_deformers',		
		'group_controls',		
		'node_do_not_touch',		
		'ribbon_path',		
		'root_skel_wingspan',		
		'root_con_wingspans',		
	]
	_outputs_ = [
		'parent',
		'character_subset',
		'root_skel_hand',
		'root_skel_arm',
		'root_con_hand',
		'root_con_arm',
		'root_skel_subspans',
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
		super(zWing_Rig, self).__init__()
		
		# set the instance variables #
		self.parent					= parent

		# set the defaults for the input variables #
		for item in self._inputs_:
			setattr(self, item, None)
			
		# set specific types #
		self.deformers = dispatch('XSI.Collection')
		
		# set the default controller sizes #
		self.size_elbow_con			= 1
		self.size_wrist_con			= 2
		self.size_hand_con			= 2.25
		self.size_arm_fk_cons		= 2
		self.size_hand_fk_cons		= 2		
		self.size_span_cons			= 1		

		self.skeleton_parent 	= xsi.ActiveSceneRoot
		self.controls_parent 	= xsi.ActiveSceneRoot
		self.deformer_parent 	= xsi.ActiveSceneRoot
		self.node_world_ref		= xsi.ActiveSceneRoot  
		self.node_do_not_touch	= xsi.ActiveSceneRoot
		
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
		
		# get the template #
		template = dispatch(self.parent.template)
		
		# setup the symmetry switches #
		left 	= True
		right 	= False
		if re.match(r'^right$', self.parent.symmetry, re.I):
			left 	= False
			right 	= True
		
		#---------------------------------------------------------------------
		# draw the wing control chain #
		
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
		self.root_con_arm = self.controls_parent.Add2DChain(
			template.v_shoulder,
			template.v_elbow,
			v_plane,
			c.si2DChainNormalRadian
		)
		
		# rename #
		self.root_con_arm.Name			= xsi.zMapName('%sCon' % self.parent.basename, 'ChainRoot', self.parent.symmetry)
		self.root_con_arm.Bones(0).Name	= xsi.zMapName('%sFk' % self.parent.basename, 'Control', self.parent.symmetry, 1)
		self.root_con_arm.Effector.Name	= xsi.zMapName('%sCon' % self.parent.basename, 'ChainEff', self.parent.symmetry)
		
		# add another bone #
		self.root_con_arm.AddBone(
			template.v_wrist,
			c.siChainBonePin,
			xsi.zMapName('%sFk' % self.parent.basename, 'Control', self.parent.symmetry, 2)
		)

		# format the chain #
		fmt = xsi.zChainFormatter(self.root_con_arm)
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
		xsi.SetNeutralPose([self.root_con_arm.Bones(0),
							self.root_con_arm.Bones(1),
							self.root_con_arm.Effector], c.siSRT, False)

		# set a default key on the rotation of the bones #
		for bone in self.root_con_arm.Bones:
			bone = dispatch(bone)
			bone.Kinematics.Local.RotX.AddFcurve2([0,0], c.siDefaultFCurve)
			bone.Kinematics.Local.RotY.AddFcurve2([0,0], c.siDefaultFCurve)
			bone.Kinematics.Local.RotZ.AddFcurve2([0,0], c.siDefaultFCurve)
			
		# constrain the control chain to the clavicle skeleton #
		self.skeleton_parent = dispatch(self.skeleton_parent)
		self.root_con_arm.Kinematics.AddConstraint('Pose', self.skeleton_parent, True)
		
		# add to the group controls #
		if self.group_controls:
			self.group_controls.AddMember(self.root_con_arm.Bones)
			
		# add a transform setup to each bone #
		for bone in self.root_con_arm.Bones:

			# add the property #
			ts = bone.AddProperty('Transform Setup')
			ts = dispatch(ts)

			# change it to rotate mode #
			ts.tool.Value = 3

			# translate the mode #
			ts.rotate.Value = 3

		#---------------------------------------------------------------------
		# draw the arm skeleton #
		self.root_skel_arm = self.skeleton_parent.Add2DChain(
			template.v_shoulder,
			template.v_elbow,
			v_plane,
			c.si2DChainNormalRadian
		)
		
		# rename #
		self.root_skel_arm.Name				= xsi.zMapName('Wing', 'ChainRoot', self.parent.symmetry)
		self.root_skel_arm.Bones(0).Name	= xsi.zMapName('Wing', 'ChainBone', self.parent.symmetry, 1)
		self.root_skel_arm.Effector.Name	= xsi.zMapName('Wing', 'ChainEff', self.parent.symmetry)
		
		# add another bone #
		self.root_skel_arm.AddBone(
			template.v_wrist,
			c.siChainBonePin,
			xsi.zMapName('Wing', 'ChainBone', self.parent.symmetry, 2)
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
			self.root_con_arm.bones(0).Kinematics.Global.Parameters('rotx').FullName
		) 
		self.root_skel_arm.bones(0).Kinematics.Global.Parameters('roty').AddExpression(
			self.root_con_arm.bones(0).Kinematics.Global.Parameters('roty').FullName
		) 
		self.root_skel_arm.bones(0).Kinematics.Global.Parameters('rotz').AddExpression(
			self.root_con_arm.bones(0).Kinematics.Global.Parameters('rotz').FullName
		) 

		self.root_skel_arm.bones(1).Kinematics.Global.Parameters('rotx').AddExpression(
			self.root_con_arm.bones(1).Kinematics.Global.Parameters('rotx').FullName
		) 
		self.root_skel_arm.bones(1).Kinematics.Global.Parameters('roty').AddExpression(
			self.root_con_arm.bones(1).Kinematics.Global.Parameters('roty').FullName
		) 
		self.root_skel_arm.bones(1).Kinematics.Global.Parameters('rotz').AddExpression(
			self.root_con_arm.bones(1).Kinematics.Global.Parameters('rotz').FullName
		) 
		
		#---------------------------------------------------------------------
		# draw the hand control chain #

		# draw the skeleton #
		self.root_con_hand = self.root_con_arm.Effector.Add2DChain(
			template.v_wrist,
			template.v_hand,
			v_plane,
			c.si2DChainNormalRadian
		)
		
		# rename #
		self.root_con_hand.Name				= xsi.zMapName('HandCon', 'ChainRoot', self.parent.symmetry)
		self.root_con_hand.Bones(0).Name	= xsi.zMapName('HandFk', 'Control', self.parent.symmetry, 1)
		self.root_con_hand.Effector.Name	= xsi.zMapName('HandCon', 'ChainEff', self.parent.symmetry)
		
		# format the chain #
		fmt = xsi.zChainFormatter(self.root_con_hand)
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
		xsi.SetNeutralPose([self.root_con_arm.Bones(0),
							self.root_con_arm.Bones(1),
							self.root_con_arm.Effector], c.siSRT, False)

		# set a default key on the rotation of the bones #
		for bone in self.root_con_hand.Bones:
			bone = dispatch(bone)
			bone.Kinematics.Local.RotX.AddFcurve2([0,0], c.siDefaultFCurve)
			bone.Kinematics.Local.RotY.AddFcurve2([0,0], c.siDefaultFCurve)
			bone.Kinematics.Local.RotZ.AddFcurve2([0,0], c.siDefaultFCurve)
			
		# add to the group controls #
		if self.group_controls:
			self.group_controls.AddMember(self.root_con_hand.Bones)
		
		# add a transform setup to each bone #
		for bone in self.root_con_hand.Bones:

			# add the property #
			ts = bone.AddProperty('Transform Setup')
			ts = dispatch(ts)

			# change it to rotate mode #
			ts.tool.Value = 3

			# translate the mode #
			ts.rotate.Value = 3

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
			self.root_con_hand.bones(0).Kinematics.Global.Parameters('rotx').FullName
		) 
		self.root_skel_hand.bones(0).Kinematics.Global.Parameters('roty').AddExpression(
			self.root_con_hand.bones(0).Kinematics.Global.Parameters('roty').FullName
		) 
		self.root_skel_hand.bones(0).Kinematics.Global.Parameters('rotz').AddExpression(
			self.root_con_hand.bones(0).Kinematics.Global.Parameters('rotz').FullName
		) 

		#---------------------------------------------------------------------
		# draw the WRIST con

		# redispatch the body con #
		if self.con_body:
			self.con_body = dispatch(self.con_body)
		else:
			self.con_body = xsi.zCon()
			self.con_body.basename = 'Body'
			self.con_body.Draw()

		# create the wrist controller #
		self.con_wrist 							= xsi.zCon()
		self.con_wrist.type 					= '4_pin'
		self.con_wrist.size 					= self.size_wrist_con * self.parent.scale
		self.con_wrist.transform.Translation	= self.root_con_arm.Effector.Kinematics.Global.Transform.Translation
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
		trans = self.root_con_hand.Bones(0).Kinematics.Global.Transform
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
		self.con_hand.transform					= self.root_con_hand.Bones(0).Kinematics.Global.Transform
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
		cns_hand_pos = self.con_hand.node_rest.Kinematics.AddConstraint('Pose', self.root_con_arm.Effector, True)
		# self.con_body = dispatch(self.con_body)
		# cns_hand_ori = self.con_hand.node_rest.Kinematics.AddConstraint('Pose', self.con_body.node_hook, True)
		# cns_hand_ori = dispatch(cns_hand_ori)
		# cns_hand_ori.cnspos.Value = False

		#---------------------------------------------------------------------
		# draw the ELBOW con

		# calculate the elbow position #
		trans = self.root_con_arm.Bones(1).Kinematics.Global.Transform
		# get the middle rotation between the bones #
		quat_1 = self.root_con_arm.Bones(0).Kinematics.Global.Transform.Rotation.Quaternion
		quat_2 = self.root_con_arm.Bones(1).Kinematics.Global.Transform.Rotation.Quaternion
		quat_mid = XSIMath.CreateQuaternion()
		quat_mid.Slerp(quat_1, quat_2, 0.5)
		# put the mid quat in the transform #
		rot = XSIMath.CreateRotation()
		rot.Quaternion = quat_mid
		trans.Rotation = rot
		# move the position out by the length of the arm #
		trans.AddLocalTranslation(
			XSIMath.CreateVector3(0, self.root_con_arm.Bones(0).length.Value*2, 0)
		)
		# set the default orientation to world 0 #
		trans.Rotation = XSIMath.CreateRotation()

		# create the elbow controller #
		self.con_elbow 							= xsi.zCon()
		self.con_elbow.type 					= 'text:E'
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
		self.root_con_arm.Effector.Kinematics.AddConstraint('Pose', self.con_wrist.node_hook, True)
		
		# hand bone #
		cns_hand_con = self.root_con_hand.Bones(0).Kinematics.AddConstraint('Pose', self.con_hand.node_hook, True)
		cns_hand_con = dispatch(cns_hand_con)
		
		# up vector #
		xsi.ApplyOp("SkeletonUpVector", "%s;%s" % \
					(self.root_con_arm.Bones(0), self.con_elbow.node_hook), 3, 
					c.siPersistentOperation, "", 0)

		#---------------------------------------------------------------------
		# add ik/fk switch to arm con #
		# create the property #
		self.prop_anim = self.con_wrist.node_con.AddProperty('CustomProperty', False, 'zAnim')
		self.prop_anim = dispatch(self.prop_anim)
		
		# add the parameter #
		param_ikfk = self.prop_anim.AddParameter3('FK_IK', c.siFloat, 1.0, 0.0, 1.0)
		
		# hook up the blend ik slider #
		self.root_con_arm.Bones(0).Properties('Kinematic Chain').Parameters('blendik').AddExpression(param_ikfk.FullName)
		
		# hook up the hand constraint blend #
		# cns_hand_ori.blendweight.AddExpression(param_ikfk.FullName)
		cns_hand_con.blendweight.AddExpression(param_ikfk.FullName)
		
		# add a HUD #
		self.prop_anim_di = self.con_wrist.node_con.AddProperty('CustomProperty', False, 'DisplayInfo_zAnim')
		self.prop_anim_di.AddProxyParameter(param_ikfk, None, 'FK_IK')
	
		# add proxy's to the other arm controllers #
		col_fk = dispatch('XSI.Collection')
		col_fk.AddItems(self.root_con_arm.Bones)
		col_fk.AddItems(self.root_con_hand.Bones)
		col_fk.Add(self.con_hand.node_con)
		col_fk.Add(self.con_elbow.node_con)
		for item in col_fk:
			prop_anim = item.AddProperty('CustomProperty', False, 'zAnim')
			prop_anim.AddProxyParameter(param_ikfk, None, 'FK_IK')

			prop_anim_di = item.AddProperty('CustomProperty', False, 'DisplayInfo_zAnim')
			prop_anim_di.AddProxyParameter(param_ikfk, None, 'FK_IK')
		
		#---------------------------------------------------------------------
		# link the color of the FK controls to the IK_FK slider #

		# build the fk expression #
		expr_fk_r = 'cond(%s.chain.blendik != 0.0, 0.0, 0.0)'  % self.root_con_arm.Bones(0).FullName
		expr_fk_g = 'cond(%s.chain.blendik != 0.0, 0.25, 1.0)' % self.root_con_arm.Bones(0).FullName
		expr_fk_b = 'cond(%s.chain.blendik != 0.0, 0.0, 0.0)'  % self.root_con_arm.Bones(0).FullName
		if right:
			expr_fk_r = 'cond(%s.chain.blendik != 0.0, 0.25, 1.0)' % self.root_con_arm.Bones(0).FullName
			expr_fk_g = 'cond(%s.chain.blendik != 0.0, 0.0, 0.0)'  % self.root_con_arm.Bones(0).FullName
			expr_fk_b = 'cond(%s.chain.blendik != 0.0, 0.0, 0.0)'  % self.root_con_arm.Bones(0).FullName

		# build the ik expression #
		expr_ik_r = 'cond(%s.chain.blendik != 1.0, 0.0, 0.0)'  % self.root_con_arm.Bones(0).FullName
		expr_ik_g = 'cond(%s.chain.blendik != 1.0, 0.25, 1.0)' % self.root_con_arm.Bones(0).FullName
		expr_ik_b = 'cond(%s.chain.blendik != 1.0, 0.0, 0.0)'  % self.root_con_arm.Bones(0).FullName
		if right:
			expr_ik_r = 'cond(%s.chain.blendik != 1.0, 0.25, 1.0)' % self.root_con_arm.Bones(0).FullName
			expr_ik_g = 'cond(%s.chain.blendik != 1.0, 0.0, 0.0)'  % self.root_con_arm.Bones(0).FullName
			expr_ik_b = 'cond(%s.chain.blendik != 1.0, 0.0, 0.0)'  % self.root_con_arm.Bones(0).FullName

		# add the expression to the fk bones #
		for bone in self.root_con_arm.Bones:
			bone = dispatch(bone)
			bone.R.AddExpression(expr_fk_r)
			bone.G.AddExpression(expr_fk_g)
			bone.B.AddExpression(expr_fk_b)
		self.root_con_hand.Bones(0).R.AddExpression(expr_fk_r)
		self.root_con_hand.Bones(0).G.AddExpression(expr_fk_g)
		self.root_con_hand.Bones(0).B.AddExpression(expr_fk_b)

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
			'cond(%s.chain.blendik != 0, 1, 0)' % self.root_con_arm.Bones(0).FullName
		)
		self.con_wrist.node_con.Properties('Visibility').viewvis.AddExpression(
			'cond(%s.chain.blendik != 0, 1, 0)' % self.root_con_arm.Bones(0).FullName
		)
		self.con_elbow.node_con.Properties('Visibility').viewvis.AddExpression(
			'cond(%s.chain.blendik != 0, 1, 0)' % self.root_con_arm.Bones(0).FullName
		)
		
		# fk #
		for bone in self.root_con_arm.Bones:
			bone = dispatch(bone)
			bone.Properties('Visibility').viewvis.AddExpression(
				'cond(%s.chain.blendik != 1, 1, 0)' % self.root_con_arm.Bones(0).FullName
			)
			
		self.root_con_hand.Bones(0).Properties('Visibility').viewvis.AddExpression(
			'cond(%s.chain.blendik != 1, 1, 0)' % self.root_con_arm.Bones(0).FullName
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
		# add a span visibility switch #
		param_spans = self.prop_anim.AddParameter3('ShowSpans', c.siBool, False)
		self.prop_anim_di.AddProxyParameter(param_spans, None, 'Show_Spans')
		prop = self.con_hand.node_con.Properties('zAnim')
		if prop:
			prop.AddProxyParameter(param_spans, None, 'Show_Spans')
		prop_di = self.con_hand.node_con.Properties('DisplayInfo_zAnim')
		if prop_di:
			prop_di.AddProxyParameter(param_spans, None, 'Show_Spans')
		
		#---------------------------------------------------------------------
		# create span root nodes #
		node_span_roots = [None] * 4
		for b in xrange(4):
			# get the bone #
			if b < 2:
				bone = self.root_con_arm.Bones(b)
			else:
				bone = self.root_con_hand.Bones(0)
			# add a null #
			node = bone.AddNull(xsi.zMapName('WingSpan%s' % (b+1), 'Custom:Root', self.parent.symmetry))
			node.Kinematics.Global.Transform = bone.Kinematics.Global.Transform
			# hide the node #
			xsi.zHide(node)
			# add it to the list #
			node_span_roots[b] = node
			log('%s %s' % (b, node_span_roots[b]))
			
		#---------------------------------------------------------------------
		# create middling nodes #
		node_span_mids = [None] * 4
		for b in xrange(4):
			# get the bone #
			if b < 2:
				bone = self.root_con_arm.Bones(b)
			else:
				bone = self.root_con_hand.Bones(0)
			# add a null #
			node = node_span_roots[b].AddNull(xsi.zMapName('WingSpan%s' % (b+1), 'Custom:Mdlr', self.parent.symmetry))
			xsi.zHide(node)
			node.Kinematics.Global.Transform = bone.Kinematics.Global.Transform
			# add the constraint #
			if b < 3:
				# node.Kinematics.Local.RotZ.AddExpression('%s.kine.local.rotz * -0.5' % bone.FullName)
				# xsi.zApplyMiddler(node, bone, bone.Parent)
				cns = node.Kinematics.AddConstraint('Pose', bone.Parent, False)
				cns = dispatch(cns)
				cns.cnspos.Value = False
				cns = node.Kinematics.AddConstraint('Pose', bone, False)
				cns = dispatch(cns)
				cns.cnspos.Value = False
				cns.blendweight.Value = 0.5
				
			# add it to the list #
			node_span_mids[b] = node
		
		
		#---------------------------------------------------------------------
		# add the wingspans
		
		self.root_con_wingspans = []

		# control chain #
		for i in xrange(len(template.v_spans)):
			# calculate the plane vector #
			v_plane = XSIMath.CreateVector3()
			v1		= XSIMath.CreateVector3()
			v2		= XSIMath.CreateVector3()
			# get vector from root to tip #
			v1.Sub(template.v_spans[i][len(template.v_spans[i])-1], template.v_spans[i][0])
			# get vector from root to next #
			v2.Sub(template.v_spans[i][1], template.v_spans[i][0])
			# get the cross product #
			v_plane.Cross(v1, v2)
			
			# draw the skeleton #
			root_con = node_span_mids[i].Add2DChain(
				template.v_spans[i][0],
				template.v_spans[i][1],
				v_plane,
				c.si2DChainNormalRadian
			)

			# rename #
			root_con.Name			= xsi.zMapName('WingSpanCon%d' % (i+1), 'ChainRoot', self.parent.symmetry)
			root_con.Bones(0).Name	= xsi.zMapName('WingSpanFk%d' % (i+1), 'Control', self.parent.symmetry, 0, True)
			root_con.Effector.Name	= xsi.zMapName('WingSpanCon%s' % (i+1), 'ChainEff', self.parent.symmetry)

			# add bones #
			for s in xrange(len(template.v_spans[i])):
				# skip the first two #
				if s < 2: continue
				
				# add the bone #
				root_con.AddBone(
					template.v_spans[i][s],
					c.siChainBonePin,
					xsi.zMapName('WingSpanFk%d' % (i+1), 'Control', self.parent.symmetry, s-1, True)
				)
				
			# format the chain #
			fmt = xsi.zChainFormatter(root_con)
			fmt.BoneDisplay = 11
			fmt.BonePrimary = 7
			fmt.BoneSize	= self.size_span_cons * self.parent.scale
			if left:
				fmt.SetBoneColor(0, 1, 0, True)
			else:
				fmt.SetBoneColor(1, 0, 0, True)

			fmt.RootDisplay = 0
			fmt.RootSize	= self.parent.scale
			if left:
				fmt.SetRootColor(0, 1, 0, True)
			else:
				fmt.SetRootColor(1, 0, 0, True)

			fmt.EffDisplay 	= 0
			fmt.EffSize		= self.parent.scale
			if left:
				fmt.SetEffColor(0, 1, 0, True)
			else:
				fmt.SetEffColor(1, 0, 0, True)

			fmt.EffLastBone	= True
			fmt.Format()	
			
			# set chain to fk #
			root_con.Bones(0).Properties('Kinematic Chain').Parameters('blendik').Value = 0			
			
			# add it to the list #
			self.root_con_wingspans.append(root_con)
			
			# add a transform setup to each bone #
			for root in self.root_con_wingspans:
				for bone in root.Bones:

					# add the property #
					ts = bone.AddProperty('Transform Setup')
					ts = dispatch(ts)
	
					# change it to rotate mode #
					ts.tool.Value = 3

					# translate the mode #
					ts.rotate.Value = 3
					
			# link the visibility to the spans switch #
			for bone in root_con.Bones:
				bone.Properties('Visibility').Parameters('Viewvis').AddExpression(param_spans)

				# add a proxy parameter to the bone #
				prop_anim 		= bone.AddProperty('CustomProperty', False, 'zAnim')
				prop_anim_di 	= bone.AddProperty('CustomProperty', False, 'DisplayInfo_zAnim')
				prop_anim.AddProxyParameter(param_spans, None, 'ShowSpans')
				prop_anim_di.AddProxyParameter(param_spans, None, 'ShowSpans')
				
		#---------------------------------------------------------------------
		# add the wingspans

		self.root_skel_wingspan = []

		# control chain #
		for i in xrange(len(template.v_spans)):
			# calculate the plane vector #
			v_plane = XSIMath.CreateVector3()
			v1		= XSIMath.CreateVector3()
			v2		= XSIMath.CreateVector3()
			# get vector from root to tip #
			v1.Sub(template.v_spans[i][len(template.v_spans[i])-1], template.v_spans[i][0])
			# get vector from root to next #
			v2.Sub(template.v_spans[i][1], template.v_spans[i][0])
			# get the cross product #
			v_plane.Cross(v1, v2)

			# determine the subspan skeleton's parent bone #
			node_skel_parent = None
			if i < 2:
				node_skel_parent = self.root_skel_arm.Bones(i)
				node_skel_parent = self.root_skel_arm.Bones(i)
			else:
				node_skel_parent = self.root_skel_hand.Bones(0)
				
			# draw the skeleton #
			root_skel = node_skel_parent.Add2DChain(
				template.v_spans[i][0],
				template.v_spans[i][1],
				v_plane,
				c.si2DChainNormalRadian
			)
			
			# rename #
			root_skel.Name			= xsi.zMapName('WingSpan%s' % (i+1), 'ChainRoot', self.parent.symmetry)
			root_skel.Bones(0).Name	= xsi.zMapName('WingSpan%s' % (i+1), 'ChainBone', self.parent.symmetry, 0, True)
			root_skel.Effector.Name	= xsi.zMapName('WingSpan%s' % (i+1), 'ChainEff', self.parent.symmetry)

			# add bones #
			for s in xrange(len(template.v_spans[i])):
				# skip the first two #
				if s < 2: continue

				# add the bone #
				root_skel.AddBone(
					template.v_spans[i][s],
					c.siChainBonePin,
					xsi.zMapName('WingSpan%d' % (i+1), 'ChainBone', self.parent.symmetry, s-1, True)
				)

			# format the chain #
			fmt = xsi.zChainFormatter(root_skel)
			fmt.Format()
			
			# # pose constrain it to the middler node #
			# root_skel.Kinematics.AddConstraint('Pose', node_span_mids[i], True)

			# add it to the list #
			self.root_skel_wingspan.append(root_skel)
	
			# hook up the skel to the control arm #
			# Note: constraints + bones don't mix, but expressions do! #
			for b in xrange(root_skel.Bones.Count):
				root_skel.Bones(b).Kinematics.Global.Parameters('rotx').AddExpression(
					self.root_con_wingspans[i].Bones(b).Kinematics.Global.Parameters('rotx').FullName
				) 
				root_skel.Bones(b).Kinematics.Global.Parameters('roty').AddExpression(
					self.root_con_wingspans[i].Bones(b).Kinematics.Global.Parameters('roty').FullName
				) 
				root_skel.Bones(b).Kinematics.Global.Parameters('rotz').AddExpression(
					self.root_con_wingspans[i].Bones(b).Kinematics.Global.Parameters('rotz').FullName
				) 
				
		#---------------------------------------------------------------------
		# add the wingsubspans

		# create a node to hold all the do not touch wing nodes #
		node_wing_dnt = self.node_do_not_touch.AddNull(
			xsi.zMapName('Wing', 'Custom:DoNotTouch', self.parent.symmetry)
		)
		xsi.zHide(node_wing_dnt)

		# create a list to hold all the subspan skeletons #
		self.root_skel_subspans = [None] * len(self.parent.sub_spans)
		for i in xrange(len(self.parent.sub_spans)):
			self.root_skel_subspans[i] = [None] * self.parent.sub_spans[i]
		
		# predefine the lists #
		for g in xrange(len(self.parent.sub_spans)):
			
			# get the current subspan #
			sub_spans = self.parent.sub_spans[g]
			
			# create a branch node to hold the subspan #
			node_con_branch = node_wing_dnt.AddNull(
				xsi.zMapName('WingSubSpan%s' % alpha[g], 'Branch', self.parent.symmetry)
			)
			xsi.zHide(node_con_branch)
			log('Branch node: %s' % node_con_branch)

			# pre build a list to hold the root nodes #
			nodes_root_subs = [None] * sub_spans
			for i in xrange(sub_spans):
				nodes_root_subs[i] = [None] * (self.parent.span_segments+1)
		
			# build the sub spans nodes #
			for i in xrange(sub_spans):
				
				log('Building locators for sub span group %s' % (i+1))
				
				# create positional locators for the sub spans #
				node_loc = node_con_branch.AddNull(
					xsi.zMapName('WingSubSpan%s%s' % (alpha[g], (i+1)), 'Custom:Loc', self.parent.symmetry, 0, True)
				)
				xsi.zHide(node_loc)
				# constrain the root #
				col = dispatch('XSI.Collection')
				col.Add(self.root_con_wingspans[g])
				col.Add(self.root_con_wingspans[g+1])
				cns = node_loc.Kinematics.AddConstraint('TwoPoints', col, False)
				cns = dispatch(cns)
				# calculate the percentage #
				cns.perc.Value = float(i+1)/float(sub_spans+1)*100
				# add the null to the list #
				nodes_root_subs[i][0] = node_loc
			
				# step through create locators for all the segments #
				for s in xrange(self.parent.span_segments):
					# skip the first one #
					if s == 0: continue

					node_segment_loc = node_con_branch.AddNull(
						xsi.zMapName('WingSubSpan%s%s' % (alpha[g], (i+1)), 'Custom:Loc', self.parent.symmetry, s, True)
					)
					xsi.zHide(node_segment_loc)
					# create a two point constratint constraint #
					col = dispatch('XSI.Collection')
					col.Add(self.root_con_wingspans[g].Bones(s))
					col.Add(self.root_con_wingspans[g+1].Bones(s))
					cns = node_segment_loc.Kinematics.AddConstraint('TwoPoints', col, False)
					cns = dispatch(cns)
					# calculate the percentage #
					cns.perc.Value = float(i+1)/float(sub_spans+1)*100
					# add the null to the list #
					nodes_root_subs[i][s] = node_segment_loc

				# build the effector #
				node_tip_loc = node_con_branch.AddNull(
					xsi.zMapName('WingSubSpan%s%s' % (alpha[g], (i+1)), 'Custom:Loc', self.parent.symmetry, self.parent.span_segments, True)
				)
				xsi.zHide(node_tip_loc)
				# two point constrain the effectors #
				col = dispatch('XSI.Collection')
				col.Add(self.root_con_wingspans[g].Effector)
				col.Add(self.root_con_wingspans[g+1].Effector)
				cns = node_tip_loc.Kinematics.AddConstraint('TwoPoints', col, False)
				cns = dispatch(cns)
				# calculate the percentage #
				cns.perc.Value = float(i+1)/float(sub_spans+1)*100
				# add the null to the list #
				nodes_root_subs[i][-1] = node_tip_loc
				
			#---------------------------------------------------------------------
			# draw the skeletons for the subspans #
			for i in xrange(len(nodes_root_subs)):
			
				# calculate the plane vector #
				v_plane = XSIMath.CreateVector3()
				v1		= XSIMath.CreateVector3()
				v2		= XSIMath.CreateVector3()
				# get vector from root to tip #
				v1.Sub(
					nodes_root_subs[i][-1].Kinematics.Global.Transform.Translation, 
					nodes_root_subs[i][0].Kinematics.Global.Transform.Translation
				)
				# get vector from root to next #
				v2.Sub(
					nodes_root_subs[i][1].Kinematics.Global.Transform.Translation, 
					nodes_root_subs[i][0].Kinematics.Global.Transform.Translation
				)
				# get the cross product #
				v_plane.Cross(v1, v2)

				# determine the subspan skeleton's parent bone #
				node_skel_parent = None
				if g < 2:
					node_skel_parent = self.root_skel_arm.Bones(g)
					node_skel_parent = self.root_skel_arm.Bones(g)
				else:
					node_skel_parent = self.root_skel_hand.Bones(0)
					
				# draw the skeleton #
				root = node_skel_parent.Add2DChain(
					nodes_root_subs[i][0].Kinematics.Global.Transform.Translation,
					nodes_root_subs[i][1].Kinematics.Global.Transform.Translation,
					v_plane,
					c.si2DChainNormalRadian
				)
			
				# rename #
				root.Name			= xsi.zMapName('WingSubSpan%s%s' % (alpha[g], (i+1)), 'ChainRoot', self.parent.symmetry)
				root.Bones(0).Name	= xsi.zMapName('WingSubSpan%s%s' % (alpha[g], (i+1)), 'ChainBone', self.parent.symmetry, 0, True)
				root.Effector.Name	= xsi.zMapName('WingSubSpan%s%s' % (alpha[g], (i+1)), 'ChainEff', self.parent.symmetry)
			
				# make the chain fk #
				root.Bones(0).Properties('Kinematic Chain').Parameters('blendik').Value = 0
			
				# constrain root position to the root node #
				root.Kinematics.AddConstraint('Position', nodes_root_subs[i][0], False)
				# constrain direction of first bone to the next node #
				root.Bones(0).Kinematics.AddConstraint('Direction', nodes_root_subs[i][1], False)
			
				# add an expression for the rotation in x #
				expr_str = '(%s.kine.local.rotx * %s) + (%s.kine.local.rotx * %s)' % (
					self.root_con_wingspans[0].Bones(0).FullName,
					float(i)/float(sub_spans+1),					
					self.root_con_wingspans[1].Bones(0).FullName,					
					float(sub_spans-i)/float(sub_spans+1)					
				)
				root.Bones(0).Kinematics.Local.RotX.AddExpression(expr_str)

				for s in xrange(len(nodes_root_subs[i])):
					# skip the first 2 #
					if s < 2: continue
				
					# add another bone #
					bone = root.AddBone(
						nodes_root_subs[i][s].Kinematics.Global.Transform.Translation,
						c.siChainBonePin,
						xsi.zMapName('WingSubSpan%s%s' % (alpha[g], (i+1)), 'ChainBone', self.parent.symmetry, s-1, True)
					)
				
					# constrain the bone direction to the next node #
					bone.Kinematics.AddConstraint('Direction', nodes_root_subs[i][s], False)
				
					# add an expression for the rotation in x #
					expr_str = '(%s.kine.local.rotx * %s) + (%s.kine.local.rotx * %s)' % (
						self.root_con_wingspans[0].Bones(s-1).FullName,
						float((sub_spans+1)-(i+1))/float(sub_spans+1),					
						self.root_con_wingspans[1].Bones(s-1).FullName,					
						float(i+1)/float(sub_spans+1)
					)
					bone.Kinematics.Local.RotX.AddExpression(expr_str)

				# format the chain #
				fmt = xsi.zChainFormatter(root)
				fmt.Format()
				
				# add the root to the subspan skeleton list #
				self.root_skel_subspans[g][i] = root
			
		#---------------------------------------------------------------------
		# create a deformer stack #

		# create a list to hold all the deformer node #
		list_deformers = []
		
		# add the wingspans #
		for root in self.root_skel_wingspan:
			for bone in root.Bones:
				list_deformers.append(bone)

		# add the subspans #
		for g in xrange(len(self.root_skel_subspans)):
			for root in self.root_skel_subspans[g]:
				for bone in root.Bones:
					list_deformers.append(bone)

		# step throuh each item in the list #
		for item in list_deformers:
			
			# get just the name #
			name = item.Name.split('_')[0]
			
			# create the nulls #
			node_dfm_parent = self.deformer_parent.AddNull(
				xsi.zMapName(name, 'Custom:DfmPrnt', self.parent.symmetry)
			)
			node_dfm_shadow = node_dfm_parent.AddNull(
				xsi.zMapName(name, 'Custom:DfmShdw', self.parent.symmetry)
			)
			node_env 		= node_dfm_shadow.AddNull(
				xsi.zMapName(name, 'Env', self.parent.symmetry, 1)
			)
			self.deformers.Add(node_env)
		
			# hide the nodes #
			xsi.zHide(node_dfm_parent, True)
			xsi.zHide(node_dfm_shadow, True)
			xsi.zHide(node_env, False)
			
			# contrain to corresponding nodes #
			node_dfm_parent.Kinematics.AddConstraint('Pose', item.Parent, False)
			node_dfm_shadow.Kinematics.AddConstraint('Pose', item, False)

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
				xsi.zMapName(self.parent.basename, 'None', self.parent.symmetry)
			)
			
			# add the parameters #
			self.character_subset.AddNodeRot(self.root_con_arm.Bones(0))
			self.character_subset.AddNodeRot(self.root_con_arm.Bones(1))
			self.character_subset.AddNodeRot(self.root_con_hand.Bones(0))
			self.character_subset.AddNodeRot(self.con_hand.node_con)
			self.character_subset.AddNodePos(self.con_wrist.node_con)
			self.character_subset.AddNodePosRot(self.con_elbow.node_con)
			for root in self.root_con_wingspans:
				for bone in root.Bones:
					self.character_subset.AddNodeRot(bone)
			self.character_subset.AddParams(param_ikfk)
			self.character_subset.AddParams(param_link_world)
			self.character_subset.AddParams(param_spans)
			
		# # for setup purposes only #
		# # report the class attributes #
		# for key in self.__dict__:
		# 	log(key)

			
			
#-----------------------------------------------------------------------------
# Commands
#-----------------------------------------------------------------------------
def zWing_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	#oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments
	oArgs.Add('symmetry', c.siArgumentInput, 'left', c.siString)
	return True
	
def zWing_Execute(symmetry):
	# export the python object #
	import win32com.server
	return win32com.server.util.wrap(
		zWing(symmetry)
	)
	
