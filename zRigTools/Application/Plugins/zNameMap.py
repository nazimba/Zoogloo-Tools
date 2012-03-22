"""
zNameMap.py

Created by Andy Buecker on 2007-06-13.
Copyright (c) 2008 Zoogloo LLC. All rights reserved.
"""

__version__ = '$Revision: 198 $'
__author__  = '$Author: andy $'
__date__    = '$Date: 2009-03-06 10:14 -0800 $'

import win32com.client
from win32com.client import constants
from win32com.client import constants as c
from win32com.client.dynamic import Dispatch as dispatch
import re

xsi = Application
log = xsi.logmessage

null = None
false = 0
true = 1

def XSILoadPlugin(in_reg):
	in_reg.Author = "andy"
	in_reg.Name = "zNameMap"
	in_reg.Email = ""
	in_reg.URL = ""
	try:
		in_reg.Major = int(__version__.split(' ')[1])
	except:
		in_reg.Major = 1
	in_reg.Minor = 0

	in_reg.RegisterProperty("zNameMap")
	
	in_reg.RegisterCommand("zMapName","zMapName")
	in_reg.RegisterCommand("zInstallNameMapPref","zInstallNameMapPref")
	in_reg.RegisterCommand("zGetNameMapValue","zGetNameMapValue")
	
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

def zNameMap_Define(ctxt):
	
	prop = ctxt.Source
	
	# name map #
	prop.AddParameter3("Prefix", 	c.siString, "PFX1")

	prop.AddParameter3("Home", 		c.siString, "Rest")
	prop.AddParameter3("Control", 	c.siString, "Con")
	prop.AddParameter3("Hook", 		c.siString, "Hook")
	prop.AddParameter3("Null", 		c.siString, "Node")
	prop.AddParameter3("UpVector", 	c.siString, "Upv")
	prop.AddParameter3("Env", 		c.siString, "Env")
	prop.AddParameter3("Jiggle", 	c.siString, "Jgl")
	
	prop.AddParameter3("Zero", 		c.siString, "Zero")
	prop.AddParameter3("Pivot", 	c.siString, "Pivot")
	prop.AddParameter3("Offset", 	c.siString, "Offset")
	prop.AddParameter3("Group", 	c.siString, "Group")
	prop.AddParameter3("Branch", 	c.siString, "Bunch")
	
	prop.AddParameter3("ChainRoot", c.siString, "Chain")
	prop.AddParameter3("ChainBone", c.siString, "Bone")
	prop.AddParameter3("ChainEff", 	c.siString, "Eff")
	
	prop.AddParameter3("GeomRen", 	c.siString, "GeomRen")
	prop.AddParameter3("GeomAnim", 	c.siString, "GeomAnim")

	prop.AddParameter3("Middle", 	c.siString, "M")
	prop.AddParameter3("Left", 		c.siString, "L")
	prop.AddParameter3("Right", 	c.siString, "R")
	prop.AddParameter3("Back", 		c.siString, "B")
	prop.AddParameter3("Front", 	c.siString, "F")
	prop.AddParameter3("Top", 		c.siString, "T")
	prop.AddParameter3("Bottom", 	c.siString, "B")

	prop.AddParameter3("ItterType", c.siString, "Numeric")

	prop.AddParameter3("Capitalize", c.siBool, True, None, None, False, False)
	
	prop.AddParameter3("Rule", c.siString, "$(BASENAME)$(ITTER)_$(SYM)_$(TYP)")

	return True
	
def zNameMap_DefineLayout(ctxt):
	lo = ctxt.Source
	lo.Clear()
	
	lo.AddGroup("Mapping Rules")
	lo.AddItem("Rule")
	lo.EndGroup()

	lo.AddGroup("Prefix (PFX)")
	lo.AddItem("Prefix")
	lo.EndGroup()
	
	lo.AddGroup("Type (TYP)")
	
	lo.AddGroup('Stack')
	lo.AddItem("Home")
	lo.AddItem("Control")
	lo.AddItem("Hook")
	lo.EndGroup()
	
	lo.AddGroup('Nulls')
	lo.AddItem("Null")
	lo.AddItem("UpVector")
	lo.AddItem("Env")
	lo.AddItem("Jiggle")
	lo.AddItem("Zero")
	lo.AddItem("Pivot")
	lo.AddItem("Offset")
	lo.AddItem("Branch")
	lo.AddItem("Group")

	lo.AddGroup('Note:')
	lo.AddStaticText('You can also use "Custom:CustomType" as an argument to pass "CustomType" through to the value.', 300)
	lo.EndGroup()

	lo.EndGroup()
	
	lo.AddGroup('Chains')
	lo.AddItem("ChainRoot")
	lo.AddItem("ChainBone")
	lo.AddItem("ChainEff")
	lo.EndGroup()
	
	lo.AddGroup('Geometry')
	lo.AddItem("GeomRen")
	lo.AddItem("GeomAnim")
	lo.EndGroup()

	lo.EndGroup()
	
	lo.AddGroup("Symmetry (SYM)")
	lo.AddItem("Middle")
	lo.AddItem("Left")
	lo.AddItem("Right")
	lo.AddItem("Back")
	lo.AddItem("Front")
	lo.AddItem("Top")
	lo.AddItem("Bottom")
	lo.EndGroup()

	lo.AddGroup('Itteration (ITTER)')
	lo.AddEnumControl('ItterType', ['Numeric', 'Numeric', 'Alpha', 'Alpha'], 'Type')
	lo.EndGroup()
	
	lo.AddGroup('Options')
	lo.AddItem('Capitalize')
	lo.EndGroup()
	
	return true

def zInstallNameMapPref_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true
	return true

def zInstallNameMapPref_Execute():

	pref = xsi.Preferences.Categories('zNameMap')
	if pref:
		log('zNameMap Pref all ready exists.', c.siError)
		return False
	
	# install the preference #
	prop = xsi.ActiveSceneRoot.AddProperty('zNameMap', False)
	xsi.InstallCustomPreferences(prop, 'zNameMap')
	xsi.DeleteObj(prop)
	
	# return the preferences #
	return xsi.Preferences.Categories('zNameMap')
	
def zMapName_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true
	oCmd.SetFlag(constants.siNoLogging, True)

	oArgs = oCmd.Arguments
	oArgs.Add("basename", c.siArgumentInput, 'basename', c.siString)
	oArgs.Add("type", c.siArgumentInput, 'Zero', c.siString)
	oArgs.Add("sym", c.siArgumentInput, 'Middle', c.siString)
	oArgs.Add("itter", c.siArgumentInput, 65535, c.siUInt2)
	oArgs.Add("use_alpha", c.siArgumentInput, False, c.siBool)
	return true

def zMapName_Execute(basename, typ, sym, itter, use_alpha):
	
	# get the preference #
	pref = xsi.Preferences.Categories('zNameMap')
	if not pref:
		pref = xsi.zInstallNameMapPref()
	pref = dispatch(pref)
	
	# get the rule #
	rule = pref.Rule.Value
	rule = rule.replace('$(BASENAME)', basename)
	
	# try to set the type #
	try:
		if typ[:7] == 'Custom:':
			rule = rule.replace('$(TYP)', typ[7:])
		else:
			rule = rule.replace('$(TYP)', pref.Parameters(typ).Value)
	except:
		xsi.logmessage('Unable to get name map for Type: %s' % typ, 
						c.siWarning)
		rule = rule.replace('$(TYP)', 'None')

	# set the symmetry #
	try:
		# handle special no symmetry #
		if sym == 'None':
			rule = rule.replace('_$(SYM)', '')
		else:
			if re.match(r'^Rgt$', sym, re.I) or re.match(r'^R$', sym, re.I) or re.match(r'^Right$', sym, re.I) : sym = 'Right'
			if re.match(r'^Lft$', sym, re.I) or re.match(r'^L$', sym, re.I) or re.match(r'^Left$', sym, re.I) : sym = 'Left'
			if re.match(r'^Mid$', sym, re.I) or re.match(r'^M$', sym, re.I) or re.match(r'^Middle$', sym, re.I) : sym = 'Middle'
			rule = rule.replace('$(SYM)', pref.Parameters(sym).Value)
	except:
		xsi.logmessage('Unable to get name map for Symmetry: %s' % sym, 
						c.siWarning)
						
	# set the itterations #
	try:
		if itter != 65535:
			# map to alpha numerics #
			if pref.ItterType.Value == 'Alpha' or use_alpha:
				alpha = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
				if type(itter) == type(int()):
					itter = alpha[itter % len(alpha)]
			# replace the itter in the rule #
			rule = rule.replace('$(ITTER)', str(itter))
	except:
		xsi.logmessage('Unable to get name map for Itter: %s' % itter, 
						c.siWarning)
		

	# replace the pfx #
	rule = rule.replace('$(PFX)', pref.Prefix.Value)
	
	# remove any leftover $() #
	import sre
	rule = sre.sub('\$(.*[|)])', '', rule)
	
	# capitalize #
	if pref.Capitalize.Value: rule = rule[0].upper() + rule[1:]
	
	return rule
	
def zGetNameMapValue_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true

	oArgs = oCmd.Arguments
	oArgs.Add("mapName",constants.siArgumentInput)
	return true

def zGetNameMapValue_Execute(mapName):
	
	# get the preference #
	pref = xsi.Preferences.Categories('zNameMap')
	if not pref:
		pref = xsi.zInstallNameMapPref()
	
	# return the value #
	try:
		return pref.Parameters(mapName).Value	
	except:
		log('Unable to find NameMap value by name "%s"' % mapName)
		return False
	
