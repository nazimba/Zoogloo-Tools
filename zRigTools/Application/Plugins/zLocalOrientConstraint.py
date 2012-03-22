#===============================================================================
# Lock Down
# Copyright 2006 Zoogloo LLC. All rights reserved.
# This plugin is provided AS IS and WITHOUT WARRANTY
#===============================================================================

import win32com.client
import win32com
from win32com.client import constants
from win32com.client import constants as c
from win32com.client.dynamic import Dispatch as dispatch

xsi = Application

null = None
false = 0
true = 1

log = xsi.logmessage

def XSILoadPlugin(in_reg):
	in_reg.Author = "Andy Buecker"
	in_reg.Name = "zLocalOrientConstraint"
	in_reg.Email = "andy@zoogloo.net"
	in_reg.URL = ""
	in_reg.Major = 1
	in_reg.Minor = 0

	
	in_reg.RegisterCommand("zLocalOrientConstraint", "zLocalOrientConstraint")
	
	
	in_reg.RegisterMenu(c.siMenuMCPConstrainID, "zLocalOrientConstraintMenu", False, False)
	in_reg.RegisterMenu(c.siMenuSEConstraintContextID, "zLocalOrientConstraintMenu", False, False)

	#RegistrationInsertionPoint - do not remove this line

	return true

def XSIUnloadPlugin(in_reg):
	strPluginName = in_reg.Name
	Application.LogMessage(str(strPluginName) + str(" has been unloaded."))
	return true

def zLocalOrientConstraintMenu_Init( in_ctxt ):
	oMenu = in_ctxt.Source
	oMenu.AddCommandItem( "&Local Orientation", "zLocalOrientConstraint" )
	
def zLocalOrientConstraint_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = "Local Orientation Constraint"
	oCmd.ReturnValue = true

#	oArgs = oCmd.Arguments
#	oArgs.Add("filename",constants.siArgumentInput)
#	oArgs.Add("appendEnv",constants.siArgumentInput, True, c.siBool)
	return true

def zLocalOrientConstraint_Execute():
		
		# make sure we have something selected #
		if not xsi.selection.Count:
			xsi.logmessage('Please select an item.', c.siError)
			return False
			
		# pick the constraining item #
		picker = xsi.PickElement(None, 'Pick the Constraining Object')
		if not picker[0]:
			return
		objCns = picker[2]
		
		# constrain #
		obj = xsi.selection(0)
		
		log('%s --> %s' % (obj, objCns))

		# cache the transform #
		origTransform = obj.Kinematics.Global.Transform
		
		# determine if comensation is on #
		comp = xsi.GetUserPref("SI3D_CONSTRAINT_COMPENSATION_MODE")
		
		cns = obj.Kinematics.AddConstraint('Pose', objCns, comp)
		cns = dispatch(cns)
		cns.cnspos.Value = False
		cns.cnsscl.Value = False
		
		# apply the original transform #
		obj.Kinematics.Global.Transform = origTransform
		
		return cns
		
			
