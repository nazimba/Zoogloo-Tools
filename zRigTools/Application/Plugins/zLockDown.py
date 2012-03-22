#===============================================================================
# Lock Down
# Copyright 2006 Zoogloo LLC. All rights reserved.
# This plugin is provided AS IS and WITHOUT WARRANTY
#===============================================================================

import win32com.client
import win32com
from win32com.client import constants
from win32com.client import constants as c

xsi = Application

null = None
false = 0
true = 1

def XSILoadPlugin( in_reg ):
	in_reg.Author = "Andy Buecker"
	in_reg.Name = "Zoo Lock Down"
	in_reg.Email = "andy@zoogloo.net"
	in_reg.URL = ""
	in_reg.Major = 1
	in_reg.Minor = 0

	
	in_reg.RegisterCommand( "Lock Down", "ZLockDown" )
	
	
	# in_reg.RegisterMenu( c.siMenuMainTopLevelID, "LockDownMenu" )
	in_reg.RegisterMenu( c.siMenuSEGeneralContextID, "LockDownMenu", False, False )
	in_reg.RegisterMenu( c.siMenu3DViewObjectContextID, "LockDownMenu", False, False )
	in_reg.RegisterMenu( c.siMenuSEObjectContextID, "LockDownMenu", False, False )
	in_reg.RegisterMenu( c.siMenu3DViewGeneralContextID, "LockDownMenu", False, False )

	
	xsi.logmessage( "\n------------------------------------------\n  Lock Down Plugin for XSI.\n  Copyright 2006 Zoogloo LLC.\n  All rights Reserved.\n------------------------------------------\n" )
	
	#RegistrationInsertionPoint - do not remove this line

	return true

def XSIUnloadPlugin( in_reg ):
	strPluginName = in_reg.Name
	Application.LogMessage(str(strPluginName) + str(" has been unloaded."))
	return true

def LockDownMenu_Init( in_ctxt ):
	oMenu = in_ctxt.Source
	oMenu.AddCommandItem( "&Lock Down", "Lock Down" )


def LockDown_Init( ctxt ):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true

#	oArgs = oCmd.Arguments
#	oArgs.Add("filename",constants.siArgumentInput)
#	oArgs.Add("appendEnv",constants.siArgumentInput, True, c.siBool )
	return true

def LockDown_Execute():

	locks = win32com.client.Dispatch( "XSI.Collection" )
	
	# step through the selection #
	for node in xsi.selection:
		
		if not node.Properties( 'zLockDown' ):
			
			# create a new lock down node #
			lockNull = xsi.ActiveSceneRoot.AddNull( 'zLockDown_%s' % node.Name )
			
			# match the global transform #
			lockNull.kinematics.Global.transform = node.kinematics.Global.transform
			
			# change the display #
			lockNull.Parameters( 'shadow_icon' ).Value = 2
			lockNull.Parameters( 'shadow_colour_custom' ).Value = 1
			lockNull.Parameters( 'R' ).Value = 1
			lockNull.Parameters( 'Size' ).Value = .02
			lockNull.Properties( 'Visibility' ).Parameters( 'selectability' ).Value = False
			
			# add the pose constraint #
			poseConstraint = node.kinematics.AddConstraint( 'Pose', lockNull, False )
			
			# add a custom property to the locked object #
			prop = node.AddProperty( 'CustomProperty', False, 'zLockDown' )
			
			# cache the lock parameters #
			prop.AddParameter3( 'LockObject', c.siString, lockNull.Fullname )
			prop.AddParameter3( 'LockConstraint', c.siString, prop.Fullname )
			
		else:
			
			# get the locking object #
			prop = xsi.PyFix( node.Properties( 'zLockDown' ) )
			lockCollection = win32com.client.Dispatch( 'XSI.Collection' )
			lockCollection.SetAsText( prop.Parameters( 'LockObject' ).Value )
			
			# add it to the locks collection #
			locks.AddItems( lockCollection )
			
			# add the property to the locks collection #
			locks.Add( prop )
			
	# cleanup the locks #
	if locks.Count > 0: xsi.DeleteObj( locks )
			
			
