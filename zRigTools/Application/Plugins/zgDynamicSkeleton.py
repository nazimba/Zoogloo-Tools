'''
XSI Plugin to generate a dynamically adjustable skeleton.
'''
import win32com.client
from win32com.client import constants
from win32com.client import constants as c
from win32com.client.dynamic import Dispatch as dispatch

xsi = Application

null = None
false = 0
true = 1

def XSILoadPlugin(in_reg):
	in_reg.Author = "andy"
	in_reg.Name = "zgDynamicSkeleton"
	in_reg.Email = ""
	in_reg.URL = ""
	in_reg.Major = 0
	in_reg.Minor = 1
	
	in_reg.RegisterOperator("zgDynamicSkeleton")
	
	in_reg.RegisterCommand("zgApplyDynamicSkeleton")
	in_reg.RegisterCommand("zgRemoveDynamicSkeleton")

	#RegistrationInsertionPoint - do not remove this line

	return true

def XSIUnloadPlugin(in_reg):
	strPluginName = in_reg.Name
	# Application.LogMessage(str(strPluginName) + str(" has been unloaded."))
	return true


def zgApplyDynamicSkeleton_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = "Create an instance of ZooDynamicBone operator"
	oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments
	oArgs.AddWithHandler("object", c.siArgHandlerSingleObj)
	oArgs.Add("lockToPlane", c.siArgumentInput, False, c.siBool)
	
	return true

def zgApplyDynamicSkeleton_Execute(object, lockToPlane):

	if not object: object = xsi.selection(0)
	
	root = object
	
	if object.type == 'bone':
		root = object.root
		
	if object.type == 'eff':
		root = object.root

	# make sure we have a chain root #
	if not root or root.type != 'root':
		xsi.logmessage('No chain root specified.', c.siError)
		return False

	root = dispatch(root)
		
	# align the root to the first bone #
	boneTform = root.bones(0).kinematics.Global.transform
	root.kinematics.Global.transform = boneTform
	root.bones(0).kinematics.Global.transform = boneTform
	
	# cache the current root and effector displays #
	dynProp = None
	if not root.Properties('zgDynamicSkeleton'):
		dynProp = root.AddProperty('CustomProperty', False, 'zgDynamicSkeleton')
		dynProp.AddParameter3('rootDisplay', c.siUByte, 0, 0, 255, False, True)
		dynProp.AddParameter3('effDisplay', c.siUByte, 0, 0, 255, False, True)
		dynProp.AddParameter3('blendik', c.siFloat, 0, 0, 1, False, True)
		dynProp.AddParameter3('markers', c.siString, '', None, None, False, True)
			
	# create the operator #
	newOp = XSIFactory.CreateObject('zgDynamicSkeleton')

	# add number of bones #
	param = newOp.AddParameter(
		XSIFactory.CreateParamDef2("Bones", c.siInt4, 0, 0, 1000000)
	)
	param.Value = root.bones.Count
	
	# create a collection to hold the marks #
	marks = win32com.client.dynamic.Dispatch('XSI.Collection')
	
	# step through all the bones #
	lastMark = None
	for b in xrange(root.bones.Count):
	
		bone = dispatch(root).bones(b)
	
		# create a marker for the controller #
		mark = root.Parent.AddNull('%s_Mark' % bone.name)
		mark.kinematics.Global.transform = bone.kinematics.Global.transform
		marks.Add(mark)
		
		# add the marker to the inputs #
		newOp.AddInputPort(mark.kinematics.Global)
	
		# add the length to output #
		newOp.AddOutputPort(bone.Parameters('Length'), 'Length_%s_Out' % b)
		
		if lastMark:
			lastMark.kinematics.AddConstraint('Direction', mark, False)
			
		lastMark = mark
		
		# turn off the selectability of the bones #
		bone.Properties('Visibility').selectability.Value = False
		
	# add the root to the outputs #
	#newOp.AddOutputPort(root.kinematics.Global, 'rootGlobalOut')
	
	# add the effector to the output #
	#newOp.AddOutputPort(root.effector.kinematics.Global, 'effGlobalOut')
	
	# create a mark for the effector #
	mark = root.Parent.AddNull('%s_Mark' % root.effector.name)
	mark.kinematics.Global.transform = root.effector.kinematics.Global.transform
	#marks.Add(mark)
	
	# add the last direction constraint #
	lastMark.kinematics.AddConstraint('Direction', mark, False)
	
	# add the marker to the inputs #
	newOp.AddInputPort(mark.kinematics.Global)
	
	# connect it all up #
	newOp.Connect()
	
	# constrain the root #
	root.kinematics.AddConstraint('Pose', marks(0), False)
	
	# constrain the bones to the marks #
	# if not lockToPlane:
	if 1:
		for m in xrange(marks.Count):
			if m == 0: 
				continue
			root.bones(m).kinematics.AddConstraint('Orientation', marks(m), 
										False)
	
	# switch the chain to evaluate with fk only #
	dynProp.Parameters('blendik').Value = root.bones(0).Properties('Kinematic Chain').Parameters('blendik').Value
	root.bones(0).Properties('Kinematic Chain').Parameters('blendik').Value = 0		
	
	# add the effector to the marks collection #
	marks.Add(mark)
	
	# add an upvector #
	upNull = None
	if lockToPlane:
		midNul = root.Parent.AddNull('%s_midNul' % root.name)
		midCol = dispatch('XSI.Collection')
		midCol.Add(marks(0))
		midCol.Add(marks(marks.Count-1))
		cns = midNul.kinematics.AddConstraint('TwoPoints', midCol, False)
		cns = dispatch(cns)
		cns.UpVectorReference = marks(1)
		upNull = midNul.AddNull('%s_upNull' % root.name)
		upNull.kinematics.Global.transform = midNul.kinematics.Global.transform
		upNull.kinematics.Local.Parameters('PosY').Value = 20
		
		# change the display #
		upNull.primary_icon.Value = 0
		upNull.Properties('Visibility').Parameters('viewvis').Value = False
		upNull.Properties('Visibility').Parameters('rendvis').Value = False
		midNul.primary_icon.Value = 0
		midNul.Properties('Visibility').Parameters('viewvis').Value = False
		midNul.Properties('Visibility').Parameters('rendvis').Value = False
		

	# change the marker display #
	for mark in marks:
		disp = mark.AddProperty('Display Property', False)
		disp.Parameters('wirecol').Value = 708
		mark.Parameters('primary_icon').Value = 4
		mark.Parameters('shadow_icon').Value = 1
		mark.Parameters('shadow_colour_custom').Value = 1
		mark.Parameters('R').Value = .9
		mark.Parameters('G').Value = .7
		mark.Parameters('B').Value = .2
		
		tSetup = mark.AddProperty("Transform Setup", False)
		tSetup.Parameters('tool').Value = 4
		tSetup.Parameters('translate').Value = 2
		
		if lockToPlane and mark.Kinematics.Constraints.Count:
			cns = dispatch(mark.kinematics.Constraints(0))
			cns.UpVectorReference = upNull
			cns.upvct_active.Value = True
		
	# cache the display of the root and the effectors #
	dynProp.Parameters('rootDisplay').Value = root.Parameters('primary_icon').Value
	dynProp.Parameters('effDisplay').Value = root.effector.Parameters('primary_icon').Value
	
	# hide the root and eff #
	root.Parameters('primary_icon').Value = 0
	root.effector.Parameters('primary_icon').Value = 0
	
	# cache the names of the markers #
	dynProp.Parameters('markers').Value = marks.GetAsText()
	
	# select the first marker #
	xsi.SelectObj(marks(0))
	
	# return the new operator #
	outCol = dispatch('XSI.Collection')
	outCol.Add(newOp)
	outCol.AddItems(marks)
	return outCol

def zgDynamicSkeleton_Define(ctxt):
	oCustomOperator = ctxt.Source

	oCustomOperator.AlwaysEvaluate = false
	oCustomOperator.Debug = 0
	return true

def zgDynamicSkeleton_Init(ctxt):
	
	# create two vector arrays to hold the point deltas #
	ctxt.UserData = [ XSIMath.CreateVector3(), XSIMath.CreateVector3() ]
	
	return true

def zgDynamicSkeleton_Update(ctxt):

	# get the variables #
	v1 = ctxt.UserData[0]
	v2 = ctxt.UserData[1]
	num = ctxt.Source.Parameters('Bones').Value
	
	#xsi.logmessage('Count: %s' % cnt.Value)	
	
	for b in xrange(num):
	
		# calculate the bone length #
		ctxt.GetInputValue(b).transform.GetTranslation(v1)
		ctxt.GetInputValue(b+1).transform.GetTranslation(v2)
		v1.SubInPlace(v2)
		
		#xsi.logmessage('Length: %s' % v1.Length())
		#xsi.logmessage('Input: %s' % ctxt.GetInputValue(b))
		#xsi.logmessage('Output: %s' % ctxt.OutputPort.Name)
	
		outName = 'Length_%s_Out' % b
		#xsi.logmessage(outName)
		if ctxt.OutputPort.Name == outName:
			ctxt.OutputPort.Value = v1.Length()
		
	return true
def zgRemoveDynamicSkeleton_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true

	oArgs = oCmd.Arguments
	oArgs.AddWithHandler("object", c.siArgHandlerSingleObj)
	return true

def zgRemoveDynamicSkeleton_Execute(object):

	if not object: object = xsi.selection(0)
	
	root = object
	
	if object.type == 'bone':
		root = object.root
		
	if object.type == 'eff':
		root = object.root

	# make sure we have a chain root #
	if not root or root.type != 'root':
		xsi.logmessage('No chain root specified.', c.siError)
		return False

	root = dispatch(root)
	
	#
	cacheProp = root.Properties('zgDynamicSkeleton')
	if not cacheProp:
		xsi.logmessage('No "zgDynamicSkeleton" property found.', c.siError)
		return False
	
	# delete all the marks #
	delCol = win32com.client.dynamic.Dispatch('XSI.Collection')
	delCol.SetAsText(cacheProp.Parameters('markers').Value)
	
	# restore the properties #
	root.Parameters('primary_icon').Value = cacheProp.Parameters('rootDisplay').Value
	root.effector.Parameters('primary_icon').Value = cacheProp.Parameters('effDisplay').Value
	root.bones(0).Properties('Kinematic Chain').Parameters('blendik').Value = cacheProp.Parameters('blendik').Value
	
	# make the skeletons selectable #
	for bone in root.bones:
		bone = dispatch(bone)
		bone.Properties('Visibility').selectability.Value = True
	
	
	# delete the cache properties #
	delCol.Add(cacheProp)
	
	xsi.DeleteObj(delCol)

	return true

