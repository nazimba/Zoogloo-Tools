#!/usr/bin/env python
# encoding: utf-8
"""
zUID.py

Created by andy on 2007-12-13.
Copyright (c) 2007 Zoogloo LLC. All rights reserved.
"""

__version__ = '$Revision: 0 $'
__author__  = '$Author: andy $'
__date__    = '$Date: 2010-04-10 14:04 -0700 $'

import time, md5, os, random

class zUID:
	'''
	A unique id class
	
	Usage:
		
	>>> id1 = zUID()
	>>> print 'ID1:', id1
	ID1: 2f1c4e377e649db1995327648950c882
	
	@ivar _uid: Direct Access to the MD5
	@type _uid: md5
	
	'''
	
	_uid = None
	
	def __init__(self):
		
		# get the hostname #
		import socket
		host = socket.getfqdn()
		
		# get the username #
		user = None
		if os.name == 'nt':
			# # works for domain controllers too ( lifted from aspn )
			import win32api
			# import win32net
			# import win32netcon
			# dc=win32net.NetServerEnum(None,100,win32netcon.SV_TYPE_DOMAIN_CTRL)
			user=win32api.GetUserName()
			# if dc[0]:
			# 	# with domain controller #
			# 	dcname=dc[0][0]['name']
			# 	user = win32net.NetUserGetInfo("\\\\"+dcname,user,1)
			# else:
			# 	# without domain controller #
			# 	user = win32net.NetUserGetInfo(None,user,1)['name']
				
		if os.name == 'posix':
			user = os.environ['USER']
			# host = os.environ['HOSTNAME']
			
		# get a random number #
		rand = random.random()
		
		# set the private id value #
		self._uid = str( md5.new( '%s:%s:%s:%s' %( time.time(), user, host, rand ) ).hexdigest() )
		
	def __repr__(self):
#		return self._uid.hexdigest()
		return self._uid
	
	def __eq__(self, other):
		try:
			if self._uid == other._uid:
				return True
			else:
				return False
		except:
			return False
# tests #
import unittest
class TestzUID(unittest.TestCase):
	'''unittesting for uid'''
	
	def setUp(self):
		self.id1 = zUID()
		self.id2 = zUID()
			
	
if __name__ == '__main__':
	
	id1 = zUID()
	print 'ID1', id1
	id2 = zUID()
	print 'ID2', id2._uid, id2
	print 'ID1', id1._uid, id1
	
	print id1 == id1
	print id1 == id2
	
	print id1
	print '-' * 72
	for i in xrange( 10 ):
		print '%s: %s' % ( i, zUID() )
		
	