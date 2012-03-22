"""
zSpineStretchy.py

xsi = Application
xsi.UpdatePlugins()
xsi.NewScene(None, False)

s = xsi.zSpine('spine')
s.template.Draw()
s.rig.Build()

o = xsi.zSpineStretchy()
o.rig.curve_control 	= s.rig.curve_control 
o.rig.curve_shrunk 		= s.rig.curve_shrunk 
o.rig.root_skel			= s.rig.root_skel
o.rig.root_ik 			= s.rig.root_ik
o.rig.root_fk 			= s.rig.root_fk
o.rig.character_set 	= s.rig.character_subset
o.rig.prop_anim_spine 	= s.rig.prop_anim
o.rig.con_iks 			= s.rig.con_iks
o.rig.default_state 	= True
o.rig.Build()

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

alpha = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

xsi = Application
log = xsi.logmessage

null = None
false = 0
true = 1

def XSILoadPlugin(in_reg):
	in_reg.Author = "Andy Buecker"
	in_reg.Name = "zSpineStretchy"
	in_reg.Email = "andy@zoogloo.net"
	in_reg.URL = ""
	in_reg.Major = 1
	in_reg.Minor = 0

	in_reg.RegisterCommand('zSpineStretchy', 'zSpineStretchy')
	
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

class zSpineStretchy(object):

	# required for COM wrapper #
	_public_methods_ = [
	]
	# define the output vars here #
	_public_attrs_ = [
		'rig',
		'template',
		'scale',
		'basename',
		'symmetry',
		'span_segments',
		'sub_spans',
	]
	# define those attrs that are read only #
	_readonly_attrs_ = [
		'rig',
		'template',
	]

	# set the class variables #
	_rig 			= None
	uid				= '2ecf2e95eff844a117b32f11bf375272'
	basename		= 'Wing'
	scale			= 1
	
	def __init__(self, sym='left'):
		super(zSpineStretchy, self).__init__()
		
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
				self._rig = win32com.server.util.wrap(zSpineStretchy_Rig(self))
			# return the private var #
			return self._rig
		def fset(self, value):
			raise Exception('Unable to modify rig value.')
		fdel = fset
		return locals()
				
class zSpineStretchy_Rig(object):

	_inputs_ = [
		'curve_control',  		
		'curve_shrunk',  		
		'root_skel',   		
		'root_fk',  		
		'root_ik',  		
		'con_iks',  		
		'character_set',  		
		'default_state',  		
		'prop_anim_spine',  		
	]
	_outputs_ = [
		'parent',
		'character_subset',
		'prop_anim',
		'prop_anim_di',
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
		super(zSpineStretchy_Rig, self).__init__()
		
		# set the instance variables #
		self.parent					= parent

		# set the defaults for the input variables #
		for item in self._inputs_:
			setattr(self, item, None)
			
		self.default_state = False
			
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
		
		#---------------------------------------------------------------------
		# create a ppg and add parameters #
		self.prop_anim = self.curve_shrunk.AddProperty('CustomProperty', False, 'zStretch')
		self.prop_anim = dispatch(self.prop_anim)
		self.prop_anim.AddParameter3('RestLength', c.siFloat, self.curve_control.ActivePrimitive.Geometry.Curves(0).Length, 0, 1000000, False, True)
		self.prop_anim.AddParameter3('Scale', c.siFloat, 1, 0, 1000000)
		
		# create the operator #
		op = XSIFactory.CreateObject('zStretchyOp')
		op = dispatch(op)

		# add the in and outports #
		op.AddOutputPort(self.prop_anim.Scale)

		op.AddInputPort(self.curve_control.ActivePrimitive)
		op.AddInputPort(self.prop_anim.RestLength)

		# connect it all up #
		op.Connect()
		
		#---------------------------------------------------------------------
		# add an activation switch to the spine prop #
		param_stretchy = self.prop_anim_spine.AddParameter3('Stretchy', c.siBool, self.default_state)

		# add the proxy to each control #
		for bone in self.root_fk.Bones:
			bone = dispatch(bone)
			prop = bone.Parameters('DisplayInfo_zAnim')
			if prop:
				prop.AddProxyParameter(param_stretchy, None, 'Stretchy')
			prop = bone.Parameters('zAnim')
			if prop:
				prop.AddProxyParameter(param_stretchy, None, 'Stretchy')

		# ik controllers #
		for con in self.con_iks:
			con = dispatch(con)
			prop = con.node_con.Properties('DisplayInfo_zAnim')
			if prop:
				prop.AddProxyParameter(param_stretchy, None, 'Stretchy')
			prop = con.node_con.Properties('zAnim')
			if prop:
				prop.AddProxyParameter(param_stretchy, None, 'Stretchy')
			
		#---------------------------------------------------------------------
		# link the curve deformer scale to the operators scale value #
		op_curve_deform = self.curve_shrunk.ActivePrimitive.ConstructionHistory.Filter('crvdeform')(0)
		op_curve_deform.sclcurve.AddExpression(
			'cond(%s == 1, %s, 1)' % (
				param_stretchy,
				self.prop_anim.Scale.FullName
			)
		)
		
		#---------------------------------------------------------------------
		# create length expressions on the ik bones #
		for b in xrange(self.root_ik.Bones.Count):
			bone = dispatch(self.root_ik.Bones(b))
			
			# store the original value #
			param_bone_rest = self.prop_anim.AddParameter3('RestLength_IkBone%s' % (b+1), c.siFloat, bone.Length.Value, 0, 1000000, False, True)
			
			# create an expression to the bone length #
			bone.Length.AddExpression(
				'cond(%s == 1, %s * %s, %s)' % (
					param_stretchy.FullName,
					self.prop_anim.Scale.FullName, 
					param_bone_rest.FullName,
					param_bone_rest.FullName
				)
			)
			
			# add an expression to the skeleton chain bone lenghts #
			# '(ikbonelength * fk_ik) + (fkbonelength * (1-fk_ik))'
			expr_str = '(%(ik_bone)s.Length * %(ik_fk)s) + (%(fk_bone)s.Length * (1 - %(ik_fk)s))' % {
				'ik_bone'	: bone.FullName,
				'fk_bone'	: self.root_fk.Bones(b).FullName,
				'ik_fk'		: self.prop_anim_spine.Fk_Ik
			}
			self.root_skel.Bones(b).Length.AddExpression(expr_str)
			
			
		
#-----------------------------------------------------------------------------
# Commands
#-----------------------------------------------------------------------------
def zSpineStretchy_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	#oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments
	# oArgs.Add()
	return True
	
def zSpineStretchy_Execute():
	# export the python object #
	import win32com.server
	return win32com.server.util.wrap(
		zSpineStretchy()
	)
	
