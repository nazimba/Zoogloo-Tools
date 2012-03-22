"""
XSI Plugin for creating a dino leg for use on JFC.

>>> # create the guide #
>>> Application.zDinoLegGuide()
>>> # build the leg #
>>> Application.zDinoLegRig('left')

Created by andy on 2007-06-12.
Copyright (c) 2007 Zoogloo LLC. All rights reserved.
"""
import win32com.client
from win32com.client import constants
from win32com.client import constants as c
from win32com.client.dynamic import Dispatch as dispatch
import copy

null = None
false = 0
true = 1

xsi = Application
log = xsi.logmessage

# controller point list #
footCONPoints = [
	[-1.115, -1.115, -1.115, -1.115, -1.115, 1.115, 1.115, -1.115, -1.115, 1.115, 1.115, 1.115, 1.115, 1.115, 1.115, -1.115], 
	[-0.32900000000000001, 0.63400000000000001, -1.54, -1.54, -0.32900000000000001, -0.32900000000000001, 0.63400000000000001, 0.63400000000000001, -1.54, -1.54, 0.63400000000000001, -0.32900000000000001, -1.54, -1.54, -1.54, -1.54], 
	[1.625, -0.096000000000000002, -0.096000000000000002, 1.625, 1.625, 1.625, -0.096000000000000002, -0.096000000000000002, -0.096000000000000002, -0.096000000000000002, -0.096000000000000002, 1.625, 1.625, -0.096000000000000002, 1.625, 1.625], 
	[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
]
hindlegCONPoints = [
	[1.5569999999999999, 1.353, 1.883, 1.99, 1.78, 1.6659999999999999, 1.5109999999999999, 1.3180000000000001, 1.0940000000000001, 0.84199999999999997, 0.94099999999999995, 0.191, 0.64000000000000001, 0.73599999999999999, 0.95599999999999996, 1.153, 1.321, 1.4570000000000001, 1.5569999999999999], 
	[0.51500000000000001, 0.44800000000000001, -0.083000000000000004, 0.65900000000000003, 0.58899999999999997, 0.86099999999999999, 1.111, 1.333, 1.5229999999999999, 1.675, 1.873, 1.875, 1.274, 1.4650000000000001, 1.3320000000000001, 1.1659999999999999, 0.97099999999999997, 0.753, 0.51500000000000001], 
	[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 
	[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
]
hindfootCONPoints = [
	[-0.92700000000000005, -0.92700000000000005, -0.92700000000000005, -0.92700000000000005, -0.92700000000000005, 0.92700000000000005, 0.92700000000000005, -0.92700000000000005, -0.92700000000000005, 0.92700000000000005, 0.92700000000000005, 0.92700000000000005, 0.92700000000000005, 0.92700000000000005, 0.92700000000000005, -0.92700000000000005], 
	[0.0040000000000000001, 0.0040000000000000001, -0.68300000000000005, -0.68300000000000005, 0.0040000000000000001, 0.0040000000000000001, 0.0040000000000000001, 0.0040000000000000001, -0.68300000000000005, -0.68300000000000005, 0.0040000000000000001, 0.0040000000000000001, -0.68300000000000005, -0.68300000000000005, -0.68300000000000005, -0.68300000000000005], 
	[-0.001, -1.9239999999999999, -1.9239999999999999, -0.001, -0.001, -0.001, -1.9239999999999999, -1.9239999999999999, -1.9239999999999999, -1.9239999999999999, -1.9239999999999999, -0.001, -0.001, -1.9239999999999999, -0.001, -0.001], 
	[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
]

def XSILoadPlugin( in_reg ):
	in_reg.Author = "Andy"
	in_reg.Name = "zDinoLeg"
	in_reg.Email = ""
	in_reg.URL = ""
	in_reg.Major = 0
	in_reg.Minor = 1

	
	# in_reg.RegisterProperty('zCon')
	in_reg.RegisterCommand('zDinoLegGuide', 'zDinoLegGuide')
	in_reg.RegisterCommand('zDinoLegRig', 'zDinoLegRig')
	
	#RegistrationInsertionPoint - do not remove this line

	return true
	
def XSIUnloadPlugin( in_reg ):
	strPluginName = in_reg.Name
	Application.LogMessage(str(strPluginName) + str(" has been unloaded."))
	return true
	
def zDinoLegGuide_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true
	oCmd.SetFlag(c.siNoLogging, False)
	
	# oArgs = oCmd.Arguments
	# oArgs.AddWithHandler('ppg', c.siArgHandlerSingleObj)
	return true

	
def zDinoLegGuide_Execute():
	
	log('Arse')
	model = xsi.ActiveSceneRoot.AddModel(None, 'DinoLegGuide')
	
	vRoot   = XSIMath.CreateVector3()
	vKnee1 = XSIMath.CreateVector3()
	vKnee2 = XSIMath.CreateVector3()
	vAnkle   = XSIMath.CreateVector3()
	vBall   = XSIMath.CreateVector3()
	vToe1   = XSIMath.CreateVector3()
	vToe2   = XSIMath.CreateVector3()
	vEff   = XSIMath.CreateVector3()
	
	vRoot.Set(0.000, 4.972, 0.021)	
	vKnee1.Set(0.0, 1.341, 3.424)	
	vKnee2.Set(0.0, -1.768, -1.135)	
	vAnkle.Set(0.000, -3.465, 0.392)	
	vBall.Set(0.000, -4.318, 1.271)	
	vToe1.Set(0.000, -4.374, 1.816)	
	vToe2.Set(0.000, -4.600, 2.437)	
	vEff.Set(0.000, -4.581, 3.359)
	
	# calculate the plane #
	v1 = XSIMath.CreateVector3()
	v2 = XSIMath.CreateVector3()
	vPlane = XSIMath.CreateVector3()
	
	v1.Sub(vRoot, vEff)
	v2.Sub(vRoot, vKnee2)
	vPlane.Cross(v1, v2)
	
	# draw the guide chain #
	root = model.Add2DChain(vRoot, vKnee1, vPlane,
								c.si2DChainNormalRadian,
								'leg_Root')
	root.bones(0).Name = 'legA_Bone'
	root.effector.Name = 'leg_Eff'
	
	root.AddBone(vKnee2, c.siChainBonePin, 'legB_Bone')
	root.AddBone(vAnkle, c.siChainBonePin, 'legC_Bone')
	root.AddBone(vBall, c.siChainBonePin, 'ankle_Bone')
	root.AddBone(vToe1, c.siChainBonePin, 'pivot_Bone')
	root.AddBone(vToe2, c.siChainBonePin, 'toeA_Bone')
	root.AddBone(vEff, c.siChainBonePin, 'toeB_Bone')
	
	# create knee1 joint area #
	knee1Area = root.AddPrimitive('Cube', 'knee1_Area')
	knee1Area.length.Value = 1
	knee1Area.kinematics.AddConstraint('Position', root.bones(1), False)
	pose = knee1Area.kinematics.AddConstraint('Pose', root.bones(0), False)
	pose = dispatch(pose)
	pose.cnspos.Value = False
	pose.cnsscl.Value = False
	pose = knee1Area.kinematics.AddConstraint('Pose', root.bones(1), False)
	pose = dispatch(pose)
	pose.cnspos.Value = False
	pose.cnsscl.Value = False
	pose.blendweight.Value = 0.5
	
	expr = '%s.length*2.5' % knee1Area.FullName
	knee1Area.Kinematics.Local.Parameters('scly').AddExpression(expr)
	
	# create knee2 joint area #
	knee2Area = root.AddPrimitive('Cube', 'knee2_Area')
	knee2Area.length.Value = 1
	knee2Area.kinematics.AddConstraint('Position', root.bones(2), False)
	pose = knee2Area.kinematics.AddConstraint('Pose', root.bones(1), False)
	pose = dispatch(pose)
	pose.cnspos.Value = False
	pose.cnsscl.Value = False
	pose = knee2Area.kinematics.AddConstraint('Pose', root.bones(2), False)
	pose = dispatch(pose)
	pose.cnspos.Value = False
	pose.cnsscl.Value = False
	pose.blendweight.Value = 0.5
	
	expr = '%s.length*2.5' % knee2Area.FullName
	knee2Area.Kinematics.Local.Parameters('scly').AddExpression(expr)
	
	# make it dynamic #
	xsi.zgApplyDynamicSkeleton(root, True)
	
	# turn off constraint comp #
	xsi.SetUserPref("SI3D_CONSTRAINT_COMPENSATION_MODE", 0)

def zDinoLegRig_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true
	oCmd.SetFlag(c.siNoLogging, False)
	
	oArgs = oCmd.Arguments
	oArgs.Add('sym', c.siArgumentInput)
	return true

	
def zDinoLegRig_Execute(sym):
	
	guide = xsi.ActiveSceneRoot.FindChild('DinoLegGuide', c.siModelType)
	
	# get the leg bone #
	root = guide.FindChild('leg_Root')
	
	# remove the dynamic leg #
	# xsi.zgRemoveDynamicSkeleton(root)

	# get the vectors #
	vRoot   = XSIMath.CreateVector3()
	vKnee1  = XSIMath.CreateVector3()
	vKnee1A = XSIMath.CreateVector3()
	vKnee1B = XSIMath.CreateVector3()
	vKnee2  = XSIMath.CreateVector3()
	vKnee2A = XSIMath.CreateVector3()
	vKnee2B = XSIMath.CreateVector3()
	vAnkle  = XSIMath.CreateVector3()
	vPivot  = XSIMath.CreateVector3()
	vBall   = XSIMath.CreateVector3()
	vToe   = XSIMath.CreateVector3()
	vEff    = XSIMath.CreateVector3()
	
	# populate the vectors #
	root.Kinematics.Global.Transform.GetTranslation(vRoot)
	root.bones(1).Kinematics.Global.Transform.GetTranslation(vKnee1)
	root.bones(2).Kinematics.Global.Transform.GetTranslation(vKnee2)
	root.bones(3).Kinematics.Global.Transform.GetTranslation(vAnkle)
	root.bones(4).Kinematics.Global.Transform.GetTranslation(vPivot)
	root.bones(5).Kinematics.Global.Transform.GetTranslation(vBall)
	root.bones(6).Kinematics.Global.Transform.GetTranslation(vToe)
	root.effector.Kinematics.Global.Transform.GetTranslation(vEff)
	
	# create nulls for the leg rig #
	group = xsi.ActiveSceneRoot.AddNull(xsi.zMapName('DinoLeg', 'Group', sym))
	group.primary_icon.Value = 0
	group.Properties('Visibility').Parameters('viewvis').Value = False
	group.Properties('Visibility').Parameters('rendvis').Value = False
	
	controls = group.AddNull('Controls')
	controls.primary_icon.Value = 0
	controls.Properties('Visibility').Parameters('viewvis').Value = False
	controls.Properties('Visibility').Parameters('rendvis').Value = False
	
	skeleton = group.AddNull('Skeleton')
	skeleton.primary_icon.Value = 0
	skeleton.Properties('Visibility').Parameters('viewvis').Value = False
	skeleton.Properties('Visibility').Parameters('rendvis').Value = False
	
	# calculate the leg plane #
	v1 = XSIMath.CreateVector3()
	v2 = XSIMath.CreateVector3()
	vPlane = XSIMath.CreateVector3()
	
	v1.Sub(vRoot, vEff)
	v2.Sub(vRoot, vKnee2)
	vPlane.Cross(v2, v1)
	
	# get the knee1A pos #
	kneeArea1 = guide.FindChild('knee1_Area')
	kneeTrans1 = kneeArea1.Kinematics.Global.Transform
	area1 = kneeArea1.length.Value
	kneeTrans1.AddLocalTranslation(XSIMath.CreateVector3(area1/-2, 0, 0))
	kneeTrans1.GetTranslation(vKnee1A)
	
	# get the knee1B pos #
	kneeTrans1.AddLocalTranslation(XSIMath.CreateVector3(area1, 0, 0))
	kneeTrans1.GetTranslation(vKnee1B)
	
	# get the knee2A pos #
	kneeArea2 = guide.FindChild('knee2_Area')
	kneeTrans2 = kneeArea2.Kinematics.Global.Transform
	area2 = kneeArea2.length.Value
	kneeTrans2.AddLocalTranslation(XSIMath.CreateVector3(area2/-2, 0, 0))
	kneeTrans2.GetTranslation(vKnee2A)
	
	# get the knee2B pos #
	kneeTrans2.AddLocalTranslation(XSIMath.CreateVector3(area2, 0, 0))
	kneeTrans2.GetTranslation(vKnee2B)
	
	# draw the hindleg #
	hindlegRoot =  skeleton.Add2DChain(vRoot, vKnee1A, vPlane, 
								c.si2DChainNormalRadian,
								xsi.zMapName('hindleg', 'ChainRoot', sym))
	hindlegRoot.bones(0).Name = xsi.zMapName('hindleg1', 'ChainBone', sym)
	hindlegRoot.effector.Name = xsi.zMapName('hindleg', 'ChainEff', sym)
	hindlegRoot.AddBone(vKnee1B, c.siChainBonePin, 
					xsi.zMapName('hindleg2', 'ChainBone', sym))
	hindlegRoot.AddBone(vKnee2A, c.siChainBonePin, 
					xsi.zMapName('hindleg3', 'ChainBone', sym))
	hindlegRoot.AddBone(vKnee2B, c.siChainBonePin, 
					xsi.zMapName('hindleg4', 'ChainBone', sym))
	xsi.zFormatChainFromPrefs(hindlegRoot)
	
	# calculate the length of the hindleg #
	legLength = 0.0
	for bone in hindlegRoot.bones:
		bone = dispatch(bone)
		legLength += bone.length.Value
	log('HindLeg length: %s' % legLength)
	
	# draw the knee con #
	# kneeStack = xsi.zCreateCon(controls, 'Knee_CON', 'Mid', 0, 1, 1, 1, 0)
	con_knee 		= xsi.zCon()
	con_knee.type	= 'round_box'
	con_knee.Draw()
	kneeStack = dispatch('XSI.Collection')
	kneeStack.Add(con_knee.node_rest)
	kneeStack.Add(con_knee.node_rest)
	kneeStack.Add(con_knee.node_con)
	kneeStack.Add(con_knee.node_hook)
	trans = hindlegRoot.bones(1).Kinematics.Global.Transform
	trans.AddLocalTranslation(XSIMath.CreateVector3(0, 10, 0))
	trans.SetRotation(XSIMath.CreateRotation())
	kneeStack(1).Kinematics.Global.Transform = trans
	
	# metatarsal #
	metaRoot = skeleton.Add2DChain(vAnkle, vKnee2B, vPlane, 
							c.si2DChainNormalRadian,
							xsi.zMapName('metatarsal', 'ChainRoot', sym))
	metaRoot.bones(0).Name = xsi.zMapName('metatarsal', 'ChainBone', sym)
	metaRoot.effector.Name = xsi.zMapName('metatarsal', 'ChainEff', sym)
	legLength += metaRoot.bones(0).length.Value
	xsi.zFormatChainFromPrefs(metaRoot)
	
	# calculate a point to draw the phantom through #
	trans = hindlegRoot.bones(1).Kinematics.Global.Transform
	trans.AddLocalTranslation(XSIMath.CreateVector3(0, -10, 0))
	trans.SetRotation(XSIMath.CreateRotation())
	vPhantomKnee = XSIMath.CreateVector3()
	trans.GetTranslation(vPhantomKnee)
	
	# draw the phantom leg #
	phantomRoot = skeleton.Add2DChain(vRoot, vPhantomKnee, vPlane,
							c.si2DChainNormalRadian,
							xsi.zMapName('hindLegPhantom', 'ChainRoot', sym))
	phantomRoot.bones(0).Name = xsi.zMapName('hindLegPhantom1', 'ChainBone', sym)
	phantomRoot.effector.Name = xsi.zMapName('hindLegPhantom', 'ChainEff', sym)
	phantomRoot.AddBone(vAnkle, c.siChainBonePin, 
					xsi.zMapName('hindLegPhantom2', 'ChainBone', sym))
					
	xsi.zFormatChainFromPrefs(phantomRoot)
	
	# draw the hindfoot #
	hindFootRoot = skeleton.Add2DChain(vPivot, vAnkle, vPlane, 
								c.si2DChainNormalRadian,
								xsi.zMapName('hindfoot', 'ChainRoot', sym))
	hindFootRoot.bones(0).Name = xsi.zMapName('hindfoot', 'ChainBone', sym)
	hindFootRoot.effector.Name = xsi.zMapName('hindfoot', 'ChainEff', sym)
	xsi.zFormatChainFromPrefs(hindFootRoot)
	
	# draw the toe #
	toeHome = skeleton.AddNull(xsi.zMapName('toe', 'Home', sym))
	toeHome.primary_icon.Value = 0
	toeHome.Properties('Visibility').Parameters('viewvis').Value = False
	toeHome.Properties('Visibility').Parameters('rendvis').Value = False
	trans = toeHome.Kinematics.Global.Transform
	trans.SetTranslation(vBall)
	toeHome.Kinematics.Global.Transform = trans
	
	toeRoot = toeHome.Add2DChain(vBall, vToe, vPlane, 
								c.si2DChainNormalRadian,
								xsi.zMapName('toeA', 'ChainRoot', sym))
	toeRoot.bones(0).Name = xsi.zMapName('toeA1', 'ChainBone', sym)
	toeRoot.effector.Name = xsi.zMapName('toeA', 'ChainEff', sym)
	toeRoot.AddBone(vEff, c.siChainBonePin, 
				xsi.zMapName('toeA2', 'ChainBone', sym))
	xsi.zFormatChainFromPrefs(toeRoot)
	
	# create a foot con #
	footCon = controls.AddNurbsCurve(footCONPoints, None, False, 1)
	footCon.Name = xsi.zMapName('foot', 'Control', sym)
	trans = footCon.Kinematics.Global.Transform
	trans.SetTranslation(vAnkle)
	footCon.Kinematics.Global.Transform = trans
	
	footHook = footCon.AddNull(xsi.zMapName('foot', 'Hook', sym))
	footHook.primary_icon.Value = 0
	footHook.Properties('Visibility').Parameters('viewvis').Value = False
	footHook.Properties('Visibility').Parameters('rendvis').Value = False
	footHook.Kinematics.Global.Transform = footCon.Kinematics.Global.Transform
	
	footRest = controls.AddNull(xsi.zMapName('foot', 'Home', sym))
	footRest.primary_icon.Value = 0
	footRest.Properties('Visibility').Parameters('viewvis').Value = False
	footRest.Properties('Visibility').Parameters('rendvis').Value = False
	footRest.Kinematics.Global.Transform = footCon.Kinematics.Global.Transform
	
	footRest.AddChild(footCon)
	
	# add the knee zero con #
	kneeZero = controls.AddNull(xsi.zMapName('knee', 'Zero', sym))
	kneeZero.Kinematics.Global.Transform = footCon.Kinematics.Global.Transform
	kneeZero.Kinematics.Local.Parameters('roty').AddExpression('%s.kine.local.roty' % footCon.FullName)
	kneeZero.AddChild(kneeStack(1))
	cns = kneeZero.Kinematics.AddConstraint('Pose', footHook, True)
	cns = dispatch(cns)
	cns.cnsori.Value = False
	
	# create the foot roll con #
	footRollRest = footHook.AddNull(xsi.zMapName('hindfootRoll', 'Home', sym))
	footRollRest.primary_icon.Value = 0
	footRollRest.Properties('Visibility').Parameters('viewvis').Value = False
	footRollRest.Properties('Visibility').Parameters('rendvis').Value = False
	trans = footRollRest.Kinematics.Global.Transform
	trans.SetTranslation(vPivot)
	footRollRest.Kinematics.Global.Transform = trans
	
	footRollCon = footRollRest.AddNurbsCurve(hindfootCONPoints, None, False, 1)
	footRollCon.Name = xsi.zMapName('hindfootRoll', 'Control', sym)
	footRollCon.Kinematics.Global.Transform = footRollRest.Kinematics.Global.Transform
	
	footRollHook = footRollCon.AddNull(xsi.zMapName('hindfootRoll', 'Hook', sym))
	footRollHook.primary_icon.Value = 0
	footRollHook.Properties('Visibility').Parameters('viewvis').Value = False
	footRollHook.Properties('Visibility').Parameters('rendvis').Value = False
	footRollHook.Kinematics.Global.Transform = footRollCon.Kinematics.Global.Transform
	
	# constrain the phantom leg effector to the foot con #
	phantomRoot.effector.Kinematics.AddConstraint('Pose', footRollHook, True)

	# set the length of the phantom leg #
	phantomRoot.bones(0).length.Value = legLength/2
	phantomRoot.bones(1).length.Value = legLength/2
	
	# draw the hindleg con #
	hindRest = footHook.AddNull(xsi.zMapName('hindleg', 'Home', sym))
	hindRest.primary_icon.Value = 0
	hindRest.Properties('Visibility').Parameters('viewvis').Value = False
	hindRest.Properties('Visibility').Parameters('rendvis').Value = False
	trans = hindRest.Kinematics.Global.Transform
	trans.SetTranslation(vAnkle)
	trans.AddLocalRotation(XSIMath.CreateRotation(0, XSIMath.DegreesToRadians(90), 0))
	hindRest.Kinematics.Global.Transform = trans
	
	hindCon = hindRest.AddNurbsCurve(hindlegCONPoints, None, False, 1)
	hindCon.Name = xsi.zMapName('hindleg', 'Control', sym)
	hindCon.Kinematics.Global.Transform = hindRest.Kinematics.Global.Transform
	
	hindHook = hindCon.AddNull(xsi.zMapName('hindleg', 'Hook', sym))
	hindHook.Kinematics.Global.Transform = hindCon.Kinematics.Global.Transform
	
	# constrain the hindleg rest to the hindleg eff $
	trans = hindRest.Kinematics.Global.Transform
	hindRest.Kinematics.AddConstraint('Pose', phantomRoot.effector, True)
	xsi.SetUserPref("SI3D_CONSTRAINT_COMPENSATION_MODE", 1)
	hindRest.Kinematics.Global.Transform = trans
	xsi.SetUserPref("SI3D_CONSTRAINT_COMPENSATION_MODE", 0)
	
	# pose constrain the hindleg eff to the meta eff #
	hindlegRoot.effector.Kinematics.AddConstraint('Position', 
									metaRoot.effector, False)

	# constrain the meta root to the roll #
	metaRoot.Kinematics.AddConstraint('Pose', footRollHook, True)
	
	# constrain the meta bone to the hind leg hook #
	metaRoot.bones(0).Kinematics.AddConstraint('Pose', hindHook, True)
	
	# constrain the toe home to the foot hook #
	toeHome.Kinematics.AddConstraint('Pose', footHook, True)
	
	# constrain the hind foot to the foot hook #
	hindFootRoot.Kinematics.AddConstraint('Pose', footHook, True)
	
	hindFootRoot.effector.Kinematics.AddConstraint('Position', metaRoot, True)
	
	# do the skel up vectors #
	xsi.ApplyOp("SkeletonUpVector", "%s;%s" % \
				(hindlegRoot.bones(0), kneeStack(3)), 3, 
				c.siPersistentOperation, "", 0)
	xsi.ApplyOp("SkeletonUpVector", "%s;%s" % \
				(phantomRoot.bones(0), kneeStack(3)), 3, 
				c.siPersistentOperation, "", 0)
	xsi.ApplyOp("SkeletonUpVector", "%s;%s" % \
				(metaRoot.bones(0), kneeStack(3)), 3, 
				c.siPersistentOperation, "", 0)
	
	
							
	
	
	
	
	
	
	
