"""
XSI Plugin for manipulating nodes by id's rather than names.
"""

__version__ = '$Revision: 185 $'
__author__  = '$Author: andy $'
__date__    = '$Date: 2009-02-06 21:04 -0800 $'

import win32com.client
from win32com.client import constants
from win32com.client import constants as c
from win32com.client.dynamic import Dispatch as dispatch
import time, md5, os, random

xsi = Application
log = xsi.logmessage

null = None
false = 0
true = 1

def XSILoadPlugin(in_reg):
	in_reg.Author = "Andy Buecker"
	in_reg.Name = "zID"
	in_reg.Email = "andy@zoogloo.net"
	in_reg.URL = ""
	try:
		in_reg.Major = int(__version__.split(' ')[1])
	except:
		in_reg.Major = 1
	in_reg.Minor = 0

	in_reg.RegisterCommand('zAddIdToNode', 'zAddIdToNode')
	in_reg.RegisterCommand('zAddIdToSelection', 'zAddIdToSelection')
	in_reg.RegisterCommand('zGetId', 'zGetId')
	in_reg.RegisterCommand('zFindNodeById', 'zFindNodeById')
	
	in_reg.RegisterFilter("zID_Nodes", c.siFilter3DObject);

	in_reg.RegisterMenu(c.siMenuTbGetPropertyID, 'zIDMenu', False)
	
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
def zIDMenu_Init(ctxt):
	menu = ctxt.Source
	
	item = menu.AddCommandItem('zAddIdToSelection', 'zAddIdToSelection')
	item.Name = '(z) Add ID to Selected'

#-----------------------------------------------------------------------------
# Filter
#-----------------------------------------------------------------------------
def zID_Nodes_Match(ctxt):
	# get the object from the input context $
	obj = ctxt.GetAttribute('Input')
	# skip if the item doesn't have a zPlot prop #
	if not obj.Properties('zID'): return False
	# return the obj #
	return True

#-----------------------------------------------------------------------------
# Commands
#-----------------------------------------------------------------------------
def zAddIdToNode_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	#oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments
	oArgs.AddObjectArgument('item')
	oArgs.Add('update', c.siArgumentInput, False, c.siBool)

	return True
	
def zAddIdToNode_Execute(item, update):
	
	# see if the tag exists #
	prop = item.Properties('zID')
	if not prop:
		prop = item.AddProperty('CustomProperty', False, 'zID')
	prop = dispatch(prop)
	
	# get the hostname #
	import socket
	host = socket.getfqdn()
	
	# get the username #
	user = None
	if os.name == 'nt':
		import win32api
		user=win32api.GetUserName()
	if os.name == 'posix':
		user = os.environ['USER']
		# host = os.environ['HOSTNAME']

	# get a random number #
	rand = random.random()

	# generate the id #
	uid = str(md5.new('%s:%s:%s:%s' %(time.time(), user, host, rand)).hexdigest())

	# add the parameter #
	param = prop.Parameters('uid')
	if not param:
		param = prop.AddParameter3('uid', c.siString, uid, None, None, False, True)
	elif update:
		param.Value = uid
	
	# return the uid #
	return uid
		
#-----------------------------------------------------------------------------

def zAddIdToSelection_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	#oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments
	oArgs.Add('update', c.siArgumentInput, False, c.siBool)

	return True
	
def zAddIdToSelection_Execute(update):
	
	# step through item in selection #
	for item in xsi.Selection:
		# add the id node #
		xsi.zAddIdToNode(item, update)
	
#-----------------------------------------------------------------------------

def zGetId_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	#oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments
	oArgs.AddObjectArgument('node')
	oArgs.Add('verbose', c.siArgumentInput, False, c.siBool)

	return True
	
def zGetId_Execute(node, verbose):
	
	# get the zID node #
	prop = node.Properties('zID')
	if not prop:
		if verbose:
			log('No zID found on "%s"' % node.FullName, c.siWarning)
		return None
	prop = dispatch(prop)
	
	# return the uid value #
	return prop.uid.Value

#-----------------------------------------------------------------------------
	
def zFindNodeById_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	#oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments
	oArgs.Add('uid', c.siArgumentInput, '', c.siString)
	oArgs.AddObjectArgument('root_node')

	return True

def zFindNodeById_Execute(uid, root_node):
	# if we don't have a root_node, give it the scene root #
	if not root_node:
		root_node = xsi.ActiveSceneRoot
	# get the filter #
	fltr = xsi.Filters('zID_Nodes')
	# get all the items under the model #
	nodes = root_node.FindChildren('*')
	# filter out the nodes #
	filtered_nodes = fltr.Subset(nodes)
	for node in filtered_nodes:
		if node.Properties('zID').Parameters('uid').Value == uid:
			return node
	return None
	