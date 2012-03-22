"""
XSI Plugin to copy the weights from one deformer to another.

Command is registered under the Animate > Envelope menu.

Created by andy on 2008-06-23.
Copyright (c) 2008 Zoogloo LLC. All rights reserved.
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

def XSILoadPlugin(in_reg):
	in_reg.Author = "Andy Buecker"
	in_reg.Name = "zEnvCopyWeight"
	in_reg.Email = "andy@zoogloo.net"
	in_reg.URL = ""
	try:
		in_reg.Major = int(__version__.split(' ')[1])
	except:
		in_reg.Major = 1
	in_reg.Minor = 0

	in_reg.RegisterCommand('zEnvCopyWeight', 'zEnvCopyWeight')

	in_reg.RegisterMenu(c.siMenuTbAnimateDeformEnvelopeID, 'zEnvCopyWeightMenu', False)
	
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

#-----------------------------------------------------------------------------
# Menus
#-----------------------------------------------------------------------------
def zEnvCopyWeightMenu_Init(ctxt):
	menu = ctxt.Source
	
	item = menu.AddCommandItem('zEnvCopyWeight', 'zEnvCopyWeight')
	item.Name = '(z) Copy Point Weight'

#-----------------------------------------------------------------------------
# Commands
#-----------------------------------------------------------------------------
def zEnvCopyWeight_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	#oCmd.SetFlag(constants.siNoLogging,false)

	#oArgs = oCmd.Arguments
	#oArgs.Add('arg', c.siArgumentInput, '', c.siString)
	#oArgs.AddObjectArgument('model')

	return True
	
def zEnvCopyWeight_Execute():
	
	if xsi.selection(0).Type != 'pntSubComponent':
		log('Please select point(s).', c.siError)
		return False
	
	# pick the source point #
	picker = xsi.PickElement('point', 'Select source point...')
	if not picker[0]:
		log('Cancelled.', c.siWarning)
		return False
	src_point = picker[2]
	src_point = dispatch(src_point)

	# get the source object #
	src_object = src_point.SubComponent.Parent3DObject
	
	# get the source point index #
	src_index = src_point.SubElements2[0]

	# make sure the point is enveloped #
	if not src_object.Envelopes.Count:
		log('No envelope on %s' % src_object, c.siError)
		return False
	
	# get the deformers and weights on the points #
	src_env = src_object.Envelopes(0)
	src_weights = src_env.Weights
	
	# create a dictionary to hold the weights by deformer name #
	src_weight_dict = {}
	# src_total_weight = 0.0
	for d in xrange(len(src_weights[src_index])):
		src_deformer = src_env.Deformers(d)
		weight = src_weights[src_index][d]
		# add the weight if it's greater than 0 #
		if weight > 0.0:
			src_weight_dict[src_deformer.Name] = weight
			# src_total_weight += weight
	# src_weight_dict['total_weights'] = src_total_weight
	log(`src_weight_dict`)
	
	# step through each item in the selection #
	trg_points =  xsi.selection(0)
	
	# get the parent object #
	trg_object = trg_points.SubComponent.Parent3DObject
	
	# get the envelope #
	trg_env = trg_object.Envelopes(0)
	trg_env = dispatch(trg_env)
	
	# get the weight array and convert to a list #
	trg_weights = list(trg_env.Weights.Array)
	for i in xrange(len(trg_weights)):
		trg_weights[i] = list(trg_weights[i])
	
	# find all the deformers #
	trg_deformer_dict = {}
	for d in xrange(trg_env.Deformers.Count):
		trg_deformer = trg_env.Deformers(d)
		trg_deformer_dict[trg_deformer.Name] = {
			'xsi': trg_deformer,
			'id': d
		}
	
	# create an array of booleans to see if we cleared the weights at that index yet #
	# cleared = [False] * len(trg_weights[0])
	
	# step through the point indexes #
	for trg_index in trg_points.SubElements2:
		log(trg_index)
		# zero the weights for the index #
		# new_weights = [0.0] * len(trg_weights[0])
		# log(`new_weights`)
		# step through the src weights #

		# # see if we need to clear the row #
		# if not cleared[trg_index]:
		# step through each deformer and zero the weight for the index #
		for d in xrange(len(trg_weights)):
			trg_weights[d][trg_index] = 0.0
		# flag that we've cleared the index #
		# cleared[trg_index] = True

		for src_dfm_name in src_weight_dict.keys():
			# get the correspoinding target deformer #
			if not src_dfm_name in trg_deformer_dict.keys():
				log('Unable to find deformer "%s" on "%s".' % (src_dfm_name, trg_object), c.siError)
				return False
			trg_dfm = trg_deformer_dict.get(src_dfm_name).get('xsi')
			trg_id  = trg_deformer_dict.get(src_dfm_name).get('id')
			src_weight = src_weight_dict.get(src_dfm_name)
			# set the weights #
			trg_weights[trg_id][trg_index] = src_weight
		
	# reapply the weights #
	log(trg_env)
	trg_env.Weights.Array = trg_weights
	
