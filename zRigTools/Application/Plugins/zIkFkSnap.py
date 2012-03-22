"""
XSI plugin for aligning nodes when switching between ik and fk.  

Note: This tool is not working properly on the legs.

Looks for a property called "zIKFK" with the following parameters:

FkNodes			= String of fk control nodes seperated by ','
Effector		= The name of the node used as the effector of the IK system, usually a contoller node
UpVector		= The name of the node used to control the plane orientation of the IK system
ControlTrans	= The name of the node used for the _transform_ reference the effector going from FK -> IK, such as the chain effector
PolePos			= The name of the node to use as the position starting point for the pole vector
PoleRot			= The name of the node to use as the rotation for the pole vector
Slider			= Fullname (minus the model name) of the slider parameter

Note: All value names should be stored without the model name.

I{Created by Andy Buecker on 2008-03-20.
Copyright (c) 2008 Zoogloo LLC. All rights reserved.}
"""

__version__ = '$Revision: 185 $'
__author__	= '$Author: andy $'
__date__	= '$Date: 2009-02-06 21:04 -0800 $'

import win32com.client
from win32com.client import constants
from win32com.client import constants as c
from win32com.client.dynamic import Dispatch as dispatch

xsi = Application
log = xsi.logmessage

null = None
false = 0
true = 1

def XSILoadPlugin( in_reg ):
	in_reg.Author = "Andy Buecker"
	in_reg.Name = "zIkFkSnap"
	in_reg.Email = ""
	in_reg.URL = ""
	try:
		in_reg.Major = int(__version__.split(' ')[1])
	except:
		in_reg.Major = 1
	in_reg.Minor = 0

	in_reg.RegisterCommand("zIkFkSnap")
	in_reg.RegisterCommand("zIkFkSnapSelection")
	
	# copyright message #
	msg = '''
------------------------------------------
  %s (v.%s.%s)
  Copyright 2008 Zoogloo LLC.
  All rights Reserved.
------------------------------------------
	''' % (in_reg.Name, in_reg.Major, in_reg.Minor)
	log(msg)

	#RegistrationInsertionPoint - do not remove this line

def XSIUnloadPlugin(in_reg):
	strPluginName = in_reg.Name
	Application.LogMessage(str(strPluginName) + str(" has been unloaded."))
	return true

#-----------------------------------------------------------------------------
# Commands
#-----------------------------------------------------------------------------
def zIkFkSnapSelection_Init( in_ctxt ):
	oCmd = in_ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = False
	return True

def zIkFkSnapSelection_Execute():
	
	# make sure there is something selected #
	if not xsi.selection.Count:
		log('Nothing Selected.', c.siError)
		return
		
	# run it #
	xsi.zIkFkSnap(xsi.selection(0))


def zIkFkSnap_Init( in_ctxt ):
	oCmd = in_ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = False

	oCmd.Arguments.AddObjectArgument('item')
	oCmd.Arguments.Add('setKey', c.siArgumentInput, True, c.siBool)

	return True

def zIkFkSnap_Execute(item, setKey):

	# find the zIkFk prob #
	prop = item.Properties('zIKFK')
	if not prop:
		xsi.logmessage('Ik/Fk property not found on item %s' % item.FullName, c.siError)
		return False
	prop = dispatch(prop)
	
	# get the fknodes #
	fkNodeList = prop.FkNodes.Value.split(',')
	# add the model name to the front #
	for i in xrange(len(fkNodeList)):
		fkNodeList[i] = '%s.%s' % (item.model.Name, fkNodeList[i])
	# build a collection #
	fkNodes = dispatch('XSI.Collection')
	try:
		fkNodes.SetAsText(','.join(fkNodeList))
	except:
		log('Unbale to find FkNodes "%s"' % prop.FkNodes.Value, c.siError)
		return False
		
	
	# get the effector #
	effCol = dispatch('XSI.Collection')
	try:
		effCol.SetAsText(item.model.Name + '.' + prop.Effector.Value)
	except:
		log('Unbale to find Effector "%s"' % prop.Effector.Value, c.siError)
		return False
	eff = effCol(0)
	
	# get the upvector #
	upvCol = dispatch('XSI.Collection')
	try:
		upvCol.SetAsText(item.model.Name + '.' + prop.UpVector.Value)
	except:
		log('Unbale to find UpVector "%s"' % prop.UpVector.Value, c.siError)
		return False
	upv = upvCol(0)
	
	# get the slider #
	sliderCol = dispatch('XSI.Collection')
	try:
		sliderCol.SetAsText(item.model.Name + '.' + prop.Slider.Value)
	except:
		log('Unbale to find Slider "%s"' % prop.Slider.Value, c.siError)
		return False
	slider = sliderCol(0)
	
	# get the Control Transform #
	conCol = dispatch('XSI.Collection')
	try:
		conCol.SetAsText(item.model.Name + '.' + prop.ControlTrans.Value)
	except:
		log('Unbale to find the Control Transform "%s"' % prop.ControlTrans.Value, c.siError)
		return False
	con = conCol(0)
	
	# get the Pole trans #
	poleCol = dispatch('XSI.Collection')
	try:
		poleCol.SetAsText(item.model.Name + '.' + prop.PolePos.Value)
	except:
		log('Unbale to find the Pole Pos "%s"' % prop.PolePos.Value, c.siError)
		return False
	polePos = poleCol(0)
	
	# get the Pole rotation #
	poleCol = dispatch('XSI.Collection')
	try:
		poleCol.SetAsText(item.model.Name + '.' + prop.PoleRot.Value)
	except:
		log('Unbale to find the Pole Pos "%s"' % prop.PoleRot.Value, c.siError)
		return False
	poleRot = poleCol(0)
	
	# make sure the slider is at 1 or 0 #
	if slider.Value != 1.0 and slider.Value != 0.0:
		log('The Ik/Fk slider is not at 0 or 1.  Unable to snap value.', c.siError)
		return False

	# deselect #
	xsi.DeselectAll()
	
	# switch from ik to fk #	
	if slider.Value == 1.0:
		# cache to global trans of the fknodes #
		transList = []
		for node in fkNodes:
			transList.append(node.Kinematics.Global.Transform)

			# select the nodes ( has to be before the slider or an update is triggered )#
			node.Selected = True
			
		# set a key on the effector #
		if setKey:
			pass
			
		# toggle the slider #
		slider.Value = 0.0
		# xsi.SceneRefresh()
		
		# set the orientation of the fknodes #
		for n in xrange(fkNodes.Count):
			trans = transList[n]
			node = fkNodes(n)
			node.Kinematics.Global.Transform = trans
			
			
	# switch from fk to ik #
	elif slider.Value == 0.0:
		# get the transform of the upvector #
		transUpv = polePos.Kinematics.Global.Transform
		rot = XSIMath.CreateRotation()
		poleRot.Kinematics.Global.Transform.GetRotation(rot)
		transUpv.AddLocalTranslation(XSIMath.CreateVector3(0,polePos.length.Value*2,0))
		
		# get the transforms for the controller #
		transEff = con.Kinematics.Global.Transform
		
		# set a key on the nodes #
		if setKey:
			pass
			
		# select the con ( has to be before the slider or an update is triggered )#
		eff.Selected = True
		
		# toggle the slider #
		slider.Value = 1.0
		
		# set the transforms #
		upv.Kinematics.Global.Transform = transUpv
		
		# set the transform of the controler #
		eff.Kinematics.Global.Transform = transEff
		
		
		
	

