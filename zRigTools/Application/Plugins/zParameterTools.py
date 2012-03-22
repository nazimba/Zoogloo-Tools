"""
zParameterTools.py

Copyright (c) 2008 Zoogloo LLC. All rights reserved.
This plugin is provided AS IS and WITHOUT WARRANTY
"""

__version__ = '$Revision: 198 $'
__author__  = '$Author: andy $'
__date__    = '$Date: 2009-03-06 10:14 -0800 $'

import win32com.client
from win32com.client import constants
from win32com.client import constants as c
from win32com.client.dynamic import Dispatch as dispatch
import time
import locale
locale.setlocale(locale.LC_ALL, '')

xsi = Application
log = xsi.logmessage

null = None
false = 0
true = 1

def XSILoadPlugin(in_reg):
	in_reg.Author = "Andy Buecker"
	in_reg.Name = "zParameterTools"
	in_reg.Email = "andy@zoogloo.net"
	in_reg.URL = ""
	try:
		in_reg.Major = int(__version__.split(' ')[1])
	except:
		in_reg.Major = 1
	in_reg.Minor = 0

	in_reg.RegisterCommand('zLockAndHideParameters', 'zLockAndHideParameters')
	in_reg.RegisterCommand('zUnlockAndUnhideParameters', 'zUnlockAndUnhideParameters')
	in_reg.RegisterCommand('zUnlockAndUnhideParametersSel', 'zUnlockAndUnhideParametersSel')

	in_reg.RegisterMenu(c.siMenuTbAnimateCreateParameterID, 'zParameterToolsMenu', False)
	
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
	# Application.LogMessage(str(strPluginName) + str(" has been unloaded."))
	return true

#-----------------------------------------------------------------------------
# Menus
#-----------------------------------------------------------------------------
def zParameterToolsMenu_Init(ctxt):
	menu = ctxt.Source

	item = menu.AddCommandItem('zLockAndHideParameters', 'zLockAndHideParameters')
	item.Name = '(z) Lock && Hide Model Parameters'
	item = menu.AddCommandItem('zUnlockAndUnhideParameters', 'zUnlockAndUnhideParameters')
	item.Name = '(z) Unlock && Unhide Model Parameters'
	item = menu.AddCommandItem('zUnlockAndUnhideParametersSel', 'zUnlockAndUnhideParametersSel')
	item.Name = '(z) Unlock && Unhide Selected Parameters'

#-----------------------------------------------------------------------------
# Commands
#-----------------------------------------------------------------------------
def zLockAndHideParameters_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	#oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments
	# oArgs.Add('model', c.siArgumentInput, '', c.siString)
	oArgs.AddObjectArgument('model')
	oArgs.Add('ignoreCharSet', c.siArgumentInput, False, c.siBool)
	oArgs.Add('lockConstraints', c.siArgumentInput, True, c.siBool)
	oArgs.Add('lockHeirarchy', c.siArgumentInput, False, c.siBool)

	return True
	
def zLockAndHideParameters_Execute(model, ignoreCharSet, lockConstraints, lockHeirarchy):
	
	# log the starting time #
	timeStart = time.time()
	
	# if we don't have a model get it from the selection #
	log('Model: %s' % model)
	if not model:
		if xsi.selection.Count and xsi.selection(0).type == '#model':
			model = xsi.selection(0)
		else:
			raise Exception('No model argument given and selected item is not a model.')

	# make sure we have a model #
	if model.type != '#model':
		raise Exception('Model Argument "%s" is not a model.' % model)
	
	# get the character set #
	charSet = model.Properties('CharacterSet')
	if not charSet:
		raise Exception('Unable to locate "CharacterSet" on "%s"' % model)
	charSet = dispatch(charSet)
		
	# step through the set #
	keyParams 	= []
	xsi_params 	= []
	def walkProp(Prop):
		# get the nested properties #
		nested = Prop.NestedObjects
		# skip if there is nothing there #
		if not nested.Count: return
		# step through the nested items #
		for item in nested:
			# catch the properties #
			if item.type == 'customparamset':
				prop = dispatch(item)
				log('Prop: %s' % prop.FullName, c.siVerbose)
				# walk through the prop #
				walkProp(prop)
			else:
				# add to the keyable parameters list #
				keyParams.append(item.MasterParameter.FullName)
				xsi_params.append(item.MasterParameter)
			
	walkProp(charSet)
	log('Params in charSet: %d' % len(keyParams), c.siVerbose)
	
	# setup the progress bar for the keyable params #
	pb = XSIUIToolkit.ProgressBar
	pb.Caption = 'Making all paramters in the character set keyable...'
	pb.Step = 1
	pb.Maximum = len(keyParams)
	if xsi.Interactive: pb.Visible = True

	# make all the params keyable #
	log('Making all parameters keyable.')
	for param in xsi_params:
		pb.Increment()
		param.Keyable = True
		
	# turn off the current progressbar #
	if xsi.Interactive: pb.Visible = False
	
	# lock the hierarchy #
	if lockHeirarchy: model.SetLock(c.siLockLevelConstruction)
	
	# setup the progress bar #
	pb = XSIUIToolkit.ProgressBar
	pb.Caption = 'Calculating the number of parameters...'
	pb.Step = 1
	if xsi.Interactive: pb.Visible = True
		
	# calculate the number if items #
	allNodes = model.FindChildren('*')
	for item in allNodes:
		# step through all the parameters #
		pb.Maximum += item.Parameters.Count
		# lock the constraints parameters #
		if lockConstraints:
			for constraint in item.Kinematics.Constraints:
				pb.Maximum += constraint.Parameters.Count
		# step through all the properties #
		for prop in item.Properties:
			if prop.Name == 'Visibility': continue
			if prop.Type == 'geomapprox': continue
			pb.Maximum += prop.Parameters.Count
	pb.Caption = 'Processing %s parameters on %s nodes' % (
		locale.format('%d', pb.Maximum, True),
		locale.format('%d', allNodes.Count, True)
	)
	
	# custom incrmentor #
	def Increment(pb, step=100):
		pb.Increment()
		if not (pb.Value % step):
			perc = float(pb.Value) / float(pb.Maximum)
			timeNow = time.time() - timeStart
			pb.StatusText = 'Elapsed: %02dm %02d.%02ds' % (int(timeNow/60), timeNow%60, timeNow%1*100)
			# remaining = now * perc remain / current perc #
			timeRemain = timeNow * (1.0-perc)/perc
			pb.StatusText += ' / Remaining: %02dm %02d.%02ds' % (int(timeRemain/60), timeRemain%60, timeRemain%1*100)
		
				

	# step through all items in the character #
	for item in allNodes:
		
		# check for cancel #
		if pb.CancelPressed:
			log('Canceled')
			return False
		
		# step through all the parameters #
		# pb.Maximum += item.Parameters.Count
		for param in item.Parameters:
			if param.type == 'ProxyParameter': continue
			# increment te progressbar #
			Increment(pb)
			# deal only with keyable parameters #
			if not param.Animatable and not param.Keyable: continue
			# skip, if it is in the character set #
			if param.FullName in keyParams: 
				# log('Keyable: %s' % param.FullName, c.siVerbose)
				continue
			# lock the parameter #
			param.SetLock(c.siLockLevelAll)
			# hide and make non keyable #
			param.SetCapabilityFlag(c.siKeyable + c.siNonKeyableVisible, False)
			# set a tag to know we hide the attribute #
			param.Tags = c.siTag9 + c.siTag1 + c.siTag4
			
		# lock the constraints parameters #
		if lockConstraints:
			for constraint in item.Kinematics.Constraints:
				# pb.Maximum += constraint.Parameters.Count
				for param in constraint.Parameters:
					if param.type == 'ProxyParameter': continue
					# increment te progressbar #
					Increment(pb)
					# deal only with keyable parameters #
					if not param.Animatable and not param.Keyable: continue
					# skip, if it is in the character set #
					if param.FullName in keyParams: 
						# log('Keyable: %s' % param.FullName, c.siVerbose)
						continue
					# lock the parameter #
					param.SetLock(c.siLockLevelAll)
					# hide and make non keyable #
					param.SetCapabilityFlag(c.siKeyable + c.siNonKeyableVisible, False)
					# set a tag to know we hide the attribute #
					param.Tags = c.siTag9 + c.siTag1 + c.siTag4
	
		# step through all the properties #
		for prop in item.Properties:
			prop = dispatch(prop)
			if prop.Name == 'Visibility': continue
			if prop.Type == 'geomapprox': continue
			# pb.Maximum += prop.Parameters.Count
			for param in prop.Parameters:
				if param.type == 'ProxyParameter': 
					# log('ProxyParameter: %s' % param.FullName)
					continue
				# increment te progressbar #
				Increment(pb)
				# deal only with keyable parameters #
				if not param.Animatable and not param.Keyable: continue
				# skip, if it is in the character set #
				if param.FullName in keyParams: 
					# log('Keyable: %s' % param.FullName, c.siVerbose)
					continue
				# lock the parameter #
				try:
					param.SetLock(c.siLockLevelAll)
				except:
					log('Unable to set lock on "%s"' % param.FullName, c.siWarning)
				# hide and make non keyable #
				try:
					param.SetCapabilityFlag(c.siKeyable + c.siNonKeyableVisible, False)
				except:
					log('Unable to set non keyable and visible on "%s"' % param.FullName, c.siWarning)
				# set a tag to know we hide the attribute #
				try:
					param.Tags = c.siTag9 + c.siTag1 + c.siTag4
				except:
					log('Unable to set tags on "%s"' % param.FullName, c.siWarning)
					
	# log the end time #
	timeEnd = time.time()
	timeElapsed = timeEnd - timeStart
	log('Total Elapsed time: %02d:%02d.%02d' % (int(timeElapsed/60), timeElapsed%60, timeElapsed%1*100))


def zUnlockAndUnhideParameters_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	#oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments
	oArgs.AddObjectArgument('model')
	oArgs.Add('doAll', c.siArgumentInput, False, c.siBool)

	return True
	
def zUnlockAndUnhideParameters_Execute(model, doAll):

	# log the starting time #
	timeStart = time.time()
	
	# if we don't have a model get it from the selection #
	if not model and xsi.selection.Count and xsi.selection(0).type == '#model':
		model = xsi.selection(0)
	else:
		raise Exception('No model argument given and selected item is not a model.')

	# make sure we have a model #
	if model.type != '#model':
		raise Exception('Model Argument "%s" is not a model.' % model)
	
	# setup the progress bar #
	pb = XSIUIToolkit.ProgressBar
	pb.Caption = 'Calculating the number of parameters...'
	pb.Step = 1
	if xsi.Interactive: pb.Visible = True

	# calculate the number if items #
	allNodes = model.FindChildren('*')
	for item in allNodes:
		# step through all the parameters #
		pb.Maximum += item.Parameters.Count
		# lock the constraints parameters #
		for constraint in item.Kinematics.Constraints:
			pb.Maximum += constraint.Parameters.Count
		# step through all the properties #
		for prop in item.Properties:
			if prop.Name == 'Visibility': continue
			if prop.Type == 'geomapprox': continue
			pb.Maximum += prop.Parameters.Count
	pb.Caption = 'Processing %s parameters on %s nodes' % (
		locale.format('%d', pb.Maximum, True),
		locale.format('%d', allNodes.Count, True)
	)
	
	# custom incrmentor #
	def Increment(pb, step=100):
		pb.Increment()
		if not (pb.Value % step):
			perc = float(pb.Value) / float(pb.Maximum)
			timeNow = time.time() - timeStart
			pb.StatusText = 'Elapsed: %02dm %02d.%02ds' % (int(timeNow/60), timeNow%60, timeNow%1*100)
			# remaining = now * perc remain / current perc #
			timeRemain = timeNow * (1.0-perc)/perc
			pb.StatusText += ' / Remaining: %02dm %02d.%02ds' % (int(timeRemain/60), timeRemain%60, timeRemain%1*100)
		
	# step through all items in the character #
	for item in allNodes:
		
		# check for cancel #
		if pb.CancelPressed:
			log('Canceled')
			return False
		
		# step through all the parameters #
		for param in item.Parameters:
			if param.type == 'ProxyParameter': continue
			# increment te progressbar #
			Increment(pb)
			# deal only with keyable parameters #
			# if not param.Animatable and not param.Keyable: continue
			# did we lock it? #
			if doAll or param.Tags == c.siTag9 + c.siTag1 + c.siTag4:
				# unlock the parameter #
				param.UnSetLock(param.LockLevel)
				# unhide and make keyable #
				param.SetCapabilityFlag(c.siKeyable + c.siNonKeyableVisible, True)
				# clear the tags #
				param.Tags = c.siTagNone
			
		# lock the constraints parameters #
		for constraint in item.Kinematics.Constraints:
			for param in constraint.Parameters:
				if param.type == 'ProxyParameter': continue 
				# increment te progressbar #
				Increment(pb)
				# deal only with keyable parameters #
				# if not param.Animatable and not param.Keyable: continue
				# did we lock it? #
				if doAll or param.Tags == c.siTag9 + c.siTag1 + c.siTag4:
					# unlock the parameter #
					param.UnSetLock(param.LockLevel)
					# unhide and make keyable #
					param.SetCapabilityFlag(c.siKeyable + c.siNonKeyableVisible, True)
					# clear the tags #
					param.Tags = c.siTagNone
	
		# step through all the properties #
		for prop in item.Properties:
			prop = dispatch(prop)
			# skip over visibility #
			if prop.Name == 'Visibility': continue
			if prop.Type == 'geomapprox': continue
			for param in prop.Parameters:
				if param.type == 'ProxyParameter': continue 
				# increment te progressbar #
				Increment(pb)
				# deal only with keyable parameters #
				# if not param.Animatable and not param.Keyable: continue
				# did we lock it? #
				if doAll or param.Tags == c.siTag9 + c.siTag1 + c.siTag4:
					# unlock the parameter #
					param.UnSetLock(param.LockLevel)
					# unhide and make keyable #
					param.SetCapabilityFlag(c.siKeyable + c.siNonKeyableVisible, True)
					# clear the tags #
					param.Tags = c.siTagNone
				
	# log the end time #
	timeEnd = time.time()
	timeElapsed = timeEnd - timeStart
	log('Total Elapsed time: %02d:%02d.%02d' % (int(timeElapsed/60), timeElapsed%60, timeElapsed%1*100))
	
#-----------------------------------------------------------------------------

def zUnlockAndUnhideParametersSel_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	#oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments
	oArgs.AddObjectArgument('model')
	oArgs.Add('doAll', c.siArgumentInput, False, c.siBool)

	return True
	
def zUnlockAndUnhideParametersSel_Execute(model, doAll):

	# log the starting time #
	timeStart = time.time()
	
	# setup the progress bar #
	pb = XSIUIToolkit.ProgressBar
	pb.Caption = 'Calculating the number of parameters...'
	pb.Step = 1
	if xsi.Interactive: pb.Visible = True

	# calculate the number if items #
	allNodes = xsi.selection
	for item in xsi.selection:
		# step through all the parameters #
		pb.Maximum += item.Parameters.Count
		# lock the constraints parameters #
		for constraint in item.Kinematics.Constraints:
			pb.Maximum += constraint.Parameters.Count
		# step through all the properties #
		for prop in item.Properties:
			if prop.Name == 'Visibility': continue
			if prop.Type == 'geomapprox': continue
			pb.Maximum += prop.Parameters.Count
	pb.Caption = 'Processing %s parameters on %s nodes' % (
		locale.format('%d', pb.Maximum, True),
		locale.format('%d', allNodes.Count, True)
	)
	
	# custom incrmentor #
	def Increment(pb, step=100):
		pb.Increment()
		if not (pb.Value % step):
			perc = float(pb.Value) / float(pb.Maximum)
			timeNow = time.time() - timeStart
			pb.StatusText = 'Elapsed: %02dm %02d.%02ds' % (int(timeNow/60), timeNow%60, timeNow%1*100)
			# remaining = now * perc remain / current perc #
			timeRemain = timeNow * (1.0-perc)/perc
			pb.StatusText += ' / Remaining: %02dm %02d.%02ds' % (int(timeRemain/60), timeRemain%60, timeRemain%1*100)
		
	# step through all items in the character #
	for item in allNodes:
		
		# check for cancel #
		if pb.CancelPressed:
			log('Canceled')
			return False
		
		# step through all the parameters #
		for param in item.Parameters:
			if param.type == 'ProxyParameter': continue
			# increment te progressbar #
			Increment(pb)
			# deal only with keyable parameters #
			# if not param.Animatable and not param.Keyable: continue
			# did we lock it? #
			if doAll or param.Tags == c.siTag9 + c.siTag1 + c.siTag4:
				# unlock the parameter #
				param.UnSetLock(param.LockLevel)
				# unhide and make keyable #
				param.SetCapabilityFlag(c.siKeyable + c.siNonKeyableVisible, True)
				# clear the tags #
				param.Tags = c.siTagNone
			
		# lock the constraints parameters #
		for constraint in item.Kinematics.Constraints:
			for param in constraint.Parameters:
				if param.type == 'ProxyParameter': continue 
				# increment te progressbar #
				Increment(pb)
				# deal only with keyable parameters #
				# if not param.Animatable and not param.Keyable: continue
				# did we lock it? #
				if doAll or param.Tags == c.siTag9 + c.siTag1 + c.siTag4:
					# unlock the parameter #
					param.UnSetLock(param.LockLevel)
					# unhide and make keyable #
					param.SetCapabilityFlag(c.siKeyable + c.siNonKeyableVisible, True)
					# clear the tags #
					param.Tags = c.siTagNone
	
		# step through all the properties #
		for prop in item.Properties:
			prop = dispatch(prop)
			# skip over visibility and geom approx #
			if prop.Name == 'Visibility': continue
			if prop.Name == 'Geometry Approximation': continue
			for param in prop.Parameters:
				if param.type == 'ProxyParameter': continue 
				# increment te progressbar #
				Increment(pb)
				# deal only with keyable parameters #
				# if not param.Animatable and not param.Keyable: continue
				# did we lock it? #
				if doAll or param.Tags == c.siTag9 + c.siTag1 + c.siTag4:
					# unlock the parameter #
					param.UnSetLock(param.LockLevel)
					# unhide and make keyable #
					param.SetCapabilityFlag(c.siKeyable + c.siNonKeyableVisible, True)
					# clear the tags #
					param.Tags = c.siTagNone
				
	# log the end time #
	timeEnd = time.time()
	timeElapsed = timeEnd - timeStart
	log('Total Elapsed time: %02d:%02d.%02d' % (int(timeElapsed/60), timeElapsed%60, timeElapsed%1*100))