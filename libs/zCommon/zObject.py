#!/usr/bin/env python
# encoding: utf-8
"""
zObject.py

Created by andy on 2007-12-13.
Copyright (c) 2007 Zoogloo LLC. All rights reserved.
"""

__version__ = '$Revision: 0 $'
__author__  = '$Author: andy $'
__date__    = '$Date: 2010-04-10 14:04 -0700 $'

import time, md5, os
import zUID
from zUtils import zProp
	   
class zObjectException(Exception): pass

class zObjectAttributeException(Exception): pass

class zObject(object):
	''' 
		A common class shared by all objects.
	
		@ivar uid: Generated by username, host, and time
		@type uid: L{zUID}
		@ivar name: Name of this object
		@type name: str
		@ivar parent: Object that is the parent of this class
		@type parent: L{zObject}
	'''
	
	_name 	= None
	_uid 	= None
	_parent = None
	
	def __init__(self, name=None, parent=None):
		
		# set the unique id for the object #
		self._uid = zUID.zUID()
		
		# setup the name #
		if name == None:
			self._name = 'zObject'
		else:
			self._name = name
		
		# setup the parent if provided #
		self._parent = parent
	
	def __repr__(self):
		return '<%s "%s">' % (self.__class__.__name__, self.name)
			
	# create uid accesor #
	@zProp
	def uid():
		def fget(self):
			return self._uid
		def fset(self):
			'''".uid" is a readonly attribute'''
			raise zObjectAttributeException, '".uid" is a readonly attribute'
		fdel = fset
		return locals()
		
	def GenerateNewUID(self):
		'''
		Generates a new id.  Such as if you copy.copy(), the ID's won't update.
		'''
		self._uid = zUID.zUID()
	
	# create type accesor #
	@zProp
	def type():
		def fget(self):
			return self.__class__
		def fset(self):
			'''".type" is a readonly attribute'''
			raise zObjectAttributeException, '".type" is a readonly attribute'
		fdel = fset
		return locals()
	
	
	# create parent accesor #
	@zProp
	def parent():
		def fget(self):
			return self._parent
		def fset(self, value):
			'''".parent" is a readonly attribute'''
			raise zObjectAttributeException, '".parent" is a readonly attribute'
		fdel = fset
		return locals()
	
	
	# create name accesor #
	@zProp
	def name():
		'''The name of the zObject'''
		def fget(self):
			return self._name
		def fset(self, value):
			'''setting the name requires a string'''
			# make sure the type is a string #
			if type(value) != type(str()):
				raise zObjectAttributeException, '".name" requires a string'
		
			# set the name #
			self._name = value
		
			return self._name
		def fdel(self):
			'''".type" is not a deletable attribute'''
			raise zObjectAttributeException, '".type" is not a deletable attribute'
		return locals()
	
	
	def __modattr__(self, attr, value):
		''' limit the creating of new attributes on objects not explicitely 
		    defined in the class
	    '''
		
		# get all attributes #
		allPublicAttrs = [item for item in dir(self) if item[:2] != '__']
		
		# set the attribute if it's been defined, otherwise raise error #
		if attr in allPublicAttrs:
			self.__dict__[attr] = value
		else:
			raise zObjectAttributeException, 'Attribute "%s" not defined' % attr
		
	
def SaveObject(zobject, filename):
	''' save to file'''
	
	import cPickle
	file = open(filename, 'wb')
	cPickle.dump(zobject, file)
	file.close()

def LoadObject(filename):
	''' save to file'''
	
	import cPickle
	file = open(filename, 'r')
	zobject = cPickle.load(file)
	file.close()
	return zobject
	
	
# tests #
import unittest
class TestzObject(unittest.TestCase):
	
	def setUp(self):
		self.z1 = zObject()
		self.z2 = zObject()
		
	def test_Variables(self):
		'''Test all the variables'''
		self.z1 = zObject()
		self.assertEquals(self.z1.name, 'zObject', 'Default name is not correct')
		self.z1.name = 'Test'
		self.assertEquals(self.z1.name, 'Test', 'Unable to correctly set name')
		
		# make sure we can't directly set the parent #
		try:
			self.z1.parent = 'test'
			self.fail('Was able to manually set the parent')
		except:
			pass
		
		# make sure we can't directly set the type #
		try:
			self.z1.type = 'type'
			self.fail('Was able to manually set the parent')
		except:
			pass
		
		# make sure we get the proper type #
		try:
			self.assertEquals(zObject().__class__, self.z1.type, 'Wrong type reported')
		except:
			pass
		
		# make sure we can't directly set the uid #
		try:
			self.z1.uid = 'uid'
			self.fail('Was able to manually set the uid')
		except:
			pass

	def test_SaveLoad(self):
		'''tests saving and loading zObjects'''
		
		# create a temporary file #
		import tempfile
		filename = tempfile.mkstemp('_1arse', '.temp')[1]
		
		# save #
		SaveObject(self.z1, filename)
		
		# load it #
		z3 = LoadObject(filename)
		
		# compare the uid's #
		self.assertEquals(self.z1.uid, z3.uid, "zUIDs don't match after save/load")
		
		import os
		os.unlink(filename)
		
if __name__ == '__main__':
	
	unittest.main()

	if 0:
		z1 = zObject()
	
		uid = z1
	
		import tempfile
		filename = tempfile.mkstemp('_1arse', '.temp')[1]
		
		# save #
		SaveObject(z1, filename)
	
		# load it #
		z3 = LoadObject(filename)
	
		# compare the uid's #
		print z1.uid
		print z3.uid
		print z1.uid == z3.uid
		print z1 == z3
	
		z1.ass = 'ass'
		print z1.ass
	
#===============================================================================
#	z1 = zObject()
#	z2 = zObject()
#	print z1, z1.uid, type(z1.uid)
#	print z2, z2.uid, type(z2.uid)
#
#	class A(zObject): 
#		def __init__(self):
#			zObject.__init__(self)
#	class B(zObject): 
#		def __init__(self):
#			zObject.__init__(self)
#	   
#	class C(A):
#		def __init__(self):
#			A.__init__(self)
#	
#	a1 = A()
#	a2 = A()
#	a1.Log(a1.uid, 'critical')
#	print 'a2', a2.uid
#	b1 = B()
#	print 'b1', b1.uid
#	
#	c1 = C()
#	print 'c1', c1.uid
#	print ' a1', a1.uid
#	print ' a2', a2.uid
#===============================================================================
