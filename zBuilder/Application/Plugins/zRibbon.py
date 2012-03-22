"""
zRibbon.py


Example:

xsi = Application
xsi.UpdatePlugins()
z = xsi.zRibbon()
z.node_start = xsi.selection(0)
z.node_end	= xsi.selection(1)
z.Install()


Created by andy on 2008-08-20.
Copyright (c) 2008 Zoogloo LLC. All rights reserved.
"""

__version__ = '$Revision: 214 $'
__author__  = '$Author: andy $'
__date__    = '$Date: 2009-12-30 00:36 -0800 $'

import win32com.client
from win32com.client import constants
from win32com.client import constants as c
from win32com.client.dynamic import Dispatch as dispatch
import os

xsi = Application
log = xsi.logmessage

null = None
false = 0
true = 1

def XSILoadPlugin(in_reg):
	in_reg.Author = "Andy Buecker"
	in_reg.Name = "zRibbon"
	in_reg.Email = "andy@zoogloo.net"
	in_reg.URL = ""
	in_reg.Major = 1
	in_reg.Minor = 1

	in_reg.RegisterProperty('zRibbon')

	in_reg.RegisterCommand('zRibbon', 'zRibbon')
	in_reg.RegisterCommand('zInstallRibbonPref', 'zInstallRibbonPref')
	in_reg.RegisterCommand('zGetRibbonPath', 'zGetRibbonPath')

	in_reg.RegisterMenu(c.siMenuTbAnimateActionsStoreID, 'zRibbonMenu', False)
	
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
# Menus
#-----------------------------------------------------------------------------
def zRibbonMenu_Init(ctxt):
	menu = ctxt.Source
	
	item = menu.AddCommandItem('zRibbonGUI', 'zRibbonGUI')
	item.Name = '(z) zRibbon'

#-----------------------------------------------------------------------------
# Properties
#-----------------------------------------------------------------------------
def zRibbon_Define(ctxt):
	prop = ctxt.Source
	
	prop.AddParameter3("Path", c.siString, '')

	
def zRibbon_DefineLayout(ctxt):
	lo = ctxt.Source
	lo.Clear()

	lo.AddGroup('zRibbon Path')
	lo.AddRow()
	lo.AddItem('Path')
	lo.AddButton('PickPath', '...')
	lo.EndRow()
	lo.EndGroup()
	
def zRibbon_PickPath_OnClicked():

	prop = PPG.Inspected(0)
	prop = dispatch(prop)
	
	# get the default path #
	path = ''
	if not prop.Path.Value or not os.path.exists(os.path.dirname(prop.Path.Value)):
		path = xsi.ActiveProject.Path
	else:
		path = os.path.dirname(prop.Path.Value)
	
	# navigate to the models directory if it exists #
	if os.path.exists(path + os.sep + 'Models'):
		path = path + os.sep + 'Models'
		 
	# build a file browser #
	fb = XSIUIToolkit.FileBrowser
	fb.DialogTitle 		= "Pick the XSI zRibbon Model..."
	fb.InitialDirectory = path
	fb.FileBaseName 	= "ribbon"
	fb.Filter 			= "XSI Model (*.emdl)|*.emdl|All Files (*.*)|*.*||"
	fb.ShowOpen()

	# get the filename #
	if fb.FilePathName:
		prop.Path.Value = fb.FilePathName
		
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

class zRibbon(object):

	# setup the input and output lists #
	_inputs_ = [
		'name',			   
		'symmetry',			   
		'parent',			   
		'model_path',		   
		'node_start',	   
		'node_end',	   
		'trans_start',	   
		'trans_end',	   
		'show_deformers',	   
		'group_deformers',
	]
	_outputs_ = [
		'ribbon_branch',
		'deformers',
		'node_b',
		'node_b_offset',
	]
	# required for COM wrapper #
	_public_methods_ = [
		'Install',
	]
	# define the output vars here #
	_public_attrs_ = [
	]
	_public_attrs_ += _inputs_ + _outputs_
	# define those attrs that are read only #
	_readonly_attrs_ = [
	]
	_readonly_attrs_ += _outputs_

	def __init__(self, name, sym='left'):
		super(zRibbon, self).__init__()

		# set the defaults for the input variables #
		for item in self._inputs_:
			setattr(self, item, None)
			
		# set the instance variables #
		self.name 			= name
		self.symmetry		= sym
		log('Sym: %s' % self.symmetry)
		self.parent			= xsi.ActiveSceneRoot
		self.model_path 	= None
		self.trans_start 	= None
		self.trans_end 		= None
		self.deformers		= dispatch('XSI.Collection')
		self.show_deformers	= False
		self.group_deformers = None

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
			
	def Install(self):
		"""docstring for Install"""
		#---------------------------------------------------------------------
		# pre-conditions #
		if not self.node_start: raise Exception('"node_start" attribute not specified.')
		if not self.node_end: 	raise Exception('"node_end" attribute not specified.')
		
		if not self.trans_start: 	self.trans_start 	= self.node_start.Kinematics.Global.Transform
		if not self.trans_end: 		self.trans_end 		= self.node_end.Kinematics.Global.Transform
		
		# get the model path from the preferences if we aren't given one #
		if not self.model_path:
			self.model_path = xsi.zGetRibbonPath()
		
		# make sure the path to the ribbon exists #
		if not os.path.exists(self.model_path):
			log('Unable to locate ribbon model: %s' % self.model_path, c.siError)
			raise Exception('Unable to locate ribbon model: %s' % self.model_path)
		
		#---------------------------------------------------------------------
		# import the model #
		rib_model = xsi.ImportModel(self.model_path, xsi.ActiveSceneRoot, False)(1)
		
		# get the hooks #
		node_a = rib_model.FindChild('XXXXA_L_Pos')
		node_c = rib_model.FindChild('XXXXC_L_Pos')
		
		# align the transforms #
		node_a.Kinematics.Global.Transform = self.trans_start
		node_c.Kinematics.Global.Transform = self.trans_end
		
		# constrain the nodes #
		node_a.Kinematics.AddConstraint('Pose', self.node_start, True)
		node_c.Kinematics.AddConstraint('Pose', self.node_end, True)
		
		# make sure node get put in the outputs #
		self.ribbon_branch  = rib_model.FindChild('XXXX_L_Bunch')
		self.node_b			= rib_model.FindChild('XXXXB_L_Pos')
		self.node_b_offset	= rib_model.FindChild('XXXXB_L_OffSet')
		
		# turn off the icon display #
		self.ribbon_branch.primary_icon.Value = 0
		self.ribbon_branch.Properties('Visibility').Parameters('viewvis').Value = False
		self.ribbon_branch.Properties('Visibility').Parameters('rendvis').Value = False
		
		# rename #
		for item in rib_model.FindChildren('*'):
			item = dispatch(item)
			# split the name #
			try:
				name, sym, typ = item.Name.split('_')
			except:
				# continue over malformed names (like model names), don't halt here #
				continue
			# build a new name #
			item.Name = xsi.zMapName(
				name.replace('XXXX', '%sRbn' % self.name),
				'Custom:%s' % typ, 
				self.symmetry
			)
			
			# add the env's to the deformer group #
			if typ == 'Env': 
				self.deformers.Add(item)
				
			# visibility #
			if not self.show_deformers:
				if item.Type == 'null':
					item.primary_icon.Value = 0
					item.Properties('Visibility').Parameters('viewvis').Value = False
					item.Properties('Visibility').Parameters('rendvis').Value = False
					
		# rename the branch node #
		self.ribbon_branch.Name = xsi.zMapName(
			'%sRbn' % self.name, 
			'Branch', 
			self.symmetry
		)

		# parent #
		self.parent.AddChild(self.ribbon_branch)
		
		# get the deformers #
		deformers = self.ribbon_branch.FindChildren('*_Env')
		log('Deformers: %s' % deformers.GetAsText())
		log('self.group_deformers: %s' % self.group_deformers)
		
		# cleanup #
		xsi.DeleteObj(rib_model)
		
		#---------------------------------------------------------------------
		# add the deformers to the deformers group #
		if self.group_deformers:
			self.group_deformers = dispatch(self.group_deformers)
			self.group_deformers.AddMember(deformers)


#-----------------------------------------------------------------------------
# Commands
#-----------------------------------------------------------------------------
def zRibbon_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	#oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments
	oArgs.Add('rib_name', c.siArgumentInput, 'zRib', c.siString)
	oArgs.Add('symmetry', c.siArgumentInput, 'left', c.siString)
	#oArgs.AddObjectArgument('model')

	return True
	
def zRibbon_Execute(rib_name, symmetry):
	return win32com.server.util.wrap(
		zRibbon(rib_name, symmetry)
	)

#-----------------------------------------------------------------------------

def zInstallRibbonPref_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true

	return true

def zInstallRibbonPref_Execute():

	# make sure the ribbon doesn't exist #
	pref = xsi.Preferences.Categories('zRibbon')
	if pref:
		log('zRibbon Pref all ready exists.', c.siError)
		return False
	
	# install the preference #
	prop = xsi.ActiveSceneRoot.AddProperty('zRibbon', False)
	xsi.InstallCustomPreferences(prop, 'zRibbon')
	xsi.DeleteObj(prop)
	
	# return the preferences #
	return xsi.Preferences.Categories('zRibbon')

#-----------------------------------------------------------------------------

def zGetRibbonPath_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true

	return true

def zGetRibbonPath_Execute():

	# get the prefs #
	pref = xsi.Preferences.Categories('zRibbon')
	if not pref:
		pref = xsi.zInstallRibbonPref()

	# make sure the path exists #
	if not pref.Path.Value or not os.path.exists(os.path.dirname(pref.Path.Value)):
		msg = 'Unable to find ribbon at path: "%s"' % pref.Path.Value
		log(msg, c.siError)
		raise Exception(msg)
	
	# return the path string #	
	return pref.Path.Value