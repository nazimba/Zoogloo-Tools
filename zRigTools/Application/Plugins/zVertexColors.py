"""
zVertexColors.py

We really need to evaluate the UV's at each sample.  Right now, we are just
associating the lit of samples to the points and looking up the UV of the
point.  However it is not straight forward to get this information.

UV's can only be accessed by triangle points.  Samples are accessed by 
Polygon Faces. The trick is finding a way to associate the samples to the
triangle points.  The API isn't very good at this.

I{Created by Andy Buecker on 2008-04-25.
Copyright (c) 2008 Zoogloo LLC. All rights reserved.}
"""

__version__ = '$Revision: 11 $'
__author__  = '$Author: andy $'
__date__    = '$Date: 2008-07-21 15:20 -0700 $'

import win32com.client
from win32com.client import constants
from win32com.client import constants as c
from win32com.client.dynamic import Dispatch as dispatch
import time
import os
import re
import xml.dom.minidom as dom

xsi = Application
log = xsi.logmessage

null = None
false = 0
true = 1

def XSILoadPlugin(in_reg):
	in_reg.Author = "Andy Buecker"
	in_reg.Name = "zVertexColors"
	in_reg.Email = "andy@zoogloo.net"
	in_reg.URL = ""
	try:
		in_reg.Major = int(__version__.split(' ')[1])
	except:
		in_reg.Major = 1
	in_reg.Minor = 0

	in_reg.RegisterCommand("zVertexColorsFromCurrentTexture", "zVertexColorsFromCurrentTexture")
	in_reg.RegisterCommand("zVertexColorsFromCurrentTextureOnSel", "zVertexColorsFromCurrentTextureOnSel")
	
	in_reg.RegisterMenu(c.siMenuTbGetPropertyID, 'zVertexColorMenu', False)

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
def zVertexColorMenu_Init(ctxt):
	menu = ctxt.Source
	
	item = menu.AddCommandItem('zVertexColorsFromCurrentTextureOnSel', 'zVertexColorsFromCurrentTextureOnSel')
	item.Name = 'Set Vertex Colors From Cur Tex (z)'
	

#-----------------------------------------------------------------------------
# Commands
#-----------------------------------------------------------------------------
def zVertexColorsFromCurrentTextureOnSel_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true
	return true

def zVertexColorsFromCurrentTextureOnSel_Execute():
	# step through all the selected items #
	for item in xsi.selection:
		# set the vertex colors #
		xsi.zVertexColorsFromCurrentTexture(item)

def zVertexColorsFromCurrentTexture_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true

	oArgs = oCmd.Arguments
	oArgs.AddWithHandler('objects', c.siArgHandlerCollection)
	oArgs.Add("propertyName",c.siArgumentInput, 'Vertex_Color', c.siString)
	oArgs.Add("useExisting",c.siArgumentInput, True, c.siBool)
	return true

def zVertexColorsFromCurrentTexture_Execute(objects, propertyName, useExisting):

	# step through all items #
	for item in objects:
		
		# make sure we have a mesh #
		if item.Type != "polymsh":
			log('Node "%s" not a polymsh. Skipping.', c.siWarning)
			continue
			
		# step through the polynodes(samples) #
		mesh = item.ActivePrimitive.Geometry
		faces = mesh.Polygons
		# for face in faces:
		# 	nodes = face.Nodes
		# 	for node in nodes: # <-- samples
		# 		# log(node.Index) # <-- sample index 
		# 		# log(node.SubComponent) # <-- here are all the samples
		# 		# for sub in node.SubComponent:
		# 		# 	log(sub)
		# 		pass
		# 	# log('Face: %s -> Tris: %s' % (face.Index, face.TriangleSubIndexArray))
		
		# create vertex colors prop #
		vc = None
		if useExisting:
			vc = mesh.CurrentVertexColor
		if not vc:
			vc = mesh.AddVertexColor()
			mesh.CurrentVertexColor = vc

		# convert the tuple to a list #
		vcColors = list(vc.Elements.Array)
		for i in xrange(len(vcColors)):
			vcColors[i] = list(vcColors[i])

		# get the parent elements, this will return a Polygon Node item #
		elems = vc.Parent.Elements

		# create a list of point id's to a list of sample id's #
		pointSamples = [None]*mesh.Points.Count 
		for point in mesh.Points:
			for smpl in point.Samples:
				# create the list if it doesn't exist #
				if not pointSamples[point.Index]: pointSamples[point.Index] = []
				pointSamples[point.Index].append(smpl.Index)
				
		

		# actually need to create a list of UV's by sample id's #

		# get the current image #
		mat = item.Materials(0)
		img = mat.CurrentImageClip.GetImage()
		resX = img.ResX
		resY = img.ResY
		#log('X:%s, Y:%s' % (resX, resY))

		# create a list of uv's by point id's #
		uvList = [None] * item.ActivePrimitive.Geometry.Points.Count
		pntCount = 0
		for tri in item.ActivePrimitive.Geometry.Triangles:
			for p in tri.Points:
				# log('%s -> %s [%s, %s]' % (p, p.Index, p.UV.U, p.UV.V))
				uvList[p.Index] = {'u': p.UV.U, 'v': p.UV.V}
				pntCount += 1
				# log(mesh.Samples.Item(p))
		# log('--> Triangles Point Count: %s' % pntCount)
		# return

		for pnt in xrange(len(uvList)):
			# get the coordinates #
			uv = uvList[pnt]
			x = uv.get('u') * (resX-1) # starts at 0 so max woud be res - 1 
			y = uv.get('v') * (resY-1)

			# make sure we have positive values #
			x = x % resX
			y = y % resY

			# get the pixel color #
			try:
				c = img.GetPixel(x,y) # GetPixelArray would probably be way faster #
			except:
				log('%s %s' % (x, y))
				log('%s %s' % (resX, resY))
				break

			#log('UV[%s,%s] -> XY[%s,%s] -> RGBA[%s,%s,%s,%s]' % (uv.get('u'), uv.get('v'), x, y, c.Red, c.Green, c.Blue, c.Alpha))
			# step through all the samples per point #
			for smpl in pointSamples[pnt]:
				#log('%s -> %s' % (pnt, smpl))

				vcColors[0][smpl] = c.Red
				vcColors[1][smpl] = c.Green
				vcColors[2][smpl] = c.Blue
				vcColors[3][smpl] = c.Alpha

		# set the new vertex colors #
		vc.Elements.Array = vcColors

