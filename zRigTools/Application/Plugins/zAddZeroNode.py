'''
XSI Plugin to add and "zero" node to a collection of input nodes returning a collection of created hook nodes

>>> from win32com.client import Dispatch as dispatch
>>> nulls = dispatch('XSI.Collection')
>>> mulls.Add(Application.ActiveSceneRoot.AddNull())
>>> mulls.Add(Application.ActiveSceneRoot.AddNull())
>>> zero_nodes = Application.zAddZeroNode(nulls, "ZeroNodeName")
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
	in_reg.Name = "zAddZeroNode"
	in_reg.Email = ""
	in_reg.URL = ""
	in_reg.Major = 1
	in_reg.Minor = 0

	in_reg.RegisterCommand("zAddZeroNode","zAddZeroNode")
	#RegistrationInsertionPoint - do not remove this line

	return true

def XSIUnloadPlugin( in_reg ):
	strPluginName = in_reg.Name
	Application.LogMessage(str(strPluginName) + str(" has been unloaded."),constants.siVerbose)
	return true

def zAddZeroNode_Init( in_ctxt ):
	oCmd = in_ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true
	
	oArgs = oCmd.Arguments
	oArgs.AddWithHandler('nodes', c.siArgHandlerCollection)
	oArgs.Add('nodeName', c.siArgumentInput, '', c.siString)
	
	return true

def zAddZeroNode_Execute(nodes, nodeName):

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
			for s in xrange(len(split)):
				if s == len(split)-1:
					nodeName += 'ZERO'  # move to preferences
				else:
					nodeName += '%s_' % split[s]
		log('Adding Zero Node "%s" to node "%s"' % (nodeName, item), c.siVerbose)
		
		# create a node #
		zero = item.parent.AddNull(nodeName)
		outCol.Add(zero)
		# match transforms #
		zero.kinematics.Global.Transform = item.kinematics.Global.Transform
		# reparent #
		zero.AddChild(item)
		# hide the icon #
		zero.primary_icon.Value = 0
		zero.Properties('Visibility').Parameters('viewvis').Value = False
		zero.Properties('Visibility').Parameters('rendvis').Value = False

	# return the out collection #
	if outCol.Count > 1:
		return outCol
	else:
		return outCol(0)


