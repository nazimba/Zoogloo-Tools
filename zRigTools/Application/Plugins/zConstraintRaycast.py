"""
XSI Plugin for the command and menu to add a raycast constraint.  The reulting
node is constrained to the surface where the ray intersects the surface from
the the center of the geometry to the target transform.

>>> # requires 3 inputs
>>> # 1. the geometry
>>> # 2. the node to use as the target
>>> # 3. the node to use for the result on the surface
>>> cns_rcast = Application.zApplyRaycastCns(node_geom, node_target, node_result)

Created by Andy Buecker on 2008-09-18.
Copyright (c) 2008 Zoogloo LLC. All rights reserved.
"""

__version__ = '$Revision: 185 $'
__author__  = '$Author: andy $'
__date__    = '$Date: 2009-02-06 21:04 -0800 $'

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
	in_reg.Name = "zConstraintRaycast"
	in_reg.Email = "andy@zoogloo.net"
	in_reg.URL = ""
	in_reg.Major = 1
	try:
		in_reg.Minor = int(__version__.split(' ')[1])
	except:
		in_reg.Minor = 0
	

	in_reg.RegisterCommand('zApplyRaycastCns', 'zApplyRaycastCns')
	in_reg.RegisterCommand('zApplyRaycastCnsFromMenu', 'zApplyRaycastCnsFromMenu')

	in_reg.RegisterMenu(c.siMenuMCPConstrainID, 'zConstraintRaycastMenu', False)
	
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
def zConstraintRaycastMenu_Init(ctxt):
	menu = ctxt.Source
	item = menu.AddCommandItem('zApplyRaycastCnsFromMenu', 'zApplyRaycastCnsFromMenu')
	item.Name = '(z) Raycast Constraint'

#-----------------------------------------------------------------------------
# Commands
#-----------------------------------------------------------------------------
def zApplyRaycastCns_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	#oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments
	oArgs.AddObjectArgument('node_geom')
	oArgs.AddObjectArgument('node_target')
	oArgs.AddObjectArgument('node_result')

	return True
	
def zApplyRaycastCns_Execute(node_geom, node_target, node_result):
	
	# create the operator #
	op = XSIFactory.CreateObject('zCnsRaycastOp')
	op = dispatch(op)
	
	# add the in and outports #
	op.AddOutputPort(node_result.Kinematics.Global)
	
	op.AddInputPort(node_geom.ActivePrimitive)
	op.AddInputPort(node_geom.Kinematics.Global)
	op.AddInputPort(node_target.Kinematics.Global)
	
	# connect it all up #
	op.Connect()
	
	# return the operator #
	return op

#-----------------------------------------------------------------------------
def zApplyRaycastCnsFromMenu_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.SetFlag(c.siNoLogging, True)

	return True
	
def zApplyRaycastCnsFromMenu_Execute():
	
	# make sure something is selected #
	if not xsi.selection.Count:
		log('Please pick an object to constrain to the surface first.', c.siError)
		return False
	
	# pick the geometry #
	picker = xsi.PickElement(c.siGeometryFilter, 'Pick the geometry', 'Pick the geometry')
	if not picker[0]: return False
	node_geom = picker[2]
	
	# pick the target node #
	picker = xsi.PickElement(None, 'Pick the node to raycast to', 'Pick the node to raycast to')
	if not picker[0]: return False
	node_target = picker[2]

	# step through each item #
	for item in xsi.selection:
		# apply the contraint #
		xsi.zApplyRaycastCns(node_geom, node_target, item)
