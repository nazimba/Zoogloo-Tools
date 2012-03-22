"""
zSkinWeights.py

TODO: Create GUI around commands.
TODO: Added envelope with only found parameters.

Created by Andy Buecker on 2008-04-16.
Copyright (c) 2008 Zoogloo LLC. All rights reserved.
"""

__version__ = '$Revision: 198 $'
__author__  = '$Author: andy $'
__date__    = '$Date: 2009-03-06 10:14 -0800 $'

import win32com.client
from win32com.client import constants
from win32com.client import constants as c
from win32com.client.dynamic import Dispatch as dispatch
import sys
import os
import re
import xml.dom.minidom as dom
import time


# import the skin weights model #
modPath = r'\\.psf\.Home\Documents\work\development\zgTools\zgRiggingTools\xsi_plugin\Application\Plugins'
if not modPath in sys.path: sys.path.append(modPath)
# import zSkinWeightsModel
# reload(zSkinWeightsModel)
# from zSkinWeightsModel import *

xsi = Application
log = xsi.logmessage

null = None
false = 0
true = 1

def XSILoadPlugin(in_reg):
	in_reg.Author = "andy"
	in_reg.Name = "zSkinWeights"
	in_reg.Email = ""
	in_reg.URL = ""
	try:
		in_reg.Major = int(__version__.split(' ')[1])
	except:
		in_reg.Major = 1
	in_reg.Minor = 0

	# in_reg.RegisterProperty("zEnvelope")
	
	# in_reg.RegisterMenu(c.siMenuMainFileSceneID, 'zSaveEnv', False)
	
	in_reg.RegisterCommand("zSaveEnv","zSaveEnv")
	in_reg.RegisterCommand("zSaveEnvXML","zSaveEnvXML")
	
	in_reg.RegisterCommand("zLoadEnv","zLoadEnv")
	in_reg.RegisterCommand("zLoadEnvXML","zLoadEnvXML")
	
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
	
def clearElixirModules(echo=False):
	import sys
	import re
	for key in sys.modules.keys():
		if re.match('elixir', key) or \
		re.match('sqlalchemy', key) or \
		re.match('pysqlite', key) or \
		re.match('zSkinWeightsModel', key):
			if echo: 
				log('Found: %s %s' % (key, sys.modules[key]))
			del(sys.modules[key])

def zSaveEnv_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true

	oArgs = oCmd.Arguments
	oArgs.Add("filename",c.siArgumentInput, '', c.siString)
	oArgs.AddWithHandler("object", c.siArgHandlerCollection)
	oArgs.Add("overwrite",c.siArgumentInput, True, c.siBool)
	return true

def zSaveEnv_Execute(filename, objects, overwrite):

	# clear any existing modules #
	clearElixirModules(echo=False)

	import zSkinWeightsModel as model 
	
	# get a temporary file #
	import tempfile
	tempname = tempfile.mktemp('.skin')

	# import the model #
	import zSkinWeightsModel as model
	
	# format the filename for any backslashes #
	sqliteName = re.subn(r'\\', '/', tempname)[0]
	
	# create a new skin object #
	model.metadata.bind = "sqlite:///%s" % sqliteName
	model.setup_all()
	model.create_all()
	skin = model.Skin('zSaveEnv')
	
	# create a deformer dictionary #
	defDict = {}
		
	# step through each item #
	for item in objects:
		
		# initialize a progress bar #
		pb = XSIUIToolkit.ProgressBar
		pb.Maximum = item.Envelopes(0).Deformers.Count
		pb.Step = 1
		pb.Caption = 'Envelope: %s' % item.name
		if xsi.Interactive: pb.Visible = True
		
		# create a point list #
		pntList = []
		
		# step through each envelope on each object #
		for env in item.Envelopes:	
			
			# add the geometry #
			geom = skin.AddGeometry(item.Name)
			
			# add all the points to the list #
			for p in xrange(item.ActivePrimitive.Geometry.Points.Count):
				# create a new point object #
				pnt = geom.AddPoint(p)
				# add it to the point list #
				pntList.append(pnt)
			
			# step through each deformer #
			for dfm in env.Deformers:

				# skip over effectors #
				if dfm.type == 'eff': continue
	
				# add the deformer to the dictionary #
				deformer = None
				if not dfm.Name in defDict.keys():
					# add the deformer to the database #
					deformer = geom.AddDeformer(dfm.Name)
					# get the deformer color #
					color = env.GetDeformerColor(dfm)
					deformer.red   = color.Red
					deformer.green = color.Green
					deformer.blue  = color.Blue
					# store the def in the dictionary #
					defDict[dfm.Name] = deformer
				
				# if the deformer isn't defined get it from the dictionary #
				if not deformer:
					deformer = defDict[dfm.Name]
					
					# add the deformer to the geometry #
					geom.deformers.append(deformer)
					
				# get the weights of the deformer #
				weights = env.GetDeformerWeights(dfm)
				for w in xrange(len(weights)):
					# add the weight to the point #
					pntList[w].AddWeight(deformer, weights[w])

				
	# close and clean the session #
	model.session.flush()
	model.session.close()
	
	# clear any existing elixir modes #
	clearElixirModules(echo=False)
	
	# if we are overwriting the file, delete it #
	if os.path.exists(filename):
		if overwrite: os.unlink(filename)
	
	# move the tempfile into place #
	# TODO: figure out why the file remains locked after writing to it #
	import shutil
	shutil.copy(tempname, filename)

def zLoadEnv_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true

	oArgs = oCmd.Arguments
	oArgs.Add("filename",c.siArgumentInput, '', c.siString)
	oArgs.AddObjectArgument("XSImodel")
	# oArgs.Add("overwrite",c.siArgumentInput, True, c.siBool)
	return true

def zLoadEnv_Execute(filename, XSImodel):

	# if we don't have a model use the scene root #
	if not XSImodel:
		XSImodel = xsi.ActiveSceneRoot
		
	# make sure we have a model #
	if XSImodel.Type != '#model':
		log('Model argument is not of type "model".', c.siError)
		return False

	# make sure the file exists #
	if not os.path.exists(filename):
		log('File doesn\'t exist: %s' % filename, c.siError)
		return False

	# clear any existing modules #
	clearElixirModules(echo=False)
	
	# import the model #
	import zSkinWeightsModel as model
	
	# connect to the database #
	sqliteName = re.subn(r'\\', '/', filename)[0]
	
	# create a new skin object #
	model.metadata.bind = "sqlite:///%s" % sqliteName
	model.setup_all()
	
	# get the skin #
	skins = model.Skin.query.all()
	for skin in skins:
		log(str(skin))
		# get the geometry #
		for geo in skin.geometry:
			log(str(geo))
			
			# find the geometry #
			obj = XSImodel.FindChild(geo.name)
			if not obj:
				log('Unable to find object: %s. Skipping' % geo.name, c.siWarning)
				continue
			
			# make sure the point counts match #
			objPointCount = obj.ActivePrimitive.Geometry.Points.Count
			if len(geo.points) != objPointCount:
				log('Point count doesn\'t match. %s != %s(%d))' % (geo, obj.FullName, objPointCount))
				
			# create a collection of deformers #
			dfmCol = dispatch('XSI.Collection')
			for dfm in geo.deformers:
				log(str(dfm))
				# find the deformer #
				xsiDfm = XSImodel.FindChild(dfm.name)
				if not xsiDfm:
					log('Unable to find deformer: %s. Skipping' % dfm, c.siWarning)
					break
				# add it to the dfm collection #
				dfmCol.Add(xsiDfm)
		
			# skip if we don't have all the deformers #
			if not dfmCol.Count != geo.deformers:
				log('Unable to find all the deformers for %s. Skipping envelope.' % geo, c.siWarning)
				continue
				
			# apply the envelope #
			log(dfmCol.GetAsText())
			env = obj.ApplyEnvelope(dfmCol, c.siNode, c.siNode)
			
			# create an array to hold the weights #
			weights = list(env.Weights.Array)
			for i in xrange(len(weights)):
				weights[i] = list(weights[i])
				
			# set the deformer color #
			color = env.GetDeformerColor(dfmCol(0))
			# step through the deformers again and set colors #
			for d in xrange(env.Deformers.Count):
				# get the deformer #
				dfm = env.Deformers(d)
				# skip over effs #
				if dfm.Type == 'eff': continue
				# get the deformer in the database #
				dbDfm = model.Deformer.get_by(name=dfm.Name)
				# build the color #
				color.Red 	= dbDfm.red
				color.Green = dbDfm.green
				color.Blue 	= dbDfm.blue
				# set the color #
				env.SetDeformerColor(dfm, color)
				# set the weights for the deformer for this geom #
				dbWeights = model.Weight.query.filter_by(deformer=dbDfm).filter_by(geometry=geo).all()
				# step through the weights and set the weight array #
				for wgt in dbWeights:
					weights[d][wgt.point.index] = wgt.value
			
			# set the weights #
			env.Weights.Array = weights
	
# xsi = Application
# xsi.UpdatePlugins()
# xsi.zSaveEnv(xsi.selection, 'c:/test5.skin')	


def zSaveEnvXML_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true

	oArgs = oCmd.Arguments
	oArgs.Add("filename",c.siArgumentInput, '', c.siString)
	oArgs.AddWithHandler("object", c.siArgHandlerCollection)
	oArgs.Add("overwrite",c.siArgumentInput, True, c.siBool)
	oArgs.Add("sparse",c.siArgumentInput, True, c.siBool)
	return true

def zSaveEnvXML_Execute(filename, objects, overwrite, sparse):

	# get the start time #
	tStart = time.time()

	# initialize a progress bar #
	pb = XSIUIToolkit.ProgressBar
	pb.Caption = 'Calculating total items...'
	pb.Step = 1
	if xsi.Interactive: pb.Visible = True

	# create an xml doc #
	impl = dom.getDOMImplementation()
	docType = impl.createDocumentType('zSkin', '-//Zoogloo LLC//zSkin//EN' , 'http://portal.zoogloo.net/dtds/zSkin.dtd')
	doc = impl.createDocument(None, "zSkin", None)
	top = doc.documentElement
	# set the date #
	top.setAttribute('date', time.asctime())
	# set the version from the plugin #
	plugin = xsi.Plugins('zSkinWeights')
	top.setAttribute('version', '%d.%d' % (plugin.Major, plugin.Minor))
	# set the username #
	if os.name == 'nt':
		import win32api
		user=win32api.GetUserName()
	if os.name == 'posix':
		user = os.environ['USER']
	top.setAttribute('author', user)
	
	# calculate the maximum itterations #
	runningCount = 0
	for item in objects:
		for env in item.Envelopes:
			weights = env.Weights.Array
			runningCount += len(weights)*len(weights[0])
			

	# update progress bar #
	pb.Maximum = runningCount
	import locale
	locale.setlocale(locale.LC_ALL, '')
	pb.StatusText = 'Processing: %s weights' % locale.format('%d', runningCount, True)
	
	# step through each item #
	for item in objects:

		# step through each envelope on each object #
		for env in item.Envelopes:	
			
			# set the progressbar caption #
			pb.Caption = 'Geometry: %s' % item.name
			
			# add the geometry #
			geom = doc.createElement('geometry')
			top.appendChild(geom)
			geom.setAttribute('name', item.Name)
			geom.setAttribute('points', str(item.ActivePrimitive.Geometry.Points.Count))
			# get the uid #
			zid = xsi.zGetId(item)
			if not zid:
				zid = xsi.zAddIdToNode(item)
			geom.setAttribute('id', zid)
			if item.type == 'polymsh':
				geom.setAttribute('type', 'Mesh')
			elif item.type == 'surfmsh':
				geom.setAttribute('type', 'Nurbs')

			# create a deformers group #
			dfmrs = doc.createElement('deformers')
			geom.appendChild(dfmrs)
			dfmrs.setAttribute('count', str(env.Deformers.Count))
			
			# create a list of deformers so we don't have to get it through xsi for each point #
			dfmList = [None]*env.Deformers.Count
			
			# get the env weights #
			weights = env.Weights.Array
	
			# step through each deformer #
			for d in xrange(env.Deformers.Count):
				
				# get the deformer #
				dfm = env.Deformers(d)

				# add the deformer to the dictionary #
				xdef = doc.createElement('deformer')
				dfmrs.appendChild(xdef)
				xdef.setAttribute('name', dfm.Name)
				xdef.setAttribute('id', str(xsi.zGetId(dfm)))
				
				# get the deformer color #
				color = env.GetDeformerColor(dfm)
				xdef.setAttribute('red', 	str(color.Red))
				xdef.setAttribute('green', 	str(color.Green))
				xdef.setAttribute('blue', 	str(color.Blue))
				
				# cache the deformer in the list #
				dfmList[d] = dfm
				
				# create a weights element #
				xwgts = doc.createElement('weights')
				xdef.appendChild(xwgts)
				
				# step through the points #
				for p in xrange(len(weights[d])):
					# catch cancel #
					if pb.CancelPressed: return False
					# get the value #
					value = weights[d][p]
					# increment the pb #
					pb.Increment()
					# if sparse, skip over point #
					if value == 0.0: continue
					# create a weight element #
					xwgt = doc.createElement('weight')
					xwgts.appendChild(xwgt)
					xwgt.setAttribute('point', str(p))
					xwgt.setAttribute('value', str(value))
					
			# store an zSkinWeights property on the object #
			prop = item.Properties('zSkinWeights')
			if not prop:
				prop = item.AddProperty('CustomProperty', False, 'zSkinWeights')
				prop.AddParameter3('FileName', c.siString)
			prop = dispatch(prop)
			locked = None
			if prop.FileName.IsLocked():
				locked = prop.FileName.LockLevel
				prop.FileName.UnSetLock(c.siLockLevelAll)
			prop.FileName.Value = filename
			if locked:
				prop.FileName.SetLock(locked)
			
					
	# calculate the time to parse the scene #
	tParse = time.time() - tStart
	log('Time to parse scene: %02d:%02d.%02d' % (int(tParse/60), tParse%60, tParse%1*100))
	
	# write it to disk #
	tStartWrite = time.time()
	fh = open(filename, 'w')
	fh.write('<?xml version="1.0" encoding="utf-8"?>\n')
	docType.writexml(fh, indent='', addindent='\t', newl='\n')
	top.writexml(fh, indent='', addindent='\t', newl='\n')
	fh.close()

	# calculate the time to write the file #
	tWrite = time.time() - tStartWrite
	log('Time to write to xml: %02d:%02d.%02d' % (int(tWrite/60), tWrite%60, tWrite%1*100))
	
	# calculate the total elapsed time #
	tDelta = time.time() - tStart
	log('Total Elapsed Time: %02d:%02d.%02d' % (int(tDelta/60), tDelta%60, tDelta%1*100))
	
	
def zLoadEnvXML_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true

	oArgs = oCmd.Arguments
	oArgs.Add("filename",c.siArgumentInput, '', c.siString)
	oArgs.AddObjectArgument("XSImodel")
	oArgs.Add("orphans", c.siArgumentInput, True, c.siBool)
	return true

def zLoadEnvXML_Execute(filename, XSImodel, orphans):

	# if we don't have a model use the scene root #
	if not XSImodel:
		XSImodel = xsi.ActiveSceneRoot
		
	# make sure we have a model #
	if XSImodel.Type != '#model':
		log('Model argument is not of type "model".', c.siError)
		return False

	# make sure the file exists #
	if not os.path.exists(filename):
		log('File doesn\'t exist: %s' % filename, c.siError)
		return False

	# initialize a progress bar #
	pb = XSIUIToolkit.ProgressBar
	pb.Caption = 'Parsing: ' + os.path.basename(filename)
	pb.Step = 1
	if xsi.Interactive: pb.Visible = True

	# read in the xml file #
	tStart = time.time()
	xml = dom.parse(filename)
	doc = xml.documentElement
	tParse = time.time() - tStart
	log('Time to parse file: %02d:%02d.%02d' % (int(tParse/60), tParse%60, tParse%1*100))
	
	# count all the weight elements #
	weightCount = len(doc.getElementsByTagName('weight'))

	# update progress bar #
	pb.Maximum = weightCount
	import locale
	locale.setlocale(locale.LC_ALL, '')
	pb.StatusText = 'Processing: %s weights' % locale.format('%d', weightCount, True)
	
	# step through the geometry #
	tApply = time.time()
	xGeometry = xml.getElementsByTagName('geometry')
	for xGeo in xGeometry:

		# get the geometry #
		nodeName = xGeo.getAttribute('name')
		
		# set the progress bar #
		pb.Caption = 'Enveloping: %s' % nodeName

		# find the geometry #
		obj = XSImodel.FindChild(nodeName)
		if not obj:
			log('Unable to find object: %s. Trying by id...' % nodeName, c.siWarning)
			# get the id #
			uid = xGeo.getAttribute('id')
			if not uid:
				log('No uid found. Skipping %s.' % obj)
				continue
			log('Id: %s' % uid)
			obj = XSImodel.FindChild(uid)
			if not obj:
				log('...Unable to find object "%s" by id "%s". Skipping' % (nodeName, uid), c.siWarning)
				continue
			else:
				log('...found by id %s' % obj)
		
		log('Enveloping: %s' % obj)
		
		# get the point count #
		xPointCount = int(xGeo.getAttribute('points'))
		
		# make sure the point counts match #
		objPointCount = obj.ActivePrimitive.Geometry.Points.Count
		if xPointCount != objPointCount:
			log('Point count doesn\'t match. %s(%d) != %s(%d))' % (nodeName, xPointCount, obj.FullName, objPointCount))
			
		# get all the xml deformers #
		xDeformers = xGeo.getElementsByTagName('deformer')

		# create a dictionary of deformers #
		xDefDict = {}

		# create list of deformers so we can get it by the id #
		xDefList = [None]*len(xDeformers)
		
		# create a collection of deformers #
		dfmCol = dispatch('XSI.Collection')
		for xDfm in xDeformers:
			# get the deformer name #
			dfmName = xDfm.getAttribute('name').lower()
			# find the deformer #
			xsiDfm = XSImodel.FindChild(xDfm.getAttribute('name'))
			if not xsiDfm:
				log('Unable to find deformer: %s. Trying by id...' % xDfm.getAttribute('name'), c.siWarning)
				# get the id #
				uid = xDfm.getAttribute('id')
				# xsiDfm = XSImodel.FindChild(uid)
				xsiDfm = xsi.zFindNodeById(uid, XSImodel)
				if not xsiDfm:
					if orphans:
						# create an orphaned deformer node under the model #
						orphan_parent = XSImodel.FindChild('Orphaned_Deformers')
						if not orphan_parent:
							orphan_parent = XSImodel.AddNull('Orphaned_Deformers')
							xsi.zHide(orphan_parent)
						# add the orphan #
						xsiDfm = orphan_parent.AddNull(xDfm.getAttribute('name'))
						xsi.zHide(xsiDfm)
					else:
						log('...Unable to find deformer "%s" by id "%s". Skipping' % (xDfm.getAttribute('name'), uid), c.siWarning)
						continue
			# add it to the dfm collection #
			dfmCol.Add(xsiDfm)
			# add the xml deformer node to the def dict #
			xDefDict[dfmName] = xDfm
	
		# skip if we don't have all the deformers #
		if dfmCol.Count != len(xDeformers):
			log('Unable to find all the deformers for %s. Skipping envelope.' % nodeName, c.siError)
			log('Found %d of %d deformers. Skipping envelope.' % (dfmCol.Count, len(xDeformers)), c.siError)
			continue
		
		# TODO: check for envelope on items #
		
		# apply the envelope #
		env = obj.ApplyEnvelope(dfmCol, c.siNode, c.siNode)
		
		# create an array to hold the weights #
		weights = list(env.Weights.Array)
		for i in xrange(len(weights)):
			weights[i] = [0.0]*len(weights[i])

		# set the deformer color #
		color = env.GetDeformerColor(dfmCol(0))
		# step through the deformers again and set colors #
		for d in xrange(env.Deformers.Count):
			# get the deformer #
			dfm = env.Deformers(d)
			# skip over effs #
			if dfm.Type == 'eff': continue
			# get the deformer in the xml file #
			xDef = xDefDict[dfm.Name.lower()]
			# build the color #
			color.Red 	= float(xDef.getAttribute('red'))
			color.Green = float(xDef.getAttribute('green'))
			color.Blue 	= float(xDef.getAttribute('blue'))
			# set the color #
			env.SetDeformerColor(dfm, color)
			# get the weights for the deformer #
			for xWgt in xDef.getElementsByTagName('weight'):
				# catch cancel #
				if pb.CancelPressed: return False
				# get the point id #
				p = int(xWgt.getAttribute('point'))
				# get the value #
				value = float(xWgt.getAttribute('value'))
				# set the weight for the deformer #
				weights[d][p] = value
				# increment the pb #
				pb.Increment()
			
		# set the weights #
		env.Weights.Array = weights

		# freeze the envelope weights cluster #
		# # log('Freezing Env: %s' % env )
		# # xsi.FreezeObj(env)
		# for cluster in obj.ActivePrimitive.Geometry.Clusters:
		# 	log('Cluster Env: %s' % cluster.Envelopes.Count)
		# 	log('Cluster Type: %s' % cluster.Type)
		# 	# for element in cluster.Elements:
		# 	# 	log('Element: %s' % element)
	
	# get the time to apply the weights #
	tElapse = time.time() - tApply
	log('Time to apply weights: %02d:%02d.%02d' % (int(tElapse/60), tElapse%60, tElapse%1*100))
	
	# get the total time #
	tTotal = time.time() - tStart
	log('Total Elapsed time: %02d:%02d.%02d' % (int(tTotal/60), tTotal%60, tTotal%1*100))

def zLoadEnvXMLGUI_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true

	oArgs = oCmd.Arguments
	oArgs.Add("filename",c.siArgumentInput, '', c.siString)
	oArgs.AddObjectArgument("XSImodel")
	oArgs.Add("orphans", c.siArgumentInput, True, c.siBool)
	return true

def zLoadEnvXMLGUI_Execute(filename, XSImodel, orphans):
	return
