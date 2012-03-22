'''
Depreciated XSI Plugin for create a grip (controller) stack.  Use zCon plugin instead.
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
	in_reg.Name = "zCreateGripStack"
	in_reg.Email = ""
	in_reg.URL = ""
	in_reg.Major = 1
	in_reg.Minor = 0

	
	in_reg.RegisterCommand("Create Grip Stack", "zCreateGripStack",)
	#RegistrationInsertionPoint - do not remove this line

	return true

def XSIUnloadPlugin( in_reg ):
	strPluginName = in_reg.Name
	Application.LogMessage(str(strPluginName) + str(" has been unloaded."))
	return true

def CreateGripStack_Init( ctxt ):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true

	return true

def CreateGripStack_Execute(  ):

	# make sure we have a selection #
	if not xsi.selection.Count:
		xsi.logmessage( 'Nothing selected.', c.siError )
		return

	# create a collection to hold the selection #
	selected = win32com.client.Dispatch( 'XSI.Collection' )
	selected.AddItems( xsi.selection )
	xsi.DeselectAll()
	
	# step through each node #
	for node in selected:
		
		# get the name #
		nameSplit = node.Name.split('_')[:-1]
		
		# build the base name #
		import string
		baseName = string.join( nameSplit, '_' )
		
		# build a ppg #
		prop = xsi.PyFix( xsi.ActiveSceneRoot.AddProperty( 'CustomProperty', False, 'ZooCreateGripStack' ) )
		baseNameParam = prop.AddParameter3( 'Base Name', c.siString, baseName )
		state = xsi.InspectObj( prop, '', 'Zoo Create Grip Stack', c.siModal, false )
		if state:
			xsi.logmessage( 'Cancelled.', c.siWarning )
			xsi.DeleteObj( prop )
			return False
			
		# get the new name #
		baseNameParam = xsi.PyFix( baseNameParam )
		baseName = baseNameParam.Value
		
		# delete the ui #
		xsi.DeleteObj( prop )
		
		# add a rest null #
		restNull = node.Model.AddNull( '%s_Rest' % baseName )
		#restNull.Parameters( 'primary_icon' ).Value = 0
		restNull.selected = True
		
		# add a grip null #
		gripNull = restNull.AddNull( '%s_Grip' % baseName )
		gripNull = xsi.PyFix( gripNull )
		gripNull.Parameters( 'primary_icon' ).Value = 4
				
		# add a hook null #
		hookNull = gripNull.AddNull( '%s_Hook' % baseName )
		hookNull.Parameters( 'primary_icon' ).Value = 0
		
		# match the transform #
		vector = XSIMath.CreateVector3()
		node.kinematics.Global.transform.GetTranslation( vector )
		trans = restNull.kinematics.Global.transform
		trans.SetTranslation( vector )
		restNull.kinematics.Global.transform = trans
		
		#restNull.kinematics.Global.transform = node.kinematics.Global.transform
		
		
	return true

