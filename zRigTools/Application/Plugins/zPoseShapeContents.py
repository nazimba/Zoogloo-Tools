#!/usr/bin/env python
"""
zPoseShapeContents.py

TODO: Convert properties to zProps

Created by andy on 2008-06-28.
Copyright (c) 2008 Zoogloo LLC. All rights reserved.
"""

import xml.dom.minidom as dom
import time
import os
import re
import sys

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

class zPoseShapeContents(object):
	'''
	Class for manipulating pose shapes contents files.
	'''
	# required for COM wrapper #
	_public_methods_ = [
		'Load',
		'Save',
		'AddDriven',
		'RemoveDriven',
		'UpdateInfo',
	]
	# define the output vars here #
	_public_attrs_ = [
		'pose_name',
		'info',
		'vectors',
		'driven',
		'pose',
		'objs',
		'XML',
	]
	# define those attrs that are read only #
	_readonly_attrs_ = [
		'pose_name'
	]

	# class variables #
	dir_pose_shape		= None
	
	# private variables #
	_info		= None
	_pose		= None
	_objs		= None
	_pose_name	= None
	_vectors	= None
	_driven		= None

	def __init__(self, dir_pose_shape):
		super(zPoseShapeContents, self).__init__()
		
		# store the pose shape dir #
		self.dir_pose_shape = dir_pose_shape

		# build the stub contents xml #
		impl = dom.getDOMImplementation()
		self._docType = impl.createDocumentType('zPoseShape', '-//Zoogloo//zPoseShape 1.0//EN' , 'http://zoogloo.net/dtds/zPoseShape-1.0.dtd')
		self._doc = impl.createDocument(None, "zPoseShape", None)
		self._top = self._doc.documentElement
		
	def __repr__(self):
		return "<zPoseShapeContents '%s'>" % self.pose_name

	@property	
	def pose_name(self):
		# get the pose name if it isn't cached #
		if not self._pose_name:
			base_name = os.path.basename(self.dir_pose_shape)
			self._pose_name = os.path.splitext(base_name)[0]
		# return the pose name #
		return self._pose_name
		
	@property
	def info(self):
		# define the info if it doesn't exist #
		if not self._info:
			if "win32com" in sys.modules:
				import win32com
				xsi = win32com.client.Dispatch('XSI.Application').Application
				self._info = win32com.server.util.wrap(
					Info(self)
				)
				# dispatch the info #
				self._info = win32com.client.Dispatch(self._info)
			else:
				self._info = Info(self)
		# return the info #
		return self._info
		
	def UpdateInfo(self):
		'''updates the info with the current session'''
		if "win32com" in sys.modules:
			import win32com
			xsi = win32com.client.Dispatch('XSI.Application').Application
			self._info = win32com.server.util.wrap(
				Info(self)
			)
			# dispatch the info #
			self._info = win32com.client.Dispatch(self._info)
		else:
			self._info = Info(self)

		# return the info #
		return self._info
			
	@property
	def objs(self):
		# add the objs class if it doesn't exist #
		if not self._objs:
			if "win32com" in sys.modules:
				import win32com
				xsi = win32com.client.Dispatch('XSI.Application').Application
				self._objs = win32com.server.util.wrap(
					Objs(self)
				)
				self._objs =  win32com.client.Dispatch(self._objs)
			else:
				self._objs = Objs(self)
		# return the objs reference #
		return self._objs

	@property
	def pose(self):
		# add the objs class if it doesn't exist #
		if not self._pose:
			if "win32com" in sys.modules:
				import win32com
				xsi = win32com.client.Dispatch('XSI.Application').Application
				self._pose = win32com.server.util.wrap(
					Pose(self)
				)
				self._pose =  win32com.client.Dispatch(self._pose)
			else:
				self._pose = Pose(self)
		# return the objs reference #
		return self._pose
		
	@property
	def driven(self):
		# return the objs reference #
		return self._driven
		
	def AddDriven(self, node='', channel='', curve=''):
		if "win32com" in sys.modules:
			import win32com
			xsi = win32com.client.Dispatch('XSI.Application').Application
			self._driven = win32com.server.util.wrap(
				Driven(self)
			)
			self._driven =  win32com.client.Dispatch(self._driven)
		else:
			self._driven = Driven(self)
		# set the defaults #
		self._driven.channel 	= channel
		self._driven.curve 		= curve
		self._driven.node 		= node
		
		return self._driven
		
	def RemoveDriven(self):
		'''Removes driven node element'''
		if self._driven:
			self._parent.removeChild(self._driven._xml)
		
	@property
	def vectors(self):
		if not self._vectors:
			if "win32com" in sys.modules:
				import win32com
				xsi = win32com.client.Dispatch('XSI.Application').Application
				self._vectors = win32com.server.util.wrap(
					Vectors(self)
				)
				self._vectors =  win32com.client.Dispatch(self._vectors)
			else:
				self._vectors = Vectors(self)
		# return the objs reference #
		return self._vectors
			

	def Save(self):
		"""Save the class to a contents xml file"""
		# write it to disk #
		file_xml = self.dir_pose_shape + os.sep + 'contents.xml'
		fh = open(file_xml, 'w')
		fh.write('<?xml version="1.0" encoding="utf-8"?>\n')
		self._docType.writexml(fh, indent='', addindent='\t', newl='\n')
		self._top.writexml(fh, indent='', addindent='\t', newl='\n')
		fh.close()
	
	@property	
	def XML(self):
		"""docstring for XML"""
		return self._top.toprettyxml()

	def Load(self):
		'''Parses and loads the contents file'''
		# make sure the file exists #
		if not os.path.exists(self.dir_pose_shape):
			raise Exception('Unable to locate path: %s' % self.dir_pose_shape)
		
		# get the contents #
		xml_contents = self.dir_pose_shape + os.sep + 'contents.xml'
		if not os.path.exists(xml_contents):
			raise Exception('Unable to locate contents.xml in "%s".' % self.dir_pose_shape)
		
		# parse contents #
		xml = dom.parse(xml_contents)
		top = xml.documentElement
		
		# step through the info attributes #
		for i in xrange(top.attributes.length):
			attr = top.attributes.item(i)
			setattr(self.info, attr.name, attr.value)
		
		# build the objs #
		obj_elements = top.getElementsByTagName('obj')
		for obj_elem in obj_elements:
			obj = self.objs.Add()
			for i in xrange(obj_elem.attributes.length):
				attr = obj_elem.attributes.item(i)
				setattr(obj, attr.name, attr.value)
				
		# build the pose #
		pose_elem = top.getElementsByTagName('pose')[0]
		for i in xrange(pose_elem.attributes.length):
			attr = pose_elem.attributes.item(i)
			setattr(self.pose, attr.name, attr.value)
		
		# build the vectors #
		v_elements = top.getElementsByTagName('vector')
		for v_elem in v_elements:
			vector = self.vectors.Add()
			for i in xrange(v_elem.attributes.length):
				attr = v_elem.attributes.item(i)
				setattr(vector, attr.name, attr.value)
			# get the rest and target vectors #
			for child in v_elem.childNodes:
				if child.nodeName == 'rest':
					for r in xrange(child.attributes.length):
						r_attr = child.attributes.item(r)
						setattr(vector.rest, r_attr.name, r_attr.value)
				elif child.nodeName == 'target':
					for r in xrange(child.attributes.length):
						r_attr = child.attributes.item(r)
						setattr(vector.target, r_attr.name, r_attr.value)

		# build the driven #
		driven_elem = top.getElementsByTagName('driven')
		if len(driven_elem):
			self.AddDriven()
			for i in xrange(driven_elem[0].attributes.length):
				attr = driven_elem[0].attributes.item(i)
				setattr(self.driven, attr.name, attr.value)
			# add the keys #
			for node in driven_elem[0].childNodes:
				if node.nodeName == 'key':
					key = self.driven.AddKey()
					for r in xrange(node.attributes.length):
						r_attr = node.attributes.item(r)
						setattr(key, r_attr.name, r_attr.value)

class Info(object):
	"""docstring for Info"""
	
	# required for COM wrapper #
	_public_methods_ = [
	]
	
	# define the output vars here #
	_public_attrs_ = [
		'author',
		'model',
		'date',
		'name',
		'version',
		'test'
	]
	
	# define those attrs that are read only #
	_readonly_attrs_ = []

	# class variables #
	_parent = None
	
	def __init__(self, parent, model_name="undefined"):
		super(Info, self).__init__()
		
		# store the parent #
		self._parent = parent
		
		# set the date #
		self.date = time.asctime()
		
		# set the version from the plugin #
		if "win32com" in sys.modules:
			import win32com
			xsi = win32com.client.Dispatch( 'XSI.Application' ).Application
			plugin = xsi.Plugins('zPoseShape')
			self.version = '%d.%d' % (plugin.Major, plugin.Minor)
		else:
			self.version = "unavailable"
			
		# set the author #
		if os.name == 'nt':
			import win32api
			user=win32api.GetUserName()
		if os.name == 'posix':
			user = os.environ['USER']
		self.author = user
		
		self.model 	= model_name
		self.name	= parent.pose_name
		
	def __repr__(self):
		return "<zPoseShapeContents.Info name='%s' author='%s' model='%s' date='%s' version='%s'>" % \
			(self.name, self.author, self.model, self.date, self.version)
		
	# .author #
	def _getAuthor(self):
		return self._parent._top.getAttribute("author")
	def _setAuthor(self, value):
		self._parent._top.setAttribute("author", str(value))
	author = property(_getAuthor, _setAuthor)

	# .model #
	def _getModel(self):
		return self._parent._top.getAttribute("model")
	def _setModel(self, value):
		self._parent._top.setAttribute("model", str(value))
	model = property(_getModel, _setModel)

	# .name #
	def _getName(self):
		return self._parent._top.getAttribute("name")
	def _setName(self, value):
		self._parent._top.setAttribute("name", str(value))
	name = property(_getName, _setName)

	# .version #
	def _getVersion(self):
		return self._parent._top.getAttribute("version")
	def _setVersion(self, value):
		self._parent._top.setAttribute("version", str(value))
	version = property(_getVersion, _setVersion)

	# .date #
	def _getDate(self):
		return time.strptime(self._parent._top.getAttribute("date"))
	def _setDate(self, value):
		self._parent._top.setAttribute("date", str(value))
	date = property(_getDate, _setDate)


class Objs(object):
	"""docstring for Objs"""
	
	# required for COM wrapper #
	_public_methods_ = [
		'Add'
	]
	
	# define the output vars here #
	_public_attrs_ = [
		'children'
	]
	
	# define those attrs that are read only #
	_readonly_attrs_ = []
	
	# class variables #
	_parent 	= None
	_xml		= None
	_children 	= []
	
	def __init__(self, parent):
		super(Objs, self).__init__()

		self._parent = parent
		self._children = []
		
		# add the xml component #
		self._xml = parent._doc.createElement('objs')
		parent._top.appendChild(self._xml)
		
	def __repr__(self):
		return "<zPoseShapeContents.Objs>"
		
	@property
	def children(self):
		"""returns all the child obj"""
		return self._children


	def Add(self, name='empty', typ='empty', fname='empty', point_count=0):
		"""docstring for AddObject"""
		# create an new obj #
		obj = None
		if "win32com" in sys.modules:
			import win32com
			xsi = win32com.client.Dispatch('XSI.Application').Application
			obj = win32com.server.util.wrap(
				Obj(self)
			)
			obj =  win32com.client.Dispatch(obj)
		else:
			obj = Obj(self)
		
		obj.file	= str(fname)
		obj.type 	= str(name)
		obj.name 	= str(typ)
		obj.points 	= str(point_count)

		# add it to the children list #
		self._children.append(obj)

		# return the new obj #
		return obj
		
class Obj(object):
	"""docstring for Obj"""

	# required for COM wrapper #
	_public_methods_ = [
	]
	
	# define the output vars here #
	_public_attrs_ = [
		'file',
		'type',
		'name',
		'points',
	]
	
	# define those attrs that are read only #
	_readonly_attrs_ = []
	
	# class variables #
	_parent 	= None
	_xml		= None
	
	def __init__(self, parent):
		super(Obj, self).__init__()
		self._parent = parent
		
		# create the xml element #
		self._xml = parent._parent._doc.createElement('obj')
		parent._xml.appendChild(self._xml)
		
	def __repr__(self):
		return "<zPoseShapeContents.Objs.Obj name='%s' points='%s'>" % \
		(self.name, self.points)
		
	# .name #
	def _getName(self):
		return self._xml.getAttribute("name")
	def _setName(self, value):
		self._xml.setAttribute("name", str(value))
	name = property(_getName, _setName)

	# .file #
	def _getFile(self):
		return self._xml.getAttribute("file")
	def _setFile(self, value):
		self._xml.setAttribute("file", str(value))
	file = property(_getFile, _setFile)

	# .type #
	def _getType(self):
		return self._xml.getAttribute("type")
	def _setType(self, value):
		self._xml.setAttribute("type", str(value))
	type = property(_getType, _setType)

	# .points #
	def _getPoints(self):
		return self._xml.getAttribute("points")
	def _setPoints(self, value):
		self._xml.setAttribute("points", str(value))
	points = property(_getPoints, _setPoints)

class Pose(object):
	"""docstring for Pose"""

	# required for COM wrapper #
	_public_methods_ = [
	]
	
	# define the output vars here #
	_public_attrs_ = [
		'file'
	]
	
	# define those attrs that are read only #
	_readonly_attrs_ = []
	
	# class variables #
	_parent 	= None
	_xml		= None
	_file		= None
	
	def __init__(self, parent):
		super(Pose, self).__init__()
		self._parent = parent
		
		# create the xml element #
		self._xml = parent._doc.createElement('pose')
		parent._top.appendChild(self._xml)
		
		# set the default filename #
		self.file = ''
		
	def __repr__(self):
		return "<Pose file='%s'>" % self.file
		
	# .filename #
	def _getFile(self):
		return self._xml.getAttribute("file")
	def _setFile(self, value):
		self._xml.setAttribute("file", str(value))
	file = property(_getFile, _setFile)

class Driven(object):
	"""docstring for Driven"""

	# required for COM wrapper #
	_public_methods_ = [
		'AddKey',
	]
	
	# define the output vars here #
	_public_attrs_ = [
		'node',
		'channel',
		'curve',
		'keys'
	]
	
	# define those attrs that are read only #
	_readonly_attrs_ = []
	
	# class variables #
	_parent 	= None
	_xml		= None
	_keys		= []
	
	def __init__(self, parent):
		super(Driven, self).__init__()
		self._parent = parent
		
		# create the xml element #
		self._xml = parent._doc.createElement('driven')
		parent._top.appendChild(self._xml)
		
		# set the defaults #
		self.node 	 = 'empty'
		self.channel = 'empty'
		self.curve	 = 'empty'
		
	def __repr__(self):
		return "<Driven node='%s' channel='%s'>" % (self.node, self.channel)
		
	def AddKey(self, value=0.0, weight=0.0):
		# create an new key #
		key = None
		if "win32com" in sys.modules:
			import win32com
			xsi = win32com.client.Dispatch('XSI.Application').Application
			key = win32com.server.util.wrap(
				Key(self)
			)
			key =  win32com.client.Dispatch(key)
		else:
			key = Key(self)
		
		key.value	= str(value)
		key.weight 	= str(weight)

		# add it to the children list #
		self._keys.append(key)

		# return the new key #
		return key
		
	# .node #
	@zProp
	def node():
		def fget(self):
			return self._xml.getAttribute("node")
		def fset(self, value):
			self._xml.setAttribute("node", str(value))
		return locals()

	# .channel #
	@zProp
	def channel():
		def fget(self):
			return self._xml.getAttribute("channel")
		def fset(self, value):
			self._xml.setAttribute("channel", str(value))
		return locals()
	
	# .curve #
	@zProp
	def curve():
		def fget(self):
			return self._xml.getAttribute("curve")
		def fset(self, value):
			self._xml.setAttribute("curve", str(value))
		return locals()

	# .keys #
	@zProp
	def keys():
		def fget(self):
			return self._keys
		return locals()
		
class Key(object):
	"""docstring for Key"""

	# required for COM wrapper #
	_public_methods_ = [
		'Destroy'
	]

	# define the output vars here #
	_public_attrs_ = [
		'value',
		'weight'
	]

	# define those attrs that are read only #
	_readonly_attrs_ = []

	# class variables #
	_parent 	= None
	_xml		= None
	
	def __init__(self, parent):
		super(Key, self).__init__()
		self._parent = parent

		# create the xml element #
		self._xml = parent._parent._doc.createElement('key')
		parent._xml.appendChild(self._xml)

	def __repr__(self):
		return "<zPoseShapeContents.Vectors.Vector axis='%s' node='%s'>" % \
		(self.axis, self.node)
		
	def Destroy(self):
		"""docstring for Destroy"""
		self._parent._xml.removeChild(self._xml)	
		
	# .value #
	@zProp
	def value():
		def fget(self):
			return self._xml.getAttribute("value")
		def fset(self, value):
			self._xml.setAttribute("value", str(value))
		return locals()

	# .weight #
	@zProp
	def weight():
		def fget(self):
			return self._xml.getAttribute("weight")
		def fset(self, value):
			self._xml.setAttribute("weight", str(value))
		return locals()

class Vectors(object):
	"""docstring for Vectors"""
	
	# required for COM wrapper #
	_public_methods_ = [
		'Add',
		'Clear'
	]
	
	# define the output vars here #
	_public_attrs_ = [
		'children'
	]
	
	# define those attrs that are read only #
	_readonly_attrs_ = []
	
	# class variables #
	_parent = None
	_xml	= None
	
	_children = []
	
	def __init__(self, parent):
		super(Vectors, self).__init__()

		self._parent 	= parent
		self._children 	= []
		
		# add the xml component #
		self._xml = parent._doc.createElement('vectors')
		parent._top.appendChild(self._xml)
		
	def __repr__(self):
		return "<zPoseShapeContents.Vectors>"
		
	@property
	def children(self):
		"""returns all the child obj"""
		return self._children


	def Add(self, axis='empty', invert='False', clamp='True', visualize='False', manips='False', scale='1', node='empty'):
		"""docstring for AddObject"""
		# create an new obj #
		vector = Vector(self)
		if "win32com" in sys.modules:
			import win32com
			xsi = win32com.client.Dispatch('XSI.Application').Application
			vector = win32com.server.util.wrap(
				vector
			)
			vector =  win32com.client.Dispatch(vector)
		
		vector.axis			= str(axis)		
		vector.invert 		= str(invert) 	
		vector.clamp 		= str(clamp)	
		vector.visualize 	= str(visualize)
		vector.manips 		= str(manips)
		vector.scale 		= str(scale) 	
		vector.node 		= str(node) 	

		# add it to the children list #
		self._children.append(vector)
		
		# return the new obj #
		return vector
		
	def Clear(self):
		'''clears the current vectors'''
		for vector in self.children:
			vector.Destroy()
			del vector
		
		
class Vector(object):
	"""docstring for Vector"""

	# required for COM wrapper #
	_public_methods_ = [
		'Destroy'
	]

	# define the output vars here #
	_public_attrs_ = [
		'axis',
		'invert',
		'clamp',
		'visualize',
		'manips',
		'scale',
		'node',
		'rest',
		'target'
	]

	# define those attrs that are read only #
	_readonly_attrs_ = []

	# class variables #
	_parent 	= None
	_xml		= None
	
	_rest		= None
	_target		= None
	
	def __init__(self, parent):
		super(Vector, self).__init__()
		self._parent = parent

		# create the xml element #
		self._xml = parent._parent._doc.createElement('vector')
		parent._xml.appendChild(self._xml)

	def __repr__(self):
		return "<zPoseShapeContents.Vectors.Vector axis='%s' node='%s'>" % \
		(self.axis, self.node)
		
	def Destroy(self):
		"""docstring for Destroy"""
		self._parent._xml.removeChild(self._xml)
		
	@property
	def rest(self):
		"""docstring for rest"""
		if not self._rest:
			if "win32com" in sys.modules:
				import win32com
				xsi = win32com.client.Dispatch('XSI.Application').Application
				self._rest = win32com.server.util.wrap(
					VectorRest(self)
				)
				self._rest =  win32com.client.Dispatch(self._rest)
			else:
				self._rest = VectorRest(self)
		# return the objs reference #
		return self._rest
	
	@property
	def target(self):
		"""docstring for target"""
		if not self._target:
			if "win32com" in sys.modules:
				import win32com
				xsi = win32com.client.Dispatch('XSI.Application').Application
				self._target = win32com.server.util.wrap(
					VectorTarget(self)
				)
				self._target =  win32com.client.Dispatch(self._target)
			else:
				self._target = VectorTarget(self)
		# return the objs reference #
		return self._target
	

	# .node #
	def _getNode(self):
		return self._xml.getAttribute("node")
	def _setNode(self, value):
		self._xml.setAttribute("node", str(value))
	node = property(_getNode, _setNode)

	# .invert #
	def _getInvert(self):
		return self._xml.getAttribute("invert")
	def _setInvert(self, value):
		self._xml.setAttribute("invert", str(value))
	invert = property(_getInvert, _setInvert)

	# .clamp #
	def _getClamp(self):
		return self._xml.getAttribute("clamp")
	def _setClamp(self, value):
		self._xml.setAttribute("clamp", str(value))
	clamp = property(_getClamp, _setClamp)

	# .visualize #
	def _getVisualize(self):
		return self._xml.getAttribute("visualize")
	def _setVisualize(self, value):
		self._xml.setAttribute("visualize", str(value))
	visualize = property(_getVisualize, _setVisualize)
				
	# .manips #
	def _getManips(self):
		return self._xml.getAttribute("manips")
	def _setManips(self, value):
		self._xml.setAttribute("manips", str(value))
	manips = property(_getManips, _setManips)

	# .scale #
	def _getScale(self):
		return self._xml.getAttribute("scale")
	def _setScale(self, value):
		self._xml.setAttribute("scale", str(value))
	scale = property(_getScale, _setScale)

	# .axis #
	def _getAxis(self):
		return self._xml.getAttribute("axis")
	def _setAxis(self, value):
		self._xml.setAttribute("axis", str(value))
	axis = property(_getAxis, _setAxis)
	
class VectorXYZ(object):
	"""docstring for VectorXYZ"""

	# required for COM wrapper #
	_public_methods_ = [
	]

	# define the output vars here #
	_public_attrs_ = [
		'x',
		'y',
		'z'
	]

	# define those attrs that are read only #
	_readonly_attrs_ = []

	# class variables #
	_parent 	= None
	_xml		= None
	
	# .x #
	def _getX(self):
		return self._xml.getAttribute("x")
	def _setX(self, value):
		self._xml.setAttribute("x", str(value))
	x = property(_getX, _setX)

	# .y #
	def _getY(self):
		return self._xml.getAttribute("y")
	def _setY(self, value):
		self._xml.setAttribute("y", str(value))
	y = property(_getY, _setY)

	# .z #
	def _getZ(self):
		return self._xml.getAttribute("z")
	def _setZ(self, value):
		self._xml.setAttribute("z", str(value))
	z = property(_getZ, _setZ)


class VectorRest(VectorXYZ):
	"""docstring for VectorRest"""
	def __init__(self, parent):
		super(VectorRest, self).__init__()
		self._parent = parent

		# create the xml element #
		self._xml = parent._parent._parent._doc.createElement('rest')
		parent._xml.appendChild(self._xml)
		
		# set the defaults #
		self.x = str(0)
		self.y = str(0)
		self.z = str(0)

class VectorTarget(VectorXYZ):
	"""docstring for VectorRest"""
	def __init__(self, parent):
		super(VectorTarget, self).__init__()
		self._parent = parent

		# create the xml element #
		self._xml = parent._parent._parent._doc.createElement('target')
		parent._xml.appendChild(self._xml)
		
		# set the defaults #
		self.x = str(0)
		self.y = str(0)
		self.z = str(0)

				
if __name__ == '__main__':

	if 0:
		ps = zPoseShapeContents("/Users/andy/Documents/work/Clients/D2/tcats/xsi/tcats_andy/zPoseShapes")
		print ps
		print ps.info
		print ps.objs
		obj = ps.objs.Add()
		obj = ps.objs.Add()
		print obj
		print ps.pose
		v1 =  ps.vectors.Add()
		v2 =  ps.vectors.Add()
		print v1.rest
		print v1.target
	
		print ps.vectors.children

	
		print ps.XML
		
		ps.vectors.Clear()
		print ps.XML
		
		driven = ps.AddDriven()
		print len(driven.keys)
		driven.AddKey()
		driven.AddKey(45, 1)
		print ps.XML
		# ps.Save()
	
	if 1:
		ps = zPoseShapeContents('/Users/andy/Documents/work/Clients/D2/tcats/xsi/tcats_andy/zPoseShapes/ArmRaisedSide_2.zpshp')
		ps.Load()
		print len(ps.vectors.children)
		print len(ps.objs.children)
		ps.objs.children[0].name='ARSE'
		print ps.XML
		