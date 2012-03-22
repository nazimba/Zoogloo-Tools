"""
XSI Class to format a chain based on either the preferences or explictly defined.

>>> fmt = Application.zChainFormatter(chain_root_node)
>>> fmt.BoneDisplay = 6
>>> fmt.BoneSize	= 0.75
>>> fmt.BoneR		= 0
>>> fmt.BoneG		= 1
>>> fmt.BoneB		= 0
>>> fmt.BoneWireR	= 0
>>> fmt.BoneWireG	= 1
>>> fmt.BoneWireB	= 0
>>>
>>> fmt.RootDisplay = 0
>>> fmt.RootSize	= self.parent.scale
>>> fmt.RootR		= 0
>>> fmt.RootG		= 1
>>> fmt.RootB		= 0
>>> fmt.RootWireR	= 0
>>> fmt.RootWireG	= 1
>>> fmt.RootWireB	= 0
>>>
>>> fmt.EffDisplay 	= 0
>>> fmt.EffSize		= self.parent.scale
>>> fmt.EffR		= 0
>>> fmt.EffG		= 1
>>> fmt.EffB		= 0
>>> fmt.EffWireR	= 0
>>> fmt.EffWireG	= 1
>>> fmt.EffWireB	= 0
>>>
>>> fmt.EffLastBone	= True
>>> fmt.Format()

Also includes:
* zChainFormat custom preference
* Applicatin.zFormatChainFromPrefs(chain_root) command

Created by andy on _date_.
Copyright (c) 2007 Zoogloo LLC. All rights reserved.
"""

__version__ = '$Revision: 185 $'
__author__  = '$Author: andy $'
__date__    = '$Date: 2009-02-06 21:04 -0800 $'

import win32com.client
from win32com.client import constants
from win32com.client import constants as c
from win32com.client.dynamic import Dispatch as dispatch
xsi = Application
log = xsi.logmessage

null = None
false = 0
true = 1

class ChainException(Exception): pass

def XSILoadPlugin(in_reg):
	in_reg.Author = 'Andy Buecker'
	in_reg.Name = "zChainFormatter"
	in_reg.Email = ""
	in_reg.URL = ""
	try:
		in_reg.Major = int(__version__.split(' ')[1])
	except:
		in_reg.Major = 1
	in_reg.Minor = 0

	in_reg.RegisterProperty("zChainFormat") 
	
	in_reg.RegisterCommand('zFormatChain', 'zFormatChain')
	in_reg.RegisterCommand('zChainFormatter', 'zChainFormatter')
	in_reg.RegisterCommand('zFormatChainFromPrefs', 'zFormatChainFromPrefs')
	in_reg.RegisterCommand('zInstallFormatChainPref', 'zInstallFormatChainPref')
	
	#RegistrationInsertionPoint - do not remove this line

	return True

def XSIUnloadPlugin(in_reg):
	strPluginName = in_reg.Name
	Application.LogMessage(str(strPluginName) + str(" has been unloaded."))
	return true


def zChainFormat_Define(ctxt):

	prop = ctxt.Source

	# chain display #
	prop.AddParameter3('RootDisplay', c.siInt4, 0, None, None, False)
	prop.AddParameter3('RootR', c.siDouble, 0, 0, 1, False)
	prop.AddParameter3('RootG', c.siDouble, 1, 0, 1, False)
	prop.AddParameter3('RootB', c.siDouble, 1, 0, 1, False)
	prop.AddParameter3('RootWireR', c.siDouble, 0.01, 0, 1, False)
	prop.AddParameter3('RootWireG', c.siDouble, 0.01, 0, 1, False)
	prop.AddParameter3('RootWireB', c.siDouble, 0.01, 0, 1, False)
	prop.AddParameter3('RootSize', c.siDouble, 1, 0, 1000, False)

	prop.AddParameter3('BoneDisplay', c.siInt4, 7, None, None, False)
	prop.AddParameter3('BoneR', c.siDouble, 0.576, 0, 1, False)
	prop.AddParameter3('BoneG', c.siDouble, 0.859, 0, 1, False)
	prop.AddParameter3('BoneB', c.siDouble, 0.11, 0, 1, False)
	prop.AddParameter3('BoneWireR', c.siDouble, 0, 0, 1, False)
	prop.AddParameter3('BoneWireG', c.siDouble, 1, 0, 1, False)
	prop.AddParameter3('BoneWireB', c.siDouble, 1, 0, 1, False)
	prop.AddParameter3('BoneSize', c.siDouble, 1, 0, 1000, False)

	prop.AddParameter3('EffDisplay', c.siInt4, 0, None, None, False)
	prop.AddParameter3('EffR', c.siDouble, 0, 0, 1, False)
	prop.AddParameter3('EffG', c.siDouble, 0, 0, 1, False)
	prop.AddParameter3('EffB', c.siDouble, 1, 0, 1, False)
	prop.AddParameter3('EffWireR', c.siDouble, 1, 0, 1, False)
	prop.AddParameter3('EffWireG', c.siDouble, 0, 0, 1, False)
	prop.AddParameter3('EffWireB', c.siDouble, 0, 0, 1, False)
	prop.AddParameter3('EffSize', c.siDouble, 1, 0, 1000, False)
	prop.AddParameter3('EffLastBone', c.siBool, True, None, None, False)

	return True

def zChainFormat_DefineLayout(ctxt):

	plo = ctxt.Source
	plo.Clear()
	
	nullDisp =  [ 
		'None', 0,
		'Null', 1, 
		'Rings', 2,
		'Arrow Rings', 3,
		'Box', 4,
		'Circle', 5,
		'Square', 6,
		'Diamond', 7,
		'Pyramid', 8,
		'Pointed Box', 9,
		'Arrow', 10 
	]
	boneDisp = [ 
		'None', 0,
		'Standard', 1, 
		'SI|3D Style', 2,
		'Pyramid', 3,
		'Wedge', 4,
		'Wedge II', 5,
		'Box', 6,
		'Line', 7,
		'Cylinder', 8,
		'Cone', 9,
		'Rings', 10,
		'Circle', 11,
		'Square', 12 
	]

	plo.AddTab('Chain Display Format')
	plo.AddGroup('Root')
	plo.AddEnumControl('RootDisplay', nullDisp, 'Display', c.siControlCombo)
	plo.AddColor('RootR', 'Color', False)
	plo.AddItem('RootSize', 'Size')
	plo.EndGroup()
	
	plo.AddGroup('Bone')
	plo.AddEnumControl('BoneDisplay', boneDisp, 'Display', c.siControlCombo)
	plo.AddColor('BoneR', 'Color', False)
	plo.AddItem('BoneSize', 'Size')
	plo.EndGroup()
	
	plo.AddGroup('Effector')
	plo.AddEnumControl('EffDisplay', nullDisp, 'Display', c.siControlCombo)
	plo.AddColor('EffR', 'Color', False)
	plo.AddItem('EffSize', 'Size')
	plo.AddItem('EffLastBone', 'Put Under Last Bone')
	plo.EndGroup()
	
	plo.AddTab('Wireframe Format')
	plo.AddGroup('Root')
	plo.AddColor('RootWireR', 'Color', False)
	plo.EndGroup()
	
	plo.AddGroup('Bone')
	plo.AddColor('BoneWireR', 'Color', False)
	plo.EndGroup()
	
	plo.AddGroup('Effector')
	plo.AddColor('EffWireR', 'Color', False)
	plo.EndGroup()

def zFormatChain_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true

	oArgs = oCmd.Arguments
	oArgs.AddWithHandler('chain', c.siArgHandlerSingleObj)
	oArgs.Add('boneDisplay', c.siArgumentInput, 7, c.siByte)
	oArgs.Add('boneColor', c.siArgumentInput, [ 0.576, 0.859, 0.11 ])
	oArgs.Add('boneSize', c.siArgumentInput, 1.0, c.siFloat)
	
	oArgs.Add('rootDisplay', c.siArgumentInput, 0, c.siByte)
	oArgs.Add('rootColor', c.siArgumentInput, [ 0, 0, 1 ])
	oArgs.Add('rootSize', c.siArgumentInput, 1.0, c.siFloat)
	
	oArgs.Add('effDisplay', c.siArgumentInput, 0, c.siByte)
	oArgs.Add('effColor', c.siArgumentInput, [ 0, 1, 1 ])
	oArgs.Add('effSize', c.siArgumentInput, 1.0, c.siFloat)
	oArgs.Add('effLastBone', c.siArgumentInput, True, c.siBool)

	oArgs.Add('boneWireColor', c.siArgumentInput, [ 0, 1, 1 ])
	oArgs.Add('rootWireColor', c.siArgumentInput, [ 0.01, 0.01, 0.01 ])
	oArgs.Add('effWireColor', c.siArgumentInput, [ 1, 0, 0 ])
	
	return True

def zFormatChain_Execute(chain, 
						   boneDisplay, 
						   boneColor, 
						   boneSize, 
						   rootDisplay, 
						   rootColor, 
						   rootSize,
						   effDisplay, 
						   effColor,
						   effSize,
						   effLastBone,
						   boneWireColor,
						   rootWireColor,
						   effWireColor
						   ):

	# make sure we have a chain #
	if not chain or chain.type != 'root':
		xsi.logmessage('No chain root given as Arg1.', c.siError)
		return False
	
	
	# change the root display #
	chain = dispatch(chain)
	chain.primary_icon.Value = 0
	chain.shadow_icon.Value = rootDisplay
	chain.shadow_colour_custom.Value = 1
	
	# hide if we are setting the display to none #
	if rootDisplay == 0:
		chain.Properties('Visibility').Parameters('viewvis').Value = False
		chain.Properties('Visibility').Parameters('rendvis').Value = False

	# set the root color #
	chain.R.Value = rootColor[0]
	chain.G.Value = rootColor[1]
	chain.B.Value = rootColor[2]
	
	# set the wirecolor #
	prop = chain.AddProperty('Display Property', False, 'Display')
	prop = dispatch(prop)
	prop.wirecolorr.Value = rootWireColor[0]
	prop.wirecolorg.Value = rootWireColor[1]
	prop.wirecolorb.Value = rootWireColor[2]
	
	# set the root size #
	chain.size.Value = rootSize

	# format the bone #
	for bone in chain.bones:
		
		bone = dispatch(bone)
		
		# change the display #
		bone.primary_icon.Value = 0
		bone.shadow_icon.Value = boneDisplay
		bone.shadow_colour_custom.Value = 1
		
		# set the color #
		# log('Bone Color: %s %s %s' % (boneColor[0], boneColor[1], boneColor[2]))
		bone.R.Value = boneColor[0]
		bone.G.Value = boneColor[1]
		bone.B.Value = boneColor[2]

		# set the wirecolor #
		prop = bone.AddProperty('Display Property', False, 'Display')
		prop = dispatch(prop)
		prop.wirecolorr.Value = boneWireColor[0]
		prop.wirecolorg.Value = boneWireColor[1]
		prop.wirecolorb.Value = boneWireColor[2]

		# set the bone size #
		bone.size.Value = boneSize

		# hide if we are setting the display to none #
		if boneDisplay == 0:
			bone.Properties('Visibility').Parameters('viewvis').Value = False
			bone.Properties('Visibility').Parameters('rendvis').Value = False

	# change the effector #
	chain.effector.primary_icon.Value = 0
	chain.effector.shadow_icon.Value = effDisplay
	chain.effector.shadow_colour_custom.Value = 1
	
	# hide if we are setting the display to none #
	if effDisplay == 0:
		chain.effector.Properties('Visibility').Parameters('viewvis').Value = False
		chain.effector.Properties('Visibility').Parameters('rendvis').Value = False
	
	# put the effector under the last bone #
	if effLastBone:
		chain.bones(chain.bones.Count-1).AddChild(chain.effector)
	else:
		chain.AddChild(chain.Effector)

	# set the root color #
	chain.effector.R.Value = effColor[0]
	chain.effector.G.Value = effColor[1]
	chain.effector.B.Value = effColor[2]

	# set the wirecolor #
	prop = chain.effector.AddProperty('Display Property', False, 'Display')
	prop = dispatch(prop)
	prop.wirecolorr.Value = effWireColor[0]
	prop.wirecolorg.Value = effWireColor[1]
	prop.wirecolorb.Value = effWireColor[2]

	# set the bone size #
	chain.effector.size.Value = effSize
	
	return True


		
def zFormatChainFromPrefs_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = false

	oArgs = oCmd.Arguments
	oArgs.AddWithHandler('chain', c.siArgHandlerSingleObj)

def zFormatChainFromPrefs_Execute(chain):

	if not chain or chain.type != 'root':
		raise ChainException, 'Incorrect Chain Argument: %s' % chain
		
	# get the prefs #
	pref = xsi.Preferences.Categories('zChainFormat')
	if not pref:
		pref = xsi.zInstallFormatChainPref()

	# format the chain #
	xsi.zFormatChain(chain,
					   pref.BoneDisplay.Value,
					   [ pref.BoneR.Value,
					     pref.BoneG.Value,
					     pref.BoneB.Value ],
					   pref.BoneSize.Value,

					   pref.RootDisplay.Value,
					   [ pref.RootR.Value,
					     pref.RootG.Value,
					     pref.RootB.Value ],
					   pref.RootSize.Value,

					   pref.EffDisplay.Value,
					   [ pref.EffR.Value,
					     pref.EffG.Value,
					     pref.EffB.Value ],
					   pref.EffSize.Value,
					   pref.EffLastBone.Value,
					
					  [ pref.BoneWireR.Value,
					    pref.BoneWireG.Value,
					    pref.BoneWireB.Value ],
					  [ pref.RootWireR.Value,
					    pref.RootWireG.Value,
					    pref.RootWireB.Value ],
					  [ pref.EffWireR.Value,
					    pref.EffWireG.Value,
					    pref.EffWireB.Value ]
	)

	return True
	
def zInstallFormatChainPref_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true

	return true

def zInstallFormatChainPref_Execute():

	pref = xsi.Preferences.Categories('zChainFormat')
	if pref:
		log('zChainFormat Pref all ready exists.', c.siError)
		return False
	
	# install the preference #
	prop = xsi.ActiveSceneRoot.AddProperty('zChainFormat', False)
	xsi.InstallCustomPreferences(prop, 'zChainFormat')
	xsi.DeleteObj(prop)
	
	# return the preferences #
	return xsi.Preferences.Categories('zChainFormat')
	
	

class zChainFormatter(object):
	'''
	Format a chain
	'''
	
	# required for COM wrapper #
	_public_methods_ = ['Format', 'SetRootColor', 'SetBoneColor', 'SetEffColor']
	
	# define the output vars here #
	_public_attrs_ = [
		'BoneDisplay', 'BoneShadow', 'BonePrimary', 'BoneR', 'BoneG', 'BoneB', 'BoneSize',    	
		'RootDisplay', 'RootShadow', 'RootPrimary', 'RootR', 'RootG', 'RootB', 'RootSize',    	
		'EffDisplay', 'EffShadow', 'EffPrimary', 'EffR', 'EffG', 'EffB', 'EffSize',     	
		'EffLastBone', 	
		'BoneWireR', 'BoneWireG', 'BoneWireB',   	
		'RootWireR', 'RootWireG', 'RootWireB',   	
		'EffWireR', 'EffWireG', 'EffWireB',    	
		'chainRoot'		
	]
	# define those attrs that are read only #
	_readonly_attrs_ = []
	
	BoneDisplay = 0
	BoneShadow	= 0
	BonePrimary	= 0
	BoneR       = 0.0
	BoneG       = 0.0
	BoneB       = 0.0
	BoneSize    = 1

	RootDisplay = 0
	RootShadow 	= 0
	RootPrimary	= 0
	RootR       = 0.0
	RootG       = 0.0
	RootB       = 0.0
	RootSize    = 1

	EffDisplay  = 0
	EffShadow  	= 0
	EffPrimary 	= 0
	EffR        = 0.0
	EffG        = 0.0
	EffB        = 0.0
	EffSize     = 1

	EffLastBone = True

	BoneWireR   = 0.0
	BoneWireG   = 0.0
	BoneWireB   = 0.0

	RootWireR   = 0.0
	RootWireG   = 0.0
	RootWireB   = 0.0

	EffWireR    = 0.0
	EffWireG    = 0.0
	EffWireB    = 0.0
	
	chainRoot	= None

	def __init__(self, chainRoot):
		# get the prefs #
		pref = xsi.Preferences.Categories('zChainFormat')
		if not pref:
			pref = xsi.zInstallFormatChainPref()
		
		# store the chain root #	
		self.chainRoot = chainRoot

		# set the class vars from the prefs #
		self.BoneDisplay = pref.BoneDisplay.Value
		self.BoneR       = pref.BoneR.Value   
		self.BoneG       = pref.BoneG.Value       
		self.BoneB       = pref.BoneB.Value       
		self.BoneSize    = pref.BoneSize.Value    
	
		self.RootDisplay = pref.RootDisplay.Value 
		self.RootR       = pref.RootR.Value       
		self.RootG       = pref.RootG.Value       
		self.RootB       = pref.RootB.Value       
		self.RootSize    = pref.RootSize.Value    
	
		self.EffDisplay  = pref.EffDisplay.Value  
		self.EffR        = pref.EffR.Value        
		self.EffG        = pref.EffG.Value        
		self.EffB        = pref.EffB.Value        
		self.EffSize     = pref.EffSize.Value     
	
		self.EffLastBone = pref.EffLastBone.Value 
	
		self.BoneWireR   = pref.BoneWireR.Value   
		self.BoneWireG   = pref.BoneWireG.Value   
		self.BoneWireB   = pref.BoneWireB.Value   
	
		self.RootWireR   = pref.RootWireR.Value   
		self.RootWireG   = pref.RootWireG.Value   
		self.RootWireB   = pref.RootWireB.Value   
	
		self.EffWireR    = pref.EffWireR.Value    
		self.EffWireG    = pref.EffWireG.Value    
		self.EffWireB    = pref.EffWireB.Value    
	
	def Format(self):
		# format the chain #
		xsi.zFormatChain(self.chainRoot,
			self.BoneDisplay,
			[ self.BoneR, self.BoneG, self.BoneB ],
			self.BoneSize,
			
			self.RootDisplay,
			[ self.RootR, self.RootG, self.RootB ],
			self.RootSize,
			
			self.EffDisplay,
			[ self.EffR, self.EffG, self.EffB ],
			self.EffSize,
			
			self.EffLastBone,
			
			[ self.BoneWireR, self.BoneWireG, self.BoneWireB ],
			[ self.RootWireR, self.RootWireG, self.RootWireB ],
			[ self.EffWireR, self.EffWireG, self.EffWireB ]
		)
		
		# align the chain roots #
		trans = self.chainRoot.Bones(0).Kinematics.Global.Transform
		self.chainRoot.Kinematics.Global.Transform = trans
		self.chainRoot.Bones(0).Kinematics.Global.Transform = trans
		
		# set root primary_icon #
		if self.RootPrimary:
			self.chainRoot.primary_icon.Value = self.RootPrimary
		# bone primary_icon #
		if self.BonePrimary:
			for bone in self.chainRoot.Bones:
				bone = dispatch(bone)
				bone.primary_icon.Value = self.BonePrimary
		# effector primary_icon #		
		if self.EffPrimary:
			self.chainRoot.Effector.primary_icon.Value = self.EffPrimary

		# set root shadow #
		if self.RootShadow:
			self.chainRoot.shadow_icon.Value = self.RootShadow
		# bone shadow #
		if self.BoneShadow:
			for bone in self.chainRoot.Bones:
				bone = dispatch(bone)
				bone.shadow_icon.Value = self.BoneShadow
		# effector shadow #		
		if self.EffShadow:
			self.chainRoot.Effector.shadow_icon.Value = self.EffShadow

	def SetRootColor(self, r, g, b, both=False, wireOnly=False):
		if not wireOnly or both:
			self.RootR = r
			self.RootG = g
			self.RootB = b
		
		if both or wireOnly:
			self.RootWireR = r
			self.RootWireG = g
			self.RootWireB = b
	
	def SetBoneColor(self, r, g, b, both=False, wireOnly=False):
		if not wireOnly or both:
			self.BoneR = r
			self.BoneG = g
			self.BoneB = b
		
		if both or wireOnly:
			self.BoneWireR = r
			self.BoneWireG = g
			self.BoneWireB = b
			
	def SetEffColor(self, r, g, b, both=False, wireOnly=False):
		if not wireOnly or both:
			self.EffR = r
			self.EffG = g
			self.EffB = b
		
		if both or wireOnly:
			self.EffWireR = r
			self.EffWireG = g
			self.EffWireB = b
			
			
def zChainFormatter_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true
	
	oArgs = oCmd.Arguments
	oArgs.AddWithHandler('chain', c.siArgHandlerSingleObj)

	return true

def zChainFormatter_Execute(chain):
	
	# create the object #
	fmt = zChainFormatter(chain)
	
	# export the python object #
	import win32com.server
	return win32com.server.util.wrap(fmt)