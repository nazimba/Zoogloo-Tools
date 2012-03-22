#!/usr/bin/env python
# encoding: utf-8
"""
zProp.py

Created by Andy Buecker on 2009-02-12.
Copyright (c) 2009 Andy Buecker. All rights reserved.
"""

__version__ = '$Revision: 192 $'
__author__  = '$Author: andy $'
__date__    = '$Date: 2009-03-03 10:14 -0800 $'

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

