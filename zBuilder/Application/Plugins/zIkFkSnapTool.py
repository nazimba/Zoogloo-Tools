"""
zIkFkSnapTool.py

Created by andy on 2008-08-20.
Copyright (c) 2008 Zoogloo LLC. All rights reserved.
"""

__version__ = '$Revision: 214 $'
__author__  = '$Author: andy $'
__date__    = '$Date: 2009-12-30 00:36 -0800 $'

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
	in_reg.Name = "zIkFkSnapTool"
	in_reg.Email = "andy@zoogloo.net"
	in_reg.URL = ""
	in_reg.Major = 1
	in_reg.Minor = 1

	in_reg.RegisterProperty('zIkFkSnapTool')

	in_reg.RegisterCommand('zIkFkSnapTool', 'zIkFkSnapTool')

	in_reg.RegisterMenu(c.siMenuTbAnimateActionsStoreID, 'zIkFkSnapToolMenu', False)
	
	# copyright message #
	msg = '''
#------------------------------------------#
  %s (v.%d.%d)
  Copyright 2008 Zoogloo LLC.
  All rights Reserved.
#------------------------------------------#
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
def zIkFkSnapToolMenu_Init(ctxt):
	menu = ctxt.Source
	
	item = menu.AddCommandItem('zIkFkSnapToolGUI', 'zIkFkSnapToolGUI')
	item.Name = '(z) zIkFkSnapTool'

#-----------------------------------------------------------------------------
# Properties
#-----------------------------------------------------------------------------
def zIkFkSnapTool_Define(ctxt):
	prop = ctxt.Source
	
	#prop.AddParameter3("ParamName", c.siString, '')

	
def zIkFkSnapTool_DefineLayout(ctxt):
	lo = ctxt.Source
	lo.Clear()

	lo.AddItem('ParamName')

#-----------------------------------------------------------------------------
# Classes
#-----------------------------------------------------------------------------
def zProp(function):
	'''
	Easy function decorator for accessing properties.
	
	Usage:
	
	>>> @zProp
	>>> def Connection():
	>>> 	\'''connection\'''
	>>> 	def fget(self):
	>>> 		return self._cnx
	>>>		def fset(self, value):
	>>>			self._cnx = value
	>>>		def fdel(self):
	>>>			raise Exception, "Can't delete attribute 'Connection'"
	>>> 	return locals()
	
	'''
	return property(doc=function.__doc__, **function())

class zIkFkSnapTool(object):

	# setup the input and output lists #
	_inputs_ = [
		'tagged_nodes',		# nodes to add tags too
		'cons_fk',			# fk controllers
		'con_eff_pos',		# ik chain contoller for position
		'con_eff_rot',		# ik chain contoller for orientation
		'con_upv',			# upvector controller
		'ref_con',			# fk node reference for the ik controller
		'ref_pole_pos',		# fk node reference for pole position
		'ref_pole_rot',		# fk node reference for pole orientation
		'slider',			# ik/fk slider parameter
	]
	_outputs_ = [
		'prop'
	]
	# required for COM wrapper #
	_public_methods_ = [
		'Install',
	]
	# define the output vars here #
	_public_attrs_ = [
	]
	_public_attrs_ += _inputs_ + _outputs_
	# define those attrs that are read only #
	_readonly_attrs_ = [
	]
	_readonly_attrs_ += _outputs_

	def __init__(self):
		super(zIkFkSnapTool, self).__init__()

		# set the defaults for the input variables #
		for item in self._inputs_:
			setattr(self, item, None)
			
		# set the instance variables #
		self.cons_fk		= dispatch('XSI.Collection')
		self.tagged_nodes	= dispatch('XSI.Collection')

	def Install(self):
		"""docstring for Install"""
		#---------------------------------------------------------------------
		# pre-conditions #
		if not self.cons_fk.Count:	raise Exception('"cons_fk" attribute not specified.')
		if not self.con_eff_pos: 	raise Exception('"con_eff_pos" attribute not specified.')
		if not self.con_eff_rot: 	raise Exception('"con_eff_ori" attribute not specified.')
		if not self.con_upv: 		raise Exception('"con_upv" attribute not specified.')
		if not self.ref_con: 		raise Exception('"ref_con" attribute not specified.')
		if not self.ref_pole_pos: 	raise Exception('"node_pole_pos" attribute not specified.')
		if not self.ref_pole_rot: 	raise Exception('"node_pole_rot" attribute not specified.')
		if not self.slider: 		raise Exception('"slider" attribute not specified.')
		
		#---------------------------------------------------------------------
		# create a colletion of all attributes that will need ik/fk properties
		
		# create a property on each item #
		for item in self.tagged_nodes:
			
			# add the property #
			prop = item.AddProperty('CustomProperty', False, 'zIkFk')
			
			# add parameters #
			cons_fk 		= prop.AddParameter3('FkControls', c.siString, '', None, None, False, True)
			eff_pos     	= prop.AddParameter3('IkEffectorPos', c.siString, '', None, None, False, True)
			eff_rot     	= prop.AddParameter3('IkEffectorRot', c.siString, '', None, None, False, True)
			upv     		= prop.AddParameter3('IkUpVector', c.siString, '', None, None, False, True)
			ref_con    		= prop.AddParameter3('FkRefEffector', c.siString, '', None, None, False, True)
			ref_pole_pos 	= prop.AddParameter3('FkRefUpvPos', c.siString, '', None, None, False, True)
			ref_pole_rot 	= prop.AddParameter3('FkRefUpvRot', c.siString, '', None, None, False, True)
			slider  		= prop.AddParameter3('Slider', c.siString, '', None, None, False, True)

			# redispatch the objects (damn COM OLE) #
			self.con_eff_pos 	= dispatch(self.con_eff_pos)
			self.con_eff_rot 	= dispatch(self.con_eff_rot)
			self.con_upv 		= dispatch(self.con_upv)
			self.ref_con 		= dispatch(self.ref_con)
			self.ref_pole_pos 	= dispatch(self.ref_pole_pos)
			self.ref_pole_rot 	= dispatch(self.ref_pole_rot)
			self.slider 		= dispatch(self.slider)
			
			# build the concatinated string for the fknodes list #
			cons_fk_string 		= self.cons_fk.GetAsText()
			cons_fk_string 		= cons_fk_string.replace(item.Model.Name + '.', '')

			# fill in the values #
			cons_fk.Value 		= cons_fk_string
			eff_pos.Value     	= self.con_eff_pos.Name
			eff_rot.Value     	= self.con_eff_rot.Name
			upv.Value     		= self.con_upv.Name
			ref_con.Value     	= self.ref_con.Name
			ref_pole_pos.Value 	= self.ref_pole_pos.Name
			ref_pole_rot.Value 	= self.ref_pole_rot.Name
			slider.Value  		= self.slider.FullName.replace(item.model.Name + '.', '')


#-----------------------------------------------------------------------------
# Commands
#-----------------------------------------------------------------------------
def zIkFkSnapTool_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	#oCmd.SetFlag(constants.siNoLogging,false)

	#oArgs = oCmd.Arguments
	#oArgs.Add('arg', c.siArgumentInput, '', c.siString)
	#oArgs.AddObjectArgument('model')

	return True
	
def zIkFkSnapTool_Execute():
	return win32com.server.util.wrap(
		zIkFkSnapTool()
	)
