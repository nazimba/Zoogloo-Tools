"""
XSI Operator for the zConstraintRaycast.


I{Created by Andy Buecker on 2008-04-08.
Copyright (c) 2008 Zoogloo LLC. All rights reserved.

Modification or distribution of this tool is not permitted without the
consent of Zoogloo LLC.}
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
	in_reg.Name = "zConstraintRaycastOp"
	in_reg.Email = "andy@zoogloo.net"
	in_reg.URL = ""
	in_reg.Major = 1
	try:
		in_reg.Minor = int(__version__.split(' ')[1])
	except:
		in_reg.Minor = 0

	in_reg.RegisterOperator('zCnsRaycastOp')
	
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
# Operator
#-----------------------------------------------------------------------------
def zCnsRaycastOp_Define(ctxt):
	op = ctxt.Source
	
	# add a parameter #
	op.AddParameter(
		XSIFactory.CreateParamDef2("Weight", c.siFloat, 1.0, 0.0, 1.0),
	)

	op.AlwaysEvaluate = false
	op.Debug = 0
	return true

def zCnsRaycastOp_Init(ctxt):
	# create vectors for the root to the target and rest + projected normals #
	ctxt.UserData = [
		XSIMath.CreateVector3(),
		XSIMath.CreateVector3(),
		XSIMath.CreateTransform(),
	]

	return true
	
def zCnsRaycastOp_Update(ctxt):

	# get the parameters #
	source 		= dispatch(ctxt.Source)
	v_ray		= ctxt.UserData[0]
	v_result 	= ctxt.UserData[1]
	t_out 		= ctxt.UserData[2]

	# get the inputs #
	geometry	 	= ctxt.GetInputValue(0)
	v_geometry 		= ctxt.GetInputValue(1).Transform.Translation
	v_target		= ctxt.GetInputValue(2).Transform.Translation
	weight			= ctxt.GetParameterValue('Weight')
	
	# get a ray from the center to the object to the target #
	v_ray.Sub(v_target, v_geometry)
	
	# get the raycast intersection #
	locs = geometry.Geometry.GetRaycastIntersections(
		[0, 0, 0],
		[v_ray.X, v_ray.Y, v_ray.Z],
		c.siSegmentIntersection
	)

	# evaluate the position on surface #
	pos = geometry.Geometry.EvaluatePositions(locs)
	v_result.Set(pos[0][0], pos[1][0], pos[2][0])

	# add the global position of the geometry to the resulting vector #
	v_result.AddInPlace(v_geometry)
	
	# multiply it by the weight #
	v_result.ScaleInPlace(weight)

	# add it to the transform #
	t_out.Translation = v_result

	# set the output value #
	ctxt.OutputPort.Value.Transform = t_out

	return
	