"""
zTopStack.py (Depreciated)

Created by Andy Buecker on 2008-04-08.
Copyright (c) 2008 Zoogloo LLC. All rights reserved.
"""

__version__ = '$Revision: 214 $'
__author__  = '$Author: andy $'
__date__    = '$Date: 2009-12-30 00:36 -0800 $'

import win32com.client
from win32com.client import constants
from win32com.client import constants as c
from win32com.client import Dispatch as dispatch
xsi = Application
log = xsi.logmessage

null = None
false = 0
true = 1

class zTailError(Exception): pass

def XSILoadPlugin(in_reg):
	in_reg.Author = __author__.split(' ')[1]
	in_reg.Name = "zTopStack (Depreciated)"
	in_reg.Email = ""
	in_reg.URL = ""
	in_reg.Major = 1
	in_reg.Minor = 0

	in_reg.RegisterCommand("zTopStack")

	return True

def XSIUnloadPlugin(in_reg):
	strPluginName = in_reg.Name
	# Application.LogMessage(str(strPluginName) + str(" has been unloaded."))
	return true

class zTopStackClass(object):
	'''
	char = xsi.zCharacterRoot('PFX')
	char.Rig()
	stack = xsi.zTopStack(char)
	stack.SetCenterVector(XSIMath.CreateVector3(0,10,0))
	stack.Rig()
	'''
	# required for COM wrapper #
	_public_methods_ = [
		'Rig',
		'SetCenterVector',
		'SetCenterVectorFromNode',
		'SetCenterVectorFromValues'
	]
	# define the output vars here #
	_public_attrs_ = [
		'character',
		'centerVector',
		'centerNode',
		'controlsNode',
		'upperBodyNode',
		'lowerBodyNode',
		'skeletonNode',
		'flightNode',	
		'offsetNode',	
		'allNode',		
		'doNotTouch',		
		'deformersNode',		
		'geometryRender',		
		'geometryAnim',		
		'scaleNode'	
	]
	# define those attrs that are read only #
	_readonly_attrs_ = _public_attrs_

	# set the class variables #
	character 		= None
	centerVector 	= XSIMath.CreateVector3(0,3.5,0)
	centerNode		= None
	controlsNode	= None
	upperBodyNode	= None
	lowerBodyNode	= None
	skeletonNode	= None
	flightNode		= None
	offsetNode		= None
	allNode			= None
	scaleNode		= None
	doNotTouch		= None
	deformersNode	= None
	geometryRender	= None
	geometryAnim	= None
	
	def __init__(self, character):
		# store model to a class variable #
		
		self.character = character
		
	def SetCenterVector(self, XSIVector3):
		'''Set the center vector from an XSI Vector3'''
		# dispatch the vector #
		XSIVector3 = dispatch(XSIVector3)
		self.centerVector = XSIVector3

	def SetCenterVectorFromNode(self, XSINode):
		'''Set the center vector from the global transform of an XSI node'''
		# dispatch the node #
		XSINode = dispatch(XSINode)
		
		log('Set Center Reference from Node: %s' % XSINode, c.siVerbose)
		
		v = XSIMath.CreateVector3()
		XSINode.Kinematics.Global.Transform.GetTranslation(v)
		self.centerVector = v

	def SetCenterVectorFromValues(self, x, y, z):
		'''Set the center vector values'''
		self.centerVector = XSIMath.CreateVector3(x, y, z)

	def Rig(self):

		# draw the OFFSET null #
		# 	TODO: add class variable for the OFFSET name
		offsetRest = self.character.model.AddNull(xsi.zMapName('offset', 'Home', 'Middle'))
		offsetRest.primary_icon.Value = 0
		offsetRest.Properties('Visibility').Parameters('viewvis').Value = False
		offsetRest.Properties('Visibility').Parameters('rendvis').Value = False

		offsetGrip = offsetRest.AddNull(xsi.zMapName('offset', 'Control', 'Middle'))
		offsetRest.primary_icon.Value = 0
		offsetRest.Properties('Visibility').Parameters('viewvis').Value = False
		offsetRest.Properties('Visibility').Parameters('rendvis').Value = False
		self.offsetNode = offsetGrip
		
		offsetHook = offsetGrip.AddNull(xsi.zMapName('offset', 'Hook', 'Middle'))
		offsetHook.primary_icon.Value = 0
		offsetHook.Properties('Visibility').Parameters('viewvis').Value = False
		offsetHook.Properties('Visibility').Parameters('rendvis').Value = False

		# add it to the controls group #
		self.character.groupControls.AddMember(offsetGrip)
		
		# add to character set #
		stackSet = self.character.charSet.AddSubset('Stack')
		stackSet.AddNodePosRot(self.offsetNode)

		# draw the ALL null #
		# 	TODO: add class variable for the ALL name
		allRest = offsetHook.AddNull(xsi.zMapName('all', 'Home', 'Middle'))
		allRest.primary_icon.Value = 0
		allRest.Properties('Visibility').Parameters('viewvis').Value = False
		allRest.Properties('Visibility').Parameters('rendvis').Value = False

		allGrip = allRest.AddGeometry('Text', 'NurbsCurve', 
							xsi.zMapName('all', 'Control', 'Middle'))
		allGrip.text = "_RTF_{\\rtf1\\ansi\\deff0{\\fonttbl{\\f0\\fnil\\fprq5\\fcharset0 Arial;}}\r\n\\viewkind4\\uc1\\pard\\qc\\lang1033\\b\\f0\\fs20 %s\\b0\\par\r\n}\r\n" % \
		 				(self.character.info.Prefix.Value + '1')
		
		self.allNode = allGrip
		

		# move it below the character #
		allGrip.Kinematics.Global.Parameters('posy').Value = -40 * self.character.scaler
		xsi.ResetTransform(allGrip, "siCtr", "siTrn", "siXYZ")
		xsi.SetValue('%s.TextToCurveList.fitsize' % allGrip.FullName, 25*self.character.scaler)

		# add a defalut transform setup #
		manip = allGrip.AddProperty('Transform Setup', False)
		manip = dispatch(manip)
		manip.tool.Value = 4
		self.character.groupControls.AddMember(allGrip)

		# add a hook to the all control #
		allHook = allGrip.AddNull(xsi.zMapName('all', 'Hook', 'Middle'))
		allHook.primary_icon.Value = 0
		allHook.Properties('Visibility').Parameters('viewvis').Value = False
		allHook.Properties('Visibility').Parameters('rendvis').Value = False

		# add to character set #
		stackSet.AddNodePosRot(self.allNode)

		# change the color of the all node #
		# 	TODO: add class variable for the all wire color
		disp = allGrip.AddProperty('Display Property', False)
		disp = dispatch(disp)
		disp.wirecolorr.Value = 1
		disp.wirecolorg.Value = 0.5
		disp.wirecolorb.Value = 0

		# add a SCALE controller #
		# 	TODO: add class variable for the scale name
		scaleRest = allHook.AddNull(xsi.zMapName('scale', 'Home', 'Middle'))
		scaleRest.primary_icon.Value = 0
		scaleRest.Properties('Visibility').Parameters('viewvis').Value = False
		scaleRest.Properties('Visibility').Parameters('rendvis').Value = False

		scaleGrip = scaleRest.AddNull(xsi.zMapName('scale', 'Control', 'Middle'))
		scaleGrip.primary_icon.Value = 0
		scaleGrip.Properties('Visibility').Parameters('viewvis').Value = False
		scaleGrip.Properties('Visibility').Parameters('rendvis').Value = False
		self.scaleNode = scaleGrip

		scaleHook = scaleGrip.AddNull(xsi.zMapName('scale', 'Hook', 'Middle'))
		scaleHook.primary_icon.Value = 0
		scaleHook.Properties('Visibility').Parameters('viewvis').Value = False
		scaleHook.Properties('Visibility').Parameters('rendvis').Value = False
		
		# add a default transform to the scale control #
		manip = scaleGrip.AddProperty('Transform Setup', False)
		manip = dispatch(manip)
		manip.tool.Value = 2
		
		# add to the controls group #
		self.character.groupControls.AddMember(scaleGrip)

		# add to character set #
		# stackSet.AddParams('%(item)s.kine.global.sclx, %(item)s.kine.global.scly, %(item)s.kine.global.sclz' % {'item': scaleGrip})
		stackSet.AddNodeScl(scaleGrip)

		# create a FLIGHT con #
		# 	TODO: pass the con class #
		flightStack = xsi.zCreateCon(scaleHook, 'flight', 'Middle', 5, 30*self.character.scaler, 0.2, 0.7, 0.6)
		
		# adjust the position of the stack 
		trans = flightStack(1).Kinematics.Global.Transform
		trans.SetTranslation(self.centerVector)
		flightStack(1).Kinematics.Global.Transform = trans
		flightStack(1).Kinematics.Global.Parameters('rotx').Value = 0
		flightStack(1).Kinematics.Global.Parameters('roty').Value = -90
		flightStack(1).Kinematics.Global.Parameters('rotz').Value = 0
		flightStack(2).Kinematics.Local.Parameters('posx').Value = 8*self.character.scaler
		xsi.ResetTransform(flightStack(2), c.siCtr, c.siTrn, c.siXYZ)
		
		self.flightNode = flightStack(2)
		
		# add to the controls group #
		self.character.groupControls.AddMember(flightStack(2))

		# add to character set #
		stackSet.AddNodePosRot(self.flightNode)

		# add the CENTER node #
		self.centerNode = flightStack(3).AddNull(xsi.zMapName('center', 'Null', 'None'))
		self.centerNode.Kinematics.Global.Transform = flightStack(1).Kinematics.Global.Transform
		self.centerNode.primary_icon.Value = 0
		self.centerNode.Properties('Visibility').Parameters('viewvis').Value = False
		self.centerNode.Properties('Visibility').Parameters('rendvis').Value = False

		# draw a CONTROLS node #
		self.controlsNode = self.centerNode.AddNull(xsi.zMapName('Controls', 'Branch', 'None'))
		self.controlsNode.primary_icon.Value = 0
		self.controlsNode.Properties('Visibility').Parameters('viewvis').Value = False
		self.controlsNode.Properties('Visibility').Parameters('rendvis').Value = False

		# add LOWER and UPPER body groups #
		self.lowerBodyNode = self.controlsNode.AddNull(xsi.zMapName('LowerBody', 'Branch', 'None'))
		self.lowerBodyNode.primary_icon.Value = 0
		self.lowerBodyNode.Properties('Visibility').Parameters('viewvis').Value = False
		self.lowerBodyNode.Properties('Visibility').Parameters('rendvis').Value = False

		self.upperBodyNode = self.controlsNode.AddNull(xsi.zMapName('UpperBody', 'Branch', 'None'))
		self.upperBodyNode.primary_icon.Value = 0
		self.upperBodyNode.Properties('Visibility').Parameters('viewvis').Value = False
		self.upperBodyNode.Properties('Visibility').Parameters('rendvis').Value = False

		# draw a SKELETON node #
		self.skeletonNode = self.centerNode.AddNull(xsi.zMapName('Skeleton', 'Branch', 'None'))
		self.skeletonNode.primary_icon.Value = 0
		self.skeletonNode.Properties('Visibility').Parameters('viewvis').Value = False
		self.skeletonNode.Properties('Visibility').Parameters('rendvis').Value = False

		# create a do not touch node #
		self.doNotTouch 	= self.character.model.AddNull(xsi.zMapName('DoNotTouchThis', 'Branch', 'None'))
		self.doNotTouch.primary_icon.Value = 0
		self.doNotTouch.Properties('Visibility').Parameters('viewvis').Value = False
		self.doNotTouch.Properties('Visibility').Parameters('rendvis').Value = False

		# create a do not touch node #
		self.deformersNode 	= self.doNotTouch.AddNull(xsi.zMapName('Deformers', 'Branch', 'None'))
		self.deformersNode.primary_icon.Value = 0
		self.deformersNode.Properties('Visibility').Parameters('viewvis').Value = False
		self.deformersNode.Properties('Visibility').Parameters('rendvis').Value = False

		# constrain the scale of the do not touch to the scale node #
		self.doNotTouch.Kinematics.AddConstraint('Scaling', self.scaleNode, False)
		
		# create nodes for the geometry #
		self.geometryRender = self.doNotTouch.AddNull(xsi.zMapName('GeometryRender', 'Branch', 'None'))
		self.geometryRender.primary_icon.Value = 0
		self.geometryRender.Properties('Visibility').Parameters('viewvis').Value = False
		self.geometryRender.Properties('Visibility').Parameters('rendvis').Value = False

		self.geometryAnim = self.doNotTouch.AddNull(xsi.zMapName('GeometryAnim', 'Branch', 'None'))
		self.geometryAnim.primary_icon.Value = 0
		self.geometryAnim.Properties('Visibility').Parameters('viewvis').Value = False
		self.geometryAnim.Properties('Visibility').Parameters('rendvis').Value = False
		

def zTopStack_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.SetFlag(constants.siNoLogging, True)

	oArgs = oCmd.Arguments
	oArgs.Add("character", c.siArgumentInput)

	return True


def zTopStack_Execute(character):
	# export the python object #
	import win32com.server
	return win32com.server.util.wrap(
		zTopStackClass(character)
	)