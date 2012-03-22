"""
zShotfile.py

Created by  on 2008-04-21.
Copyright (c) 2008 Zoogloo LLC. All rights reserved.
"""

__version__ = '$Revision: 11 $'
__author__  = '$Author: andy $'
__date__    = '$Date: 2008-07-21 15:20 -0700 $'

import win32com.client
from win32com.client import constants
from win32com.client import constants as c
from win32com.client.dynamic import Dispatch as dispatch
import time
import os
import re
import xml.dom.minidom as dom

xsi = Application
log = xsi.logmessage

null = None
false = 0
true = 1

def XSILoadPlugin(in_reg):
	in_reg.Author = "andy"
	in_reg.Name = "zShotfile"
	in_reg.Email = ""
	in_reg.URL = ""
	try:
		in_reg.Major = int(__version__.split(' ')[1])
	except:
		in_reg.Major = 1
	in_reg.Minor = 0

	in_reg.RegisterProperty("zShotfile")
	
	in_reg.RegisterCommand("zLoadShotfile", "zLoadShotfile")
	
	# copyright message #
	msg = '''
------------------------------------------
  %s (v.%d.%d)
  Copyright 2008 Zoogloo LLC.
  All rights Reserved.
------------------------------------------
	''' % (in_reg.Name, in_reg.Major, in_reg.Minor)
	log(msg)

	return true

def XSIUnloadPlugin(in_reg):
	strPluginName = in_reg.Name
	Application.LogMessage(str(strPluginName) + str(" has been unloaded."))
	return true

def zLoadShotfile_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true

	oArgs = oCmd.Arguments
	oArgs.Add("filename",c.siArgumentInput, '', c.siString)
	oArgs.Add("section",c.siArgumentInput, 'rig', c.siString)
	oArgs.Add("execute",c.siArgumentInput, 'build', c.siString)
	oArgs.Add("newScene",c.siArgumentInput, True, c.siBool)
	return true

def zLoadShotfile_Execute(filename, section, execute, newScene):
	
	# make sure the file exists #
	if not os.path.exists(filename):
		log('Unable to locate "%s"' % filename, c.siError)
		return False

	# get the dirname #
	dirname = None
	dirname = os.path.dirname(filename)
	
	# parse the xml file #
	xml = dom.parse(filename)
	zShotXML = xml.documentElement
	
	# create a new scene #
	if newScene: xsi.NewScene(None, False)
	
	# get an instance of zShot #
	zshot = zShot()
	
	# get the corresponding section element #
	sectionXML = None
	sectionsXML = zShotXML.getElementsByTagName('section')
	if not sectionsXML:
		log('Unable to locate sections xml element.', c.siError)
		return False
	# step through the sections #
	for sectXML in sectionsXML:
		# get the name attribute #
		if re.match('rig', sectXML.getAttribute('name'), re.I):
			sectionXML = sectXML
			break
			
	# get the xsi application element off of the section #
	applicationsXML = sectionXML.getElementsByTagName('application')
	applicationXML = None
	for element in applicationsXML:
		if re.match('xsi', element.getAttribute('name'), re.I):
			applicationXML = element
			break
	if not applicationXML:
		log('Unable to find XSI application in section %s.' % section, c.siError)
		return False
			
	# get the assets #
	assetsXML = applicationXML.getElementsByTagName('asset')
	for assetXML in assetsXML:
		log(`assetsXML`)
		# add the assets to the property #
		zShotProp.AddParameter3(
			'Asset_%s' % assetXML.getAttribute('name'),
			c.siString,
			assetXML.getAttribute('filename')
		)
	
	# get the executable #
	execsXML = applicationXML.getElementsByTagName('exec')
	execXML = None
	for element in execsXML:
		if re.match(execute, element.getAttribute('name'), re.I):
			execXML = element
	if not execXML:
		log('Unable to find executable "%s" in section %s for XSI.' % \
			(execute, section), c.siError)
		return False

	
class zShot(object):
	"""docstring for zShot"""
	
	sections 	= []
	asset		= []
	
	def __init__(self, arg):
		super(zShot, self).__init__()
		self.arg = arg
			
	def AddAsset(self, element):
		'''
		@param element: The xml minidom element of the asset.
		'''
		pass
		
	def GetAssetByName(self, name):
		'''
		Returns a dictionary of the assets info found by name.
		'''
		pass
		
	def GetAssetsByType(self, typeName):
		'''
		Returns a dictionary of the assets info found by name.
		'''
		pass

	def RegisterExecAsMethod(self, element):
		'''
		Adds the code from the executable element as a method to this zShot

		@param element: The xml minidom element of the executable.
		'''
		pass
		
		