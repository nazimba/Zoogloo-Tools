#!/usr/bin/env python
# encoding: utf-8
"""
zSkinWeightsModel.py

Created by	on 2008-04-16.
Copyright (c) 2008 Zoogloo LLC. All rights reserved.
"""

__version__ = '$Revision: 6 $'
__author__	= '$Author: andy $'
__date__	= '$Date: 2008-07-19 16:31 -0700 $'

import sys
import os
from elixir import *

class SkinError(Exception): pass

class Skin(Entity):
	"""Skin elixir table"""

	using_options(tablename='Skin')

	name		= Field(Unicode(255), primary_key=True, unique=True)

	geometry	= OneToMany('Geometry')
	deformers	= OneToMany('Deformer')
	
	def __init__(self, name):
		self.name = name
	
	def __repr__(self):
		return '<Skin "%s">' % self.name
		
	def AddGeometry(self, name, type='Mesh'):
		if Geometry.get_by(name=name):
			raise SkinError, 'Geometry "%s" all ready exists.' % name
		# create a new piece of geometry #
		geom = Geometry(name=name, type=type)
		# append it to the skin #
		self.geometry.append(geom)
		# commit it to the database #
		#session.flush()
		# return the geometry #
		return geom

class Geometry(Entity):

	using_options(tablename='Geometry')

	name	= Field(Unicode(255), required=True, unique=True)
	type	= Field(Unicode(255), required=True)

	points		= OneToMany('Point')
	deformers	= ManyToMany('Deformer')
	skin		= ManyToOne('Skin', required=True)
	weights		= OneToMany('Weight')
	
	def __repr__(self):
		return '<Geometry "%s(%d):%s">' % (self.type, len(self.points), self.name)
		
	def AddDeformer(self, name):
		"""docstring for AddDeformer"""
		# get the deformer #
		if Deformer.get_by(name=name):
			raise SkinError, 'Deformer "%s" all ready exists.' % name
		# create the deformer if it doesn't exist #
		dfm = Deformer(name=name)
		# append it to the geometry's deformers #
		self.deformers.append(dfm)
		# add the deformer to the skin #
		self.skin.deformers.append(dfm)
		# commit it to the database #
		#session.flush()
		# return the deformer #
		return dfm

	def AddPoint(self, index):
		"""docstring for AddPoint"""
		# make sure the point doesn't exist #
		if Point.get_by(index=index, geometry=self):
			raise SkinError, 'Point "%d" all ready exists for "%s".' % (index, self.name)
		# create a new point #
		point = Point(index=index)
		# append it to the points #
		self.points.append(point)
		# return the point #
		return point

class Point(Entity):
	"""Point elixr table"""
	
	using_options(tablename='Point')

	index		= Field(Integer(), required=True)
	
	deformers	= ManyToMany('Deformer')
	weights		= ManyToMany('Weight')
	geometry	= ManyToOne('Geometry', required=True)
	
	def __repr__(self):
		return '<Point "%s">' % self.index
		
	def AddWeight(self, deformer, value):
		"""docstring for AddWeight"""
		# make sure we have a deformer object #
		if not isinstance(deformer, Deformer):
			raise SkinError, 'AddWeight(): "deformer" arg not of type Deformer.'
		# make sure the point isn't attached to deformer #
		if deformer in self.deformers:
			raise SkinError, 'AddWeight(): "%s" all ready applied to "%s"' % \
				(deformer, self)
		# create a new weight object #
		weight = Weight(deformer=deformer, point=self, geometry=self.geometry, value=value)
		# add it to the point's weights #
		self.weights.append(weight)
		# append it to the geometry's weight list #
		self.geometry.weights.append(weight)
		# add the deformer to the list #
		self.deformers.append(deformer)
		# commit it to the database #
		# session.flush()
		# return the weight #
		return weight
	
class Deformer(Entity):
	'''Deformer elixir table'''
	
	using_options(tablename='Deformer')
	
	name	= Field(Unicode(255), required=True, unique=True)
	red		= Field(Float())
	green	= Field(Float())
	blue	= Field(Float())
	
	points	 = ManyToMany('Point')
	geometry = ManyToMany('Geometry')
	skin	 = ManyToOne('Skin')
	
	def __repr__(self):
		return '<Deformer "%s">' % self.name
		
class Weight(Entity):
	'''Weight elixir table'''

	using_options(tablename='Weight')
		
	value		= Field(Float(), required=True)

	point		= ManyToOne('Point', required=True)
	deformer	= ManyToOne('Deformer', required=True)
	geometry	= ManyToOne('Geometry')
	
	def __repr__(self):
		return '<Weight Pnt:%s Dfm:%s %.4f>' % (self.point.index, self.deformer.name, self.value)

import unittest
class SkinWeightTests(unittest.TestCase):

	filename = 'test.weights.sqlite'

	def setUp(self):
		metadata.bind = "sqlite:///%s" % self.filename
		if os.path.exists(self.filename): os.unlink(self.filename)
		setup_all()
		create_all()

	def test_Geom(self):
		'''testing geometry'''
		skin = Skin('TestGeom')
		skin.AddGeometry('geo')
		# should fail if adding geom of the same name #
		self.failUnlessRaises(SkinError, skin.AddGeometry, 'geo')
		
	def test_Deformer(self):
		skin = Skin('TestDef')
		geo = skin.AddGeometry('geo')
		# add a deformer #
		geo.AddDeformer('blah')
		# should fail if trying to add the same deformer #
		self.failUnlessRaises(SkinError, geo.AddDeformer, 'blah')
		
	def test_Points(self):
		'''Testing Points'''
		
		# create a new skin #
		skin = Skin('Test')
		# add some geom #
		geo = skin.AddGeometry('geo')
		# add a point #
		geo.AddPoint(0)
		# should fail if adding another point with the same id #
		self.failUnlessRaises(SkinError, geo.AddPoint, 0)
		
		# add more geom #
		geo2 = skin.AddGeometry('geo2')
		# shouldn't fail if adding a point with same index to the new geom #
		try:
			geo2.AddPoint(0)
		except:
			self.fail()
			
	def tearDown(self):
		os.unlink(self.filename)
	

if __name__ == '__main__':
	# unittest.main()
			
	filename = 'weights.sqlite'
	metadata.bind = "sqlite:///%s" % filename
	if os.path.exists(filename):
		os.unlink(filename)
	# metadata.bind.echo = True
	setup_all()
	create_all()
	
	skin = Skin(name='arse')
	geo = skin.AddGeometry('blah')
	point = geo.AddPoint(0)
	dfm = geo.AddDeformer('Tits')
	geo.AddDeformer('T3')
	wgt = point.AddWeight(dfm, 1.0)

	geo2 = skin.AddGeometry('blah2')
	point2 = geo2.AddPoint(0)
	# dfm = geo.AddDeformer('Tits')
	session.flush()
	
	print skin
	print geo
	print point
	print wgt
	print point.weights
	print geo.weights
	print skin.deformers
	