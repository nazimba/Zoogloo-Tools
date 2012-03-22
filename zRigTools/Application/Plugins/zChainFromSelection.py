'''
XSI Plugin to build a chain from the current selection in the order they were picked.

>>> chain_root = Application.BuildChainFromSel()
'''
import win32com.client
from win32com.client import constants
from win32com.client import constants as c

xsi = Application
null = None
false = 0
true = 1

def XSILoadPlugin( in_reg ):
	in_reg.Author = "Andy"
	in_reg.Name = "zChainFromSelection"
	in_reg.Email = ""
	in_reg.URL = ""
	in_reg.Major = 1
	in_reg.Minor = 0

	
	in_reg.RegisterCommand("Build Chain From Sel", "zBuildChainFromSelection")
	#RegistrationInsertionPoint - do not remove this line

	return true

def XSIUnloadPlugin( in_reg ):
	strPluginName = in_reg.Name
	Application.LogMessage(str(strPluginName) + str(" has been unloaded."))
	return true

def BuildChainFromSel_Init( ctxt ):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true

	return true

def BuildChainFromSel_Execute(  ):
	''' return the chain root '''

	# make sure we have a proper selecton #
	if xsi.selection.Count < 2:
		xsi.logmessage( 'Need 2 or more objects selected to create a chain.', c.siError )
		return False
		
	# get the property page #
	prop = xsi.ActiveSceneRoot.Properties( 'zooBuildChainFromSelection' )
	
	# build the property if it doesn't exist #
	if not prop:
		prop = xsi.ActiveSceneRoot.AddProperty( 'CustomProperty', false, 'zooBuildChainFromSelection' )
		prop.AddParameter3( 'Name', c.siString, 'bone' )
		prop.AddParameter3( 'Symmetry', c.siString, 'Lft' )
		prop.AddParameter3( 'EndString', c.siString, 'Bone' )


	# Inspect the ppg #
	result = xsi.InspectObj( prop, '', 'Build Chain From Selection', c.siModal, False )
	if result:
		xsi.logmessage( 'User cancelled.', c.siWarning )
		return False

	# get the values from the ppg #
	boneName = prop.Parameters( 'Name' ).Value
	symmetry = prop.Parameters( 'Symmetry' ).Value
	endString = prop.Parameters( 'EndString' ).Value

	# create vectors #	
	v1 = XSIMath.CreateVector3()
	v2 = XSIMath.CreateVector3()
	v3 = XSIMath.CreateVector3()
	v12 = XSIMath.CreateVector3()
	v13 = XSIMath.CreateVector3()

	# calculate a default cross product #
	crossProduct = XSIMath.CreateVector3()
	xsi.selection(0).kinematics.Global.transform.GetTranslation( v1 )
	xsi.selection(1).kinematics.Global.transform.GetTranslation( v2 )
	
	# get a vector in y along the local axis, assuming #
	trans = xsi.selection(0).kinematics.Global.transform
	trans.AddLocalTranslation( XSIMath.CreateVector3( 0, 1, 0) )
	trans.GetTranslation( v3 )
	
	v12.Sub( v1, v2 )
	v13.Sub( v1, v3 )

	# calculate the cross product #
	crossProduct.Cross( v12, v13 )
	
	# calculate the cross product on 2 or more vectors #
	if xsi.selection.Count > 2:
		xsi.selection( xsi.selection.Count-1 ).kinematics.Global.transform.GetTranslation( v3 )
		v12.Sub( v1, v2 )
		v13.Sub( v1, v3 )
		crossProduct.Cross( v13, v12 )
	

	root = None
	for i in range( xsi.selection.Count ):

		currentName = '%s%s_%s_%s' % (boneName, i, symmetry, endString)

		if i==0:
			xsi.selection(i).kinematics.Global.Transform.GetTranslation( v1 )
			xsi.selection(i+1).kinematics.Global.Transform.GetTranslation( v2 )
#			v_plain.Cross( v1, v2 )
			root = xsi.ActiveSceneRoot.Add2DChain( v1, v2, crossProduct, 3, '%s_%s_Chain' % (boneName, symmetry) )
			root.bones(0).Name = '%s1_%s_Bone' % (boneName, symmetry )
			root.effector.Name = '%s_%s_Eff' % (boneName, symmetry )
		
		elif i>1:
			xsi.selection(i).kinematics.Global.Transform.GetTranslation( v3 )
			root.AddBone( v3, 1, '%s%s_%s_Bone' % (boneName, i, symmetry )	)

	# parent the effector under the last bone #
	root.bones( root.bones.Count-1 ).AddChild( root.effector )
	
	# align the root #
	transBone1 = root.Bones(0).Kinematics.Global.Transform
	root.kinematics.Global.Transform = transBone1
	root.Bones(0).Kinematics.Global.Transform = transBone1
	root.Bones(0).Kinematics.Local.Parameters('rotx').Value = 0
	root.Bones(0).Kinematics.Local.Parameters('roty').Value = 0
	root.Bones(0).Kinematics.Local.Parameters('rotz').Value = 0
	

