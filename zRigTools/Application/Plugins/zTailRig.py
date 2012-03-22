"""
zTailRig.py

TODO: Expose argument or calculate vector for plane

Created by Andy Buecker on 2008-03-28.
Copyright (c) 2008 Zoogloo LLC. All rights reserved.
"""

__version__ = '$Revision: 124 $'
__author__  = '$Author: andy $'
__date__    = '$Date: 2008-09-09 17:12 -0700 $'

import win32com.client
from win32com.client import constants
from win32com.client import constants as c
from win32com.client import Dispatch as dispatch
xsi = Application
log = xsi.logmessage

null = None
false = 0
true = 1

class zTailError(Exception): pass

def XSILoadPlugin(in_reg):
	in_reg.Author = 'Andy Buecker'
	in_reg.Name = "zTailRig"
	in_reg.Email = ""
	in_reg.URL = ""
	try:
		in_reg.Major = int(__version__.split(' ')[1])
	except:
		in_reg.Major = 1
	in_reg.Minor = 0

	in_reg.RegisterProperty("zTailCurve")
	
	in_reg.RegisterCommand("zInitTailCurve")
	
	in_reg.RegisterCommand("zBuildTailRig")

	return True

def XSIUnloadPlugin(in_reg):
	strPluginName = in_reg.Name
	Application.LogMessage(str(strPluginName) + str(" has been unloaded."))
	return true

def zTailCurve_Define(ctxt):
	
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
	
def zTailCurve_DefineLayout(ctxt):
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
	
class zTailClass:
	'''
	
	'''
	# required for COM wrapper #
	_public_methods_ = []
	# define the output vars here #
	_public_attrs_ = ['controls', 'controlCurve', 'shrinkCurve', 
						'chainRootFk',
						'chainRootIk',
						'chainRootSkel',
						'guideCurve',
						'guideClusterGroup',
						'zAnim']
	# define those attrs that are read only #
	_readonly_attrs_ = _public_attrs_
	
	controls 		= []
	controlCurve 	= None
	shrinkCurve 	= None
	guideCurve 		= None
	chainRootIk 	= None
	chainRootSkel 	= None
	zAnim 			= None
	guideClusterGroup	= None
	
	def __init__(self):
		self.controls = []

def zBuildTailRig_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	# oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments
	oArgs.AddObjectArgument("curve")
	oArgs.Add("conSize", c.siArgumentInput, 1, c.siFloat)
	oArgs.Add("basename", c.siArgumentInput, 'Tail', c.siFloat)

	return true


def zBuildTailRig_Execute(curve, conSize, basename):
	
	# make sure it has the property #
	prop = curve.Properties('zTailCurve')
	if not prop:
		msg = 'Property "zTailCurve" not found on "%s"' % curve
		log(msg, c.siError)
		raise zTailError, msg
	prop = dispatch(prop)
		
	# make sure the scale is one #
	vScale = XSIMath.CreateVector3()
	curve.Kinematics.Global.Transform.GetScaling(vScale)
	vUnit = XSIMath.CreateVector3(1,1,1)
	if vScale.Length() != vUnit.Length():
		msg = 'Scale of curve "%s" must be 1.' % curve
		log(msg, c.siError)
		raise zTailError, msg

	# make sure we have 4 or more points on the curve #
	if curve.ActivePrimitive.Geometry.Points.Count < 4:
		msg = 'Generating curves must have at least 4 points.'
		log(msg, c.siError)
		raise zTailError, msg

	# get the vars #
	segments = prop.Segments.Value
	# IkCons = prop.IkCons.Value
	fcv = prop.Falloff.Value
	
	# create a new output class #
	outClass = zTailClass()

	# get the geometry object #
	geom = curve.ActivePrimitive.Geometry

	# get the curve object #
	crv = geom.Curves(0)

	# get the global position #
	vGlobal = XSIMath.CreateVector3()
	curve.Kinematics.Global.Transform.GetTranslation(vGlobal)
	
	#-------------------------------------------------------------------------
	# create a node stack #
	main_node 	= xsi.ActiveSceneRoot.AddNull('%s_Bunch' % basename)
	dnt_node 	= main_node.AddNull('%s_DoNotTouch' % basename)
	skel_node 	= main_node.AddNull('%s_Sekelton' % basename)
	con_node 	= main_node.AddNull('%s_Controls' % basename)
	
	main_node.primary_icon.Value = 0
	main_node.Properties('Visibility').Parameters('viewvis').Value = False
	main_node.Properties('Visibility').Parameters('rendvis').Value = False
	dnt_node.primary_icon.Value = 0 
	dnt_node.Properties('Visibility').Parameters('viewvis').Value = False 
	dnt_node.Properties('Visibility').Parameters('rendvis').Value = False 
	skel_node.primary_icon.Value = 0
	skel_node.Properties('Visibility').Parameters('viewvis').Value = False
	skel_node.Properties('Visibility').Parameters('rendvis').Value = False
	con_node.primary_icon.Value = 0
	con_node.Properties('Visibility').Parameters('viewvis').Value = False
	con_node.Properties('Visibility').Parameters('rendvis').Value = False
	
	#-------------------------------------------------------------------------
	# build a curve to shrink on the spline ik curve #
	
	# draw 2 curves, one for the control curve and one to shrink on top #
	crvLength = crv.Length
	pointCount = geom.Points.Count
	segmentLength = 1.0/(geom.Points.Count-1)*crvLength
	vCrv = XSIMath.CreateVector3()
	# build a point list #
	pointList = [0,0,0,1]
	for p in xrange(pointCount-1):
		pointList += [0, segmentLength*(p+1), 0, 1]
	
	# since the points are drawn through the control curve, add a bunch of points
	#  to lessen the deviation from the original curve
	pointList2 = [0,0,0,1]
	count = 25
	for p in xrange(count):
		segmentLength2 = 1.0/(count)*crvLength
		pointList2 += [0, segmentLength2*(p+1), 0, 1]
	
	# draw the curves #
	controlCurve = dnt_node.AddNurbsCurve(pointList)
	controlCurve.Name = '%s_SourceCurve' % basename
	shrinkCurve = dnt_node.AddNurbsCurve(pointList2)
	shrinkCurve.Name = '%s_ShrunkCurve' % basename
	
	# turn off the selectability of the source curve #
	controlCurve.Properties('Visibility').selectability.Value = 0
	shrinkCurve.Properties('Visibility').viewvis.Value = 0
	
	# put them in the out class #
	outClass.controlCurve = controlCurve
	outClass.shrinkCurve = shrinkCurve
	
	# shrink wrap the curve #
	op = xsi.ApplyOp('CrvDeform', '%s;%s' % (shrinkCurve.FullName, controlCurve.FullName),
	 					c.siNode, c.siPersistentOperation)
	
	# realign the control curve #
	controlCurve.ActivePrimitive.Geometry.Points.PositionArray = \
		geom.Points.PositionArray
		
	#--------------------------------------#
	# create control clusters on the control curve #
	controlGeom = controlCurve.ActivePrimitive.Geometry
	for p in xrange(controlGeom.Points.Count):
		
		# create the cluster #
		cls = controlGeom.AddCluster(c.siVertexCluster, '%s%s_Cls' % (basename, p), [p])
		
		# create the con #
		conStack = xsi.zCreateCon(con_node, '%sIk%s' % (basename, p), 'Mid', 0, 2*conSize, 1, 1, 0)
		
		# add a transform setup #
		ts = conStack(2).AddProperty('Transform Setup', False)
		ts = dispatch(ts)
		ts.tool.Value = 4
		ts.translate.Value = 2
		ts.xaxis.Value = True
		ts.yaxis.Value = True
		ts.zaxis.Value = True

		# align the stack to the point #
		pa = controlGeom.Points.PositionArray
		trans = conStack(1).Kinematics.Global.Transform
		localPointVector = XSIMath.CreateVector3(pa[0][p], pa[1][p], pa[2][p])
		localPointVector.AddInPlace(vGlobal)
		trans.SetTranslation(localPointVector)
		conStack(1).Kinematics.Global.Transform = trans
		
		# create the cluster centers #
		cls.CenterReference = conStack(3)
		
		# put the stacks in the out class #
		outClass.controls.append(conStack(1))
	
	#----------------------------------------#	
	# draw a quide line through the controls #
	pointList = []
	for con in outClass.controls:
		v = XSIMath.CreateVector3()
		con.Kinematics.Global.Transform.GetTranslation(v)
		pointList += [v.X, v.Y, v.Z, 1]
	guideCurve = dnt_node.AddNurbsCurve(pointList, None, False, 1)
	guideCurve.Name = '%s_CurveHull' % basename
	guideCurve.Properties('Visibility').selectability.Value = False
	outClass.guideCurve = guideCurve
	
	# create clusters at each center #
	guideClusters = dnt_node.AddNull('%s_HullClusters' % basename)
	guideClusters.primary_icon.Value = 0
	guideClusters.Properties('Visibility').Parameters('viewvis').Value = False
	guideClusters.Properties('Visibility').Parameters('rendvis').Value = False
	for p in xrange(guideCurve.ActivePrimitive.Geometry.Points.Count):
		# create the cluster #
		cls = guideCurve.ActivePrimitive.Geometry.AddCluster(c.siVertexCluster, '%sHull%s_Cls' % (basename, p), [p])
	
		# create a cluster center #
		clsCenter = guideClusters.AddNull('%s_HullClsCenter%s' % (basename, p))
		clsCenter.primary_icon.Value = 0
		clsCenter.Properties('Visibility').Parameters('viewvis').Value = False
		clsCenter.Properties('Visibility').Parameters('rendvis').Value = False
		
		# constrain it to the controller #
		clsCenter.Kinematics.AddConstraint('Pose', outClass.controls[p].Children(0).Children(0), False)
	
		# create the cluster centers #
		cls.CenterReference = clsCenter
	
	# add to the outClass #	
	outClass.guideClusterGroup = guideClusters
	
	#-------------------------------------------------------------------------	
	# build the skeleton #
	chainRootIk 	= None
	chainRootFk 	= None
	chainRootSkel 	= None
	vPrev 			= None
	wPercPrev 		= None
	shrinkCrv 		= shrinkCurve.ActivePrimitive.Geometry.Curves(0)
	weighted_percs	= [0.0] * (segments+1)
	# null_stack		= []
	for i in xrange(segments+1):
		# start #
		uValue = float(i)/float(segments)
		perc = uValue*100
		# get the weighted percentage #
		wPerc = fcv.Eval(perc)
		# store the weighted percentage #
		weighted_percs[i] = wPerc
		# start #
		if i == 0:
			# get the current positon on the curve #
			v = shrinkCrv.EvaluatePositionFromPercentage(0)[0]
			# add the global transform  to the current position on curve #
			v.AddInPlace(vGlobal)
			# store it as the previous position vector #
			vPrev = v
			log('Start: 0%% (w:%0.2f%%) Pos:<%0.2f, %0.2f, %0.2f>' % \
				(wPerc, v.X, v.Y, v.Z), c.siVerbose)
				
		else:
			# get the current positon on the curve #
			v = shrinkCrv.EvaluatePositionFromPercentage(wPerc)[0]
			# add the global transform  to the current position on curve #
			v.AddInPlace(vGlobal)
			log('%d: %0.2f%% (w:%0.2f%%) Pos:<%0.2f, %0.2f, %0.2f>' % \
				(i,perc,wPerc,v.X, v.Y, v.Z), c.siVerbose)
			# add the chain root if it doesn't exist #
			if not chainRootSkel:
				
				#-------------------------------------------------------------
				# draw the ik chain root #
				chainRootIk = dnt_node.Add2DChain(
					vPrev, v, XSIMath.CreateVector3(-1,0,0), 
					c.si2DChainNormalRadian
				)
				chainRootIk = dispatch(chainRootIk)
				# constrain the root to the path #
				cns = chainRootIk.Kinematics.AddConstraint('Path', shrinkCurve, False)
				
				# rename #
				chainRootIk.Name = '%sIk_Root' % basename
				chainRootIk.Bones(0).Name = '%s1Ik_Bone' % basename
				chainRootIk.effector.Name = '%sIk_Eff' % basename
				
				#-------------------------------------------------------------
				# draw the fk chain root #
				chainRootFk = con_node.Add2DChain(
					vPrev, v, XSIMath.CreateVector3(-1,0,0), 
					c.si2DChainNormalRadian
				)
				chainRootFk = dispatch(chainRootFk)
				# rename #
				chainRootFk.Name = '%sFk_Root' % basename
				chainRootFk.Bones(0).Name = '%s1Fk_Con' % basename
				chainRootFk.effector.Name = '%sFk_Eff' % basename

				#-------------------------------------------------------------
				# draw the skeleton chain root #
				chainRootSkel = skel_node.Add2DChain(
					vPrev, v, XSIMath.CreateVector3(-1,0,0), 
					c.si2DChainNormalRadian
				)
				chainRootSkel = dispatch(chainRootSkel)
				# rename #
				chainRootSkel.Name = '%s_Root' % basename
				chainRootSkel.Bones(0).Name = '%s1_Bone' % basename
				chainRootSkel.effector.Name = '%s_Eff' % basename
				
				#-------------------------------------------------------------
				# create fk switch on chain root #
				propAnim = chainRootFk.AddProperty('CustomProperty', False, 'zAnim')
				propAnim = dispatch(propAnim)
				fkswitch = propAnim.AddParameter3('Fk_Ik', c.siFloat, 1, 0, 1)
				twist 	 = propAnim.AddParameter3('Twist', c.siFloat, 0, -90, 90)
				
				# add to the out class #
				outClass.zAnim = propAnim
				
				# turn on the secondary display for the ik bone #
				bone_ik = dispatch(chainRootIk.bones(0))
				bone_ik.shadow_icon.Value = 1
				bone_ik.shadow_colour_custom.Value = 1
				
				bone_fk = dispatch(chainRootFk.bones(0))
				bone_fk.shadow_icon.Value = 1
				bone_fk.shadow_colour_custom.Value = 1

				# add a proxy param to the fk bone for the ik/fk slider #
				prop = bone_fk.AddProperty('CustomProperty', False, 'zAnim')
				prop = dispatch(prop)
				prop.AddProxyParameter(outClass.zAnim.Fk_Ik, None, 'Fk_Ik')
				
				propDi = bone_fk.AddProperty('CustomProperty', False, 'DisplayInfo_zAnim')
				propDi = dispatch(propDi)
				propDi.AddProxyParameter(outClass.zAnim.Fk_Ik, None, 'Fk_Ik')

				# add a transform setup to the bone #
				ts = bone_fk.AddProperty('Transform Setup', False)
				ts = dispatch(ts)
				ts.tool.Value = 3
				ts.rotate.Value = 3
				ts.xaxis.Value = True
				ts.yaxis.Value = True
				ts.zaxis.Value = True

			# all other bones #
			else:
				
				# add the bone #
				boneIk 		= chainRootIk.AddBone(v)
				boneFk 		= chainRootFk.AddBone(v)
				boneSkel 	= chainRootSkel.AddBone(v)
				
				# rename #
				segment_number 	= boneSkel.root.Bones.Count
				boneIk.Name 	= '%s%sIk_Bone' % (basename, segment_number)
				boneFk.Name 	= '%s%sFk_Con' 	% (basename, segment_number)
				boneSkel.Name 	= '%s%s_Bone' 	% (basename, segment_number)
				
				# turn on the secondary display for the boneIk #
				boneIk.shadow_icon.Value = 1
				boneIk.shadow_colour_custom.Value = 1
				
				boneFk.shadow_icon.Value = 1
				boneFk.shadow_colour_custom.Value = 1
				
				# add a proxy param to the fk bone for the ik/fk slider #
				prop = boneFk.AddProperty('CustomProperty', False, 'zAnim')
				prop = dispatch(prop)
				prop.AddProxyParameter(outClass.zAnim.Fk_Ik, None, 'Fk_Ik')
				
				propDi = boneFk.AddProperty('CustomProperty', False, 'DisplayInfo_zAnim')
				propDi = dispatch(propDi)
				propDi.AddProxyParameter(outClass.zAnim.Fk_Ik, None, 'Fk_Ik')
			
				# add a transform setup to the fk bone #
				ts = boneFk.AddProperty('Transform Setup', False)
				ts = dispatch(ts)
				ts.tool.Value = 3
				ts.rotate.Value = 3
				ts.xaxis.Value = True
				ts.yaxis.Value = True
				ts.zaxis.Value = True
				
		# store the previously weighted percentage #
		wPercPrev = wPerc

	#-------------------------------------------------------------------------
	# constraint the ik chain to the path
	for i in xrange(chainRootIk.Bones.Count):
		# add the path constraint #
		cns = chainRootIk.Bones(i).Kinematics.AddConstraint('Path', shrinkCurve, False)
		cns = dispatch(cns)
		cns.perc.Value = weighted_percs[i]
	# constrain the effector #
	cns = chainRootIk.effector.Kinematics.AddConstraint('Path', shrinkCurve, False)
	cns = dispatch(cns)
	cns.perc.Value = 100

	#-------------------------------------------------------------------------
	# create a twist heirarchy #
	twisters 	= dispatch('XSI.Collection')
	parent 		= dnt_node
	for i in xrange(chainRootIk.Bones.Count):
		# create the twist node #
		twist = parent.AddNull('%s%s_Twist' % (basename, i))
		# pose constrain it to the corresponding bone #
		cns = twist.Kinematics.AddConstraint('Pose', chainRootIk.Bones(i), False)
		cns = dispatch(cns)
		# add the twist #
		cns.rotx.AddExpression(
			'%s * %s / %s' % (outClass.zAnim.Twist.FullName, i+1, segments)
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
	cns_root_ik = chainRootSkel.Kinematics.AddConstraint('Pose', chainRootIk, False)
	cns_root_fk = chainRootSkel.Kinematics.AddConstraint('Pose', chainRootFk, False)
	cns_root_ik = dispatch(cns_root_ik)
	cns_root_fk = dispatch(cns_root_fk)
	cns_root_fk.cnspos.Value = False
	cns_root_ik.cnspos.Value = False
	cns_root_ik.blendweight.AddExpression(
		'1 - ' + propAnim.Fk_Ik.FullName
	)
	
	for i in xrange(chainRootSkel.Bones.Count):
		cns_bone_ik = chainRootSkel.Bones(i).Kinematics.AddConstraint('Pose', twisters(i), False)
		cns_bone_fk = chainRootSkel.Bones(i).Kinematics.AddConstraint('Pose', chainRootFk.Bones(i), False)
		cns_bone_ik = dispatch(cns_bone_ik)
		cns_bone_fk = dispatch(cns_bone_fk)
		cns_bone_fk.cnspos.Value = False
		cns_bone_ik.cnspos.Value = False
		# hook it up to the ik/fk slider 
		# since xsi constraints aren't blended like maya, we only need to 
		# hook up the expression to the second constraint, since at 100%
		# it'll take control
		cns_bone_fk.blendweight.AddExpression(
			'1 - ' + outClass.zAnim.Fk_Ik.FullName
		)
	
	#-------------------------------------------------------------------------
	# align the chain root #
	xsi.zgAlignChainRoot(chainRootIk)
	xsi.zgAlignChainRoot(chainRootFk)
	xsi.zgAlignChainRoot(chainRootSkel)
	
	# neutral pose the bones #
	col = dispatch('XSI.Collection')
	# for item in null_stack:
	# 	col.AddItems(item)
	col.AddItems(chainRootIk.Bones)
	col.AddItems(chainRootFk.Bones)
	col.AddItems(chainRootSkel.Bones)
	xsi.SetNeutralPose(col, c.siSRT, False)
		
	# put the effector under the last bone #
	chainRootIk.Bones(chainRootIk.Bones.Count-1).AddChild(chainRootIk.effector)
	chainRootFk.Bones(chainRootFk.Bones.Count-1).AddChild(chainRootFk.effector)
	chainRootSkel.Bones(chainRootSkel.Bones.Count-1).AddChild(chainRootSkel.effector)
	
	# turn off chain roots and effectors #
	chainRootIk.primary_icon.Value = 0
	chainRootIk.Properties('Visibility').Parameters('viewvis').Value = False
	chainRootIk.Properties('Visibility').Parameters('rendvis').Value = False
	chainRootFk.primary_icon.Value = 0
	chainRootFk.Properties('Visibility').Parameters('viewvis').Value = False
	chainRootFk.Properties('Visibility').Parameters('rendvis').Value = False
	chainRootSkel.primary_icon.Value = 0
	chainRootSkel.Properties('Visibility').Parameters('viewvis').Value = False
	chainRootSkel.Properties('Visibility').Parameters('rendvis').Value = False

	chainRootIk.effector.primary_icon.Value = 0
	chainRootIk.effector.Properties('Visibility').Parameters('viewvis').Value = False
	chainRootIk.effector.Properties('Visibility').Parameters('rendvis').Value = False
	chainRootFk.effector.primary_icon.Value = 0
	chainRootFk.effector.Properties('Visibility').Parameters('viewvis').Value = False
	chainRootFk.effector.Properties('Visibility').Parameters('rendvis').Value = False
	chainRootSkel.effector.primary_icon.Value = 0
	chainRootSkel.effector.Properties('Visibility').Parameters('viewvis').Value = False
	chainRootSkel.effector.Properties('Visibility').Parameters('rendvis').Value = False
	
	# turn fk bones into boxes #
	for bone in chainRootFk.Bones:
		bone = dispatch(bone)
		bone.primary_icon.Value = 6
	
	# turn skel bone into wedges #
	for bone in chainRootSkel.Bones:
		bone = dispatch(bone)
		bone.primary_icon.Value = 4
	
	# add the fkswitch to the cons #
	for con in outClass.controls:
		
		# add a proxy param to the bone to the ik/fk slider #
		prop = con.Children(0).AddProperty('CustomProperty', False, 'zAnim')
		prop = dispatch(prop)
		prop.AddProxyParameter(outClass.zAnim.Fk_Ik, None, 'Fk_Ik')
		prop.AddProxyParameter(outClass.zAnim.Twist, None, 'Twist')
		
		propDi = con.Children(0).AddProperty('CustomProperty', False, 'DisplayInfo_zAnim')
		propDi = dispatch(propDi)
		propDi.AddProxyParameter(outClass.zAnim.Fk_Ik, None, 'Fk_Ik')
		propDi.AddProxyParameter(outClass.zAnim.Twist, None, 'Twist')
		
	# put the root in the out class #
	outClass.chainRootIk = chainRootIk
	outClass.chainRootSkel = chainRootSkel
	
	# add the pickwalker to the controls #
	lastCon = None
	lastProp = None
	for con in outClass.controls:
		con = con.Children(0)
		# add the property #
		prop = con.AddProperty('zPickWalk')
		prop = dispatch(prop)
		# add the previous (up) con #
		if lastCon: prop.Up.Value = lastCon.Name
		# add the next (down) con #
		if lastProp: lastProp.Down.Value = con.Name
		# set the last con #
		lastCon = con
		# set the last prop #
		lastProp = prop
		
	# add the pickwalker to the bone controls #
	lastBone = None
	lastProp = None
	for bone in chainRootIk.bones:
		# add the property #
		prop = bone.AddProperty('zPickWalk')
		prop = dispatch(prop)
		# add the previous (up) con #
		if lastBone: prop.Up.Value = lastBone.Name
		# add the next (down) con #
		if lastProp: lastProp.Down.Value = bone.Name
		# set the last con #
		lastBone = bone
		# set the last prop #
		lastProp = prop
		
	# align the fk chain to the ik chain #
	chainRootFk.Kinematics.Global.Transform = chainRootIk.Kinematics.Global.Transform
	for b in xrange(chainRootFk.Bones.Count):
		bone_fk = dispatch(chainRootFk.Bones(b))
		bone_ik = dispatch(chainRootIk.Bones(b))
		bone_fk.Kinematics.Global.RotX.Value = bone_ik.Kinematics.Global.RotX.Value
		bone_fk.Kinematics.Global.RotY.Value = bone_ik.Kinematics.Global.RotY.Value
		bone_fk.Kinematics.Global.RotZ.Value = bone_ik.Kinematics.Global.RotZ.Value
	# export the python object #
	import win32com.server
	return win32com.server.util.wrap(outClass)

def zInitTailCurve_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	# oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments
	oArgs.AddObjectArgument("curve")
	oArgs.Add("inspect", c.siArgumentInput, True, c.siBool)

	return true


def zInitTailCurve_Execute(curve, inspect):
	
	# make sure we have a curve #
	if curve.Type != 'crvlist':
		raise Exception('Argument 1 is not a curve.')
		
	# install the property if it doesn't exist #
	prop = curve.Properties('zTailCurve')
	if not prop:
		prop = curve.AddProperty('zTailCurve')
	else:
		log('Curve "%s" all ready initialized.' % curve)
	
	# show the ppg #
	if inspect:
		xsi.InspectObj(prop, '', '', c.siLock)

	# return the property #
	return prop
	