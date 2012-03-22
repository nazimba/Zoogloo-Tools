"""
zSymConstraint.py

Created by  on 2008-03-27.
Copyright (c) 2008 Zoogloo LLC. All rights reserved.
"""


__version__ = '$Revision: 106 $'
__author__  = '$Author: andy $'
__date__    = '$Date: 2008-09-04 18:07 -0700 $'

import win32com.client
from win32com.client import constants
from win32com.client import constants as c
from win32com.client.dynamic import Dispatch as dispatch
xsi = Application
log = xsi.logmessage

null = None
false = 0
true = 1

class ChainException(Exception): pass

def XSILoadPlugin(in_reg):
	in_reg.Author = 'Andy Buecker'
	in_reg.Name = "zSymConstraint"
	in_reg.Email = ""
	in_reg.URL = ""
	try:
		in_reg.Major = int(__version__.split(' ')[1])
	except:
		in_reg.Major = 1
	in_reg.Minor = 0

	in_reg.RegisterOperator("zSymConstraint")
	
	in_reg.RegisterCommand("zApplySymConstraint")
	# in_reg.RegisterCommand("zRemoveSymConstraint")

	in_reg.RegisterMenu(c.siMenuMCPConstrainID, "zSymConstraintMenu", False, False)

	return True

def XSIUnloadPlugin(in_reg):
	strPluginName = in_reg.Name
	Application.LogMessage(str(strPluginName) + str(" has been unloaded."))
	return true


def zSymConstraintMenu_Init( in_ctxt ):
	oMenu = in_ctxt.Source
	oMenu.AddCommandItem( "zSymConstraint", "zApplySymConstraint" )

def zApplySymConstraint_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = "Apply a unidirectional symmetry constraint."
	# oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments
	oArgs.AddWithHandler("objects", c.siArgHandlerCollection)
	oArgs.AddObjectArgument("target")

	return true

def zApplySymConstraint_Execute(objects, target):
	
	# make sure we have some objects #
	if not objects.Count:
		log('No objects given.', c.siError)
		return False
	
	# pick the target #
	if not target:
		picker = xsi.PickElement(None, 'Pick Reference Object', 'Pick Reference Object')

		# catch the right click #
		if not picker[0]:
			log('Cancelled.', c.siWarning)
			return False
		
		# set the target #
		target = picker[2]
	
	# step through each object in the collection #
	for item in objects:
		
		# create the operator #
		newOp = XSIFactory.CreateObject('zSymConstraint')

		# add number of bones #
		# enable = newOp.AddParameter(
		# 	XSIFactory.CreateParamDef2("Mute", c.siBool, 1)
		# )
		axis = newOp.AddParameter(
			XSIFactory.CreateParamDef2("Axis", c.siString, 'XZ')
		)
		
		# add the target as the input port #
		newOp.AddInputPort(target.Kinematics.Global)
	
		# add the item as the output port #
		newOp.AddOutputPort(item.Kinematics.Global, 'ObjectGlobal')
		
		# connect the operator #
		newOp.Connect()

def zSymConstraint_Define(ctxt):
	oCustomOperator = ctxt.Source

	oCustomOperator.AlwaysEvaluate = false
	oCustomOperator.Debug = 0
	return true

def zSymConstraint_Init(ctxt):
	Application.LogMessage("zgDynamicSkeleton_Init called", c.siVerbose)
	
	# create two vector arrays to hold the point deltas #
	m_sym_yz = XSIMath.CreateMatrix4()
	m_sym_yz.Set(
		-1.0, 0.0, 0.0, 0.0,
		 0.0, 1.0, 0.0, 0.0,
		 0.0, 0.0, 1.0, 0.0,
		 0.0, 0.0, 0.0, 1.0 
	)
	
	# write the peristant user data #
	ctxt.UserData = [ 
		XSIMath.CreateMatrix4(), 		# result matrix
		XSIMath.CreateTransform(),		# reslut transform
		m_sym_yz						# reflection on the YZ plane
	]
	
	return true

def zSymConstraint_Update(ctxt):

	# get the variables #
	m_result 	= ctxt.UserData[0]
	trans_out 	= ctxt.UserData[1]
	# axis 		= ctxt.Source.Parameters('Axis').Value 	# not yet supported
	
	# get the reference node #
	ref = ctxt.GetInputValue(0)
	
	# get the matrix #
	m_in = ref.Transform.Matrix4

	m_result.Set(
		-m_in.Value(0,0),  m_in.Value(0,1),  m_in.Value(0,2), m_in.Value(0,3), 
		-m_in.Value(1,0),  m_in.Value(1,1),  m_in.Value(1,2), m_in.Value(1,3), 
		 m_in.Value(2,0), -m_in.Value(2,1), -m_in.Value(2,2), m_in.Value(2,3), 
		-m_in.Value(3,0),  m_in.Value(3,1),  m_in.Value(3,2), m_in.Value(3,3)
	)

	# set the transform from the matrix #
	trans_out.Matrix4 	= m_result

	# set the output #
	if ctxt.OutputPort.Name == "ObjectGlobal":
		ctxt.OutputPort.Value.Transform = trans_out	
