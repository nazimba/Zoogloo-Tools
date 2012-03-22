#!/usr/bin/env python
"""
zRigMenu.py

Created by andy on 2007-05-24.
Copyright (c) 2007 Zoogloo LLC. All rights reserved.

$Author: andy $
$Date: 2008-07-21 15:20 -0700 $
$Rev: 64 $
"""
import win32com.client
from win32com.client import constants
from win32com.client import constants as c

xsi = Application
log = xsi.logmessage

null = None
false = 0
true = 1

def XSILoadPlugin( in_reg ):
	in_reg.Author = "Andy"
	in_reg.Name = "zSymmetry"
	in_reg.Email = ""
	in_reg.URL = ""
	try:
		in_reg.Major = int(__version__.split(' ')[1])
	except:
		in_reg.Major = 1
	in_reg.Minor = 0

	
	in_reg.RegisterCommand("Dup Sym Chain", "zDuplicateSymmetricalChain" )
	in_reg.RegisterCommand("zSymmetry", "zSymmetry" )
	in_reg.RegisterCommand("zTagSymmetry", "zTagSymmetry" )
	
	in_reg.RegisterProperty("zTagSymmetryGUI")
	
	#RegistrationInsertionPoint - do not remove this line

	return true
	
def XSIUnloadPlugin( in_reg ):
	strPluginName = in_reg.Name
	Application.LogMessage(str(strPluginName) + str(" has been unloaded."))
	return true

def DupSymChain_Init( ctxt ):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = False

	return true

def DupSymChain_Execute(  ):
	
	# make sure we have a chain root selected #
	dupCol = win32com.client.Dispatch( 'XSI.Collection' )
	for node in xsi.selection:
		if node.Type == 'root':
			dupCol.Add( node )
			
	if not dupCol.Count:
		xsi.logmessage( 'Chain Root not selected', c.siError )
		return
	
	# step through each item in the dup collection #
	for sourceNode in dupCol:
		
		# duplicate the chain #
		dupRootStr = xsi.DuplicateSymmetry("B:%s" % sourceNode.FullName, 1, 1, 1, 0, 0, 0, 1)
		print dupRootStr
		
		# step through the resulting chain and switch the symmetrical name #
		col = win32com.client.Dispatch( 'XSI.Collection' )
		col.SetAsText( dupRootStr )
		dupNodes = col(0).FindChildren('*')
		
		# step through the duplicated nodes and Rename #
		for node in dupNodes:
			import sre
			if sre.match( '.*_Lft_.*', node.Name ):
				node.Name = node.Name[:-1].replace( '_Lft_', '_Rgt_' )
			elif sre.match( '.*_Rgt_.*', node.Name ):
				node.Name = node.Name[:-1].replace( '_Rgt_', '_Lft_' )
	
def zSymmetry_Init( ctxt ):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = False

	return true

def zSymmetry_Execute():
	
	for item in xsi.selecton:
		
		# duplicate the branch #
		dup = xsi.Duplicate( 'B:%s' % item, 1, c.siDuplicateHistory,
		 					c.siNoParent, c.siNoGrouping, 
							c.siDuplicateProperties, c.siNoAnimation,
							c.siNoConstraints, c.siSetSelection,
							c.siGlobalXForm
							)
	pass


def zTagSymmetry_Init( ctxt ):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = False
	
	oArgs = oCmd.Arguments
	oArgs.Add('axis', c.siArgumentInput, 'x', c.siString)
	oArgs.Add('tollerance', c.siArgumentInput, 0.002, c.siDouble)

	return true

def zTagSymmetry_Execute(axis, tollerance):
	
	
	for item in xsi.selection:
		
		if item.type == 'polymsh':
			points = item.ActivePrimitive.Geometry.Points
			pointList = []
			for p in xrange(points.Count):
				if axis == 'x':
					if points(p).Position.X > tollerance:
						pointList.append(str(p))
				elif axis == '-x':
					if points(p).Position.X < -tollerance:
						pointList.append(str(p))
				elif axis == 'y':
					if points(p).Position.Y > tollerance:
						pointList.append(str(p))
				elif axis == '-y':
					if points(p).Position.Y < -tollerance:
						pointList.append(str(p))
				elif axis == 'z':
					if points(p).Position.Z > tollerance:
						pointList.append(str(p))
				elif axis == '-z':
					if points(p).Position.Z < -tollerance:
						pointList.append(str(p))
						
			xsi.SelectGeometryComponents('%s.pnt[%s]' % (item.Fullname, ','.join(pointList)))
					
def zTagSymmetryGUI_Define(ctxt):
	cp = ctxt.Source
	
	cp.AddParameter3("Tollerance", c.siDouble, 0.002, 0, 0.1, False, False)
	# cp.AddParameter3("_inSubName", c.siString, None, None, None, False, False)
	
	return True
				

def zTagSymmetryGUI_DefineLayout(ctxt):
	lo = ctxt.Source
	lo.Clear()
	
	lo.AddRow()
	lo.AddSpacer()
	lo.AddButton('_X', '-X')
	lo.AddButton('X', 'X')
	lo.AddSpacer()
	lo.EndRow()
	
	lo.AddRow()
	lo.AddSpacer()
	lo.AddButton('_Y', '-Y')
	lo.AddButton('Y', 'Y')
	lo.AddSpacer()
	lo.EndRow()
	
	lo.AddRow()
	lo.AddSpacer()
	lo.AddButton('_Z', '-Z')
	lo.AddButton('Z', 'Z')
	lo.AddSpacer()
	lo.EndRow()
	
	
	lo.AddItem('Tollerance', 'Tollerance')
	
def zTagSymmetryGUI_X_OnClicked():
	xsi.zTagSymmetry('x')
	
def zTagSymmetryGUI__X_OnClicked():
	xsi.zTagSymmetry('-x')

def zTagSymmetryGUI_Y_OnClicked():
	xsi.zTagSymmetry('y')
	
def zTagSymmetryGUI__Y_OnClicked():
	xsi.zTagSymmetry('-y')

def zTagSymmetryGUI_Z_OnClicked():
	xsi.zTagSymmetry('z')
	
def zTagSymmetryGUI__Z_OnClicked():
	xsi.zTagSymmetry('-z')
