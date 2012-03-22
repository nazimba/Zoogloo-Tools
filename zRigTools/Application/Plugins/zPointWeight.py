"""
zPointWeight.py

Created by andy on 2008-06-17.
Copyright (c) 2008 Zoogloo LLC. All rights reserved.
"""

__version__ = '$Revision: 11 $'
__author__  = '$Author: andy $'
__date__    = '$Date: 2008-07-21 15:20 -0700 $'

import win32com.client
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
	in_reg.Name = "zPointWeight"
	in_reg.Email = "andy@zoogloo.net"
	in_reg.URL = ""
	try:
		in_reg.Major = int(__version__.split(' ')[1])
	except:
		in_reg.Major = 1
	in_reg.Minor = 0

	in_reg.RegisterOperator('zPointWeights')
	
	in_reg.RegisterProperty('zBindPose')

	in_reg.RegisterCommand('zApplyPointWeights', 'zApplyPointWeights')

	# in_reg.RegisterMenu(c.siMenuTbAnimateActionsStoreID, 'zPointWeightMenu', False)
	
	# copyright message #
	msg = '''
------------------------------------------
  %s (v.%d.%d)
  Copyright 2008 Zoogloo LLC.
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
# Menus
#-----------------------------------------------------------------------------
# def zPointWeightMenu_Init(ctxt):
# 	menu = ctxt.Source
# 	
# 	item = menu.AddCommandItem('zPointWeightGUI', 'zPointWeightGUI')
# 	item.Name = '(z) zPointWeight'

#-----------------------------------------------------------------------------
# Operators
#-----------------------------------------------------------------------------
def zPointWeights_Define(ctxt):
	op = ctxt.Source
	
	# op.AddParameter(
	# 	XSIFactory.CreateParamDef2("Invert", c.siBool, False),
	# )
	# op.AddParameter(
	# 	XSIFactory.CreateParamDef2("Clamp", c.siBool, True),
	# )
	
	ctxt.UserData = [
		
	]

	op.AlwaysEvaluate = false
	op.Debug = 0
	return true

def zPointWeights_Init(ctxt):
	ctxt.UserData = [
		None,	# 0: geometry bind pose
		None,	# 1: list geometry bind point vectors
		None,	# 2: list of deformer bind poses
	]

def zPointWeights_Update(ctxt):

	# get the parameters #
	source 	= dispatch(ctxt.Source)
	# invert 	= source.Invert.Value

	# get the variables #
	v_geo_points 	= ctxt.UserData[0]
	pa_cache		= ctxt.UserData[1]
	# bind_pose_dfms 	= ctxt.UserData[2]
	
	# get the geometry mesh input #
	geom = ctxt.GetInputValue(0)
	
	# get the bind poses #
	bind_geom 	= None
	bind_poses 	= []
	for i in xrange(source.GetNumPortsInGroup(1)):
		# geometry is the first #
		if i == 0:
			bind_geom = source.GetInputValue(i, 1)
		# the rest are deformer ports #
		else:
			bind_poses.append(source.GetInputValue(i, 1))
			
	# get the deformer transforms #
	t_geom = None
	t_dfms = []
	for i in xrange(source.GetNumPortsInGroup(2)):
		# geom transform is the first #
		if i == 0:
			t_geom = source.GetInputValue(i, 2)
		# the rest are deformer inputs #
		else:
			t_dfms.append(source.GetInputValue(i, 2))
			
	# cache the existing point vectors #
	# if not v_geo_points:
	# 	pa_bind			= geom.Geometry.Points.PositionArray
	# 	v_geo_points	= [None] * len(pa_bind[0])
	# 	for p in xrange(len(pa_bind[0])):
	# 		# build the vector #
	# 		v_geo_points[p] = XSIMath.CreateVector3(
	# 			pa_bind[0][p],
	# 			pa_bind[1][p],
	# 			pa_bind[2][p]
	# 		)
	if not pa_cache:
		pa_cache = geom.Geometry.Points.PositionArray
			
	# build the bind matrices #
	t_bind_geom = XSIMath.CreateTransform()
	t_bind_geom.Translation = XSIMath.CreateVector3(
		bind_geom.posx.Value,
		bind_geom.posy.Value,
		bind_geom.posz.Value
	)
	t_bind_geom.Scaling = XSIMath.CreateVector3(
		bind_geom.sclx.Value,
		bind_geom.scly.Value,
		bind_geom.sclz.Value
	)
	t_bind_geom.Rotation = XSIMath.CreateRotation(
		XSIMath.DegreesToRadians(bind_geom.rotx.Value),
		XSIMath.DegreesToRadians(bind_geom.roty.Value),
		XSIMath.DegreesToRadians(bind_geom.rotz.Value)
	)
	mtx_bind_geom = t_bind_geom.Matrix4
	
	# build the dfm matrices #
	mtx_bind_dfms = []
	for bind_pose in bind_poses:
		
		t_bind_dfm = XSIMath.CreateTransform()
		t_bind_dfm.Translation = XSIMath.CreateVector3(
			bind_pose.posx.Value,
			bind_pose.posy.Value,
			bind_pose.posz.Value
		)
		t_bind_dfm.Scaling = XSIMath.CreateVector3(
			bind_pose.sclx.Value,
			bind_pose.scly.Value,
			bind_pose.sclz.Value
		)
		t_bind_dfm.Rotation = XSIMath.CreateRotation(
			XSIMath.DegreesToRadians(bind_pose.rotx.Value),
			XSIMath.DegreesToRadians(bind_pose.roty.Value),
			XSIMath.DegreesToRadians(bind_pose.rotz.Value)
		)
		mtx_bind_dfms.append(t_bind_dfm.Matrix4)
		
	# step through the points #
	pa = list(geom.Geometry.Points.PositionArray)
	pa[0] = list(pa[0])
	pa[1] = list(pa[1])
	pa[2] = list(pa[2])
	v1 = XSIMath.CreateVector3()
	for p in xrange(len(pa[0])):
		# build a vector #
		v1.X = pa[0][p]
		v1.Y = pa[1][p]
		v1.Z = pa[2][p]
		# put it in global space #
		v1.AddInPlace(t_geom.Transform.Translation)
		# weight #
		w = 0.5
		# step through the deformers #
		v_result = XSIMath.CreateVector3()
		for d in xrange(len(t_dfms)):
			# invert the bind matrix #
			mtx_bind_invert = XSIMath.CreateMatrix4()
			mtx_bind_invert.Invert(mtx_bind_dfms[d])
			# multiply it by the current matrix #
			mtx_bind_invert.MulInPlace(t_dfms[d].Transform.Matrix4)
			# for i in xrange(4):
			# 	log(t_dfms[d])
			# 	log('M0: %0.2f %0.2f %0.2f %0.2f ' % (mtx_bind_invert.Value(0, i), mtx_bind_invert.Value(0, i), mtx_bind_invert.Value(0, i), mtx_bind_invert.Value(0, i)))
			# 	log('M1: %0.2f %0.2f %0.2f %0.2f ' % (mtx_bind_invert.Value(1, i), mtx_bind_invert.Value(1, i), mtx_bind_invert.Value(1, i), mtx_bind_invert.Value(1, i)))
			# 	log('M2: %0.2f %0.2f %0.2f %0.2f ' % (mtx_bind_invert.Value(2, i), mtx_bind_invert.Value(2, i), mtx_bind_invert.Value(2, i), mtx_bind_invert.Value(2, i)))
			# 	log('M3: %0.2f %0.2f %0.2f %0.2f ' % (mtx_bind_invert.Value(3, i), mtx_bind_invert.Value(3, i), mtx_bind_invert.Value(3, i), mtx_bind_invert.Value(3, i)))
			# multiply it by our vector #
			v_temp = XSIMath.CreateVector3()
			v_temp.Copy(v1)
			v_temp.MulByMatrix4InPlace(mtx_bind_invert)
			# scale it by the weight #
			v_temp.ScaleInPlace(w)
			# add it to the result #
			v_result.AddInPlace(v_temp)
			
		# put the point back in object space #
		v_result.SubInPlace(t_geom.Transform.Translation)
			
		# log('v1 <%0.2f, %0.2f, %0.2f>' % (v1.X, v1.Y, v1.Z))
		# log('v_result <%0.2f, %0.2f, %0.2f>' % (v_result.X, v_result.Y, v_result.Z))
		pa[0][p] = v_result.X
		pa[1][p] = v_result.Y
		pa[2][p] = v_result.Z
		
	# set the output #
	log(ctxt.OutputPort.Value)
	ctxt.OutputPort.Value.Geometry.Points.PositionArray = pa
	
#-----------------------------------------------------------------------------
# Properties
#-----------------------------------------------------------------------------
def zBindPose_Define(ctxt):
	prop = ctxt.Source
	
	prop.AddParameter3("posx", c.siFloat)
	prop.AddParameter3("posy", c.siFloat)
	prop.AddParameter3("posz", c.siFloat)
	
	prop.AddParameter3("sclx", c.siFloat)
	prop.AddParameter3("scly", c.siFloat)
	prop.AddParameter3("sclz", c.siFloat)

	prop.AddParameter3("rotx", c.siFloat)
	prop.AddParameter3("roty", c.siFloat)
	prop.AddParameter3("rotz", c.siFloat)

	
def zBindPose_DefineLayout(ctxt):
	lo = ctxt.Source
	lo.Clear()

	lo.AddGroup('Scale')
	lo.AddItem('sclx')
	lo.AddItem('scly')
	lo.AddItem('sclz')
	lo.EndGroup()

	lo.AddGroup('Rotation')
	lo.AddItem('rotx')
	lo.AddItem('roty')
	lo.AddItem('rotz')

	lo.AddGroup('Rotation')
	lo.AddItem('posx')
	lo.AddItem('posy')
	lo.AddItem('posz')

#-----------------------------------------------------------------------------
# Commands
#-----------------------------------------------------------------------------
def zApplyPointWeights_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	#oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments
	oArgs.AddObjectArgument('geom')
	oArgs.AddWithHandler('deformers', c.siArgHandlerCollection)

	return True
	
def zApplyPointWeights_Execute(geom, deformers):
	
	# add a bind pose to the geometry #
	bind_pose_geom = geom.AddProperty('zBindPose')
	bind_pose_geom = dispatch(bind_pose_geom)

	bind_pose_geom.posx.Value = geom.Kinematics.Global.PosX.Value
	bind_pose_geom.posy.Value = geom.Kinematics.Global.PosY.Value
	bind_pose_geom.posz.Value = geom.Kinematics.Global.PosZ.Value

	bind_pose_geom.rotx.Value = geom.Kinematics.Global.RotX.Value
	bind_pose_geom.roty.Value = geom.Kinematics.Global.RotY.Value
	bind_pose_geom.rotz.Value = geom.Kinematics.Global.RotZ.Value

	bind_pose_geom.sclx.Value = geom.Kinematics.Global.SclX.Value
	bind_pose_geom.scly.Value = geom.Kinematics.Global.SclY.Value
	bind_pose_geom.sclz.Value = geom.Kinematics.Global.SclZ.Value
		
	# add bind poses to the deformers #
	bind_poses_dfms = [None]*deformers.Count
	for d in xrange(deformers.Count):
		
		deformer = deformers(d)
		
		# attach the bind pose for future reference #
		bind_prop = deformer.AddProperty('zBindPose')
		bind_prop = dispatch(bind_prop)
		
		bind_prop.posx.Value = deformer.Kinematics.Global.PosX.Value
		bind_prop.posy.Value = deformer.Kinematics.Global.PosY.Value
		bind_prop.posz.Value = deformer.Kinematics.Global.PosZ.Value

		bind_prop.rotx.Value = deformer.Kinematics.Global.RotX.Value
		bind_prop.roty.Value = deformer.Kinematics.Global.RotY.Value
		bind_prop.rotz.Value = deformer.Kinematics.Global.RotZ.Value

		bind_prop.sclx.Value = deformer.Kinematics.Global.SclX.Value
		bind_prop.scly.Value = deformer.Kinematics.Global.SclY.Value
		bind_prop.sclz.Value = deformer.Kinematics.Global.SclZ.Value
		
		
		# add it to the bind poses lis #
		bind_poses_dfms[d] = bind_prop
		
	# create the operator #
	op = XSIFactory.CreateObject('zPointWeights')
	op = dispatch(op)

	# add the in and out ports #
	op.AddPortGroup('Main')
	op.AddIOPort(geom.ActivePrimitive) 	# id: 0

	# add the bind poses #
	op.AddPortGroup('BindPoses')
	op.AddInputPort(bind_pose_geom)		# id: 0
	for bind_pose in bind_poses_dfms:
		op.AddInputPort(bind_pose)		# id: 1+
	
	# current transforms #
	op.AddPortGroup('CurrentTransforms')
	op.AddInputPort(geom.Kinematics.Global)					# id: 0
	for d in xrange(deformers.Count):
		op.AddInputPort(deformers(d).Kinematics.Global)		# id: 1+

	# connect it all up #
	op.Connect()	




		

		