#!/usr/bin/env python
# encoding: utf-8
"""
zUtils.py

Created by  on 2008-02-27.
Copyright (c) 2008 Zoogloo LLC. All rights reserved.
"""

__version__ = '$Revision: 0 $'
__author__  = '$Author: andy $'
__date__    = '$Date: 2010-04-10 14:04 -0700 $'

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

