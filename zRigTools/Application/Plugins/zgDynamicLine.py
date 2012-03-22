'''
Operator for creating a dynamic line.  Similar to cluster contraints but with out all the ugly nodes.
'''
import win32com.client
from win32com.client import constants
from win32com.client import constants as c
from win32com.client.dynamic import Dispatch as dispatch

xsi = Application

null = None
false = 0
true = 1

def XSILoadPlugin( in_reg ):
	in_reg.Author = "ab"
	in_reg.Name = "zgDynamicLine"
	in_reg.Email = ""
	in_reg.URL = ""
	in_reg.Major = 0
	in_reg.Minor = 5

	in_reg.RegisterOperator("zgDynamicLine")
	in_reg.RegisterCommand("zgApplyDynamicLine")
	
	#RegistrationInsertionPoint - do not remove this line

def XSIUnloadPlugin( in_reg ):
	strPluginName = in_reg.Name
	Application.LogMessage(str(strPluginName) + str(" has been unloaded."))
	return true

def zgApplyDynamicLine_Init( ctxt ):
	oCmd = ctxt.Source
	oCmd.Description = "Create an instance of ZooDynamicBone operator"
	oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments
	oArgs.AddWithHandler("objects","Collection")
	oArgs.Add( "close", c.siArgumentInput, False, c.siBool );

	return true

def zgApplyDynamicLine_Execute( objects, close ):
	
	# TODO: This generated code works by hardcoding the exact names of the
	# input and output objects.
	# If you want to operator to be applied to objects with different names
	# you way want to generalise this code to determine the objects
	# based on the Selection or the arguments to this command
	# 
	# Note: The AddCustomOp command is an alternative way to build the operator

	# generate a point array with the selected objects #
	pointArray = []
	v = XSIMath.CreateVector3()
	for obj in objects:
		obj.kinematics.Global.transform.GetTranslation( v )
		pointArray.append( v.X )
		pointArray.append( v.Y )
		pointArray.append( v.Z )
		pointArray.append( 1 )
	
	# draw a curve through the points #
	newCurve = xsi.ActiveSceneRoot.AddNurbsCurve( pointArray, None, close, 1 )
	
	# change it's color #
	prop = newCurve.AddProperty( 'Display Property', False )
	prop.Parameters( 'wirecol' ).Value = 742
	
	# create the operator #
	newOp = XSIFactory.CreateObject( 'zgDynamicLine' )
	
	# add the in and outports #
	newOp.AddOutputPort( newCurve.ActivePrimitive )
	for obj in objects:
		newOp.AddInputPort( obj.kinematics.Global )
		
	
	# add a parameter to store the number of input objects #
	param = dispatch( newOp.AddParameter(
		XSIFactory.CreateParamDef2("Num", c.siInt4, 0, 0, 1000)
	) )
	param.Value = objects.Count
	
	# connect it all up #
	newOp.Connect()
	
	# return the new operator #
	return newCurve

def zgDynamicLine_Define( ctxt ):
	oCustomOperator = ctxt.Source

	oCustomOperator.AlwaysEvaluate = false
	oCustomOperator.Debug = 0
	return true

def zgDynamicLine_Init( ctxt ):
	Application.LogMessage("ZooDynamicBone_Init called", c.siVerbose)
	
	# create two vector arrays to hold the point deltas #
	#ctxt.UserData = [ XSIMath.CreateVector3(), XSIMath.CreateVector3() ]
	
	return true

def zgDynamicLine_Term( ctxt ):
	Application.LogMessage("ZooDynamicBone_Term called", c.siVerbose)
	return true

def zgDynamicLine_Update( ctxt ):

	# get the number of input object #	
	num = dispatch( ctxt.Source ).Parameters('Num').Value
	
	# build a point position array #
	x = [0]*num
	y = [0]*num
	z = [0]*num
	pointArray = [x,y,z]
	
	# step through each input #
	for i in xrange( num ):
		#xsi.logmessage( ctxt.GetInputValue(i) )
		posArray = ctxt.GetInputValue(i).transform.GetTranslationValues2()
		pointArray[0][i] = posArray[0]
		pointArray[1][i] = posArray[1]
		pointArray[2][i] = posArray[2]

	# set the output position array #		
	ctxt.OutputPort.Value.Geometry.ControlPoints.PositionArray = pointArray
	
	
	return true

