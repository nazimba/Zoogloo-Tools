#!/usr/bin/env python
"""
zRigMenu.py

Created by andy on 2007-05-24.
Copyright (c) 2007 Zoogloo LLC. All rights reserved.
"""

import win32com.client
from win32com.client import constants
from win32com.client import constants as c
from win32com.client.dynamic import Dispatch as dispatch

null = None
false = 0
true = 1

xsi = Application
log = xsi.logmessage

def XSILoadPlugin( in_reg ):
	in_reg.Author = "Andy"
	in_reg.Name = "zRigMenu"
	in_reg.Email = ""
	in_reg.URL = ""
	in_reg.Major = 1
	in_reg.Minor = 0

	
	in_reg.RegisterMenu(c.siMenuMainTopLevelID, "zRigging Tools" )
	
	#RegistrationInsertionPoint - do not remove this line

	return true
	
def XSIUnloadPlugin( in_reg ):
	strPluginName = in_reg.Name
	Application.LogMessage(str(strPluginName) + str(" has been unloaded."))
	return true

def zRiggingTools_Init( ctxt ):

	menu = ctxt.Source
	# menu.AddCommandItem("Build Chain From Sel", "zBuildChainFromSelection")
	chains = menu.AddItem('Chains', c.siMenuItemSubmenu)
	chains = dispatch(chains)
	chains.AddCommandItem("Build Chain From Sel", "Build Chain From Sel")
	chains.AddSeparatorItem()
	chains.AddCommandItem( "Create Spine From Curve", "curveToSpine" );
	chains.AddCommandItem( "Spine Curve to Chains", "ZooBuildSpineFromSpineCurve" );
	chains.AddSeparatorItem()
	chains.AddCommandItem( "Scene Effectors to Last Bone", "zReorderEff" );
	
	env = menu.AddItem('Envelope', c.siMenuItemSubmenu)
	env = dispatch(env)
	env.AddCommandItem('Envelope To Mel', 'EnvToMelGUI')
	env.AddCommandItem('Swap Deformer', 'SwapDeformer')
	env.AddCommandItem('Normalize Envelope', 'NormalizeEnvelope')
	
	menu.AddCommandItem('Create Grip Stack From Sel', 'Create Grip Stack')
	menu.AddCommandItem('Duplicate Symmetrical Chain', 'Dup Sym Chain')
	
	menu.AddSeparatorItem()
	
	nodes = menu.AddItem('Node Utilities', c.siMenuItemSubmenu)
	nodes = dispatch(nodes)
	nodes.AddCommandItem('Add Zero Node', 'zAddZeroNode')
	nodes.AddCommandItem('Add Hook Node', 'zAddHookNode')
	nodes.AddCommandItem('Add Env Node', 'zAddEnvNode')

	menu.AddCallbackItem('Tag by Symmetry', 'OpenTagSymmetryGUI')
	
	menu.AddSeparatorItem()

	menu.AddCallbackItem('Get Controller Stack', 'zCreateConFromMenu')
	
	rigs = menu.AddItem('Rigs', c.siMenuItemSubmenu)
	rigs = dispatch(rigs)
	
	dinoLeg = rigs.AddItem('Rigs', c.siMenuItemSubmenu)
	dinoLeg = dispatch(dinoLeg)
	dinoLeg.AddCommandItem('Dino Leg Guide', 'zDinoLegGuide')
	dinoLeg.AddCallbackItem('Dino Leg Rig', 'zDinoLegRigGUI')
	
	menu.AddCommandItem('Jiggle', 'zJiggle')

def zCreateConFromMenu(ctxt):
	stack = xsi.zCreateCon(xsi.ActiveSceneRoot, 'zCon')
	xsi.InspectObj(stack(0))
	
def OpenTagSymmetryGUI(ctxt):
	
	prop = xsi.ActiveSceneRoot.Properties('zTagSymmetryGUI')
	if not prop:
		prop = xsi.ActiveSceneRoot.AddProperty('zTagSymmetryGUI')
	xsi.InspectObj(prop)
	
def zDinoLegRigGUI(ctxt):
	prop = xsi.ActiveSceneRoot.AddProperty('CustomProperty', False, 'zDinoLegGUI')
	prop = dispatch(prop)
	prop.AddParameter3("Symmetry", c.siString, "Right")
	try:
		xsi.InspectObj(prop, None, 'DinoLeg', c.siModal)
		xsi.zDinoLegRig(prop.Symmetry.Value)
	except:
		pass
	xsi.DeleteObj(prop)
	
	
	
