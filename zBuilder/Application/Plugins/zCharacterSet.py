"""
zCharacterSet.py

Created by andy on 2008-09-23.
Copyright (c) 2008 Zoogloo LLC. All rights reserved.
"""

__version__ = '$Revision: 200 $'
__author__  = '$Author: andy $'
__date__    = '$Date: 2009-03-12 18:15 -0700 $'

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
	in_reg.Name = "zCharacterSet"
	in_reg.Email = "andy@zoogloo.net"
	in_reg.URL = ""
	in_reg.Major = 1
	try:
		in_reg.Minor = int(__version__.split(' ')[1])
	except:
		in_reg.Minor = 0

	in_reg.RegisterCommand("zCharacterSet")
	in_reg.RegisterCommand("zCharacterSubset")
	
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
# zCharacterSubset
#-----------------------------------------------------------------------------
class zCharacterSubset(object):

	# required for COM wrapper #
	_public_methods_ = [
		'AddSubset',
		'AddNodePosRot',
		'AddNodePos',
		'AddNodeRot',
		'AddNodeScl',
		'AddParams',
		'Get',
	]
	# define the output vars here #
	_public_attrs_ = [
		'name',
		'model',
		'sceneItem',
		'parentSet'
	]
	# define those attrs that are read only #
	_readonly_attrs_ = _public_attrs_

	# class variables #
	parentSet		= None
	sceneItem		= None
	model			= None
	name			= None
	sets			= {}

	def __init__(self, charset, setname):
		'''
		@param charset: XSI Character Set Node
		'''
		# argument callbacks are converting this to a collection, correct it #
		if charset.type == 'XSICollection':
			charset = charset(0)

		# create the character set #
		self.sceneItem = xsi.CreateSubCharacterKeySet(charset, None, setname)

		# set the instance variables #
		self.name 		= setname
		self.model 		= charset.model
		self.parentSet	= charset
		self.sets	   	= {}

	def Get(self, setname):
		if not self.sets.has_key(setname):
			raise Exception('Unable to locate character set by name: %s' % setname)
		# return the subset #
		return self.sets.get(setname)

	def AddSubset(self, setname):
		# make sure the set name doesn't exist #
		if setname in self.sets.keys():
			raise Exception('Character set "%s" all ready exists.' % setname)
		log('SceneItem: %s' % self.sceneItem)
		log('setname: %s' % setname)
		subset = xsi.zCharacterSubset(self.sceneItem, setname)
		# add it to the subsets dictionary #
		self.sets[setname] = subset
		# return the subset #
		return subset

	def AddParams(self, paramString):
		xsi.AddProxyParamToCharacterKeySet(self.sceneItem, paramString)

	def AddNodePosRot(self, item):
		'''
		@param item: XSI Collection of objects
		'''
		# re dispatch #
		item = dispatch(item)
		# add the parameters #
		xsi.AddProxyParamToCharacterKeySet(
			self.sceneItem, 
			'%(item)s.kine.local.posx, %(item)s.kine.local.posy, %(item)s.kine.local.posz ,' % {'item': item.FullName} + \
			'%(item)s.kine.local.rotx, %(item)s.kine.local.roty, %(item)s.kine.local.rotz '  % {'item': item.FullName}

		)

	def AddNodePos(self, item):
		'''
		@param item: XSI object
		'''
		# re dispatch #
		item = dispatch(item)
		# add the parameters #
		xsi.AddProxyParamToCharacterKeySet(
			self.sceneItem, 
			'%(item)s.kine.local.posx, %(item)s.kine.local.posy, %(item)s.kine.local.posz ,' % {'item': item.FullName}
		)

	def AddNodeRot(self, item):
		'''
		@param item: XSI object
		'''
		# re dispatch #
		item = dispatch(item)
		# add the parameters #
		xsi.AddProxyParamToCharacterKeySet(
			self.sceneItem, 
			'%(item)s.kine.local.rotx, %(item)s.kine.local.roty, %(item)s.kine.local.rotz '  % {'item': item.FullName}
		)

	def AddNodeScl(self, item):
		'''
		@param item: XSI object
		'''
		# re dispatch #
		item = dispatch(item)
		# add the parameters #
		xsi.AddProxyParamToCharacterKeySet(
			self.sceneItem, 
			'%(item)s.kine.local.sclx, %(item)s.kine.local.scly, %(item)s.kine.local.sclz '  % {'item': item.FullName}
		)

	def __repr__(self):
		return '<zCharacterSet "%s">' % self.setname	

def zCharacterSubset_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	# oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments
	oArgs.Add("charset", c.siArgumentInput)
	oArgs.Add("setname", c.siArgumentInput, 'CharacterSubset', c.siString)

	return True


def zCharacterSubset_Execute(charset, setname):

	log('charset: %s' % charset)
	# export the python object #
	import win32com.server
	return win32com.server.util.wrap(
		zCharacterSubset(charset, setname)
	)

#-----------------------------------------------------------------------------
# zCharacterSet
#-----------------------------------------------------------------------------
class zCharacterSet(zCharacterSubset):

	def __init__(self, setname, model):
		
		# create the character set #
		tempNull = model.AddNull()
		self.sceneItem = xsi.CreateCharacterKeySet(tempNull, setname)
		xsi.DeleteObj(tempNull)

		# set the instance variables #
		self.name 		= setname
		self.model 		= model
		self.parentSet	= None
		self.sets	   	= {}


def zCharacterSet_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	# oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments
	oArgs.Add("setname", c.siArgumentInput, 'CharacterSet', c.siString)
	oArgs.AddObjectArgument("model")

	return True


def zCharacterSet_Execute(setname, model):

	# export the python object #
	import win32com.server
	return win32com.server.util.wrap(
		zCharacterSet(setname, model)
	)