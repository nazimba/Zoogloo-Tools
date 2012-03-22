"""
zMiddler.py

Created by andy on 2008-07-03.
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
	in_reg.Name = "zMiddler"
	in_reg.Email = "andy@zoogloo.net"
	in_reg.URL = ""
	try:
		in_reg.Major = int(__version__.split(' ')[1])
	except:
		in_reg.Major = 1
	in_reg.Minor = 0

	in_reg.RegisterOperator('zMiddlerOp')

	in_reg.RegisterCommand('zApplyMiddler', 'zApplyMiddler')
	in_reg.RegisterCommand('zCreateMiddler', 'zCreateMiddler')

	in_reg.RegisterMenu(c.siMenuMCPConstrainID, 'zMiddlerMenu', False)
	
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
def zMiddlerMenu_Init(ctxt):
	menu = ctxt.Source
	
	item = menu.AddCommandItem('zCreateMiddler', 'zCreateMiddler')
	item.Name = '(z) Create Middler'

#-----------------------------------------------------------------------------
# Operator
#-----------------------------------------------------------------------------
def zMiddlerOp_Define(ctxt):
	op = ctxt.Source
	
	# add a parameter #
	op.AddParameter(
		XSIFactory.CreateParamDef2("BlendWeight", c.siFloat, 0.5, 0.0, 1.0),
	)

	op.AlwaysEvaluate = false
	op.Debug = 0
	return true

def zMiddlerOp_Init(ctxt):
	# create vectors for the root to the target and rest + projected normals #
	ctxt.UserData = [
		XSIMath.CreateQuaternion(),
		XSIMath.CreateRotation(),
	]

	return true

def zMiddlerOp_Update(ctxt):

	# get the parameters #
	source 		= dispatch(ctxt.Source)
	mid_quat	= ctxt.UserData[0]
	out_rot 	= ctxt.UserData[1]

	# get the inputs #
	node_global 	= ctxt.GetInputValue(0)
	t1_global 		= ctxt.GetInputValue(1)
	t2_global		= ctxt.GetInputValue(2)
	weight		= ctxt.GetParameterValue('BlendWeight')
	
	# get the quaternions for both global transforms #
	t1_quat = t1_global.Transform.Rotation.Quaternion
	t2_quat = t2_global.Transform.Rotation.Quaternion

	# get teh mid point #
	mid_quat.Slerp(t1_quat, t2_quat, 0.5)

	# build the new transform #
	tfrm = node_global.Transform
	out_rot.Quaternion = mid_quat
	tfrm.Rotation = out_rot
	tfrm.Translation = t1_global.Transform.Translation

	# set the output value #
	ctxt.OutputPort.Value.Transform = tfrm
	
#-----------------------------------------------------------------------------
# Commands
#-----------------------------------------------------------------------------
def zApplyMiddler_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	#oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments
	oArgs.AddObjectArgument('node')
	oArgs.AddObjectArgument('transform1')
	oArgs.AddObjectArgument('transform2')

	return True
	
def zApplyMiddler_Execute(node, transform1, transform2):
	
	# create the operator #
	op = XSIFactory.CreateObject('zMiddlerOp')
	op = dispatch(op)
	
	# add the in and outports #
	op.AddOutputPort(node.Kinematics.Global)
	
	op.AddInputPort(node.Kinematics.Global)
	op.AddInputPort(transform1.Kinematics.Global)
	op.AddInputPort(transform2.Kinematics.Global)
	
	# connect it all up #
	op.Connect()
	
	# return the operator #
	return op

#-----------------------------------------------------------------------------

def zCreateMiddler_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	#oCmd.SetFlag(constants.siNoLogging,false)

	# oArgs = oCmd.Arguments
	# oArgs.AddObjectArgument('transform1')
	# oArgs.AddObjectArgument('transform2')
	# oArgs.Add('weight', c.siArgumentInput, 0.5, c.siFloat)

	return True
	
def zCreateMiddler_Execute():

	# pick the elements #
	transform1 = None
	transform2 = None
	picker = xsi.PickElement('', 'Pick the 1st Transform', 'Pick the 1st Transform')
	if not picker[0]:
		log('Cancelled.')
		return None
	transform1 = picker[2]
	picker = xsi.PickElement('', 'Pick the 2nd Transform', 'Pick the 2nd Transform')
	if not picker[0]:
		log('Cancelled.')
		return None
	transform2 = picker[2]

	# create a null #
	node = xsi.ActiveSceneRoot.AddNull('zMiddler')
	
	# install the operator #
	op = xsi.zApplyMiddler(node, transform1, transform2)
	
	# return the node #
	return node
	