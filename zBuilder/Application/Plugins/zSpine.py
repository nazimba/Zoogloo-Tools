"""
zSpine.py

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
	in_reg.Name = "zSpine"
	in_reg.Email = "andy@zoogloo.net"
	in_reg.URL = ""
	in_reg.Major = 1
	in_reg.Minor = 1

	in_reg.RegisterProperty('zSpineCurve')

	in_reg.RegisterCommand('zSpine', 'zSpine')
	
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
# Properties
#-----------------------------------------------------------------------------

def zSpineCurve_Define(ctxt):
	
	prop = ctxt.Source
	
	prop.AddParameter3("Segments", c.siUInt2, 6, 1, 20)
	# prop.AddParameter3("IkCons", c.siUInt2, 4, 3, 10)
	
	fcv = prop.AddFCurveParameter("Falloff").Value
	fcv = dispatch(fcv)
	fcv.BeginEdit()
	fcv.RemoveKeys()
	fcv.AddKey(0,0)
	fcv.AddKey(100,100)
	fcv.Keys(0).RightTanY = 20
	fcv.Keys(0).RightTanX = 20
	fcv.Keys(1).LeftTanY = -20
	fcv.Keys(1).LeftTanX = -20
	# lock the key times and values #
	fcv.EndEdit()
	
	return True
	
def zSpineCurve_DefineLayout(ctxt):
	lo = ctxt.Source
	lo.Clear()

	lo.AddGroup('Info')
	lo.AddItem('Segments', 'Num of Segments')
	# lo.AddItem('IkCons', 'Num of IkCons')
	lo.EndGroup()
	
	lo.AddGroup('Bone Size Falloff')
	fcv = lo.AddFCurve('Falloff')
	# fcv.SetAttribute(c.siUIFCurveLabelX, 'Percentage')
	# fcv.SetAttribute(c.siUIFCurveLabelY, 'Scale')
	# fcv.SetAttribute(c.siUIFCurveViewMaxY, 2)
	fcv.SetAttribute(c.siUIFCurveGridSpaceX, 10)
	fcv.SetAttribute(c.siUIFCurveGridSpaceY, 0.1)
	fcv.SetAttribute(c.siUIFCurveGhosting, True)
	# turns yellow if the colors go back on its self #
	fcv.SetAttribute(c.siUIFCurveColorNonBijective, True)
	lo.EndGroup()
	
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

class zSpine(object):

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
	uid				= '4ee4c420a6ae04305a1eb6c344acdbbe'
	
	def __init__(self, basename='Spine'):
		super(zSpine, self).__init__()
		
		# reset the instance varaibles #
		self._template 		= None
		self._rig		 	= None
		
		self.basename		= basename.capitalize()
		self.scale			= 1
	
	@zProp
	def template():
		'''Template Accessor'''
		def fget(self):
			# create a template if it doesn't exist #
			if not self._template:
				# wrap a new class #
				self._template = dispatch(win32com.server.util.wrap(zSpine_Template(self)))
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
				self._rig = dispatch(win32com.server.util.wrap(zSpine_Rig(self)))
			# return the private var #
			return self._rig
		def fset(self, value):
			raise Exception('Unable to modify rig value.')
		fdel = fset
		return locals()
			
				
class zSpine_Template(object):
	"""docstring for zSpine_Template"""
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
		'curve',
		'point_array',
		'segments',
	]
	# define those attrs that are read only #
	_readonly_attrs_ = [
		'parent'
	]

	def __init__(self, parent):
		super(zSpine_Template, self).__init__()
		
		# set the instance variables #
		self.parent			= parent
		self.scale 			= 1
		self.model 			= None
		
		self.curve			= None
		self.point_array	= None
		self.segments		= None
		
		# load the default values #
		self.LoadDefaultValues()
	
	def LoadDefaultValues(self):
		"""Sets the default values for the template"""
		
		
		defaults = {
			'Neck': {
				'points': [
					[1.8189894035458565e-012, 1.8189894035458565e-012, 1.8189894035458565e-012, 1.8189894035458565e-012],
					[20.085929159056754, 21.161815067093119, 22.086582154994552, 23.250284597089671],
					[-0.25412479246169589, -0.032194785225891615, 0.42407594912423291, 0.53400351467319151],
					[1, 1, 1, 1]
				],
				'segments': 3
			},
			'Spine': {
				'points': [
					[1.8189894035458565e-012, 1.8189894035458565e-012, 1.8189894035458565e-012, 1.8189894035458565e-012],
					[13.777594798396617, 15.685045063977535, 17.897780083849767, 20.085929159056754],
					[-0.049620940721573525, 0.36037860121183601, -0.67198710015969865, -0.25412479246169589],
					[1, 1, 1, 1]
				],
				'segments': 6
			},
			'Tail': {
				'points': [
					[1.8189894035458565e-012, 1.8189894035458565e-012, 1.8189894035458565e-012, 1.8189894035458565e-012],
					[39.469162553338705, 25.354051130487719, 15.571300639402864, 10.260664658528235],
					[-6.4659583732912482, -15.827235818401029, -35.807275738560705, -57.463962365307218],
					[1, 1, 1, 1]
				],
				'segments': 8
			}
		}
		
		# set the defaults #
		if not self.parent.basename in defaults.keys():
			raise Exception(
				'What an ass, there is no default key named "%s"' % self.parent.basename
			)
		self.point_array	= defaults.get(self.parent.basename).get('points')
		self.segments		= defaults.get(self.parent.basename).get('segments')
		
		# set the default model #
		self.model			= xsi.ActiveSceneRoot
		
	def Draw(self):
		"""docstring for Draw"""
		# get the model #
		if not self.model:
			raise Exception('Model attribute for template not specified.')
		
		# dispatch the model #
		self.model = dispatch(self.model)
		
		#---------------------------------------------------------------------
		# create a node to hold the template #
		node_parent = self.model.AddNull('%s_Container' % self.parent.basename)
		node_parent.primary_icon.Value = 0
		node_parent.Properties('Visibility').Parameters('viewvis').Value = False
		node_parent.Properties('Visibility').Parameters('rendvis').Value = False
		node_parent.AddProperty('CustomProperty', False, 'zBuilderTemplateItem')
		prop = node_parent.AddProperty('CustomProperty', False, 'zContainer')
		prop = dispatch(prop)
		prop.AddParameter3('ContainerName', c.siString, self.parent.basename)
		prop.AddParameter3('ContainerUID', c.siString, self.parent.uid)
		
		# draw the curve #
		self.curve 	= node_parent.AddNurbsCurve(
			self.point_array, 
			None, 
			False, 
			3,
			c.siNonUniformParameterization,
			c.siSINurbs
		)
		self.curve.Name = '%s_Curve' % self.parent.basename
		
		# tag the curve with the spine property #
		self.prop_spine = self.curve.AddProperty('zSpineCurve')
		
		# set the default number of segments #
		self.prop_spine.Segments.Value = self.segments
		
		# tag the nodes #
		self.curve.AddProperty('CustomProperty', False, 'zBuilderTemplateManip')

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
				if node.Properties('zContainer').Parameters('ContainerUID').Value == self.parent.uid \
				and	node.Properties('zContainer').Parameters('ContainerName').Value == self.parent.basename:
					node_parent = node
					break
		# make sure we have the container #
		if not node_parent:
			raise Exception('Unable to find pelvis template container by id: %s and name: %s' % (self.parent.uid, self.parent.basename))
		
		#---------------------------------------------------------------------
		# get all the nodes under the container #
		child_nodes = node_parent.FindChildren('*')

		#---------------------------------------------------------------------
		# get the vectors #
		for node in child_nodes:
			prop = node.Properties('zSpineCurve')
			if prop:
				self.curve 	= node
				self.prop 	= prop
		
class zSpine_Rig(object):

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
		'character_root',
		'do_not_touch',
		'add_pick_walk',
		'controls_constraint',
		'character_set',
		'character_subset',
		'size_ik_cons',
		'size_fk_cons',
		'size_chest_con',
		'size_head_con',
		'group_deformers',
		'group_controls',
		'add_chest_con',
		'add_head_con',
		'hide_first_con',
		'param_twist_prev',
		
		# outs #
		'root_ik',
		'root_skel',
		'root_fk',	
		'con_iks',
		'con_chest',
		'con_head',
		'prop_anim',
		'deformers',
		'curve_control',
		'curve_shrunk',
		
	]
	# define those attrs that are read only #
	_readonly_attrs_ = [
		'parent',

		# outs #
		'character_subset',
		'root_ik',
		'root_skel',
		'root_fk',	
		'con_iks',
		'prop_anim',
		'deformers',
		'con_chest',
		'con_head',
		'curve_control',
		'curve_shrunk',
	]

	def __init__(self, parent):
		super(zSpine_Rig, self).__init__()
		
		# initialize the public attributes #
		for item in self._public_attrs_:
			setattr(self, item, None)
		
		# set the instance variables #
		self.parent					= parent
		self.skeleton_parent 		= xsi.ActiveSceneRoot
		self.controls_parent 		= xsi.ActiveSceneRoot
		self.controls_constraint	= None
		self.deformer_parent 		= xsi.ActiveSceneRoot
		self.do_not_touch	 		= xsi.ActiveSceneRoot
		self.character_root 		= None
		self.add_pick_walk 			= True
		self.group_deformers		= None
		self.add_chest_con			= False
		self.add_head_con			= False
		self.hide_first_con			= True
		
		# create a list to hold all the spine ik controls #
		self.con_iks 				= []
		# create a collection to hold all the spine deformers #
		self.deformers				= dispatch('XSI.Collection')
		
		# set the default controller sizes #
		self.size_ik_cons			= 1
		self.size_fk_cons			= 1
		self.size_chest_con			= 6
		self.size_head_con			= 5
		
	
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
		
		# make sure we have the template values #
		template = self.parent.template
		template = dispatch(template)
		if not template.curve:
			raise Exception(
				'Missing template curve.  Try using zSpine.template.Draw()'
			)
		
		# make sure the curve has the property #
		prop_spine = template.curve.Properties('zSpineCurve')
		if not prop_spine:
			raise Exception(
				'Property "zSpineCurve" not found on "%s"' % template.curve
			)
		prop_spine = dispatch(prop_spine)
		
		# make sure the scale is one #
		v_scale = template.curve.Kinematics.Global.Transform.Scaling
		v_unit 	= XSIMath.CreateVector3(1,1,1)
		if v_scale.Length() != v_unit.Length():
			raise Exception(
				'Scale of curve "%s" must be 1.' % template.curve
			)

		# make sure we have 4 or more points on the curve #
		if template.curve.ActivePrimitive.Geometry.Points.Count < 4:
			raise Exception(
				'Generating curves must have at least 4 points.'
			)

		#---------------------------------------------------------------------
		# get the vars #
		segments 	= prop_spine.Segments.Value
		fcv 		= prop_spine.Falloff.Value

		# get the geometry object of the curve #
		geom 		= template.curve.ActivePrimitive.Geometry

		# get the curve object #
		crv 		= geom.Curves(0)

		# get the global position of the curve #
		v_global 	= template.curve.Kinematics.Global.Transform.Translation

		#-------------------------------------------------------------------------
		# create a node stack #
		# main_node 	= xsi.ActiveSceneRoot.AddNull('%s_Bunch' % basename)
		self.do_not_touch 		= dispatch(self.do_not_touch)
		self.controls_parent 	= dispatch(self.controls_parent)
		dnt_node 	= self.do_not_touch.AddNull('%s_DoNotTouch' % self.parent.basename)
		con_node 	= self.controls_parent.AddNull('%s_Bunch' % self.parent.basename)

		# match the position to the controls constraint #
		if self.controls_constraint:
			self.controls_constraint = dispatch(self.controls_constraint)
			con_node.Kinematics.Global.Transform = self.controls_constraint.Kinematics.Global.Transform
			dnt_node.Kinematics.Global.Transform = self.controls_constraint.Kinematics.Global.Transform
		
		# main_node.primary_icon.Value = 0
		# main_node.Properties('Visibility').Parameters('viewvis').Value = False
		# main_node.Properties('Visibility').Parameters('rendvis').Value = False
		dnt_node.primary_icon.Value = 0 
		dnt_node.Properties('Visibility').Parameters('viewvis').Value = False 
		dnt_node.Properties('Visibility').Parameters('rendvis').Value = False 
		con_node.primary_icon.Value = 0
		con_node.Properties('Visibility').Parameters('viewvis').Value = False
		con_node.Properties('Visibility').Parameters('rendvis').Value = False

		#-------------------------------------------------------------------------
		# build a curve to shrink on the spline ik curve #
		# Draw 2 curves, one for the control curve and one to shrink on top #
		crv_length 		= crv.Length
		point_count 	= geom.Points.Count
		segment_length 	= 1.0/(geom.Points.Count-1)*crv_length
		v_crv = XSIMath.CreateVector3()
		
		# build a point list of just Y values #
		point_list = [0,0,0,1]
		for p in xrange(point_count-1):
			point_list += [0, segment_length*(p+1), 0, 1]

		# since the points are drawn through the control curve, add a bunch of points
		#  to lessen the deviation from the original curve
		point_list2 = [0,0,0,1]
		count = 25
		for p in xrange(count):
			segment_length2 = 1.0/(count)*crv_length
			point_list2 += [0, segment_length2*(p+1), 0, 1]

		# draw the curves #
		control_curve = dnt_node.AddNurbsCurve(point_list)
		control_curve.Name = '%s_SourceCurve' % self.parent.basename
		self.curve_control = control_curve
		
		shrink_curve = dnt_node.AddNurbsCurve(point_list2)
		shrink_curve.Name = '%s_ShrunkCurve' % self.parent.basename
		self.curve_shrunk = shrink_curve

		# turn off the selectability of the source curve #
		control_curve.Properties('Visibility').selectability.Value = 0
		shrink_curve.Properties('Visibility').viewvis.Value = 0

		# shrink wrap the curve #
		op = xsi.ApplyOp('CrvDeform', '%s;%s' % (shrink_curve.FullName, control_curve.FullName),
		 					c.siNode, c.siPersistentOperation)

		
		# realign the control curve #
		control_curve.ActivePrimitive.Geometry.Points.PositionArray = \
			geom.Points.PositionArray

		# realign the control curve #
		control_curve.Kinematics.Global.Transform 	= self.parent.template.curve.Kinematics.Global.Transform
		shrink_curve.Kinematics.Global.Transform 	= self.parent.template.curve.Kinematics.Global.Transform
			
		#--------------------------------------#
		# create control clusters on the control curve #
		control_geom = control_curve.ActivePrimitive.Geometry
		for p in xrange(control_geom.Points.Count):

			# create the cluster #
			cluster = control_geom.AddCluster(c.siVertexCluster, '%s%s_Cls' % (self.parent.basename, p), [p])

			# build the global vector for the controller position #
			pa = control_geom.Points.PositionArray
			v_point_local = XSIMath.CreateVector3(pa[0][p], pa[1][p], pa[2][p])
			v_point_local.AddInPlace(v_global)

			# create the con #  
			# conStack = xsi.zCreateCon(con_node, '%sIk%s' % (basename, p), 'Mid', 0, 2*conSize, 1, 1, 0)

			con_ik 					= xsi.zCon()
			if re.match(r'^Tail$', self.parent.basename, re.I):
				con_ik.type 			= 'text:T'
			else:
				con_ik.type 			= 'round_box'
			con_ik.size 			= self.size_ik_cons * self.parent.scale
			con_ik.transform.translation = v_point_local
			con_ik.basename 		= '%sIk%s' % (self.parent.basename, p)
			con_ik.symmetry 		= 'Mid'
			con_ik.parent_node 		= con_node
			con_ik.red 				= 0.75
			con_ik.green 			= 0.75
			con_ik.blue 			= 0
			con_ik.Draw()
			con_ik.AddTransformSetupPos('local')
			
			# add it to the spine control collection #
			self.con_iks.append(con_ik)

			# create the cluster centers #
			cluster.CenterReference = con_ik.node_hook
			
			# hide the first controller #
			if p == 0 and self.hide_first_con:
				# con_ik.node_rest.Properties('Visibility').viewvis.Value 	= False
				con_ik.node_con.Properties('Visibility').viewvis.Value 		= False
				# con_ik.node_hook.Properties('Visibility').viewvis.Value 	= False


		#---------------------------------------------------------------------
		# draw a guide line through the controls #
		point_list = []
		for con in self.con_iks:
			v = con.node_con.Kinematics.Global.Transform.Translation
			point_list += [v.X, v.Y, v.Z, 1]
		guide_curve = dnt_node.AddNurbsCurve(point_list, None, False, 1)
		guide_curve.Name = '%s_CurveHull' % self.parent.basename
		guide_curve.Properties('Visibility').selectability.Value = False
		
		# create center at each cluster #
		guide_clusters = dnt_node.AddNull('%s_HullClusters' % self.parent.basename)
		guide_clusters.primary_icon.Value = 0
		guide_clusters.Properties('Visibility').Parameters('viewvis').Value = False
		guide_clusters.Properties('Visibility').Parameters('rendvis').Value = False
		for p in xrange(guide_curve.ActivePrimitive.Geometry.Points.Count):
			# create the cluster #
			cluster = guide_curve.ActivePrimitive.Geometry.AddCluster(c.siVertexCluster, '%sHull%s_Cls' % (self.parent.basename, p), [p])

			# create a cluster center #
			cluster_center = guide_clusters.AddNull('%s_HullClsCenter%s' % (self.parent.basename, p))
			cluster_center.primary_icon.Value = 0
			cluster_center.Properties('Visibility').Parameters('viewvis').Value = False
			cluster_center.Properties('Visibility').Parameters('rendvis').Value = False

			# constrain it to the controller #
			cluster_center.Kinematics.AddConstraint('Pose', self.con_iks[p].node_hook, False)

			# create the cluster centers #
			cluster.CenterReference = cluster_center
		
		#---------------------------------------------------------------------
		# constraint the spine do not touch group to the controls parent object #
		if self.controls_constraint:
			dnt_node.Kinematics.AddConstraint('Pose', self.controls_constraint, True)

		#-------------------------------------------------------------------------	
		# build the skeleton #

		self.root_ik 		= None
		self.root_fk 		= None
		self.root_skel 		= None
		v_prev 				= None
		weight_perc_prev 	= None
		shrink_crv 			= shrink_curve.ActivePrimitive.Geometry.Curves(0)
		weighted_percs		= [0.0] * (segments+1)
		
		# step through the segments #
		for i in xrange(segments+1):
			# start #
			u_value = float(i)/float(segments)
			perc = u_value*100
			# get the weighted percentage #
			w_perc = fcv.Eval(perc)
			# store the weighted percentage #
			weighted_percs[i] = w_perc
			# start #
			if i == 0:
				# get the current positon on the curve #
				v = shrink_crv.EvaluatePositionFromPercentage(0)[0]
				# add the global transform  to the current position on curve #
				v.AddInPlace(v_global)
				# store it as the previous position vector #
				v_prev = v
				# log('Start: 0%% (w:%0.2f%%) Pos:<%0.2f, %0.2f, %0.2f>' % \
				# 	(w_perc, v.X, v.Y, v.Z), c.siVerbose)

			else:
				# get the current positon on the curve #
				v = shrink_crv.EvaluatePositionFromPercentage(w_perc)[0]
				# add the global transform  to the current position on curve #
				v.AddInPlace(v_global)
				# log('%d: %0.2f%% (w:%0.2f%%) Pos:<%0.2f, %0.2f, %0.2f>' % \
				# 	(i,perc,w_perc,v.X, v.Y, v.Z), c.siVerbose)
				# add the chain root if it doesn't exist #
				if not self.root_skel:

					#-------------------------------------------------------------
					# draw the ik chain root #
					self.root_ik = dnt_node.Add2DChain(
						v_prev, v, XSIMath.CreateVector3(-1,0,0), 
						c.si2DChainNormalRadian
					)
					self.root_ik = dispatch(self.root_ik)
					# constrain the root to the path #
					cns = self.root_ik.Kinematics.AddConstraint('Path', shrink_curve, False)

					# rename #
					self.root_ik.Name 			= xsi.zMapName('%sIk' % self.parent.basename, 'ChainRoot', 'Mid')
					self.root_ik.Bones(0).Name 	= xsi.zMapName('%sIk' % self.parent.basename, 'ChainBone', 'Mid', 1)
					self.root_ik.effector.Name 	= xsi.zMapName('%sIk' % self.parent.basename, 'ChainEff', 'Mid')

					#-------------------------------------------------------------
					# draw the fk chain root #
					self.root_fk = con_node.Add2DChain(
						v_prev, v, XSIMath.CreateVector3(-1,0,0), 
						c.si2DChainNormalRadian
					)
					self.root_fk = dispatch(self.root_fk)
					# rename #
					self.root_fk.Name 			= xsi.zMapName('%sFk' % self.parent.basename, 'ChainRoot', 'Mid')
					self.root_fk.Bones(0).Name 	= xsi.zMapName('%sFk' % self.parent.basename, 'Control', 'Mid', 1)
					self.root_fk.effector.Name 	= xsi.zMapName('%sFk' % self.parent.basename, 'ChainEff', 'Mid')

					#-------------------------------------------------------------
					# draw the skeleton chain root #
					self.root_skel = self.skeleton_parent.Add2DChain(
						v_prev, v, XSIMath.CreateVector3(-1,0,0), 
						c.si2DChainNormalRadian
					)
					self.root_skel = dispatch(self.root_skel)
					# rename #
					self.root_skel.Name 			= xsi.zMapName(self.parent.basename, 'ChainRoot', 'Mid')
					self.root_skel.Bones(0).Name 	= xsi.zMapName(self.parent.basename, 'ChainBone', 'Mid', 1)
					self.root_skel.effector.Name 	= xsi.zMapName(self.parent.basename, 'ChainEff', 'Mid')

					#-------------------------------------------------------------
					# create fk switch on chain root #
					self.prop_anim 	= self.root_fk.AddProperty('CustomProperty', False, 'zAnim')
					self.prop_anim 	= dispatch(self.prop_anim)
					fk_switch 		= self.prop_anim.AddParameter3('Fk_Ik', c.siFloat, 1, 0, 1)
					twist 	 		= self.prop_anim.AddParameter3('Twist', c.siFloat, 0, -90, 90)

					# add a proxy param to the fk bone for the ik/fk slider #
					prop = self.root_fk.Bones(0).AddProperty('CustomProperty', False, 'zAnim')
					prop = dispatch(prop)
					prop.AddProxyParameter(self.prop_anim.Fk_Ik, None, 'Fk_Ik')

					prop_di = self.root_fk.Bones(0).AddProperty('CustomProperty', False, 'DisplayInfo_zAnim')
					prop_di = dispatch(prop_di)
					prop_di.AddProxyParameter(self.prop_anim.Fk_Ik, None, 'Fk_Ik')

					# add a transform setup to the bone #
					ts = self.root_fk.Bones(0).AddProperty('Transform Setup', False)
					ts = dispatch(ts)
					ts.tool.Value = 3
					ts.rotate.Value = 3
					ts.xaxis.Value = True
					ts.yaxis.Value = True
					ts.zaxis.Value = True

				# all other bones #
				else:

					# add the bone #
					bone_ik 		= self.root_ik.AddBone(v)
					bone_fk 		= self.root_fk.AddBone(v)
					bone_skel 		= self.root_skel.AddBone(v)

					# rename #
					segment_number 	= bone_skel.root.Bones.Count
					bone_ik.Name 	= xsi.zMapName('%sIk' % self.parent.basename, 'ChainBone', 'Mid', segment_number)
					bone_fk.Name 	= xsi.zMapName('%sFk' % self.parent.basename, 'Control', 'Mid', segment_number)
					bone_skel.Name 	= xsi.zMapName('%s' % self.parent.basename, 'ChainBone', 'Mid', segment_number)

					# add a proxy param to the fk bone for the ik/fk slider #
					prop = bone_fk.AddProperty('CustomProperty', False, 'zAnim')
					prop = dispatch(prop)
					prop.AddProxyParameter(self.prop_anim.Fk_Ik, None, 'Fk_Ik')

					prop_di = bone_fk.AddProperty('CustomProperty', False, 'DisplayInfo_zAnim')
					prop_di = dispatch(prop_di)
					prop_di.AddProxyParameter(self.prop_anim.Fk_Ik, None, 'Fk_Ik')

					# add a transform setup to the fk bone #
					ts = bone_fk.AddProperty('Transform Setup', False)
					ts = dispatch(ts)
					ts.tool.Value = 3
					ts.rotate.Value = 3
					ts.xaxis.Value = True
					ts.yaxis.Value = True
					ts.zaxis.Value = True

			# store the previously weighted percentage #
			weight_perc_prev = w_perc

		#-------------------------------------------------------------------------
		# constraint the ik chain to the path
		for i in xrange(self.root_ik.Bones.Count):
			# add the path constraint #
			cns = self.root_ik.Bones(i).Kinematics.AddConstraint('Path', shrink_curve, False)
			cns = dispatch(cns)
			cns.perc.Value = weighted_percs[i]
		# constrain the effector #
		cns = self.root_ik.effector.Kinematics.AddConstraint('Path', shrink_curve, False)
		cns = dispatch(cns)
		cns.perc.Value = 100

		#-------------------------------------------------------------------------
		# create a twist heirarchy #
		#  there are issues
		twisters 	= dispatch('XSI.Collection')
		parent 		= dnt_node
		for i in xrange(self.root_ik.Bones.Count):
			# create the twist node #
			twist = parent.AddNull(xsi.zMapName(self.parent.basename, 'Custom:Twist', 'Mid', i))
			# pose constrain it to the corresponding bone #
			cns = twist.Kinematics.AddConstraint('Pose', self.root_ik.Bones(i), False)
			cns = dispatch(cns)
			# add the twist #
			cns.rotx.AddExpression(
				'%s * %s / %s' % (self.prop_anim.Twist.FullName, i+1, segments)
			)
			# make the current twist the new parent #
			parent = twist
			# add it to the collection #
			twisters.Add(twist)
			# turn off the null icon #
			twist.primary_icon.Value = 0
			twist.Properties('Visibility').Parameters('viewvis').Value = False
			twist.Properties('Visibility').Parameters('rendvis').Value = False

		#-------------------------------------------------------------
		# constrain the skeleton chain to the twisters and fk #
		cns_root_ik = self.root_skel.Kinematics.AddConstraint('Pose', self.root_ik, False)
		cns_root_fk = self.root_skel.Kinematics.AddConstraint('Pose', self.root_fk, False)
		cns_root_ik = dispatch(cns_root_ik)
		cns_root_fk = dispatch(cns_root_fk)
		cns_root_fk.cnspos.Value = False
		cns_root_ik.cnspos.Value = False
		cns_root_ik.blendweight.AddExpression(
			'1 - ' + self.prop_anim.Fk_Ik.FullName
		)

		for i in xrange(self.root_skel.Bones.Count):
			cns_bone_ik = self.root_skel.Bones(i).Kinematics.AddConstraint('Pose', twisters(i), False)
			cns_bone_fk = self.root_skel.Bones(i).Kinematics.AddConstraint('Pose', self.root_fk.Bones(i), False)
			cns_bone_ik = dispatch(cns_bone_ik)
			cns_bone_fk = dispatch(cns_bone_fk)
			cns_bone_fk.cnspos.Value = False
			cns_bone_ik.cnspos.Value = False
			# hook it up to the ik/fk slider 
			# since xsi constraints aren't blended like maya, we only need to 
			# hook up the expression to the second constraint, since at 100%
			# it'll take control
			cns_bone_fk.blendweight.AddExpression(
				'1 - ' + self.prop_anim.Fk_Ik.FullName
			)

		#-------------------------------------------------------------------------
		# align the chain roots #
		
		trans = self.root_ik.Bones(0).Kinematics.Global.Transform
		self.root_ik.Kinematics.Global.Transform = trans
		self.root_ik.Bones(0).Kinematics.Global.Transform = trans
		
		trans = self.root_fk.Bones(0).Kinematics.Global.Transform
		self.root_fk.Kinematics.Global.Transform = trans
		self.root_fk.Bones(0).Kinematics.Global.Transform = trans

		trans = self.root_skel.Bones(0).Kinematics.Global.Transform
		self.root_skel.Kinematics.Global.Transform = trans
		self.root_skel.Bones(0).Kinematics.Global.Transform = trans

		#-------------------------------------------------------------------------
		# neutral pose the bones #
		col = dispatch('XSI.Collection')
		# for item in null_stack:
		# 	col.AddItems(item)
		col.AddItems(self.root_ik.Bones)
		col.AddItems(self.root_fk.Bones)
		col.AddItems(self.root_skel.Bones)
		xsi.SetNeutralPose(col, c.siSRT, False)

		#-------------------------------------------------------------------------
		# format the bone #
		
		# ik #
		fmt = xsi.zChainFormatter(self.root_ik)
		fmt.BoneDisplay = 0
		fmt.BoneSize	= self.parent.scale
		fmt.BoneR		= 0.75
		fmt.BoneG		= 0.75
		fmt.BoneB		= 0
		fmt.BoneWireR	= 0.75
		fmt.BoneWireG	= 0.75
		fmt.BoneWireB	= 0
		
		fmt.RootDisplay = 0
		fmt.RootSize	= self.parent.scale
		fmt.RootR		= 0.75
		fmt.RootG		= 0.75
		fmt.RootB		= 0
		fmt.RootWireR	= 0.75
		fmt.RootWireG	= 0.75
		fmt.RootWireB	= 0

		fmt.EffDisplay 	= 0
		fmt.EffSize		= self.parent.scale
		fmt.EffR		= 0.75
		fmt.EffG		= 0.75
		fmt.EffB		= 0
		fmt.EffWireR	= 0.75
		fmt.EffWireG	= 0.75
		fmt.EffWireB	= 0
		
		fmt.EffLastBone	= True
		fmt.Format()
		
		# fk #
		fmt = xsi.zChainFormatter(self.root_fk)
		fmt.BoneDisplay = 6
		fmt.BoneSize	= self.size_fk_cons * self.parent.scale
		fmt.BoneR		= 0.75
		fmt.BoneG		= 0.75
		fmt.BoneB		= 0
		fmt.BoneWireR	= 0.75
		fmt.BoneWireG	= 0.75
		fmt.BoneWireB	= 0
		
		fmt.RootDisplay = 0
		fmt.RootSize	= self.parent.scale
		fmt.RootR		= 0.75
		fmt.RootG		= 0.75
		fmt.RootB		= 0
		fmt.RootWireR	= 0.75
		fmt.RootWireG	= 0.75
		fmt.RootWireB	= 0

		fmt.EffDisplay 	= 0
		fmt.EffSize		= self.parent.scale
		fmt.EffR		= 0.75
		fmt.EffG		= 0.75
		fmt.EffB		= 0
		fmt.EffWireR	= 0.75
		fmt.EffWireG	= 0.75
		fmt.EffWireB	= 0
		
		fmt.EffLastBone	= True
		fmt.Format()
		
		# skel #
		fmt = xsi.zChainFormatter(self.root_skel)
		fmt.EffLastBone	= True
		fmt.Format()
		
		#---------------------------------------------------------------------
		# add the fk_switch to the cons #
		for con in self.con_iks:

			# add a proxy param to the bone to the ik/fk slider #
			prop = con.node_con.AddProperty('CustomProperty', False, 'zAnim')
			prop = dispatch(prop)
			prop.AddProxyParameter(self.prop_anim.Fk_Ik, None, 'Fk_Ik')
			prop.AddProxyParameter(self.prop_anim.Twist, None, 'Twist')

			prop_di = con.node_con.AddProperty('CustomProperty', False, 'DisplayInfo_zAnim')
			prop_di = dispatch(prop_di)
			prop_di.AddProxyParameter(self.prop_anim.Fk_Ik, None, 'Fk_Ik')
			prop_di.AddProxyParameter(self.prop_anim.Twist, None, 'Twist')


		#---------------------------------------------------------------------
		if self.add_pick_walk:
			# add the pickwalker to the controls #
			last_con = None
			last_prop = None
			for con in self.con_iks:
				con = con.node_con
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

			# add the pickwalker to the bone controls #
			last_bone = None
			last_prop = None
			for bone in self.root_ik.bones:
				# add the property #
				prop = bone.AddProperty('zPickWalk')
				prop = dispatch(prop)
				# add the previous (up) con #
				if last_bone: prop.Up.Value = last_bone.Name
				# add the next (down) con #
				if last_prop: last_prop.Down.Value = bone.Name
				# set the last con #
				last_bone = bone
				# set the last prop #
				last_prop = prop

		#---------------------------------------------------------------------
		# align the fk chain to the ik chain #
		self.root_fk.Kinematics.Global.Transform = self.root_ik.Kinematics.Global.Transform
		for b in xrange(self.root_fk.Bones.Count):
			bone_fk = dispatch(self.root_fk.Bones(b))
			bone_ik = dispatch(self.root_ik.Bones(b))
			bone_fk.Kinematics.Global.RotX.Value = bone_ik.Kinematics.Global.RotX.Value
			bone_fk.Kinematics.Global.RotY.Value = bone_ik.Kinematics.Global.RotY.Value
			bone_fk.Kinematics.Global.RotZ.Value = bone_ik.Kinematics.Global.RotZ.Value

		#---------------------------------------------------------------------
		# constrain the controls to a given node #
		if self.controls_constraint:
			# controls #
			# con_node.Kinematics.AddConstraint('Pose', self.controls_constraint, True)
			con_node.Kinematics.AddConstraint('Position', self.controls_constraint, True)
			# fk chain #
			self.root_fk.Kinematics.AddConstraint('Pose', self.controls_constraint, True)
		
		#---------------------------------------------------------------------
		# link the color of the FK controls to the IK_FK slider #

		# build the fk expression #
		expr_fk_r = 'cond(%s != 0.0, 0.25, 0.75)' 	% self.prop_anim.Fk_Ik.FullName
		expr_fk_g = 'cond(%s != 0.0, 0.25, 0.75)'	% self.prop_anim.Fk_Ik.FullName
		expr_fk_b = 'cond(%s != 0.0, 0.0, 0.0)'  	% self.prop_anim.Fk_Ik.FullName

		# build the ik expression #
		expr_ik_r = 'cond(%s != 1.0, 0.25, 0.75)' 	% self.prop_anim.Fk_Ik.FullName
		expr_ik_g = 'cond(%s != 1.0, 0.25, 0.75)' 	% self.prop_anim.Fk_Ik.FullName
		expr_ik_b = 'cond(%s != 1.0, 0.0, 0.0)'  	% self.prop_anim.Fk_Ik.FullName

		# add the expression to the fk bones #
		for bone in self.root_fk.Bones:
			bone = dispatch(bone)
			bone.R.AddExpression(expr_fk_r)
			bone.G.AddExpression(expr_fk_g)
			bone.B.AddExpression(expr_fk_b)

		# add the expression to the controller #
		for con in self.con_iks:
			disp = con.node_con.AddProperty('Display Property')
			disp = dispatch(disp)
			disp.wirecolorr.AddExpression(expr_ik_r)
			disp.wirecolorg.AddExpression(expr_ik_g)
			disp.wirecolorb.AddExpression(expr_ik_b)
		
		#---------------------------------------------------------------------
		# link the visbility on the controls to the ik fk switcher #
		
		# controller #
		for i in xrange(len(self.con_iks)):
			# get the controller by the id #
			con = self.con_iks[i]
			# see if we need to turn off the first and last con #
			if (i == 0 and self.hide_first_con) or \
			(i == len(self.con_iks)-1 and (self.add_chest_con or self.add_head_con)):
				con.node_con.Properties('Visibility').viewvis.AddExpression(
					'cond(%s != 0, 0, 0)' % self.prop_anim.Fk_Ik.FullName
				)
				continue
			con.node_con.Properties('Visibility').viewvis.AddExpression(
				'cond(%s != 0, 1, 0)' % self.prop_anim.Fk_Ik.FullName
			)
		# link the visibility of the helper curves #
		guide_curve.Properties('Visibility').viewvis.AddExpression(
			'cond(%s != 0, 1, 0)' % self.prop_anim.Fk_Ik.FullName
		)
		control_curve.Properties('Visibility').viewvis.AddExpression(
			'cond(%s != 0, 1, 0)' % self.prop_anim.Fk_Ik.FullName
		)
		
		# fk #
		for bone in self.root_fk.Bones:
			bone = dispatch(bone)
			bone.Properties('Visibility').viewvis.AddExpression(
				'cond(%s != 1, 1, 0)' % self.prop_anim.Fk_Ik.FullName
			)
				
		#---------------------------------------------------------------------
		# add to the controls group #
		if self.group_controls:
			for con in self.con_iks:
				self.group_controls.AddMember(con.node_con)
			for bone in self.root_fk.Bones:
				self.group_controls.AddMember(bone)
		
		#---------------------------------------------------------------------
		# create a deformer stack #
		for b in xrange(self.root_skel.Bones.Count):
			bone = self.root_skel.Bones(b)
			# create the nodes #
			node_dfm_parent = self.deformer_parent.AddNull(xsi.zMapName('%s' % self.parent.basename, 'Custom:DfmPrnt', 'Mid', b))
			node_dfm_shadow = node_dfm_parent.AddNull(xsi.zMapName('%s' % self.parent.basename, 'Custom:DfmShdw', 'Mid', b))
			env   			= node_dfm_shadow.AddNull(xsi.zMapName('%s' % self.parent.basename, 'Env', 'Mid', b))
			self.deformers.Add(env)
		
			# turn off the icons #
			node_dfm_parent.primary_icon.Value 	= 0
			node_dfm_parent.Properties('Visibility').Parameters('viewvis').Value = False
			node_dfm_parent.Properties('Visibility').Parameters('rendvis').Value = False
			node_dfm_shadow.primary_icon.Value 	= 0
			node_dfm_shadow.Properties('Visibility').Parameters('viewvis').Value = False
			node_dfm_shadow.Properties('Visibility').Parameters('rendvis').Value = False
			env.primary_icon.Value 				= 0
			env.Properties('Visibility').Parameters('viewvis').Value = False
			env.Properties('Visibility').Parameters('rendvis').Value = False
			
			# add the constraint #
			node_dfm_parent.Kinematics.AddConstraint('Pose', bone.parent, False)
			node_dfm_shadow.Kinematics.AddConstraint('Pose', bone, False)

		#---------------------------------------------------------------------
		# add the deformers to the deformers group #
		if self.group_deformers:
			self.group_deformers = dispatch(self.group_deformers)
			self.group_deformers.AddMember(self.deformers)
			
		#---------------------------------------------------------------------
		# add a chest controller #
		if self.add_chest_con:
			
			# create the con #
			self.con_chest 							= xsi.zCon()
			self.con_chest.type 					= 'circle'
			self.con_chest.size 					= self.size_chest_con * self.parent.scale
			self.con_chest.transform.Translation 	= self.root_skel.Effector.Kinematics.Global.Transform.Translation
			self.con_chest.transform.Rotation 		= XSIMath.CreateRotation(0, XSIMath.DegreesToRadians(-90), 0)
			self.con_chest.basename 				= 'Chest'
			self.con_chest.symmetry 				= 'Mid'
			self.con_chest.parent_node 				= con_node
			self.con_chest.red 						= 0.75
			self.con_chest.green 					= 0.75
			self.con_chest.blue 					= 0
			self.con_chest.Draw()
			self.con_chest.AddTransformSetupLast()
			
			# constrain the last ik node to the con #
			self.con_iks[-1].node_con.Kinematics.AddConstraint('Pose', self.con_chest.node_hook, True)
			
			# add a twist proxy parameter #
			prop = self.con_chest.node_con.AddProperty('CustomProperty', False, 'zAnim')
			prop.AddProxyParameter(self.prop_anim.Fk_Ik, None, 'Fk_Ik')
			prop.AddProxyParameter(self.prop_anim.Twist, None, '%s_Twist' % self.parent.basename.capitalize())
			prop_di = self.con_chest.node_con.AddProperty('CustomProperty', False, 'DisplayInfo_zAnim')
			prop_di.AddProxyParameter(self.prop_anim.Fk_Ik, None, 'Fk_Ik')
			prop_di.AddProxyParameter(self.prop_anim.Twist, None, '%s_Twist' % self.parent.basename.capitalize())
			
			# parent the last two ik cons to the chest con #
			self.con_chest.node_hook.AddChild(self.con_iks[-1].node_rest)
			self.con_chest.node_hook.AddChild(self.con_iks[-2].node_rest)
			
			# add to the control group #
			if self.group_controls:
				self.group_controls.AddMember(self.con_chest.node_con)
				
			# link the rot y to the twist #
			self.prop_anim.Twist.AddExpression(
				self.con_chest.node_con.Kinematics.Local.RotY.FullName
			)
			
		#---------------------------------------------------------------------
		# add a head controller #
		if self.add_head_con:
			
			# create the con #
			self.con_head 							= xsi.zCon()
			self.con_head.type 						= 'hemi'
			self.con_head.size 						= self.size_head_con * self.parent.scale
			self.con_head.transform.Translation 	= self.root_skel.Effector.Kinematics.Global.Transform.Translation
			self.con_head.transform.Rotation 		= XSIMath.CreateRotation(0, XSIMath.DegreesToRadians(-90), 0)
			self.con_head.basename 					= 'Head'
			self.con_head.symmetry 					= 'Mid'
			self.con_head.parent_node 				= con_node
			self.con_head.red 						= 1
			self.con_head.green 					= 1
			self.con_head.blue 						= 0
			self.con_head.rotation_order			= 'zxy'
			self.con_head.Draw()
			self.con_head.AddTransformSetupLast()
			
			# constrain the last ik node to the con #
			self.con_iks[-1].node_con.Kinematics.AddConstraint('Pose', self.con_head.node_hook, True)
			
			# add a twist proxy parameter #
			prop = self.con_head.node_con.AddProperty('CustomProperty', False, 'zAnim')
			prop.AddProxyParameter(self.prop_anim.Fk_Ik, None, 'Fk_Ik')
			prop.AddProxyParameter(self.prop_anim.Twist, None, '%s_Twist' % self.parent.basename.capitalize())
			prop_di = self.con_head.node_con.AddProperty('CustomProperty', False, 'DisplayInfo_zAnim')
			prop_di.AddProxyParameter(self.prop_anim.Fk_Ik, None, 'Fk_Ik')
			prop_di.AddProxyParameter(self.prop_anim.Twist, None, '%s_Twist' % self.parent.basename.capitalize())
			
			# parent the last two ik cons to the chest con #
			self.con_head.node_hook.AddChild(self.con_iks[-1].node_rest)
			self.con_head.node_hook.AddChild(self.con_iks[-2].node_rest)
			
			# add to the control group #
			if self.group_controls:
				self.group_controls.AddMember(self.con_head.node_con)
			
			# link the rot y to the twist #
			self.prop_anim.Twist.AddExpression(
				self.con_head.node_con.Kinematics.Local.RotY.FullName
			)
			
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
			self.character_subset = upper_set.AddSubset(
				xsi.zMapName(self.parent.basename, 'None', 'Mid')
			)

			# add the ik cons #
			for con in self.con_iks:
				self.character_subset.AddNodePos(con.node_con)

			# add the fk cons #
			for bone in self.root_fk.Bones:
				bone = dispatch(bone)
				self.character_subset.AddNodeRot(bone)
			
			if self.con_head:
				self.character_subset.AddNodePosRot(self.con_head.node_con)

			if self.con_chest:
				self.character_subset.AddNodePosRot(self.con_chest.node_con)
				
			# add the parameters #
			self.character_subset.AddParams(self.prop_anim.Twist)
			self.character_subset.AddParams(self.prop_anim.Fk_Ik)

	# # report the class attributes #
		# for key in self.__dict__:
		# 	log(key)

#-----------------------------------------------------------------------------
# Commands
#-----------------------------------------------------------------------------
def zSpine_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	#oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments
	oArgs.Add('basename', c.siArgumentInput, 'spine', c.siString)
	#oArgs.AddObjectArgument('model')

	return True
	
def zSpine_Execute(basename):
	# export the python object #
	import win32com.server
	return win32com.server.util.wrap(
		zSpine(basename)
	)
	
