# zReorderEff
import win32com.client
from win32com.client import constants
from win32com.client import constants as c
from win32com.client.dynamic import Dispatch as dispatch

xsi = Application
log = xsi.logmessage

null = None
false = 0
true = 1

def XSILoadPlugin( in_reg ):
	in_reg.Author = "andy"
	in_reg.Name = "zAddChangeEffPlugin"
	in_reg.Email = ""
	in_reg.URL = ""
	in_reg.Major = 1
	in_reg.Minor = 0

	in_reg.RegisterCommand("zReorderEff", "zReorderEff")
	#RegistrationInsertionPoint - do not remove this line

	return true

def XSIUnloadPlugin( in_reg ):
	strPluginName = in_reg.Name
	Application.LogMessage(str(strPluginName) + str(" has been unloaded."),constants.siVerbose)
	return true

def zReorderEff_Init( in_ctxt ):
	oCmd = in_ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true

	return true

def zReorderEff_Execute():

	# grab all effectors in the scene #
	for item in xsi.ActiveSceneRoot.FindChildren('*', c.siChainEffPrimType):
		
		lastBone = item.root.bones(item.root.bones.Count-1)
		log('Reparenting effector "%s" under "%s"' % (item, lastBone), c.siVerbose)
		#put the effector under the last bone #
		lastBone.AddChild(item)
		
	return true

