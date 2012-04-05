#!/usr/bin/env python
# encoding: utf-8
"""
zCollection.py

Created by andy on 2007-12-13.
Copyright (c) 2007 Zoogloo LLC. All rights reserved.
"""

__version__ = '$Revision: 0 $'
__author__  = '$Author: andy $'
__date__    = '$Date: 2010-04-10 14:04 -0700 $'

import unittest
import zObject

class zCollectionAttributeError(Exception): pass
class zCollectionTypeError(Exception): pass

class zCollection(zObject.zObject):
	''' 
	Collection of zObjects.
	
	Usage:
	
	>>> class MyCollection(zCollection):
	>>> 	def __init__(self):
	>>> 		# initialize a collection of 'MyClass' objects #
	>>> 		zCollection.__init__(self, MyClass)
	>>> 	def __repr__(self):
	>>> 		return '<MyCollection Object [%s]>' % self.Count
	>>>
	>>> class MyClass(zObject):
	>>> 	pass

	>>> m1 = MyClass()
	>>> col = MyCollection()
	>>> col.Add(m1)
	>>> col.Count
	1
	
	>>> # create 2 test zObject classes #
	>>> class Test1(zObject.zObject):
	>>> 	def __init__(self):
	>>> 		zObject.zObject.__init__(self)
	>>> 		
	>>> class Test2(zObject.zObject):
	>>> 	def __init__(self):
	>>> 		zObject.zObject.__init__(self)
	>>> 
	>>> # create an instance of test1 #		
	>>> a = Test1()
	>>> 
	>>> # create a collection that can only hold Test1 objects #
	>>> col = zCollection(Test1) 
	>>> col.Count
	0
	>>> 
	>>> # add a test1 item to the collection #
	>>> col.Add(a)
	>>> col.Count
	1
	>>> 
	>>> # add a list of items #
	>>> lst = []
	>>> for i in range(4): lst.append(Test1())
	>>> col.AddItems(lst)
	>>> col.Count
	4
	>>> 
	>>> # access a collection item directly #
	>>> print col(2)
	Class: <class '__main__.Test1' 1b4179c862b38dd9a5d95051ae73a5bd >
	>>> 
	>>> # get the last item in the collection #
	>>> print col(-1)
	Class: <class '__main__.Test1' 0b6fa37517bb834f787a731d1ab695f2 >
	
	@type Count: Integer
	@type CollectionType: Class
	'''
	
	_list = None
	_classCache = None
	_inc = None
	
	def __init__(self, classObject):
		'''
		Pass in a class object to determine what kind of collection
		this is going to be.
		
		@param classObject: class object that the collection can hold
		@type classObject: class
		'''
		# init the zooObject #
		zObject.zObject.__init__(self)
		
		# cache a clean version of the class for future reference #
		self._classCache = classObject
		
		# setup a new list #
		self._list = []

		# make sure we have a class #
		import inspect
		if not inspect.isclass(classObject):
			raise zCollectionTypeError, \
			'Expecting class object on init. Got: %r' % type(classObject)
			
		# make sure the class definition is a derivative of a zObject #
		iszObject = False
		for klass in inspect.getmro(classObject):
			if klass == zObject.zObject:
				iszObject = True
				break
		if not iszObject:
			raise zCollectionTypeError, \
			'%r not a subclass of a zObject' % classObject
			
			  
	def _getCount(self):
		'''Get the collection count'''
		return len(self._list)
		
	def _modCount(self, value):
		raise zCollectionAttributeError, "Can't modify a collection's count."
	   
	Count = property(_getCount, _modCount, doc='Get Collection Count')  
	
	
	def _getColType(self):
		'''Returns the collection class type.'''
		return self._classCache	  
	def _modColType(self):
		'''Can't modify a collection's CollectionType.'''
		raise zCollectionAttributeError, "Can't modify a collection's CollectionType"
	CollectionType = property(_getColType, _modColType, _modColType)
	
	def Add(self, object):
		'''
		Add an object to a collection.  Object must be instance of L{zCollection.CollectionType}.
		
		@param object: zObject to add to the collection
		@type  object: L{zObject.zObject}
		'''
		
		if isinstance(object, self._classCache):
			self._list.append(object)
		else:
			raise zCollectionTypeError, \
			  'Object "%s" doesn\'t match collection type "%s"' % \
									  (object.__class__,
										self._classCache)
	
	def AddItems(self, objects):
		'''
		Adds a list of objects to the collection.
		
		@param objects:
		@type objects: list of L{zObject.zObject}
		'''
		
		# check the type #
		if type(objects) != type(list()):
			raise zCollectionTypeError, \
			  "AddItems Parameter is not a list.  It's a %s" % (type(objects))
			  
		# step through the objects and add them #	  
		for obj in objects:
			try:
				self.Add(obj)
			except zCollectionTypeError, e:
				print 'AddItems:', 'Skipping "%s."' % (obj.__class__), e
				
	def Unique(self):
		'''
		Makes the collection unique in place.
		'''
		# run backwards through the list, #
		# this will allow is to keep the first instance of the item #
		self._list.reverse()
		
		# step through each item in the list #
		for item in self._list:
			while self._list.count(item) > 1:
				self._list.remove(item)
	
		# reverse the list again #
		self._list.reverse()
		
	def Remove(self, obj, allInstances=True):
		'''
		Removes an object from a zCollection.
		(if it exists).
		
		@param obj: the zooObject to remove
		@type obj: zObject
		@param allInstances: Removes all instances of this item from the collection.
				If false, it does the first instance only.
		
		@return: Returns true if items were removed from the collection, otherwise returns false
		@rtype: bool
		'''
		# make sure we are handed a zObject #
		if not isinstance(obj, zObject.zObject):
			raise zCollectionTypeError, 'Item passed to remove not a zObject'

		# cache the size of the collection #
		originalSize = len(self._list)
			
		# remove the first instance of the object from the collection #
		if not allInstances:
			self._list.remove(obj)
		
		# remove all instances of the obj #
		else:
			while 1:
				# remove the first occurance of obj #
				try:
					self._list.remove(obj)
					continue
				except:
					break
					
		if len(self._list) < originalSize:
			return True
		else:
			return False
		
	# build the itterator functions #		
	def __iter__(self):
		'''turn class into itterator'''
		return self
	
	# implement the 'next' function #
	def next(self):
		'''next function for itterator'''
		
		# create a private attribute to hold the itteration counter #
		if not '_inc' in self.__dict__:
			self._inc = -1
			
		# increment the counter #
		self._inc = self._inc + 1
	
		if self._inc < len(self._list):
			
			# return item at itteration index #
			return self._list[ self._inc ]
		
		else:
			
			# cleanup the reference to the counter #
			del self.__dict__['_inc' ]
			
			# stop the itteration #
			raise StopIteration
		
	def __call__(self, value):
		'''
		Callable formats:
		
		zCollection(0) : returns the first item in the collection
		
		zCollection(-1) : returns the index counting from the end
		
		zCollection('string') : returns the first item where the name attribute 
		matches input value
		'''
		
		# catch the integer input #
		if type(value) == type(int()):
			
			# catch negative values #
			if value < 0:
				
				# make sure index is in range #
#				if value > (len(self._list) * -1):
				if len(self._list) + value >= 0:
					
					return self._list[ value ]
				
				else:
					raise zCollectionAttributeError, \
						  'Index(%s) out of range of zCollection Length (%s)' % (value, len(self._list)) 
					
				
			# make sure the integer is in range #
			elif len(self._list)- value > 0:
				
				# return the object at the index #
				return self._list[ value ]
			
			else:
				raise zCollectionAttributeError, \
					  'Index(%s) out of range of zCollection Length (%s)' % (value, len(self._list)) 
		elif type(value) == type(str()):
			# step through each item in the list looking for the name #
			for item in self._list:
				if item.name == value:
					return item
			# if we made it this far we didn't find the name #
			raise zCollectionAttributeError, 'Unable to locate collection item by name "%s"' % value
				
		else:
			raise zCollectionAttributeError, 'Expecting an Integer or string as the value'
		

	def GetUniqueName(self, name):
		'''Return a unique name in the collection for the supplied name'''
		
		newName = name
		
		# make sure the name is unique #
		notUnique = True
		while notUnique:
			
			found = False
			
			# itterate through the class items #
			for item in self:
				
				# if the name matches #
				if item.name == newName:
					
					# trigger the found flag #
					found = True
					
					# numerical increment the name #
					inc = 0
					
					try:
						# convert the character to an integer #
						i = int(newName[inc-1])
						inc = inc-1
					except:
						pass
					
					if not inc:
						newName = newName + '1'
					else:
						newName = '%s%s' % (newName[:inc], int(newName[inc:])+1)
						
					
			# set the unique status to the found status #
			notUnique = found
			
		# return the new name #
		return newName
		
	def __repr__(self):
		return '<%s (%s)>' % (self.__class__.__name__, self.Count)
	
class zGenericCollection(zCollection):
	'''A generic collection of any L{zObject.zObject} '''
	def __init__(self, *args, **kwargs):
		
		# initialize the collection object #
		zCollection.__init__(self, zObject.zObject)
		
	
class TestCollection(unittest.TestCase):
	
	def setUp(self):
		
		# create some test classes #
		class Test1(zObject.zObject):
			def __init__(self):
				zObject.zObject.__init__(self)
			
		class Test2(zObject.zObject):
			def __init__(self):
				zObject.zObject.__init__(self)
				
		self.Test1 = Test1
		self.Test2 = Test2
		
	def tearDown(self):
		del self.Test1
		del self.Test2
			
	def getTestClass(self):
		# create a test zObject class #
		class Test(zObject.zObject):
			def __init__(self):
				zObject.zObject.__init__(self)
		
		return Test
	
	def test_Init(self):
		'''Test the collection initialization'''
		
		# create a new collection with a zooobject
		# should not raise an error
		testClass = self.getTestClass()
		col = zCollection(testClass)
		self.assertTrue(isinstance(col, zCollection), 'zCollection not initing properly')
		
		# create a generic class #
		class Generic: pass
		
		# create a new collection with a dictionary
		# should fail
		self.assertRaises(zCollectionTypeError, zCollection, Generic)
		
	def test_Add(self):
		'''Test the Add() method'''
		
		# get a new collection #	
		c = zCollection(self.Test1)
		
		# try to add the same type object #
		try:
			c.Add(self.Test1())
		except:
			self.fail('Unable to Add correct type to collection')
			
		# should fail when adding a type of a different class #	
		self.assertRaises(zCollectionTypeError, c.Add, self.Test2())
		
	def test_zGenericCollection(self):
		'''Test the generic zGenericCollection'''
		
		# create a generic zoo collection #
		zc = zGenericCollection(DEBUG=False)
		
		# try to add each object to the class #
		try:		
			zc.Add(self.Test1())
		except:
			self.fail('unable to add object to generic1 zoo collection')
			
		try:		
			zc.Add(self.Test2())
		except:
			self.fail('unable to add object to generic2 zoo collection')
		
		# make sure the items are there #	
		self.assertEquals(zc.Count, 2, 'zoo collection count incorrect')


	def test_Count(self):
		'''Test the collection Count attribute'''
		
		col = zGenericCollection()
		
		# populate the collection #		
		for i in range(10):
			col.Add(self.Test1())
			col.Add(self.Test2())
			
		# append the lists #
		self.assertEquals(col.Count, 20, 'Count Failed.  Incorrect zCollection Count')			
		
		# shouldn't be able to set the count #
		try:
			self.Count = 2
			self.fail('Was able to set the count of a collection')
		except:
			pass

		
	def test_Itter(self):
		'''Test the collection itterator function'''
		
		# create a collection #
		col = zCollection(self.Test1)
		
		# populate it #
		for i in range(3):
			col.Add(self.Test1())

		# try to run the itterotor over it #
		count = 0
		try:
			for item in col:
				count = count + 1
		except:
			self.fail('Unable to itterate over collection')
		self.assertEquals(count, 3, 'Did not itterate to correct number of times')

	def test_DirectIndex(self):
		'''Test accessing the collection by index'''
		
		col = zCollection(self.Test1)
		
		# should raise an error when calling an index on an empty collection #
		try:
			col(0)
			self.fail('Able to reach 0 index on an empty collection')
		except:
			pass

		col.Add(self.Test1())
		col.Add(self.Test1())
		
		try:
			col(-3)
			self.fail('Able to reach index -3 index.  Should be out if range.')
		except:
			pass
		
		try:
			col(-2)
		except:
			self.fail('Unable to reach -2 index. Should be in range.')
			
		try:
			col(1)
		except:
			self.fail('Unable to reach 1 index.  Should be in range.')
			

	def test_AddItems(self):
		'''Test AddItems() method'''
		
		col = zGenericCollection()
		
		a = []
		for i in range(3):
			a.append(self.Test1())
		
		# this is how it was ment to be used #
		try:
			col.AddItems(a)
		except:
			self.fail('Unable to AddItems to collecton')
			
		try:
			col.AddItems(str())
			self.fail('Was able to add items other than a list')
		except:
			pass
		
			
	def test_Remove(self):
		'''Test the Remove() method'''
		
		col = zGenericCollection()
		a = []
		for i in range(3):
			a.append(self.Test1())
		col.AddItems(a)

		# add 2 non unique objects #
		b = self.Test2()
		col.Add(b)
		col.Add(b)
		
		# remove an item #
		self.assertTrue(col.Remove(a[1]))
		
		# remove all instances of b #
		self.assertTrue(col.Remove(b))
		self.assertEquals(col.Count, 2, 'Unable to remove all instances of like objects')
		
		# try to remove an item not in the collection #
		self.assertFalse(col.Remove(self.Test2()), 'Was able to remove an item from the collection that was not in the collection')
		
		# pass in an item other than a zoo object #
		try:
			col.Remove('arse')
			self.fail('Was able to remove a non zObject from the collection')
		except:
			pass
		
		# try to remove only one instance of b #
		col = zGenericCollection()
		b = self.Test2()
		for i in range(4): col.Add(b)
		col.Remove(b, allInstances=False)
		self.assertEquals(col.Count, 3, 'Unable to remove only the first instance')
		
	def test_Unique(self):
		'''Test the Unique() method'''
		
		# build a collection of similar objects #
		c = zCollection(self.Test1)
		a = self.Test1()
		for i in range(3): c.Add(a)
		c.Add(self.Test1())
		
		# should remove all but the 2 unique instances #
		c.Unique()
		self.assertEquals(c.Count, 2, 'Unable to create a unique collection')
		
		# test is with a zGenericCollection #
		col = zGenericCollection()
		b = self.Test1()
		for i in range(3): col.Add(b)
		col.Add(self.Test2())
		col.Add(self.Test1())
		
		col.Unique()
		self.assertEquals(col.Count, 3, 'Unable to create a unique collection with a zGenericCollection')
	
	def test_GetByString(self):
		c = zCollection(self.Test1)
		a = self.Test1()
		a.name = 'arse'
		c.Add(a)
		self.assertEquals(a, c('arse'), 'Unable to call with a string value')
								    			
if __name__ == '__main__':
	unittest.main()
	pass

#===============================================================================
#	# create 2 test zObject classes #
#	class Test1(zObject.zObject):
#		def __init__(self):
#			zObject.zObject.__init__(self)
#			
#	class Test2(zObject.zObject):
#		def __init__(self):
#			zObject.zObject.__init__(self)
#	
#	# create an instance of test1 #		
#	a = Test1()
#	
#	# create a collection that can only hold Test1 objects #
#	col = zCollection(Test1) 
#	col.Count
#	
#	# add a test1 item to the collection #
#	col.Add(a)
#	col.Count
#	
#	# add a 
#	lst = []
#	for i in range(4): lst.append(Test1())
#	col.AddItems(lst)
#	col.Count
#	
#	# access a collection item directly #
##	print col(2)
#	
#	# get the last item in the collection #
##	print col(-1)
#
#	class A(object):
#		pass
#	zCollection(A)
#===============================================================================
