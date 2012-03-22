'''
Depreciated.  XSI Plugin for generating component based rigs. However,
zgAlignChainRoot is a usefull tool for aligning the root of a chain to the 
first bone.
'''
import win32com.client
from win32com.client import constants
from win32com.client import constants as c
from win32com.client.dynamic import Dispatch as dispatch
import sre

# import the zoo flo #
zgPath = r'C:\Documents and Settings\ab\My Documents\workspace\zooFlo\src'
import sys
if not zgPath in sys.path: sys.path.append( zgPath )

xsi = Application

null = None
false = 0
true = 1

def XSILoadPlugin( in_reg ):
	in_reg.Author = "andy"
	in_reg.Name = "zgRigUtils"
	in_reg.Email = ""
	in_reg.URL = ""
	in_reg.Major = 1
	in_reg.Minor = 0

	
	in_reg.RegisterCommand( "zgInitRigBuilder", "zgInitRigBuilder" )
	
	in_reg.RegisterCommand("zgGuides", "zgGuides")
	in_reg.RegisterCommand("zgGetGuide", "zgGetGuide")
	
	in_reg.RegisterCommand("zgFlats", "zgFlats")
	in_reg.RegisterCommand("zgNewFlat","zgNewFlat")
	in_reg.RegisterCommand("zgGetFlat","zgGetFlat")
	
	in_reg.RegisterCommand("zgAddRestNode","zgAddRestNode")
	in_reg.RegisterCommand("zgAlignChainRoot","zgAlignChainRoot")

##################

	in_reg.RegisterCommand("zgNewPackGuide", "zgNewPackGuide")

	in_reg.RegisterProperty( "zgCharacter" ) 
	in_reg.RegisterCommand("zgGetAllCharacters","zgGetAllCharacters")
	in_reg.RegisterCommand("zgAddCharacter","zgAddCharacter")
	
	in_reg.RegisterProperty( "zgGuide" ) 
	in_reg.RegisterCommand("zgGetAllGuides", "zgGetAllGuides")
	in_reg.RegisterCommand("zgAddGuide", "zgAddGuide")
	
	in_reg.RegisterProperty( "zgFlat" ) 
	in_reg.RegisterCommand("zgGetAllFlats", "zgGetAllFlats")
	in_reg.RegisterCommand("zgAddFlat", "zgAddFlat")
	
	in_reg.RegisterCommand("zgGetAllPackGuides", "zgGetAllPackGuides")
	in_reg.RegisterCommand("zgGetAllPackFlats", "zgGetAllPackFlats")

	in_reg.RegisterCommand("zgListAllPacks", "zgListAllPacks")

	#RegistrationInsertionPoint - do not remove this line

	return true

def XSIUnloadPlugin( in_reg ):
	strPluginName = in_reg.Name
	Application.LogMessage(str(strPluginName) + str(" has been unloaded."))
	return true


def zgGuide_Define( ctxt ):
	
	prop = ctxt.Source
	typ  = prop.AddParameter3( 'GuideName', c.siString, '', None, None, False, True )

	return True
	
def zgGuide_DefineLayout( ctxt ):
	
	lay = ctxt.Source
	lay.Clear()
	
	lay.AddGroup("")
	lay.AddItem("GuideName", 'Name' )
	lay.EndGroup()

	return True


def zgGetAllGuides_Init( ctxt ):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true
	oCmd.SetFlag( c.siNoLogging, True )
	
	oArgs = oCmd.Arguments
	oArgs.AddWithHandler( "character", c.siArgHandlerSingleObj )

	return true

def zgGetAllGuides_Execute( character ):
	''' Gets all the guides for a character '''
	
	# verify the model #
	if not character or character.type != '#model' or \
	not character.Properties( 'zgCharacter' ):
		xsi.logmessage( 'Character argument incorrect.', c.siError )
		return False
	
	# create an output collection #
	outCol = xsi.zgNewCol()
	
	# find all the guides for the character #
	allModels = character.FindChildren( '*', c.siModelType )
	for model in allModels:
		if model.Properties( 'zgGuide' ):
			outCol.Add( model )
	
	# return the output collection #
	return outCol

def zgListAllPacks_Init( ctxt ):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true
	oCmd.SetFlag( c.siNoLogging, True )
	
#	oArgs = oCmd.Arguments
#	oArgs.AddWithHandler( "character", c.siArgHandlerSingleObj )

	return true

def zgListAllPacks_Execute():
	''' list all packs available to the system '''
	
	# create a output list #
	outList = []
	# step through the plugins #
	import sre
	for plugin in xsi.Plugins:
		if sre.match( '^zgPack_', plugin.Name ): 
#			xsi.logmessage( plugin )
			outList.append( plugin.Name )

	# return the outlist #	
	return outList


def zgAddGuide_Init( ctxt ):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true
	oCmd.SetFlag( c.siNoLogging, True )
	
	oArgs = oCmd.Arguments
	oArgs.AddWithHandler( "character", c.siArgHandlerSingleObj )
	oArgs.Add( "guideName", c.siArgumentInput )

	return true

def zgAddGuide_Execute( character, guideName ):
	'''add's a guide to the character'''
	
	# create a new guide #
	guideModel = character.AddModel( None, guideName )
	prop = guideModel.AddProperty( 'zgGuide', False )
	prop = dispatch( prop )
	prop.Parameters('GuideName').Value = guideName
	
	# return the character models #
	return guideModel
	


def zgFlat_Define( ctxt ):
	
	prop = ctxt.Source
	typ  = prop.AddParameter3( 'FlatName', c.siString, '', None, None, False, True )

	return True
	
def zgFlat_DefineLayout( ctxt ):
	
	lay = ctxt.Source
	lay.Clear()
	
	lay.AddGroup("")
	lay.AddItem("FlatName", 'Name' )
	lay.EndGroup()

	return True

def zgGetAllFlats_Init( ctxt ):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true
	oCmd.SetFlag( c.siNoLogging, True )
	
	oArgs = oCmd.Arguments
	oArgs.AddWithHandler( "character", c.siArgHandlerSingleObj )

	return true

def zgGetAllFlats_Execute( character ):
	''' Gets all the flat for a character '''
	# verify the model #
	if not character or character.type != '#model' or \
	not character.Properties( 'zgCharacter' ):
		xsi.logmessage( 'Character argument incorrect.', c.siError )
		return False
	
	# create an output collection #
	outCol = xsi.zgNewCol()
	
	# find all the guides for the character #
	allModels = character.FindChildren( '*', c.siModelType )
	for model in allModels:
		if model.Properties( 'zgFlat' ):
			outCol.Add( model )
	
	# return the output collection #
	return outCol
	
def zgAddFlat_Init( ctxt ):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true
	oCmd.SetFlag( c.siNoLogging, True )
	
	oArgs = oCmd.Arguments
	oArgs.AddWithHandler( "character", c.siArgHandlerSingleObj )
	oArgs.Add( "flatName", c.siArgumentInput )

	return true

def zgAddFlat_Execute( character, flatName ):
	'''add's a guide to the character'''
	
	# create a new guide #
	flatModel = character.AddModel( None, flatName )
	prop = flatModel.AddProperty( 'zgFlat', False )
	prop = dispatch( prop )
	prop.Parameters('FlatName').Value = flatName
	
	# return the character models #
	return flatModel
	








def zgGuides_Init( ctxt ):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true

	oArgs = oCmd.Arguments
	oArgs.Add( "rigBuilder", c.siArgumentInput )

	return true

def zgGuides_Execute( rigBuilder ):
	''' finds all zgGuide models in the scene.  
	If none found, creates and returns one '''
	
	if not rigBuilder:
		xsi.logmessage()

	# find the guide model in scenet #
	outCol = win32com.client.dynamic.Dispatch( 'XSI.Collection' )
	
	# find all the models in the scene #
	models = xsi.ActiveSceneRoot.FindChildren( '*', c.siModelType)
	
	# step through the models looking for a zgGuides tag #
	for model in models:
		if model.Properties( 'zgGuides' ): outCol.Add( model )
		
	# make a model if we haven't found one #
	if not outCol.Count:
		guides = xsi.ActiveSceneRoot.AddModel( None, 'zgGuides' )
		guides.AddProperty( 'CustomProperty', False, 'zgGuides' )
		guides.AddProperty( 'zgNameMap', False )
		outCol.Add( guides )
		
	
	return outCol

def zgNewPackGuide_Init( ctxt ):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true

	oArgs = oCmd.Arguments
	oArgs.Add("guideName", c.siArgumentInput, 'zgGuide', c.siString )
	oArgs.AddWithHandler( "guideModel", "SingleObj")
	return true

def zgNewPackGuide_Execute( guideName, guideModel ):

	Application.LogMessage("zgNewGuide_Execute called")
	
	# make sure this is a guide model #
	if not guideModel.Properties( 'zgGuide' ):
		xsi.logmessage( '%s is not a zgGuide model.', c.siError )
		return False
	
	# make sure this guide doesn't all ready exist #
	kids = guideModel.FindChildren('*', c.siModelType)
	for kid in kids:
		prop = kid.Properties('zgPackGuide')
		if prop:
			prop = dispatch( prop )
			if prop.Parameters( 'PackGuideName' ).Value == guideName:
				xsi.logmessage( 'Guide "%s" all ready exists in "%s"' % (guideName, guideModel.FullName), c.siWarning )
				return False
				
	
	# add the guide model #
	guide = dispatch( guideModel.AddModel( '', guideName ) )
	
	# tag it #
	prop = guide.AddProperty('CustomProperty', False, 'zgPackGuide' )
	prop.AddParameter3( 'PackGuideName', c.siString, guideName, None, None, False, True )
	
	# add a tag to the guide #
	prop = guideModel.AddProperty('CustomProperty', False, guideName )
	prop.AddParameter3( 'PackGuideModel', c.siString, guide, None, None, False, True )
	
	# return the guide model #
	return guide

def zgGetGuide_Init( ctxt ):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true

	oArgs = oCmd.Arguments
	oArgs.Add("guideName",constants.siArgumentInput)
	return true

def zgGetGuide_Execute( guideName ):

	# step through all the models in the scene #
	for model in xsi.ActiveSceneRoot.FindChildren( '*', c.siModelType ):
		prop = model.Properties( 'zgGuide' )
		if prop:
			prop = dispatch( prop )
			if prop.Parameters('GuideName').Value == guideName:
				# return the guide #
				return model

	# return False if the model isn't found #
	xsi.logmessage( 'Unable to find Guide "%s".' % guideName, c.siError)
	return False

def zgFlats_Init( ctxt ):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true

	return true

def zgFlats_Execute(  ):
	''' finds all zgFlat models in the scene.  
	If none found, creates and returns one '''

	# find the guide model in scenet #
	outCol = win32com.client.dynamic.Dispatch( 'XSI.Collection' )
	
	# find all the models in the scene #
	models = xsi.ActiveSceneRoot.FindChildren( '*', c.siModelType)
	
	# step through the models looking for a zgGuides tag #
	for model in models:
		if model.Properties( 'zgFlats' ): outCol.Add( model )
		
	# make a model if we haven't found one #
	if not outCol.Count:
		guides = xsi.ActiveSceneRoot.AddModel( None, 'zgFlats' )
		guides.AddProperty( 'CustomProperty', False, 'zgFlats' )
		outCol.Add( guides )
		
	return outCol
def zgNewFlat_Init( ctxt ):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true

	oArgs = oCmd.Arguments
	oArgs.Add("flatName",constants.siArgumentInput)
	oArgs.AddWithHandler( "flatModel", "SingleObj")
	return true

def zgNewFlat_Execute( flatName, flatModel ):

	# get the guides in the scene #
	if not flatModel:
		flatModel = xsi.zgFlats()(0)
		
	# make sure this is a guides model #
	if not flatModel.Properties( 'zgFlats' ):
		xsi.logmessage( '%s is not a zgFlats model.', c.siError )
		return False
	
	# make sure this guide doesn't all ready exist #
	kids = flatModel.FindChildren('*', c.siModelType)
	for kid in kids:
		prop = kid.Properties('zgFlat')
		if prop:
			prop = dispatch( prop )
			if prop.Parameters( 'FlatName' ).Value == flatName:
				xsi.logmessage( 'Flat "%s" all ready exists in "%s"' % (flatName, flatModel.FullName), c.siError )
				return False
				
	
	# add the flat model #
	flat = dispatch( flatModel.AddModel( '', flatName ) )
	
	# tag it #
	prop = flat.AddProperty('CustomProperty', False, 'zgFlat' )
	prop.AddParameter3( 'FlatName', c.siString, flatName )
	
	# return the guide model #
	return flat


def zgGetFlat_Init( ctxt ):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true

	oArgs = oCmd.Arguments
	oArgs.Add("flatName",constants.siArgumentInput)
	return true

def zgGetFlat_Execute( flatName ):

	# step through all the models in the scene #
	for model in xsi.ActiveSceneRoot.FindChildren( '*', c.siModelType ):
		prop = model.Properties( 'zgFlat' )
		if prop:
			prop = dispatch( prop )
			if prop.Parameters('FlatName').Value == flatName:
				# return the guide #
				return model

	# return False if the model isn't found #
#	xsi.logmessage( 'Unable to find Flat "%s".' % flatName, c.siError)
	return False

def zgAddRestNode_Init( ctxt ):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true

	oArgs = oCmd.Arguments
	oArgs.AddWithHandler("node","SingleObj")
	oArgs.Add("restName", c.siArgumentInput, None, c.siString )
	oArgs.Add("display", c.siArgumentInput, 0, c.siBool )
	return true

def zgAddRestNode_Execute( node, restName, display ):

	# precondidtions #
	if not node:
		xsi.logmessage( 'No node provided', c.siError )
		return False
	
	# build the new name #
	newName = restName
	if not newName:
		splits = node.Name.split('_')
		if len(splits) <= 1:
			newName = node.Name
		else:
			splits = splits[:-1]
			newName = '%s_Rest' % '_'.join( splits )
		
	# add the rest node #
	restNode = node.parent.AddNull( newName )
	restNode = dispatch( restNode )
	
	# align the rest node #
	restNode.kinematics.Global.transform = node.kinematics.Global.transform
	
	# reparent the node #
	restNode.AddChild( node )
	
	# set the display #
	if not display:
		restNode.Parameters( 'primary_icon' ).Value = 0
	
	# return the rest node #
	return restNode

def zgAlignChainRoot_Init( ctxt ):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true

	oArgs = oCmd.Arguments
	oArgs.AddWithHandler( "root", "SingleObj")
	return true

def zgAlignChainRoot_Execute( root ):
	
	root = win32com.client.dynamic.Dispatch( root )
	
	if not root or root.type != 'root':
		xsi.logmessage( 'No Chain Root as argument.', c.siError )
		return False
	
	# align the chain root #
	boneTrans = root.bones(0).kinematics.Global.transform
	root.kinematics.Global.transform = boneTrans
	root.bones(0).kinematics.Global.transform = boneTrans

	return True



def zgInitRigBuilder_Init( ctxt ):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true

	oArgs = oCmd.Arguments
	oArgs.Add( "rigName", c.siArgumentInput )
	oArgs.Add( "create", c.siArgumentInput, 0, c.siBool )
	
	return True

def zgInitRigBuilder_Execute( rigName, create ):
	
	rigModel = None
	
	#  no name given #
	if not rigName:
		
		xsi.logmessage( 'No Rig specified.', c.siError )
		return False
	
	# create a new rig #
	if create:
		
		# create the model #
		rigModel = xsi.ActiveSceneRoot.AddModel( None, rigName )
		
		# tag the model #
		prop = dispatch( rigModel.AddProperty( 'CustomProperty', False, 'zgRigBuilder' ) )
		
		# cache the name #
		prop.AddParameter3( 'RigName', c.siString, rigName )
		
		# install the preferences #
		rigModel.AddProperty( 'zgRigBuilderPrefs', False )
	
	else:
		
		# find and return the rigbuilder model #
		rigModel = xsi.ActiveSceneRoot.FindChild( rigName, c.siModelType )
		if not rigModel or not rigModel.Properties( 'zgRigBuilder' ):
			xsi.logmessage( 'RigBuilder "%s" not found.' % rigName, c.siError )
			return False

	# return the rig model #
	return rigModel


def zgGetAllCharacters_Init( ctxt ):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true
	oCmd.SetFlag( c.siNoLogging, True )

#	oArgs = oCmd.Arguments
#	oArgs.Add( "rigName", c.siArgumentInput )
#	oArgs.Add( "create", c.siArgumentInput, 0, c.siBool )
	
	return True

def zgGetAllCharacters_Execute():
	'''find all the character models in the scene'''
	
	# create an out collection #
	outCol = xsi.zgNewCol()
	
	# find all the models in the scene #
	allModels = xsi.ActiveSceneRoot.FindChildren( '*', c.siModelType )
	
	# step through each model looking for characters #
	for model in allModels:
		if model.Properties( 'zgCharacter' ):
			outCol.Add( model )
			
	# return the character models #
	return outCol
	
def zgCharacter_Define( ctxt ):
	
	prop = ctxt.Source
	typ  = prop.AddParameter3( 'CharacterName', c.siString, '', None, None, False, True )

	return True
	
def zgCharacter_DefineLayout( ctxt ):
	
	lay = ctxt.Source
	lay.Clear()
	
	lay.AddGroup("")
	lay.AddItem("CharacterName", 'Character Name' )
	lay.EndGroup()

	return True
	
def zgAddCharacter_Init( ctxt ):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true

	oArgs = oCmd.Arguments
	oArgs.Add( "characterName", c.siArgumentInput )
	
	return True

def zgAddCharacter_Execute( characterName ):
	'''find all the character models in the scene'''
	
	# create a new character #
	charModel = xsi.ActiveSceneRoot.AddModel( None, characterName )
	prop = charModel.AddProperty( 'zgCharacter', False )
	prop = dispatch( prop )
	prop.Parameters('CharacterName').Value = characterName
	
	# add the prefs tag to the character #
	charModel.AddProperty( 'zgRigBuilderPrefs', False )
	
	# return the character models #
	return charModel
	



def zgGetAllPackGuides_Init( ctxt ):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true
	oCmd.SetFlag( c.siNoLogging, True )

	oArgs = oCmd.Arguments
	oArgs.AddWithHandler("guideModel","SingleObj")
	
	return True

def zgGetAllPackGuides_Execute( guideModel ):
	'''find all the character models in the scene'''
	
	# create an out collection #
	outCol = xsi.zgNewCol()
	
	# find all the models in the scene #
	allModels = guideModel.FindChildren( '*', c.siModelType )
	
	# step through each model looking for pack guides #
	for model in allModels:
		if model.Properties( 'zgPackGuide' ):
			outCol.Add( model )
			
	# return the character models #
	return outCol
	
def zgGetAllPackFlats_Init( ctxt ):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true
	oCmd.SetFlag( c.siNoLogging, True )

	oArgs = oCmd.Arguments
	oArgs.AddWithHandler("flatModel","SingleObj")
	
	return True

def zgGetAllPackFlats_Execute( flatModel ):
	'''find all the character models in the scene'''
	
	# create an out collection #
	outCol = xsi.zgNewCol()
	
	# find all the pack tags on the flat model #
	for prop in flatModel.Properties:
		# find the properties matching the pattern #
		if sre.match( '^zgPack_(.+)_Flat$', prop.Name ):
			# add them to the out col #
			outCol.Add( prop )
	# return the out col #
	return outCol
	
	
