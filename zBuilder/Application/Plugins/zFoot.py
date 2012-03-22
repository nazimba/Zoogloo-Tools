"""
zFoot.py

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
	in_reg.Name = "zFoot"
	in_reg.Email = "andy@zoogloo.net"
	in_reg.URL = ""
	in_reg.Major = 1
	in_reg.Minor = 1

	# in_reg.RegisterProperty('zFoot')

	in_reg.RegisterCommand('zFoot', 'zFoot')

	# in_reg.RegisterMenu(c.siMenuTbAnimateActionsStoreID, 'zFootMenu', False)
	
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
# Commands
#-----------------------------------------------------------------------------
def zFoot_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	#oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments
	oArgs.Add('symmetry', c.siArgumentInput, 'left', c.siString)
	#oArgs.AddObjectArgument('model')

	return True

def zFoot_Execute(symmetry):
	# export the python object #
	import win32com.server
	return win32com.server.util.wrap(
		zFoot(symmetry)
	)
	
	
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

class zFoot(object):

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
	_readonly_attrs_ = [
		'rig',
		'template',
	]

	# set the class variables #
	uid				= '5c4088413d078fb6a7f703b35a9a5dc7'
	
	def __init__(self, symmetry='left'):
		super(zFoot, self).__init__()
		
		# reset the instance varaibles #
		self._template 		= None
		self._rig		 	= None
		
		self.basename		= 'Foot'
		self.scale			= 1
		self.symmetry		= symmetry
	
	@zProp
	def template():
		'''Template Accessor'''
		def fget(self):
			# create a template if it doesn't exist #
			if not self._template:
				# wrap a new class #
				self._template = dispatch(win32com.server.util.wrap(zFoot_Template(self)))
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
				self._rig = dispatch(win32com.server.util.wrap(zFoot_Rig(self)))
			# return the private var #
			return self._rig
		def fset(self, value):
			raise Exception('Unable to modify rig value.')
		fdel = fset
		return locals()
			
				
class zFoot_Template(object):
	"""docstring for zFoot_Template"""
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
		
		'v_ankle',
		'v_heel',
		'v_ball',
		'v_toe',
	]    
	# defv_toe  ine those attrs that are read only #
	_readonly_attrs_ = [
		'parent'
	]

	def __init__(self, parent):
		super(zFoot_Template, self).__init__()
		
		# set the instance variables #
		self.parent		= parent
		self.model 		= None
		
		# load the default values #
		self.LoadDefaultValues()
	
	def LoadDefaultValues(self):
		"""Sets the default values for the template"""
		self.v_ankle	= XSIMath.CreateVector3(2.580, 3.454, 0.216)
		self.v_ball 	= XSIMath.CreateVector3(3.290, 0.986, 2.343)
		self.v_toe  	= XSIMath.CreateVector3(4.063, 0.495, 4.761)
		self.v_heel		= XSIMath.CreateVector3(2.052, 0.454, -1.739)
		if re.match(r'^right$', self.parent.symmetry, re.I): # right #
			self.v_ankle.X	*= -1
			self.v_ball.X 	*= -1
			self.v_toe.X  	*= -1
			self.v_heel.X	*= -1

		# set the default model #
		self.model = xsi.ActiveSceneRoot
			
	def Draw(self):
		"""docstring for Draw"""
		
		#---------------------------------------------------------------------
		# get the model #
		if not self.model:
			raise Exception('Model attribute for template not specified.')
		
		# dispatch the model #
		self.model = dispatch(self.model)
		
		#---------------------------------------------------------------------
		# create a node to hold the template #
		node_parent = self.model.AddNull('Foot_%s_Container' % self.parent.symmetry[0].upper())
		node_parent.primary_icon.Value = 0
		node_parent.Properties('Visibility').Parameters('viewvis').Value = False
		node_parent.Properties('Visibility').Parameters('rendvis').Value = False
		node_parent.AddProperty('CustomProperty', False, 'zBuilderTemplateItem')
		prop = node_parent.AddProperty('CustomProperty', False, 'zContainer')
		prop = dispatch(prop)
		prop.AddParameter3('ContainerName', c.siString, 'Foot')
		prop.AddParameter3('ContainerSym', c.siString, self.parent.symmetry)
		prop.AddParameter3('ContainerUID', c.siString, self.parent.uid)
		
		# draw the nodes #
		node_ankle 	= node_parent.AddNull(xsi.zMapName('FootAnkle', 'Custom:Tmp', self.parent.symmetry))
		node_ball 	= node_parent.AddNull(xsi.zMapName('FootBall', 'Custom:Tmp', self.parent.symmetry))
		node_toe 	= node_parent.AddNull(xsi.zMapName('FootToe', 'Custom:Tmp', self.parent.symmetry))
		node_heel 	= node_parent.AddNull(xsi.zMapName('FootHeel', 'Custom:Tmp', self.parent.symmetry))
		
		# tag the nodes #
		node_ankle.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_ankle.AddProperty('CustomProperty', False, 'zFootAnkle')
		
		node_ball.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_ball.AddProperty('CustomProperty', False, 'zFootBall')
		
		node_toe.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_toe.AddProperty('CustomProperty', False, 'zFootToe')
		
		node_heel.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')
		node_heel.AddProperty('CustomProperty', False, 'zFootHeel')
		
		#---------------------------------------------------------------------
		# set the positions #
		trans = XSIMath.CreateTransform()
		v_result = XSIMath.CreateVector3()
		
		# ankle #
		v_result.Scale(self.parent.scale, self.v_ankle)
		trans.Translation = v_result
		node_ankle.Kinematics.Global.Transform = trans
		
		# ball #
		v_result.Scale(self.parent.scale, self.v_ball)
		trans.Translation = v_result
		node_ball.Kinematics.Global.Transform = trans
		
		# toe #
		v_result.Scale(self.parent.scale, self.v_toe)
		trans.Translation = v_result
		node_toe.Kinematics.Global.Transform = trans
		
		# heel #
		v_result.Scale(self.parent.scale, self.v_heel)
		trans.Translation = v_result
		node_heel.Kinematics.Global.Transform = trans

		#---------------------------------------------------------------------
		# add a visual upvector #
		node_upv						= node_parent.AddNull(xsi.zMapName('%sUpv' % self.parent.basename, 'Custom:Tmp', self.parent.symmetry))
		node_upv.primary_icon.Value 	= 0
		node_upv.shadow_icon.Value  	= 10
		node_upv.size.Value				= 1
		node_upv.shadow_offsetZ.Value	= node_upv.size.Value
		
		node_upv.shadow_colour_custom	= True
		node_upv.R.Value				= 1
		node_upv.G.Value				= 0.8
		node_upv.B.Value				= 1
		
		cns_upv							= node_upv.Kinematics.AddConstraint('Direction', node_toe, False)
		cns_upv							= dispatch(cns_upv)
		cns_upv.upvct_active.Value 		= True
		cns_upv.UpVectorReference		= node_ankle
		cns_upv.dirx					= 0
		cns_upv.diry					= 0
		cns_upv.dirz					= 1
		cns_upv.upx						= 1
		cns_upv.upy						= 0
		cns_upv.upz						= 0
		
		cns_pos							= node_upv.Kinematics.AddConstraint('Position', node_heel, False)
		
		node_upv.Size.AddExpression(
			'ctr_dist( %s.kine.global, %s.kine.global ) / 2' % (
				node_heel.FullName, node_toe.FullName
			)
		)
		
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
		set_zFootAnkle	= False
		set_zFootBall	= False
		set_zFootToe	= False
		set_zFootHeel	= False
		for node in child_nodes:
			if node.Properties('zFootAnkle'):
				self.v_ankle 	= node.Kinematics.Global.Transform.Translation
				set_zFootAnkle	= True
			elif node.Properties('zFootBall'):
				self.v_ball 	= node.Kinematics.Global.Transform.Translation
				set_zFootBall	= True
			elif node.Properties('zFootToe'):
				self.v_toe 		= node.Kinematics.Global.Transform.Translation
				set_zFootToe	= True
			elif node.Properties('zFootHeel'):
				self.v_heel		= node.Kinematics.Global.Transform.Translation
				set_zFootHeel	= True

		# see if all the variables are set #		
		for varname in locals().keys():
			if re.match(r'^set_.+', varname):
				if not locals().get(varname):
					raise Exception(
						'Unable to set "%s" template value from scene.' % varname
					)
		
class zFoot_Rig(object):
	"""
	Class for drawing a Foot.
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
		'node_pelvis',	   
		'character_set',	   
	    'con_foot',	 
	    'con_ankle',	 
	    'ik_switch',	 
	    'prop_anim',	 
	    'prop_anim_di', 
	    'root_leg_con', 
	    'root_skel_leg', 
		'size_ball_con',		
		'size_toe_con',		
		'size_toe_pivot_con',	
		'size_ball_pivot_con',
		'size_fk_cons',	
		'group_deformers',	
		'group_controls',	
		'realign_foot_con',
		'add_middlers',

		# outs #
		'deformers',
		'character_subset',
		'root_foot',
		'root_foot_rev',
		'con_foot_fk',
		'con_toe',
		'con_toe_fk',
		'con_toe_pivot',
		'con_ball_pivot',
		'con_ball',
		'env_toe',
		'env_foot',
	]
	# define those attrs that are read only #
	_readonly_attrs_ = [
		'parent',
		# outs #
		'deformers',
		'character_subset',
		'root_foot',
		'root_foot_rev',
		'con_foot_fk',
		'con_toe',
		'con_toe_fk',
		'con_toe_pivot',
		'con_ball_pivot',
		'con_ball',
		'env_toe',
		'env_foot',
	]

	def __init__(self, parent):
		super(zFoot_Rig, self).__init__()

		# set the instance variables #
		self.parent					= parent
		self.skeleton_parent 		= None
		self.controls_parent 		= None
		self.deformer_parent 		= None
		self.character_set			= None
		self.con_foot           	= None
		self.con_ankle	   			= None
		self.ik_switch          	= None
		self.prop_anim          	= None
		self.prop_anim_di       	= None
		self.root_leg_con       	= None
		self.root_skel_leg      	= None
		self.group_deformers		= None
		self.group_controls			= None
		self.realign_foot_con		= True
		self.add_middlers			= False
		
		self.size_ball_con			= 1
		self.size_toe_con			= 1
		self.size_toe_pivot_con		= 1
		self.size_ball_pivot_con	= 1
		self.size_fk_cons			= 1.75
		
		# outputs #
		self.character_subset		= None
		self.root_foot_rev			= None
		self.root_foot				= None
		self.deformers				= dispatch('XSI.Collection')
		
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
				'zFoot.rig.skeleton_parent is not defined.'
			)
		self.skeleton_parent = dispatch(self.skeleton_parent)
		
		# make sure we have the controls_parent #
		if not self.controls_parent:
			raise Exception(
				'zFoot.rig.controls_parent is not defined.'
			)
		self.controls_parent = dispatch(self.controls_parent)
		
		# make sure we have the deformer_parent #
		if not self.deformer_parent:
			raise Exception(
				'zFoot.rig.deformer_parent is not defined.'
			)
		self.deformer_parent = dispatch(self.deformer_parent)
		
		# make sure we have the template values #
		template = self.parent.template
			
		# make sure we have all items needed from the leg #
		if not self.con_foot:
			raise Exception(
				'Missing reference to a foot controller.'
			)
		if not self.con_ankle:
			raise Exception(
				'Missing reference to leg ankle controller.'
			)
		if not self.ik_switch:
			raise Exception(
				'Missing reference to a leg ik switch.'
			)
		if not self.prop_anim:
			raise Exception(
				'Missing reference to a leg animation property.'
			)
		if not self.prop_anim_di:
			raise Exception(
				'Missing reference to a leg animation property (display info).'
			)
		if not self.root_leg_con:
			raise Exception(
				'Missing reference to a leg controller root.'
			)

		#---------------------------------------------------------------------
		# create a null to locate the foot orientation 
		self.con_foot = dispatch(self.con_foot)
		node_temp = xsi.ActiveSceneRoot.AddNull()
		node_temp.Kinematics.Global.Transform = self.con_foot.node_rest.Kinematics.Global.Transform
		
		# get the global vector #
		v_temp_global = node_temp.Kinematics.Global.Transform.Translation
		
		# create a vector at the toe #
		node_temp_toe = xsi.ActiveSceneRoot.AddNull()
		trans = XSIMath.CreateTransform()

		# match the global y vector #
		v_toe_flat = XSIMath.CreateVector3()
		v_toe_flat.Copy(self.parent.template.v_toe)
		v_toe_flat.Y = v_temp_global.Y
		trans.Translation = v_toe_flat
		node_temp_toe.Kinematics.Global.Transform = trans
		
		# aim the temp foot at the toe with a world up #
		cns = node_temp.Kinematics.AddConstraint('Direction', node_temp_toe, False)
		cns = dispatch(cns)
		cns.upvct_active.Value = True

		# set the foot rest con to this transform #
		trans_foot = node_temp.Kinematics.Global.Transform
		if self.realign_foot_con:
			log('Realigning the foot con to the orientation of the foot.')
			self.con_foot.node_rest.Kinematics.Global.Transform = trans_foot 
		
		# remove the temp nulls #
		xsi.DeleteObj('%s,%s' % (node_temp.FullName, node_temp_toe.FullName))

		#---------------------------------------------------------------------
		# draw the REVERSE FOOT
	
		# calculate the plane vector #
		v_plane = XSIMath.CreateVector3()
		v1		= XSIMath.CreateVector3()
		v2		= XSIMath.CreateVector3()
		# get vector from root to ankle #
		v1.Sub(template.v_heel, template.v_ankle)
		# get vector from root to knee #
		v2.Sub(template.v_heel, template.v_toe)
		# get the cross product #
		v_plane.Cross(v1, v2)
	
		# draw the chain #
		self.root_foot_rev = self.controls_parent.Add2DChain(
			template.v_heel, 
			template.v_toe, 
			v_plane, 
			c.si2DChainNormalRadian,
			xsi.zMapName('footRev', 'ChainRoot', self.parent.symmetry)
		)
		self.root_foot_rev.Effector.Name = xsi.zMapName('footRev', 'ChainEff', self.parent.symmetry)
		self.root_foot_rev.Bones(0).Name = xsi.zMapName('footRev', 'ChainBone', self.parent.symmetry, 1)
		
		# add bones #
		self.root_foot_rev.AddBone(
			template.v_ball, 
			c.siChainBonePin,
			xsi.zMapName('footRev', 'ChainBone', self.parent.symmetry, 2)
		)
		self.root_foot_rev.AddBone(
			template.v_ankle, 
			c.siChainBonePin,
			xsi.zMapName('footRev', 'ChainBone', self.parent.symmetry, 3)
		)

		# format the bones #
		fmt = xsi.zChainFormatter(self.root_foot_rev)
		if re.match(r'^left$', self.parent.symmetry, re.I):
			fmt.BoneDisplay = 0
			fmt.BoneSize	= self.parent.scale
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
			fmt.BoneDisplay = 0
			fmt.BoneSize	= self.size_fk_cons
			fmt.BoneR		= 1
			fmt.BoneG		= 0
			fmt.BoneB		= 0
			fmt.BoneWireR	= 1
			fmt.BoneWireG	= 0
			fmt.BoneWireB	= 0
			
			fmt.RootDisplay = 0
			fmt.RootSize	= self.size_fk_cons
			fmt.RootR		= 1
			fmt.RootG		= 0
			fmt.RootB		= 0
			fmt.RootWireR	= 1
			fmt.RootWireG	= 0
			fmt.RootWireB	= 0

			fmt.EffDisplay 	= 0
			fmt.EffSize		= self.size_fk_cons
			fmt.EffR		= 1
			fmt.EffG		= 0
			fmt.EffB		= 0
			fmt.EffWireR	= 1
			fmt.EffWireG	= 0
			fmt.EffWireB	= 0
			
			fmt.EffLastBone	= True

		fmt.Format()
		
		#---------------------------------------------------------------------
		# contrain the reverse foot to the controller #
		self.con_foot = dispatch(self.con_foot)
		self.root_foot_rev.Kinematics.AddConstraint('Pose', self.con_foot.node_hook, True)

		# constrain the ankle rest to the reverse foot effector #
		self.con_ankle = dispatch(self.con_ankle)
		self.con_ankle.node_rest.Kinematics.AddConstraint('Position', self.root_foot_rev.Effector, False)

		#---------------------------------------------------------------------
		# add the BALL controller
		self.con_ball 						= xsi.zCon()
		self.con_ball.type 					= 'round_box'
		self.con_ball.size 					= self.size_ball_con * self.parent.scale
		self.con_ball.transform.Translation = self.root_foot_rev.Bones(2).Kinematics.Global.Transform.Translation
		self.con_ball.transform.Rotation	= trans_foot.Rotation
		self.con_ball.basename 				= 'Ball'
		self.con_ball.symmetry 				= self.parent.symmetry
		self.con_ball.parent_node 			= self.con_foot.node_hook
		if re.match(r'^right$', self.parent.symmetry, re.I):
			self.con_ball.red 				= 0.8
			self.con_ball.green 			= 0
			self.con_ball.blue 				= 0
		else:                       		
			self.con_ball.red 				= 0
			self.con_ball.green 			= 0.8
			self.con_ball.blue 				= 0
		self.con_ball.Draw()
		self.con_ball.AddTransformSetupPos('local')

		#---------------------------------------------------------------------
		# add the TOE controller
		self.con_toe 						= xsi.zCon()
		self.con_toe.type 					= 'round_box'
		self.con_toe.size 					= self.size_toe_con * self.parent.scale
		self.con_toe.transform.Translation 	= self.root_foot_rev.Bones(1).Kinematics.Global.Transform.Translation
		self.con_toe.transform.Rotation		= trans_foot.Rotation
		self.con_toe.basename 				= 'Toe'
		self.con_toe.symmetry 				= self.parent.symmetry
		self.con_toe.parent_node 			= self.con_foot.node_hook
		if re.match(r'^right$', self.parent.symmetry, re.I):
			self.con_toe.red 	   			= 0.8
			self.con_toe.green 	   			= 0
			self.con_toe.blue 	   			= 0
		else:                      			
			self.con_toe.red 	   			= 0
			self.con_toe.green 	   			= 0.8
			self.con_toe.blue 	   			= 0
		self.con_toe.Draw()
		self.con_toe.AddTransformSetupPos('local')

		#---------------------------------------------------------------------
		# add to the control group 
		if self.group_controls:
			self.group_controls.AddMember(self.con_ball.node_con)
			self.group_controls.AddMember(self.con_toe.node_con)
			
		#---------------------------------------------------------------------
		# create up vectors for the feet
		
		# foot #
		upv_foot = self.con_foot.node_hook.AddNull(
			xsi.zMapName('Foot', 'UpVector', self.parent.symmetry)
		)
		upv_foot.primary_icon.Value = 0
		upv_foot.Properties('Visibility').Parameters('viewvis').Value = False
		upv_foot.Properties('Visibility').Parameters('rendvis').Value = False
		trans = self.root_foot_rev.Bones(2).Kinematics.Global.Transform
		trans.AddLocalTranslation(XSIMath.CreateVector3(-50*self.parent.scale, 50*self.parent.scale, 0))
		upv_foot.Kinematics.Global.Transform = trans
	
		# toe #
		upv_toe = self.con_ball.node_hook.AddNull(
			xsi.zMapName('Toe', 'UpVector', self.parent.symmetry)
		)
		upv_toe.primary_icon.Value = 0
		upv_toe.Properties('Visibility').Parameters('viewvis').Value = False
		upv_toe.Properties('Visibility').Parameters('rendvis').Value = False
		trans = self.root_foot_rev.Bones(1).Kinematics.Global.Transform
		trans.AddLocalTranslation(XSIMath.CreateVector3(50*self.parent.scale, 70*self.parent.scale, 0))
		upv_toe.Kinematics.Global.Transform = trans

		#---------------------------------------------------------------------
		# Draw the foot fk control setup
		self.root_leg_con = dispatch(self.root_leg_con)
		
		self.con_foot_fk 				= xsi.zCon()
		self.con_foot_fk.type 			= 'box'
		self.con_foot_fk.size 			= self.size_fk_cons * self.parent.scale
		self.con_foot_fk.transform 		= self.root_leg_con.Effector.Kinematics.Global.Transform
		self.con_foot_fk.basename 		= 'FootFk'
		self.con_foot_fk.symmetry 		= self.parent.symmetry
		self.con_foot_fk.parent_node 	= self.controls_parent
		if re.match(r'^right$', self.parent.symmetry, re.I):
			self.con_foot_fk.red 		= 1
			self.con_foot_fk.green 		= 0
			self.con_foot_fk.blue 		= 0
		else:                   
			self.con_foot_fk.red 		= 0
			self.con_foot_fk.green 		= 1
			self.con_foot_fk.blue 		= 0
		self.con_foot_fk.Draw()
		self.con_foot_fk.AddTransformSetupRot('add')
		
		# add to the control group 
		if self.group_controls:
			self.group_controls.AddMember(self.con_foot_fk.node_con)

		# constrain it to the effector of the control leg #
		self.con_foot_fk.node_rest.Kinematics.AddConstraint('Pose', self.root_leg_con.Effector, True)

		# create a spacer node to help fix direction constraint blending issues #
		#   Note: do nothing with this node #
		node_foot_spacer = self.con_foot_fk.node_rest.AddNull(xsi.zMapName('FootFk', 'Zero', self.parent.symmetry))
		node_foot_spacer.primary_icon.Value = 0
		node_foot_spacer.Properties('Visibility').Parameters('viewvis').Value = False
		node_foot_spacer.Properties('Visibility').Parameters('rendvis').Value = False
		node_foot_spacer.Kinematics.Global.Transform = node_foot_spacer.parent.Kinematics.Global.Transform
		node_foot_spacer.AddChild(self.con_foot_fk.node_con)

		# aim it #
		cns_foot_fk = self.con_foot_fk.node_con.Kinematics.AddConstraint('Direction', self.con_ball.node_hook, False)
		cns_foot_fk = dispatch(cns_foot_fk)
		cns_foot_fk.upvct_active.Value = True
		cns_foot_fk.UpVectorReference = upv_foot
		
		# calculate the size #
		v_len 	= XSIMath.CreateVector3()
		v1		= self.con_foot_fk.node_con.Kinematics.Global.Transform.Translation
		v2		= self.con_ball.node_con.Kinematics.Global.Transform.Translation
		# calculate the length #
		v_len.Sub(v2,v1)
		length 	= v_len.Length()
		# get the point array of the controller #
		pa = list(self.con_foot_fk.node_con.ActivePrimitive.Geometry.Points.PositionArray)
		pa[0] = list(pa[0])
		pa[1] = list(pa[1])
		pa[2] = list(pa[2])
		# shift all the points #
		for p in xrange(len(pa[0])):
			# scale the points #
			pa[0][p] *= length/(self.size_fk_cons * self.parent.scale)
			pa[1][p] *= (self.size_fk_cons * self.parent.scale)
			pa[2][p] *= (self.size_fk_cons * self.parent.scale)

			# shift them down the X axis #
			pa[0][p] += length/2

		# put the points back on the array #
		self.con_foot_fk.node_con.ActivePrimitive.Geometry.Points.PositionArray = pa

		# set the neutral pose #
		xsi.SetNeutralPose(self.con_foot_fk.node_con, c.siSRT, False)

		# set default keys, blend constraints need something to blend to #
		self.con_foot_fk.node_con.Kinematics.Local.RotX.AddFcurve2([0,0])
		self.con_foot_fk.node_con.Kinematics.Local.RotY.AddFcurve2([0,0])
		self.con_foot_fk.node_con.Kinematics.Local.RotZ.AddFcurve2([0,0])

		#---------------------------------------------------------------------
		# Draw the toe fk control setup
		self.con_toe_fk 				= xsi.zCon()
		self.con_toe_fk.type 			= 'box'
		self.con_toe_fk.size 			= self.size_fk_cons * self.parent.scale
		self.con_toe_fk.transform 		= self.con_ball.node_con.Kinematics.Global.Transform
		self.con_toe_fk.basename 		= 'ToeFk'
		self.con_toe_fk.symmetry 		= self.parent.symmetry
		self.con_toe_fk.parent_node 	= self.con_foot_fk.node_hook
		if re.match(r'^right$', self.parent.symmetry, re.I):
			self.con_toe_fk.red 		= 1
			self.con_toe_fk.green 		= 0
			self.con_toe_fk.blue 		= 0
		else:                   
			self.con_toe_fk.red 		= 0
			self.con_toe_fk.green 		= 1
			self.con_toe_fk.blue 		= 0
		self.con_toe_fk.Draw()
		self.con_toe_fk.AddTransformSetupRot('add')
		
		# add to the control group 
		if self.group_controls:
			self.group_controls.AddMember(self.con_toe_fk.node_con)

		# create a spacer node to help fix direction constraint blending issues #
		#   Note: do nothing with this node #
		node_toe_spacer = self.con_toe_fk.node_rest.AddNull(xsi.zMapName('ToeFk', 'Zero', self.parent.symmetry))
		node_toe_spacer.primary_icon.Value = 0
		node_toe_spacer.Properties('Visibility').Parameters('viewvis').Value = False
		node_toe_spacer.Properties('Visibility').Parameters('rendvis').Value = False
		node_toe_spacer.Kinematics.Global.Transform = node_toe_spacer.parent.Kinematics.Global.Transform
		node_toe_spacer.AddChild(self.con_toe_fk.node_con)
		
		# aim it #
		cns_toe_fk = self.con_toe_fk.node_con.Kinematics.AddConstraint('Direction', self.con_toe.node_hook, False)
		cns_toe_fk = dispatch(cns_toe_fk)
		cns_toe_fk.upvct_active.Value = True
		cns_toe_fk.UpVectorReference = upv_toe
		
		# calculate the size #
		v_len 	= XSIMath.CreateVector3()
		v1		= self.con_toe_fk.node_con.Kinematics.Global.Transform.Translation
		v2		= self.con_toe.node_con.Kinematics.Global.Transform.Translation
		# calculate the length #
		v_len.Sub(v2,v1)
		length 	= v_len.Length()
		# get the point array of the controller #
		pa = list(self.con_toe_fk.node_con.ActivePrimitive.Geometry.Points.PositionArray)
		pa[0] = list(pa[0])
		pa[1] = list(pa[1])
		pa[2] = list(pa[2])
		# shift all the points #
		for p in xrange(len(pa[0])):
			# scale the points #
			pa[0][p] *= length/(self.size_fk_cons * self.parent.scale)
			pa[1][p] *= (self.size_fk_cons * self.parent.scale)
			pa[2][p] *= (self.size_fk_cons * self.parent.scale)

			# shift them down the X axis #
			pa[0][p] += length/2

		# put the points back on the array #
		self.con_toe_fk.node_con.ActivePrimitive.Geometry.Points.PositionArray = pa
		
		# set the neutral pose #
		xsi.SetNeutralPose(self.con_toe_fk.node_con, c.siSRT, False)
		
		# set default keys, blend constraints need something to blend to #
		self.con_toe_fk.node_con.Kinematics.Local.RotX.AddFcurve2([0,0])
		self.con_toe_fk.node_con.Kinematics.Local.RotY.AddFcurve2([0,0])
		self.con_toe_fk.node_con.Kinematics.Local.RotZ.AddFcurve2([0,0])
		
		#---------------------------------------------------------------------
		# add transform setups 
		
		# foot #
		ts = self.con_foot_fk.node_con.AddProperty('Transform Setup', False)
		ts = dispatch(ts)
		ts.tool.Value = 3
		ts.rotate.Value = 3
		ts.xaxis.Value = True
		ts.yaxis.Value = True
		ts.zaxis.Value = True
		
		# toe #
		ts = self.con_toe_fk.node_con.AddProperty('Transform Setup', False)
		ts = dispatch(ts)
		ts.tool.Value = 3
		ts.rotate.Value = 3
		ts.xaxis.Value = True
		ts.yaxis.Value = True
		ts.zaxis.Value = True
		
		#---------------------------------------------------------------------
		# draw the foot skeleton
		
		# calculate the plane vector #
		v_plane = XSIMath.CreateVector3()
		v1		= XSIMath.CreateVector3()
		v2		= XSIMath.CreateVector3()
		# get vector from root to ankle #
		v1.Sub(template.v_ankle, template.v_ball)
		# get vector from root to knee #
		v2.Sub(template.v_ankle, template.v_toe)
		# get the cross product #
		v_plane.Cross(v1, v2)
		
		# draw the skeleton #
		self.root_foot = self.skeleton_parent.Add2DChain(
			template.v_ankle,
			template.v_ball,
			v_plane,
			c.si2DChainNormalRadian
		)
		
		# rename #
		self.root_foot.Name 			= xsi.zMapName(self.parent.basename, 'ChainRoot', self.parent.symmetry)
		self.root_foot.Bones(0).Name 	= xsi.zMapName(self.parent.basename, 'ChainBone', self.parent.symmetry, 1)
		self.root_foot.effector.Name 	= xsi.zMapName(self.parent.basename, 'ChainEff', self.parent.symmetry)
		
		# draw the shin #
		self.root_foot.AddBone(
			template.v_toe,
			c.siChainBonePin,
			xsi.zMapName(self.parent.basename, 'ChainBone', self.parent.symmetry, 2)
		)
		
		# put the effector under the last bone #
		self.root_foot.Bones(1).AddChild(self.root_foot.effector)
		
		# align the chain root #
		trans =self.root_foot.Bones(0).Kinematics.Global.Transform
		self.root_foot.Kinematics.Global.Transform =self.root_foot.Bones(0).Kinematics.Global.Transform
		self.root_foot.Bones(0).Kinematics.Global.Transform = trans
		
		# format the chain colors
		fmt = xsi.zChainFormatter(self.root_foot)
		fmt.Format()
		
		# set neutral pose on foot joints
		for bone in self.root_foot.Bones:
			bone = dispatch(bone)
			# set the neutral pose #
			xsi.SetNeutralPose(bone, c.siSRT, False)
		
		# constraints + bones don't mix, but expressions do! #
		self.root_foot.Bones(0).Kinematics.Global.RotX.AddExpression(
			self.con_foot_fk.node_con.Kinematics.Global.RotX.FullName
		) 
		self.root_foot.Bones(0).Kinematics.Global.RotY.AddExpression(
			self.con_foot_fk.node_con.Kinematics.Global.RotY.FullName
		) 
		self.root_foot.Bones(0).Kinematics.Global.RotZ.AddExpression(
			self.con_foot_fk.node_con.Kinematics.Global.RotZ.FullName
		) 
		
		self.root_foot.Bones(1).Kinematics.Global.RotX.AddExpression(
			self.con_toe_fk.node_con.Kinematics.Global.RotX.FullName
		) 
		self.root_foot.Bones(1).Kinematics.Global.RotY.AddExpression(
			self.con_toe_fk.node_con.Kinematics.Global.RotY.FullName
		) 
		self.root_foot.Bones(1).Kinematics.Global.RotZ.AddExpression(
			self.con_toe_fk.node_con.Kinematics.Global.RotZ.FullName
		) 

		#---------------------------------------------------------------------
		# hook up the cons to the reverse foot 
		self.con_ankle.node_rest.Kinematics.AddConstraint('Pose', self.root_foot_rev.Effector, True)
		self.con_ankle.node_rest.Kinematics.AddConstraint('Pose', self.root_foot_rev.Effector, True)

		self.con_toe.node_rest.Kinematics.AddConstraint('Pose', self.root_foot_rev.Bones(1), True)
		self.con_toe.node_rest.Kinematics.AddConstraint('Pose', self.root_foot_rev.Bones(1), True)

		self.con_ball.node_rest.Kinematics.AddConstraint('Pose', self.root_foot_rev.Bones(2), True)
		self.con_ball.node_rest.Kinematics.AddConstraint('Pose', self.root_foot_rev.Bones(2), True)

		#---------------------------------------------------------------------
		# add a toe pivot 
		self.con_toe_pivot 						= xsi.zCon()
		self.con_toe_pivot.type 				= 'rot'
		self.con_toe_pivot.size 				= self.size_toe_pivot_con * self.parent.scale
		self.con_toe_pivot.transform 			= self.root_foot_rev.Bones(1).Kinematics.Global.Transform
		self.con_toe_pivot.transform.AddLocalRotation(
			XSIMath.CreateRotation(0, 0, XSIMath.DegreesToRadians(180))
		)
		self.con_toe_pivot.basename 			= 'ToePivot'
		self.con_toe_pivot.symmetry 			= self.parent.symmetry
		self.con_toe_pivot.parent_node 			= self.controls_parent
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
		self.root_foot_rev.Bones(1).Kinematics.AddConstraint('Pose', self.con_toe_pivot.node_con, True)

		# add to the control group 
		if self.group_controls:
			self.group_controls.AddMember(self.con_toe_pivot.node_con)

		#---------------------------------------------------------------------
		# add a ball pivot 
		self.con_ball_pivot					= xsi.zCon()
		self.con_ball_pivot.type 			= 'rot'
		self.con_ball_pivot.size 			= self.size_ball_pivot_con * self.parent.scale
		self.con_ball_pivot.transform 		= self.root_foot_rev.Bones(2).Kinematics.Global.Transform
		self.con_ball_pivot.transform.Rotation = self.con_toe_pivot.node_con.Kinematics.Global.Transform.Rotation
		self.con_ball_pivot.basename 		= 'BallPivot'
		self.con_ball_pivot.symmetry 		= self.parent.symmetry
		self.con_ball_pivot.parent_node 	= self.con_toe_pivot.node_hook
		self.con_ball_pivot.rotation_order = 'zyx'
		if re.match(r'^right$', self.parent.symmetry, re.I):
			self.con_ball_pivot.red 		= 0.8
			self.con_ball_pivot.green 		= 0
			self.con_ball_pivot.blue 		= 0
		else:                   
			self.con_ball_pivot.red 		= 0
			self.con_ball_pivot.green 		= 0.8
			self.con_ball_pivot.blue 		= 0
		self.con_ball_pivot.Draw()
		self.con_ball_pivot.AddTransformSetupRot('add', False, False, True) # only z axis
		
		# move the controller points down a bit #
		self.con_ball_pivot.Offset(0, self.parent.scale, 0)
		
		# constrain the reverse foot to the constraint #
		self.root_foot_rev.Bones(2).Kinematics.AddConstraint('Pose', self.con_ball_pivot.node_con, True)
		
		# add to the control group 
		if self.group_controls:
			self.group_controls.AddMember(self.con_ball_pivot.node_con)

		#---------------------------------------------------------------------
		# hook up foot to Ik/Fk switch
		self.ik_switch = dispatch(self.ik_switch)
		cns_foot_fk.blendweight.AddExpression(self.ik_switch.FullName)
		cns_toe_fk.blendweight.AddExpression(self.ik_switch.FullName)
		
		#---------------------------------------------------------------------
		# add items to the animation parameters
		self.prop_anim = dispatch(self.prop_anim)
		self.prop_anim.AddParameter3('ShowBallPivot', c.siBool, False, None, None, True, False)
		self.prop_anim.AddParameter3('ShowToePivot', c.siBool, False, None, None, True, False)

		self.prop_anim_di = dispatch(self.prop_anim_di)
		self.prop_anim_di.AddProxyParameter('%s.ShowBallPivot' % self.prop_anim.FullName)
		self.prop_anim_di.AddProxyParameter('%s.ShowToePivot' % self.prop_anim.FullName)

		#---------------------------------------------------------------------
		# hook up the parameters to the scene items #
		
		# visibillity #
		self.con_toe_pivot.node_con.Properties('Visibility').viewvis.AddExpression(self.prop_anim.ShowToePivot.FullName)
		self.con_ball_pivot.node_con.Properties('Visibility').viewvis.AddExpression(self.prop_anim.ShowBallPivot.FullName)
		self.con_toe.node_con.Properties('Visibility').viewvis.AddExpression(self.prop_anim.ShowFootCons.FullName)
		self.con_ball.node_con.Properties('Visibility').viewvis.AddExpression(self.prop_anim.ShowFootCons.FullName)

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

		# add the expression to the controllers #
		
		# toe IK #
		disp = self.con_toe.node_con.AddProperty('Display Property')
		disp = dispatch(disp)
		disp.wirecolorr.AddExpression(expr_ik_r)
		disp.wirecolorg.AddExpression(expr_ik_g)
		disp.wirecolorb.AddExpression(expr_ik_b)

		# ball IK #
		disp = self.con_ball.node_con.AddProperty('Display Property')
		disp = dispatch(disp)
		disp.wirecolorr.AddExpression(expr_ik_r)
		disp.wirecolorg.AddExpression(expr_ik_g)
		disp.wirecolorb.AddExpression(expr_ik_b)

		# toe FK #
		disp = self.con_toe_fk.node_con.AddProperty('Display Property')
		disp = dispatch(disp)
		disp.wirecolorr.AddExpression(expr_fk_r)
		disp.wirecolorg.AddExpression(expr_fk_g)
		disp.wirecolorb.AddExpression(expr_fk_b)

		# foot FK #
		disp = self.con_foot_fk.node_con.AddProperty('Display Property')
		disp = dispatch(disp)
		disp.wirecolorr.AddExpression(expr_fk_r)
		disp.wirecolorg.AddExpression(expr_fk_g)
		disp.wirecolorb.AddExpression(expr_fk_b)

		#---------------------------------------------------------------------
		# link the visbility on the controls to the ik fk switcher #
		
		# controller #
		self.con_ball.node_con.Properties('Visibility').viewvis.AddExpression(
			'cond(%s.chain.blendik != 0, 1, 0)' % self.root_leg_con.Bones(0).FullName
		)
		self.con_toe.node_con.Properties('Visibility').viewvis.AddExpression(
			'cond(%s.chain.blendik != 0, 1, 0)' % self.root_leg_con.Bones(0).FullName
		)
		
		# fk #
		self.con_foot_fk.node_con.Properties('Visibility').viewvis.AddExpression(
			'cond(%s.chain.blendik != 1, 1, 0)' % self.root_leg_con.Bones(0).FullName
		)
		self.con_toe_fk.node_con.Properties('Visibility').viewvis.AddExpression(
			'cond(%s.chain.blendik != 1, 1, 0)' % self.root_leg_con.Bones(0).FullName
		)
		
		#---------------------------------------------------------------------
		# add character sets
		self.character_set = dispatch(self.character_set)
		if self.character_set:
			
			# get the lower subset #
			self.character_set = dispatch(self.character_set)
			lower_set = None
			try:
				lower_set = self.character_set.Get('LowerBody')
			except:                            
				lower_set = self.character_set.AddSubset('LowerBody')
	
			# add the foot subset #
			self.character_subset = lower_set.AddSubset(
				xsi.zMapName(self.parent.basename, 'None', self.parent.symmetry)
			)
			
			# fk rotations #
			self.character_subset.AddNodeRot(self.con_foot_fk.node_con)
			self.character_subset.AddNodeRot(self.con_toe_fk.node_con)

			# con pos and rot #
			self.character_subset.AddNodePosRot(self.con_toe.node_con)
			self.character_subset.AddNodePosRot(self.con_ball.node_con)
			
			# add the pivots #
			self.character_subset.AddParams('%s.kine.local.rotz' % self.con_toe_pivot.node_con.FullName)
			self.character_subset.AddParams('%s.kine.local.rotz' % self.con_ball_pivot.node_con.FullName)
			
			# parameters #
			self.character_subset.AddParams(
				'%(item)s.ShowBallPivot, %(item)s.ShowToePivot' % \
				{'item': self.prop_anim.FullName}
			)
		
		#---------------------------------------------------------------------
		# add fk switch to controllers
		col = dispatch('XSI.Collection')
		col.Add(self.con_foot_fk.node_con) 
		col.Add(self.con_toe_fk.node_con) 
		col.Add(self.con_toe.node_con) 
		col.Add(self.con_ball.node_con) 
		for item in col:
			di = item.AddProperty('CustomProperty', False, 'DisplayInfo_zAnim_Foot_%s' % self.parent.symmetry[0].upper())
			di.AddProxyParameter(self.ik_switch, None, 'FK_IK')
		
		#---------------------------------------------------------------------
		# link the toe and ball con visibility to the prop #
		self.con_ball.node_con.Properties('Visibility').viewvis.AddExpression(
			self.prop_anim.ShowFootCons.FullName
		)
		self.con_toe.node_con.Properties('Visibility').viewvis.AddExpression(
			self.prop_anim.ShowFootCons.FullName
		)
		
		#---------------------------------------------------------------------
		# add middling nulls #
		
		if self.add_middlers:
			
			# create a middling stack under the deformer bunch #
			node_dfm_parent = self.deformer_parent.AddNull(xsi.zMapName('Ankle', 'Custom:DfmPrnt', self.parent.symmetry))
			node_dfm_shadow = node_dfm_parent.AddNull(xsi.zMapName('Ankle', 'Custom:DfmShdw', self.parent.symmetry))
			node_ankle_env  = node_dfm_shadow.AddNull(xsi.zMapName('Ankle', 'Env', self.parent.symmetry))
			self.deformers.Add(node_ankle_env)
		
			# hide the display #
			xsi.zHide(node_dfm_parent)
			xsi.zHide(node_dfm_shadow)
			xsi.zHide(node_ankle_env)
			
			# add the constraints #
			last_leg_bone = self.root_skel_leg.Bones(self.root_skel_leg.Bones.Count-1)
			node_dfm_parent.Kinematics.AddConstraint('Pose', last_leg_bone, False)
			node_dfm_shadow.Kinematics.AddConstraint('Pose', self.root_foot.Bones(0), False)
			cns = node_dfm_shadow.Kinematics.AddConstraint('Pose', last_leg_bone, False)
			cns = dispatch(cns)
			cns.cnspos.Value = False
			cns.cnsscl.Value = False
			cns.blendweight.Value = 0.5
			
		#---------------------------------------------------------------------
		# create a deformer stack #
		
		# foot #
		node_dfm_parent = self.deformer_parent.AddNull(xsi.zMapName('Foot', 'Custom:DfmPrnt', self.parent.symmetry))
		node_dfm_shadow = node_dfm_parent.AddNull(xsi.zMapName('Foot', 'Custom:DfmShdw', self.parent.symmetry))
		self.env_foot   = node_dfm_shadow.AddNull(xsi.zMapName('Foot', 'Env', self.parent.symmetry))
		self.deformers.Add(self.env_foot)
		
		node_dfm_parent.primary_icon.Value 	= 0
		node_dfm_parent.Properties('Visibility').Parameters('viewvis').Value = False
		node_dfm_parent.Properties('Visibility').Parameters('rendvis').Value = False
		node_dfm_shadow.primary_icon.Value 	= 0
		node_dfm_shadow.Properties('Visibility').Parameters('viewvis').Value = False
		node_dfm_shadow.Properties('Visibility').Parameters('rendvis').Value = False
		self.env_foot.primary_icon.Value 	= 0
		self.env_foot.Properties('Visibility').Parameters('viewvis').Value = False
		self.env_foot.Properties('Visibility').Parameters('rendvis').Value = False
		
		node_dfm_parent.Kinematics.AddConstraint('Pose', self.root_foot, False)
		node_dfm_shadow.Kinematics.AddConstraint('Pose', self.root_foot.Bones(0), False)

		# toe #
		node_dfm_parent = self.deformer_parent.AddNull(xsi.zMapName('Toe', 'Custom:DfmPrnt', self.parent.symmetry))
		node_dfm_shadow = node_dfm_parent.AddNull(xsi.zMapName('Toe', 'Custom:DfmShdw', self.parent.symmetry))
		self.env_toe	= node_dfm_shadow.AddNull(xsi.zMapName('Toe', 'Env', self.parent.symmetry))
		self.deformers.Add(self.env_toe)
		
		node_dfm_parent.primary_icon.Value 	= 0
		node_dfm_parent.Properties('Visibility').Parameters('viewvis').Value = False
		node_dfm_parent.Properties('Visibility').Parameters('rendvis').Value = False
		node_dfm_shadow.primary_icon.Value 	= 0
		node_dfm_shadow.Properties('Visibility').Parameters('viewvis').Value = False
		node_dfm_shadow.Properties('Visibility').Parameters('rendvis').Value = False
		self.env_toe.primary_icon.Value		= 0
		self.env_toe.Properties('Visibility').Parameters('viewvis').Value = False
		self.env_toe.Properties('Visibility').Parameters('rendvis').Value = False
		
		node_dfm_parent.Kinematics.AddConstraint('Pose', self.root_foot, False)
		node_dfm_shadow.Kinematics.AddConstraint('Pose', self.root_foot.Bones(1), False)
		
		#---------------------------------------------------------------------
		# add the deformers to the deformers group #
		if self.group_deformers:
			self.group_deformers = dispatch(self.group_deformers)
			self.group_deformers.AddMember(self.deformers)

		# # for setup purposes only #
		# # report the class attributes #
		# for key in self.__dict__:
		# 	log(key)
	
			