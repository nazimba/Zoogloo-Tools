'''
XSI Plugin to add and "hook" node to a collection of input nodes returning a 
collection of created hook nodes

>>> from win32com.client import Dispatch as dispatch
>>> nulls = dispatch('XSI.Collection')
>>> mulls.Add(Application.ActiveSceneRoot.AddNull())
>>> mulls.Add(Application.ActiveSceneRoot.AddNull())
>>> hook_nodes = Application.zAddHookNode(nulls, "HookName")
'''
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
	in_reg.Name = "zAddHookNode"
	in_reg.Email = ""
	in_reg.URL = ""
	in_reg.Major = 1
	in_reg.Minor = 0

	in_reg.RegisterCommand("zAddHookNode","zAddHookNode")
	#RegistrationInsertionPoint - do not remove this line

	return true

def XSIUnloadPlugin( in_reg ):
	strPluginName = in_reg.Name
	Application.LogMessage(str(strPluginName) + str(" has been unloaded."),constants.siVerbose)
	return true

def zAddHookNode_Init( in_ctxt ):
	oCmd = in_ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true

	oArgs = oCmd.Arguments
	oArgs.AddWithHandler('nodes', c.siArgHandlerCollection)
	# oArgs.AddObjectArgument ('nodes')
	oArgs.Add('nodeName', c.siArgumentInput, '', c.siString)
	
	return true

def zAddHookNode_Execute(nodes, nodeName):

	# collection to return #
	outCol = dispatch('XSI.Collection')

	# make sure something is selected #
	if not nodes and not xsi.selection:
		log('No objects provided.', c.siError)
	
	# setup the input collection #	
	inCol = dispatch('XSI.Collection')
	if nodes:
		inCol.AddItems(nodes)
	else:
		inCol.AddItems(xsi.selection)
		
	# step through each item #
	for item in inCol:
		
		# generate the new name #
		if not nodeName or nodeName == '':
			split = item.name.split('_')
			nodeName = ''
			for s in xrange(len(split)):
				if s == len(split)-1:
					nodeName += 'HOOK'  # move to preferences
				else:
					nodeName += '%s_' % split[s]
		log('Adding Hook "%s" to node "%s"' % (nodeName, item), c.siVerbose)
		
		# create a node #
		hook = item.AddNull(nodeName)
		outCol.Add(hook)
		# hide the icon #
		hook.primary_icon.Value = 0
		hook.Properties('Visibility').Parameters('viewvis').Value = False
		hook.Properties('Visibility').Parameters('rendvis').Value = False
		# match the transforms #
		hook.kinematics.Global.Transform = item.kinematics.Global.Transform

	# return the out collection #
	if outCol.Count > 1:
		return outCol
	else:
		return outCol(0)

