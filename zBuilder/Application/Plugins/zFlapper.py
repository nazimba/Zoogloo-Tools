"""
zFlapper.py

Created by andy on 2008-07-22.
Copyright (c) 2008 Zoogloo LLC. All rights reserved.
"""

__version__ = '$Revision: 214 $'
__author__  = '$Author: andy $'
__date__    = '$Date: 2009-12-30 00:36 -0800 $'

import win32com.client
import win32com.server
from win32com.client import constants
from win32com.client import constants as c
from win32com.client.dynamic import Dispatch as dispatch
import re

xsi = Application
log = xsi.logmessage

null = None
false = 0
true = 1

def XSILoadPlugin(in_reg):
	in_reg.Author = "Andy Buecker"
	in_reg.Name = "zFlapper"
	in_reg.Email = "andy@zoogloo.net"
	in_reg.URL = ""
	in_reg.Major = 1
	in_reg.Minor = 1

	in_reg.RegisterCommand('zFlapper', 'zFlapper')
	
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

class zFlapper(object):

	# required for COM wrapper #
	_public_methods_ = [
	]
	# define the output vars here #
	_public_attrs_ = [
		'rig',
		'scale',
		'basename',
		'symmetry',
	]
	# define those attrs that are read only #
	_readonly_attrs_ = [
		'rig',
		# 'template',
	]

	# set the class variables #
	_rig 			= None
	uid				= '7757b33f020661c07bc745feea136aa2'
	basename		= '3BoneFk'
	scale			= 1
	
	def __init__(self, sym='left'):
		super(zFlapper, self).__init__()
		
		# reset the instance varaibles #
		self._rig	  	= None
		
		self.symmetry	= sym
	
	@zProp
	def rig():
		'''Rig accessor'''
		def fget(self):
			# create a rig class if it doesn't exist #
			if not self._rig:
				# wrap a new class #
				self._rig = win32com.server.util.wrap(zFlapper_Rig(self))
			# return the private var #
			return dispatch(self._rig)
		def fset(self, value):
			raise Exception('Unable to modify rig value.')
		fdel = fset
		return locals()
				
class zFlapper_Rig(object):

	_inputs_ = [
		'character_set',   		
		'node_do_not_touch',  
		'node_root',  
		'nodes_flap',	# in flap order #	
		'value_speed',	
		'value_angle',	
		'value_offset',	
		'axis',	
	]
	_outputs_ = [
		'parent',
		'prop_flap',
		'character_subset',			
		'node_bunch',	
	]
	# required for COM wrapper #
	_public_methods_ = [
		'Build',
	]
	# define the output vars here #
	_public_attrs_ = [
	]
	_public_attrs_ += _inputs_ + _outputs_
	# define those attrs that are read only #
	_readonly_attrs_ = [
	]
	_readonly_attrs_ += _outputs_

	def __init__(self, parent):
		super(zFlapper_Rig, self).__init__()
		
		# set the instance variables #
		self.parent					= parent

		# set the defaults for the input variables #
		for item in self._inputs_:
			setattr(self, item, None)
			
		# set specific types #
		self.nodes_flap  = []
		
		# set the default values #
		self.value_speed 	= 20
		self.value_angle 	= 30
		self.value_offset 	= 2
		self.axis 			= 'Z'
	
	# override the attribute setter to dispatch objects when setting #
	def __setattr__(self, name, value):
		# if the name is in the inputs...#
		if name in self._inputs_ or name in self._outputs_:
			# ... dispatch the value (if we can)#
			try:
				self.__dict__[name] = dispatch(value)
			except:
				self.__dict__[name] = value
		else:
			raise Exception('Unable to locate attribute "%s"' % (name))
			
	def Build(self):
		
		# build the property on the root #
		self.prop_flap = self.node_root.AddProperty('CustomProperty', False, 'zFlapper')
		self.prop_flap = dispatch(self.prop_flap)
		
		# add the parameters #
		param_active 	= self.prop_flap.AddParameter3('Active', c.siBool, False)
		param_speed 	= self.prop_flap.AddParameter3('Speed', c.siFloat, self.value_speed, 0.01, 100)
		param_angle 	= self.prop_flap.AddParameter3('MaxAngle', c.siFloat, self.value_angle, 0, 90)
		param_offset 	= self.prop_flap.AddParameter3('SecondaryOffset', c.siFloat, self.value_offset, -100, 100)
		param_weight 	= self.prop_flap.AddParameter3('SecondaryWeight', c.siFloat, 0, 0, 1)
		
		# create a node to hold the flappers #
		self.node_bunch = self.node_do_not_touch.AddNull(
			xsi.zMapName(self.parent.basename, 'Branch', self.parent.symmetry)
		)
		xsi.zHide(self.node_bunch)
		
		# add the expressions #
		node_flap_shadow = None
		for i in xrange(len(self.nodes_flap)):
			node_flap = dispatch(self.nodes_flap[i])
			
			# create a stack and match #
			if not node_flap_shadow:
				node_flap_home = self.node_bunch.AddNull(
					xsi.zMapName(self.parent.basename, 'Custom:FlapHome', self.parent.symmetry)
				)
				xsi.zHide(node_flap_home)
				node_flap_home.Kinematics.Global.Transform = node_flap.Kinematics.Global.Transform
				# constrain it the 1st node_flap's parent #
				node_flap_home.Kinematics.AddConstraint('Pose', node_flap.Parent, True)
				node_flap_shadow = node_flap_home.AddNull(
					xsi.zMapName(self.parent.basename, 'Custom:Flap', self.parent.symmetry, i, True)
				)
			else:
				node_flap_shadow = node_flap_shadow.AddNull(
					xsi.zMapName(self.parent.basename, 'Custom:Flap', self.parent.symmetry, i, True)
				)
			xsi.zHide(node_flap_shadow)
			node_flap_shadow.Kinematics.Global.Transform = node_flap.Kinematics.Global.Transform
			
			# set the neutral pose #
			xsi.SetNeutralPose([node_flap_shadow], c.siSRT, False)
			
			# build the expression string #
			# sin(Fc*Speed) * MaxAngle
			expr_string = '(sin(Fc * %s) * %s)' % (
				param_speed.FullName, 
				param_angle.FullName
			)
			if i > 0:
				# sin((Fc+SecondaryOffset)*Speed)*MaxAngle) * SecondaryWeight
				expr_string = '(sin((Fc+%s) * %s) * %s) * %s' % (param_offset, param_speed, param_angle, param_weight)
			# param = node_flap.Kinematics.Local.Parameters('Rot%s' % self.axis.upper())
			param = node_flap_shadow.Kinematics.Local.Parameters('Rot%s' % self.axis.upper())
			# remove 
			if param.Source:
				param.Disconnect()
			# add the expression #
			expr = param.AddExpression(expr_string)
			
			# add a proxyed menu #
			prop = node_flap.AddProperty('CustomProperty', False, 'zFlapper')
			prop.AddProxyParameter(param_active, None, 'Active')
			prop.AddProxyParameter(param_speed, None, 'Speed')
			prop.AddProxyParameter(param_angle, None, 'Max_Angle')
			prop.AddProxyParameter(param_offset, None, 'Secondary_Offset')
			prop.AddProxyParameter(param_weight, None, 'Secondary_Weight')

			# add the proxy HUD #
			prop_di = node_flap.AddProperty('CustomProperty', False, 'DisplayInfo_zFlapper')
			prop_di.AddProxyParameter(param_active, None, 'Active')
			prop_di.AddProxyParameter(param_speed, None, 'Speed')
			prop_di.AddProxyParameter(param_angle, None, 'Max_Angle')
			prop_di.AddProxyParameter(param_offset, None, 'Secondary_Offset')
			prop_di.AddProxyParameter(param_weight, None, 'Secondary_Weight')
			
			# add the expression for the activeness #
			expr.Parameters('Active').AddExpression(param_active)
			
			# constrain the 
			cns = node_flap.Kinematics.AddConstraint('Pose', node_flap_shadow, True)
			cns = dispatch(cns)
			cns.active.AddExpression(param_active)

		#---------------------------------------------------------------------
		# add character sets
		if self.character_set:

			# add flapping parameters #
			self.character_set.AddParams(param_active)
			self.character_set.AddParams(param_speed)
			self.character_set.AddParams(param_angle)
			self.character_set.AddParams(param_offset)
			self.character_set.AddParams(param_weight)

#-----------------------------------------------------------------------------
# Commands
#-----------------------------------------------------------------------------
def zFlapper_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	#oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments
	oArgs.Add('symmetry', c.siArgumentInput, 'left', c.siString)
	return True
	
def zFlapper_Execute(symmetry):
	# export the python object #
	import win32com.server
	return win32com.server.util.wrap(
		zFlapper(symmetry)
	)
	
