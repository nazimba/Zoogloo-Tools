"""
XSI Plugin to convert weighted bones to weighted null.

>>> # requires 4 inputs:
>>> # 1. geometry node
>>> # 2. node to parent the nulls to
>>> # 3. group to add the new nulls to
>>> # 4. boolean wether to use existing nodes, if found
>>> Application.zEnvBonesToNulls(node_geom, node_env_parent, group_deformer, True)
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
	in_reg.Name = "zEnvBonesToNulls"
	in_reg.Email = "andy@zoogloo.net"
	in_reg.URL = ""
	in_reg.Major = 1
	try:
		in_reg.Major = int(__version__.split(' ')[1])
	except:
		in_reg.Major = 1
	in_reg.Minor = 0

	# in_reg.RegisterProperty('zEnvBonesToNulls')

	in_reg.RegisterCommand('zEnvBonesToNulls', 'zEnvBonesToNulls')

	# in_reg.RegisterMenu(c.siMenuTbAnimateActionsStoreID, 'zEnvBonesToNullsMenu', False)
	
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
def zEnvBonesToNullsMenu_Init(ctxt):
	menu = ctxt.Source
	
	item = menu.AddCommandItem('zEnvBonesToNullsGUI', 'zEnvBonesToNullsGUI')
	item.Name = '(z) zEnvBonesToNulls'

#-----------------------------------------------------------------------------
# Properties
#-----------------------------------------------------------------------------
def zEnvBonesToNulls_Define(ctxt):
	prop = ctxt.Source
	
	#prop.AddParameter3("ParamName", c.siString, '')

	
def zEnvBonesToNulls_DefineLayout(ctxt):
	lo = ctxt.Source
	lo.Clear()

	lo.AddItem('ParamName')

#-----------------------------------------------------------------------------
# Commands
#-----------------------------------------------------------------------------
def zEnvBonesToNulls_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	#oCmd.SetFlag(constants.siNoLogging,false)

	oArgs = oCmd.Arguments
	oArgs.AddObjectArgument('geom_node')
	oArgs.AddObjectArgument('env_parent_node')
	oArgs.AddObjectArgument('deformer_group')
	oArgs.Add('use_existing_nodes', c.siArgumentInput, True, c.siBool)

	return True
	
def zEnvBonesToNulls_Execute(
	geom_node, 
	env_parent_node, 
	deformer_group, 
	use_existing_nodes):
	'''
	TODO: 	Could probably speed it up by not applying the weights each time.
			Do it all on one large array.
	'''

	# make sure we have the arguments #
	if not geom_node:
		raise Exception('geom_node argument not defined.')
	if not env_parent_node:
		raise Exception('env_parent_node argument not defined.')
		
	# make sure the env_parent_node is under the same model #
	if geom_node.Model.Name != env_parent_node.Model.Name:
		raise Exception(
			'env_parent_node model "%s" is not the sames as the geom model "%s"' % \
			(geom_node.Model.Name, env_parent_node.Model.Name)
		)
		
	# make sure the deformer_group is a group #
	if deformer_group and deformer_group.Type != '#Group':
		raise Exception('deformer_group is not a Group.')
		
	# step through the geom #
	# for node in model.FindChildren('*', '', [c.siMeshFamily, c.siNurbsSurfaceMeshFamily]):
	log('Processing Geom: %s' % geom_node)
	# Make sure there is an envelope #
	if not geom_node.Envelopes.Count:
		log('No envelope found on: %s' % geom_node, c.siWarning)
		return False
	env = geom_node.Envelopes(0)
	
	# step through the deformers and add the new ones to the envelope #
	name_map_old2new = {}
	name_map_new2old = {}
	deformers = dispatch('XSI.Collection')
	deformers.AddItems(geom_node.Envelopes(0).Deformers)
	for dfm in deformers:
		# skip over non-bones #
		if dfm.type != 'bone': continue

		# build the new name #
		dfm_name, sym, typ = dfm.name.split('_')
		zero_name = xsi.zMapName(dfm_name, 'Zero', sym)
		env_name = xsi.zMapName(dfm_name, 'Env', sym)
		
		# get or create the nodes under the model #
		zero_node 	= geom_node.model.FindChild(zero_name)
		env_node 	= geom_node.model.FindChild(env_name)
		if not use_existing_nodes or not zero_node:
			zero_node = env_parent_node.AddNull(zero_name)
			zero_node.primary_icon.Value = 0
			zero_node.Properties('Visibility').Parameters('viewvis').Value = False
			zero_node.Properties('Visibility').Parameters('rendvis').Value = False
			# constrain it to the bone #
			zero_node.Kinematics.AddConstraint('Pose', dfm, False)
		if not use_existing_nodes or not env_node:
			env_node = xsi.zAddHookNode(zero_node, env_name)
			env_node.primary_icon.Value = 0
			env_node.Properties('Visibility').Parameters('viewvis').Value = False
			env_node.Properties('Visibility').Parameters('rendvis').Value = False
			# add it to the group #
			if deformer_group and deformer_group.type == '#Group':
				deformer_group.AddMember(env_node)
				
		# add the relationships to the name maps #
		name_map_old2new[dfm.FullName] = {'self': dfm, 'target': env_node}
		name_map_new2old[env_node.FullName] = {'self': env_node, 'source': dfm}
				
		# remove the bone from the existing deformer group #
		if deformer_group and deformer_group.IsMember(dfm):
			log('Removing "%s" from Deformer Group' % dfm, c.siVerbose)
			deformer_group.RemoveMember(dfm)
			
		# add the new deformer #
		log('Adding deformer "%s" to envelope.' % env_node, c.siVerbose)
		xsi.ApplyFlexEnv('%s;%s' % (geom_node.FullName, env_node.FullName), False, 2)
		


	# create a dictionary of weights #
	weight_list = list(env.Weights.Array)
	weight_table = {}
	for d in xrange(env.Deformers.Count):
		dfm = geom_node.Envelopes(0).Deformers(d)
		weight_table[dfm.Name] = {
			'id': d,
			'weights': weight_list[d]
		}
	
	# copy the old weights to the new weights #
	for dfm_name in name_map_old2new.keys():
		dfm_node = name_map_old2new.get(dfm_name).get('self')
		env_node = name_map_old2new.get(dfm_name).get('target')
		log('%s -> %s' % (dfm_name, env_node))
		# get the source weights #
		dfm_weights = weight_table.get(dfm_node.Name).get('weights')
		# get the ids #
		source_id = weight_table.get(dfm_node.Name).get('id')
		target_id = weight_table.get(env_node.Name).get('id')
		# set the new weights #
		weight_list[target_id] = weight_list[source_id]
		# reset the old weights #
		weight_list[source_id] = [0.0] * len(weight_list[source_id])
		
	# set the weights #
	env.Weights.Array = weight_list
	
	# remove the old deformers #
	dfm_remove = ''
	for dfm_name in name_map_old2new.keys():
		dfm_node = name_map_old2new.get(dfm_name).get('self')
		dfm_remove += dfm_node.FullName + ','
	# remove the last ',' #
	dfm_remove = dfm_remove[:-1]

	# remove the old deformer #
	log('Removing deformer "%s" from envelope.' % dfm_remove, c.siVerbose)
	xsi.RemoveFlexEnvDeformer('%s;%s' % (geom_node.FullName, dfm_remove), False)

	