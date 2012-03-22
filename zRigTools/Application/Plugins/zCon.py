"""
zConMaker.py

XSI Class for creating contollers.

>>> # foot con #
>>> con_foot 							= xsi.zCon()
>>> con_foot.type 						= 'sphere'
>>> con_foot.size 						= 10
>>> con_foot.transform			 		= Appication.ActiveSceneRoot()
>>> con_foot.basename 					= 'Foot'
>>> con_foot.symmetry 					= 'left'
>>> con_foot.parent_node 				= Application.ActiveSceneRoot()
>>> con_foot.rotation_order 			= 'zyx'
>>> con_foot.red 				   		= 0
>>> con_foot.green 			   			= 1
>>> con_foot.blue 				   		= 0
>>> con_foot.Draw()
>>> con_foot.AddTransformSetupLast()
>>> con_foot.node_rest					# rest node
>>> con_foot.node_con					# control node
>>> con_foot.node_hook					# hook node

Created by andy on 2007-05-24.
Copyright (c) 2007 Zoogloo LLC. All rights reserved.
"""

import win32com.client
from win32com.client import constants
from win32com.client import constants as c
from win32com.client.dynamic import Dispatch as dispatch
import copy
import re

null = None
false = 0
true = 1

xsi = Application
log = xsi.logmessage

def XSILoadPlugin( in_reg ):
	in_reg.Author = "Andy"
	in_reg.Name = "zCon"
	in_reg.Email = ""
	in_reg.URL = ""
	in_reg.Major = 0
	in_reg.Minor = 1

	
	in_reg.RegisterProperty('zConGUI')
	
	in_reg.RegisterCommand('zCon', 'zCon')
	in_reg.RegisterCommand('zConGUI', 'zConGUI')

	in_reg.RegisterMenu(c.siMenuTbGetPrimitiveID, 'zConMenu', False)
	
	#RegistrationInsertionPoint - do not remove this line

	return true
	
def XSIUnloadPlugin( in_reg ):
	strPluginName = in_reg.Name
	Application.LogMessage(str(strPluginName) + str(" has been unloaded."))
	return true
	
#-----------------------------------------------------------------------------
# Menus
#-----------------------------------------------------------------------------
def zConMenu_Init(ctxt):
	menu = ctxt.Source
	
	item = menu.AddCommandItem('zConGUI', 'zConGUI')
	item.Name = '(z) Cons'

#-----------------------------------------------------------------------------
# Commands
#-----------------------------------------------------------------------------

point_dict = {
	'box': {
		'array': [
			[-0.5, 0.5, 0.5, -0.5, -0.5, -0.5, -0.5, -0.5, 0.5, 0.5, -0.5, -0.5, 0.5, 0.5, 0.5, 0.5], 
			[-0.5, -0.5, 0.5, 0.5, -0.5, -0.5, 0.5, 0.5, 0.5, 0.5, 0.5, -0.5, -0.5, 0.5, -0.5, -0.5], 
			[0.5, 0.5, 0.5, 0.5, 0.5, -0.5, -0.5, 0.5, 0.5, -0.5, -0.5, -0.5, -0.5, -0.5, -0.5, 0.5], 
			[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
		],
		'degree': 1
	},

	'round_box': {
		'array': [
			[0.5, 0.5, 0.5, 0.5, -0.5, -0.5, -0.5, -0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, -0.5, -0.5, -0.5, -0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, -0.5, -0.5, -0.5, -0.5, 0.5, 0.5, 0.5, 0.5, -0.5, -0.5, -0.5, -0.5, 0.5, 0.5, 0.5, 0.5, -0.5, -0.5, -0.5, -0.5, -0.5, -0.5, -0.5, -0.5, -0.5, -0.5, -0.5, -0.5], 
			[-0.5, -0.5, 0.5, 0.5, 0.5, 0.5, -0.5, -0.5, -0.5, -0.5, 0.5, 0.5, 0.5, 0.5, -0.5, -0.5, -0.5, -0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, -0.5, -0.5, -0.5, -0.5, 0.5, 0.5, 0.5, 0.5, -0.5, -0.5, -0.5, -0.5, -0.5, -0.5, -0.5, -0.5, -0.5, -0.5, -0.5, -0.5, -0.5, -0.5, 0.5, 0.5, 0.5, 0.5, -0.5, -0.5, -0.5, -0.5], 
			[-0.5, -0.5, -0.5, -0.5, -0.5, -0.5, -0.5, -0.5, -0.5, -0.5, -0.5, -0.5, 0.5, 0.5, 0.5, 0.5, -0.5, -0.5, -0.5, -0.5, 0.5, 0.5, 0.5, 0.5, -0.5, -0.5, -0.5, -0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, -0.5, -0.5, -0.5, -0.5, 0.5, 0.5, 0.5, 0.5, -0.5, -0.5, -0.5, -0.5, 0.5, 0.5, 0.5, 0.5, -0.5, -0.5], 
			[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
		],
		'degree': 3
	},

	'square': {
		'array': [
			[0.5,  0.5, -0.5, -0.5, 0.5], 
			[0.0,  0.0,  0.0,  0.0, 0.0], 
			[0.5, -0.5, -0.5,  0.5, 0.5], 
			[1,      2,    3,    4,   5]
		],
		'degree': 1
	},
	
	'sphere': {
		'array': [
			[0.0, -0.38300000000000001, -0.70699999999999996, -0.92400000000000004, -1.0, -0.92400000000000004, -0.70699999999999996, -0.38300000000000001, 0.0, 0.38300000000000001, 0.70699999999999996, 0.92400000000000004, 1.0, 0.92400000000000004, 0.70699999999999996, 0.38300000000000001, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.38300000000000001, -0.70699999999999996, -0.92400000000000004, -1.0, -0.92400000000000004, -0.70699999999999996, -0.38300000000000001, 0.0, 0.38300000000000001, 0.70699999999999996, 0.92400000000000004, 1.0, 0.92400000000000004, 0.70699999999999996, 0.38300000000000001, 0.0, -0.38300000000000001, -0.70699999999999996, -0.92400000000000004, -1.0],
			[1.0, 0.92400000000000004, 0.70699999999999996, 0.38300000000000001, 0.0, -0.38300000000000001, -0.70699999999999996, -0.92400000000000004, -1.0, -0.92400000000000004, -0.70699999999999996, -0.38300000000000001, 0.0, 0.38300000000000001, 0.70699999999999996, 0.92400000000000004, 1.0, 0.92400000000000004, 0.70699999999999996, 0.38300000000000001, 0.0, -0.38300000000000001, -0.70699999999999996, -0.92400000000000004, -1.0, -0.92400000000000004, -0.70699999999999996, -0.38300000000000001, 0.0, 0.38300000000000001, 0.70699999999999996, 0.92400000000000004, 1.0, 0.92400000000000004, 0.70699999999999996, 0.38300000000000001, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
			[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.38300000000000001, 0.70699999999999996, 0.92400000000000004, 1.0, 0.92400000000000004, 0.70699999999999996, 0.38300000000000001, 0.0, -0.38300000000000001, -0.70699999999999996, -0.92400000000000004, -1.0, -0.92400000000000004, -0.70699999999999996, -0.38300000000000001, 0.0, 0.0, 0.0, 0.0, 0.0, 0.38300000000000001, 0.70699999999999996, 0.92400000000000004, 1.0, 0.92400000000000004, 0.70699999999999996, 0.38300000000000001, 0.0, -0.38300000000000001, -0.70699999999999996, -0.92400000000000004, -1.0, -0.92400000000000004, -0.70699999999999996, -0.38300000000000001, 0.0],
			[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53]
		],
		'degree': 1
	},

	'hemi': {
		'array': [
			[1.8847317514027658e-016, 1.8847317514027658e-016, 1.741265089395166e-016, 1.3327066021344942e-016, 7.2125561571427846e-017, 0.0, -7.2125561571427784e-017, -1.3327066021344946e-016, -1.7412650893951663e-016, -1.8847317514027658e-016, -1.8847317514027658e-016, -0.39264623741499444, -0.72551564453056139, -0.94793187158204539, -1.0260340642089771, -1.0260340642089771, -0.94793187158204573, -0.72551564453056172, -0.39264623741499449, 0.0, 0.39264623741499488, 0.72551564453056139, 0.94793187158204539, 1.0260340642089771, 1.0260340642089771, 0.94793187158204539, 0.7255156445305615, 0.39264623741499499, 1.2564878342685105e-016, 1.2564878342685105e-016, 1.741265089395166e-016, 1.3327066021344942e-016, 7.2125561571427846e-017, 0.0, -7.2125561571427784e-017, -1.3327066021344946e-016, -1.7412650893951663e-016, -1.8847317514027658e-016, -1.8847317514027658e-016, 0.3926462374149941, 0.72551564453056105, 0.94793187158204528, 1.0260340642089771, 1.0260340642089771, 0.94793187158204539, 0.72551564453056139, 0.39264623741499488, 0.0, -0.39264623741499449, -0.72551564453056172, -0.94793187158204573, -1.0260340642089771, -1.0260340642089771, -0.94793187158204573, -0.72551564453056161, -0.39264623741499438],
			[0.0, 0.0, 0.39264623741499416, 0.72551564453056117, 0.94793187158204517, 1.0260340642089771, 0.94793187158204528, 0.72551564453056072, 0.39264623741499316, 0.0, 0.0, -5.804216964650553e-017, -4.442355340448313e-017, -2.404185385714258e-017, 0.0, 0.0, 0.39264623741499316, 0.72551564453056072, 0.94793187158204528, 1.0260340642089771, 0.94793187158204517, 0.72551564453056117, 0.39264623741499416, 0.0, 0.0, 2.4041853857142574e-017, 4.4423553404483124e-017, 5.8042169646505518e-017, 6.2824391713425523e-017, 6.2824391713425523e-017, 0.39264623741499416, 0.72551564453056117, 0.94793187158204517, 1.0260340642089771, 0.94793187158204528, 0.72551564453056072, 0.39264623741499316, 0.0, 0.0, -5.804216964650553e-017, -4.442355340448313e-017, -2.4041853857142586e-017, 0.0, 0.0, 0.39264623741499416, 0.72551564453056117, 0.94793187158204517, 1.0260340642089771, 0.94793187158204528, 0.72551564453056072, 0.39264623741499316, 0.0, 0.0, 2.4041853857142512e-017, 4.4423553404483099e-017, 5.8042169646505518e-017],
			[-1.0260340642089771, -1.0260340642089771, -0.94793187158204539, -0.72551564453056139, -0.39264623741499488, 0.0, 0.39264623741499449, 0.72551564453056172, 0.94793187158204573, 1.0260340642089771, 1.0260340642089771, 0.94793187158204539, 0.72551564453056117, 0.39264623741499416, -1.2564878342685105e-016, -1.2564878342685105e-016, -1.1608433929301109e-016, -8.884710680896631e-017, -4.8083707714285191e-017, 0.0, 4.8083707714285234e-017, 8.8847106808966273e-017, 1.1608433929301106e-016, 1.2564878342685105e-016, 1.2564878342685105e-016, -0.39264623741499405, -0.72551564453056105, -0.94793187158204517, -1.0260340642089771, -1.0260340642089771, -0.94793187158204539, -0.72551564453056139, -0.39264623741499488, 0.0, 0.39264623741499449, 0.72551564453056172, 0.94793187158204573, 1.0260340642089771, 1.0260340642089771, 0.94793187158204539, 0.72551564453056139, 0.39264623741499449, 1.2564878342685105e-016, 1.2564878342685105e-016, 1.1608433929301106e-016, 8.8847106808966273e-017, 4.8083707714285234e-017, 0.0, -4.8083707714285191e-017, -8.884710680896631e-017, -1.1608433929301109e-016, -1.2564878342685105e-016, -1.2564878342685105e-016, -0.39264623741499327, -0.72551564453056083, -0.94793187158204528],
			[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
		],
		'degree': 3,
		'closed': True
	},

	'rot':  {
		'array': [
			[-0.34499999999999997, -1.0880000000000001, -0.85999999999999999, -0.75800000000000001, -0.63100000000000001, -0.28199999999999997, 0.27300000000000002, 0.624, 0.752, 0.85199999999999998, 1.0880000000000001, 0.34200000000000003, 0.57499999999999996, 0.47799999999999998, 0.20899999999999999, -0.216, -0.48299999999999998, -0.57999999999999996, -0.34499999999999997], 
			[0.38900000000000001, 0.012, 0.89500000000000002, 0.65300000000000002, 0.79900000000000004, 1.022, 1.024, 0.80500000000000005, 0.65900000000000003, 0.90200000000000002, 0.021000000000000001, 0.39200000000000002, 0.504, 0.61599999999999999, 0.78400000000000003, 0.78200000000000003, 0.61199999999999999, 0.499, 0.38900000000000001], 
			[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 
			[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
		],
		'degree': 1
	},
	
	'spike':  {
		'array': [
			[0.0, 0.0, -0.75, 0.0, 0.0, -0.75, 0.0, 0.0], 
			[0.0, 0.75, 0.0, 0.0, 0.0, 0.0, 0.75, 0.0], 
			[0.0, 2.0, 2.0, 0.0, 2.0, 2.0, 2.0, 2.0], 
			[1, 2, 3, 4, 5, 6, 7, 8]
		],
		'degree': 1
	},
	
	'pyramid':  {
		'array': [
			[0.0, 0.0, -0.75, 0.0, 0.0, -0.75, 0.0, 0.0], 
			[0.0, 0.75, 0.0, 0.0, 0.0, 0.0, 0.75, 0.0], 
			[0.0, 2.0, 2.0, 0.0, 2.0, 2.0, 2.0, 2.0], 
			[1, 2, 3, 4, 5, 6, 7, 8]
		],
		'degree': 1
	},

	'flight':  {
		'array': [
			[1.0, 0.0, -3.0, 0.0, 1.0, 0.0, -3.0, 0.0, 0.0, 0.0, 0.0], 
			[0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0], 
			[0.0, 1.0, 0.0, -1.0, 0.0, 0.0, 0.0, -1.0, 1.0, 0.0, -1.0], 
			[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
		],
		'degree': 1
	},

	'pointer':  {
		'array': [
			[0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0], 
			[1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 0.0, 0.0], 
			[0.0, -1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, -1.0], 
			[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
		],
		'degree': 1
	},
	
	'circle': {
		'array': [
			[-1.0, -1.0, -0.78400000000000003, 0.0, 0.78400000000000003, 1.1080000000000001, 0.78400000000000003, 0.0, -0.78400000000000003, -1.0, -1.0], 
			[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 
			[0.0, 0.26100000000000001, 0.78400000000000003, 1.1080000000000001, 0.78400000000000003, 0.0, -0.78400000000000003, -1.1080000000000001, -0.78400000000000003, -0.26100000000000001, 0.0], 
			[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
		],
		'degree': 3
	},
	
	'pointy_circle': {
		'array': [
			[1.0260340642089771, 0.41762033503264923, 0.72551564453056128, 0.17298400669331909, 0.0, -0.1729840066933192, -0.72551564453056117, -0.41762033503264939, -1.0260340642089771, -0.41762033503264945, -0.72551564453056139, -0.17298400669331948, 0.0, 0.17298400669331915, 0.72551564453056172, 0.41762033503264939],
			[0.0, -1.0591865685314591e-017, -4.442355340448313e-017, -2.5571025788320642e-017, -6.2824391713425523e-017, -2.5571025788320642e-017, -4.442355340448313e-017, -1.0591865685314594e-017, 0.0, 1.0591865685314531e-017, 4.4423553404483124e-017, 2.5571025788320581e-017, 6.2824391713425523e-017, 2.5571025788320584e-017, 4.4423553404483099e-017, 1.0591865685314504e-017],
			[0.0, 0.17298400669331962, 0.72551564453056128, 0.41762033503264978, 1.0260340642089771, 0.41762033503264978, 0.72551564453056128, 0.17298400669331965, 0.0, -0.17298400669331862, -0.72551564453056117, -0.41762033503264878, -1.0260340642089771, -0.41762033503264884, -0.72551564453056072, -0.1729840066933182],
			[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]		
		],
		'degree': 3,
		'closed': True
	},
	
	'4_arrow_rot': {
		'array': [
			[0.0, -0.33700000000000002, -0.096000000000000002, -0.096000000000000002, -0.096000000000000002, -0.501, -0.751, -0.751, -1.002, -0.751, -0.751, -0.501, -0.096000000000000002, -0.096000000000000002, -0.096000000000000002, -0.33700000000000002, 0.0, 0.33700000000000002, 0.096000000000000002, 0.096000000000000002, 0.096000000000000002, 0.501, 0.751, 0.751, 1.002, 0.751, 0.751, 0.501, 0.096000000000000002, 0.096000000000000002, 0.096000000000000002, 0.33700000000000002, 0.0], 
			[0.34999999999999998, 0.67800000000000005, 0.67800000000000005, 0.84999999999999998, 0.95399999999999996, 0.84999999999999998, 0.67800000000000005, 0.67800000000000005, 0.34999999999999998, 0.67800000000000005, 0.67800000000000005, 0.84999999999999998, 0.95399999999999996, 0.84999999999999998, 0.67800000000000005, 0.67800000000000005, 0.34999999999999998, 0.67800000000000005, 0.67800000000000005, 0.84999999999999998, 0.95399999999999996, 0.84999999999999998, 0.67800000000000005, 0.67800000000000005, 0.34999999999999998, 0.67800000000000005, 0.67800000000000005, 0.84999999999999998, 0.95399999999999996, 0.84999999999999998, 0.67800000000000005, 0.67800000000000005, 0.34999999999999998], 
			[-1.002, -0.751, -0.751, -0.501, -0.099000000000000005, -0.099000000000000005, -0.099000000000000005, -0.33700000000000002, 0.0, 0.33700000000000002, 0.099000000000000005, 0.099000000000000005, 0.099000000000000005, 0.501, 0.751, 0.751, 1.002, 0.751, 0.751, 0.501, 0.099000000000000005, 0.099000000000000005, 0.099000000000000005, 0.33700000000000002, 0.0, -0.33700000000000002, -0.099000000000000005, -0.099000000000000005, -0.099000000000000005, -0.501, -0.751, -0.751, -1.002], 
			[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33]
		],
		'degree': 1
	},
	
	'arrow': {
		'array': [
			[0.80600000000000005, 0.80600000000000005, 1.6120000000000001, 0.0, -1.6120000000000001, -0.80600000000000005, -0.80600000000000005, 0.80600000000000005], 
			[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 
			[-1.6120000000000001, 0.0, 0.0, 2.419, 0.0, 0.0, -1.6120000000000001, -1.6120000000000001], 
			[1, 2, 3, 4, 5, 6, 7, 8]
		],
		'degree': 1
	},
	
	'4_pin': {
		'array': [
			[-1.2, -1.276, -1.476, -1.724, -1.9239999999999999, -2.0, -1.9239999999999999, -1.724, -1.476, -1.276, -1.2, 0.0, 1.2, 1.276, 1.476, 1.724, 1.9239999999999999, 2.0, 1.9239999999999999, 1.724, 1.476, 1.276, 1.2, 0.0, 0.0, -0.23499999999999999, -0.38, -0.38, -0.23499999999999999, 0.0, 0.23499999999999999, 0.38, 0.38, 0.23499999999999999, 0.0, 0.0, 0.0, -0.23499999999999999, -0.38, -0.38, -0.23499999999999999, 0.0, 0.23499999999999999, 0.38, 0.38, 0.23499999999999999, 0.0], 
			[0.0, 0.23499999999999999, 0.38, 0.38, 0.23499999999999999, 0.0, -0.23499999999999999, -0.38, -0.38, -0.23499999999999999, 0.0, 0.0, 0.0, 0.23499999999999999, 0.38, 0.38, 0.23499999999999999, 0.0, -0.23499999999999999, -0.38, -0.38, -0.23499999999999999, 0.0, 0.0, -1.2, -1.276, -1.476, -1.724, -1.9239999999999999, -2.0, -1.9239999999999999, -1.724, -1.476, -1.276, -1.2, 0.0, 1.2, 1.276, 1.476, 1.724, 1.9239999999999999, 2.0, 1.9239999999999999, 1.724, 1.476, 1.276, 1.2], 
			[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 
			[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47]
		],
		'degree': 1
	},
	
	'cone': {
		'array': [
			[0.0, 0.0, 0.0, -0.70699999999999996, 0.0, -0.70699999999999996, -1.0, 0.0, -1.0, -0.70699999999999996, 0.0, -0.70699999999999996, 0.0, 0.0, 0.0, 0.70699999999999996, 0.0, 0.70699999999999996, 1.0, 0.0, 1.0, 0.70699999999999996, 0.0, 0.70699999999999996, 0.0, 0.0, 0.0, -0.70699999999999996, 0.0, -0.70699999999999996, -1.0, 0.0], 
			[0.0, 2.0, 0.0, 0.0, 2.0, 0.0, 0.0, 2.0, 0.0, 0.0, 2.0, 0.0, 0.0, 2.0, 0.0, 0.0, 2.0, 0.0, 0.0, 2.0, 0.0, 0.0, 2.0, 0.0, 0.0, 2.0, 0.0, 0.0, 2.0, 0.0, 0.0, 2.0], 
			[-1.0, 0.0, -1.0, -0.70699999999999996, 0.0, -0.70699999999999996, 0.0, 0.0, 0.0, 0.70699999999999996, 0.0, 0.70699999999999996, 1.0, 0.0, 1.0, 0.70699999999999996, 0.0, 0.70699999999999996, 0.0, 0.0, 0.0, -0.70699999999999996, 0.0, -0.70699999999999996, -1.0, 0.0, -1.0, -0.70699999999999996, 0.0, -0.70699999999999996, 0.0, 0.0], 
			[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32]
		],
		'degree': 1
	},
	
	'pin': {
		'array': [
			[0.0, 0.0, -0.23499999999999999, -0.38, -0.38, -0.23499999999999999, 0.0, 0.23499999999999999, 0.38, 0.38, 0.23499999999999999, 0.0], 
			[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 
			[0.0, 1.2, 1.276, 1.476, 1.724, 1.9239999999999999, 2.0, 1.9239999999999999, 1.724, 1.476, 1.276, 1.2], 
			[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
		],
		'degree': 1
	},

	'null': {
		'array': [
			[0.0, 0.0, 0.0, -1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0],
			[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0, 1.0, 0.0],
			[0.0, 1.0, 0.0, 0.0, 0.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
			[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],		
		],
		'degree': 1
	},

	'round_flight': {
		'array': [
			[0.0, -1.0, 0.0, 0.0, 1.0],
			[-6.1230317691156358e-017, -6.1230317691156358e-017, -6.1230317691156358e-017, -6.1230317691156358e-017, -6.1230317691156358e-017],
			[1.0, 0.0, -3.0, -3.0, 0.0],
			[1, 1, 1, 1, 1],
		],
		'degree': 3,
		'closed': True
	},

}


class zCon(object):
	"""class for creating controllers in XSI"""
	
	# required for COM wrapper #
	_public_methods_ = [
		'Draw',
		'AddTransformSetupPos',
		'AddTransformSetupRot',
		'AddTransformSetupLast',
		'Offset',
		'Scale',
		'Rotate',
		'Xform',
	]
	# define the output vars here #
	_public_attrs_ = [
		'basename',
		'parent_node',
		'symmetry',
		'type',
		'size',
		'red',
		'green',
		'blue',
		'transform',
		'node_rest',
		'node_con',
		'node_hook',
		'transform_setup',
		'rotation_order',
	]
	# define those attrs that are read only #
	_readonly_attrs_ = [
		'node_rest',
		# 'node_con',
		'node_hook',
		'transform_setup',
	]

	# class variables #
	basename		= 'zCon'
	symmetry		= None
	red				= None
	green			= None
	blue			= None
	transform		= None
	parent_node		= None
	rotation_order	= 'xyz'

	def __init__(self, con_type, basename):
		super(zCon, self).__init__()

		# set the con type #
		self.basename	= basename
		self.type		= con_type
		
		# set the default instance vars #
		self.size			= 1.0
		self.red			= 0.25
		self.green			= 0.25
		self.blue			= 0.5
		self.transform		= XSIMath.CreateTransform()
		self.rotation_order	= 'xyz'
		
	def AddTransformSetupPos(self, mode='local', x=True, y=True, z=True):
		"""assigns transform setup to the node"""
		
		# add the property #
		ts = self.node_con.AddProperty('Transform Setup')
		ts = dispatch(ts)
		self.transform_setup = ts
		
		# change it to translate mode #
		ts.tool.Value = 4
		
		# translate the mode #
		translate = 3
		if re.match(r'^view$', mode, re.I): 		translate = 0
		elif re.match(r'^global$', mode, re.I): 	translate = 1
		elif re.match(r'^local$', mode, re.I): 		translate = 2
		elif re.match(r'^parent$', mode, re.I): 	translate = 3
		elif re.match(r'^ref$', mode, re.I): 		translate = 4
		elif re.match(r'^plane$', mode, re.I): 		translate = 5
		ts.translate.Value = translate
		
		# set the axis #
		ts.xaxis.Value	= x
		ts.yaxis.Value	= y
		ts.zaxis.Value	= z
		
		# return the transform setup #
		return ts
		
	def AddTransformSetupRot(self, mode='add', x=True, y=True, z=True):
		"""assigns transform setup to the node"""
		
		# add the property #
		ts = self.node_con.AddProperty('Transform Setup')
		ts = dispatch(ts)
		self.transform_setup = ts
		
		# change it to translate mode #
		ts.tool.Value = 3
		
		# translate the mode #
		rotate = 3
		if re.match(r'^view$', mode, re.I): 		rotate = 0
		elif re.match(r'^global$', mode, re.I): 	rotate = 1
		elif re.match(r'^local$', mode, re.I): 		rotate = 2
		elif re.match(r'^add$', mode, re.I): 		rotate = 3
		elif re.match(r'^ref$', mode, re.I): 		rotate = 4
		elif re.match(r'^plane$', mode, re.I): 		rotate = 5
		ts.rotate.Value = rotate
		
		# set the axis #
		ts.xaxis.Value	= x
		ts.yaxis.Value	= y
		ts.zaxis.Value	= z
		
		# return the transform setup #
		return ts
		
	def AddTransformSetupLast(self):
		"""assigns transform setup to the node"""
		
		# add the property #
		ts = self.node_con.AddProperty('Transform Setup')
		ts = dispatch(ts)
		self.transform_setup = ts
		
		# change it to translate mode #
		ts.tool.Value = 1

		# return the transform setup #
		return ts
		
	def Offset(self, x, y, z):
		"""docstring for Offset"""
		
		# get all the position array #
		pa = list(self.node_con.ActivePrimitive.Geometry.Points.PositionArray)
		pa[0] = list(pa[0])
		pa[1] = list(pa[1])
		pa[2] = list(pa[2])
		
		# step through all the points #
		for p in xrange(len(pa[0])):
			pa[0][p] += x
			pa[1][p] += y
			pa[2][p] += z
			
		# put the array back on the curve #
		self.node_con.ActivePrimitive.Geometry.Points.PositionArray = pa
		

	def Xform(self, 
		m1,  m2,  m3,  m4,
		m5,  m6,  m7,  m8,
		m9,  m10, m11, m12,
		m13, m14, m15, m16
		):
		
		# assemble the source matrix #
		matrix4 = XSIMath.CreateMatrix4(
			m1,  m2,  m3,  m4,
			m5,  m6,  m7,  m8,
			m9,  m10, m11, m12,
			m13, m14, m15, m16
		)

		# get the current global transform matrix #
		matrix = self.node_con.Kinematics.Global.Transform.Matrix4
		matrix_invert = XSIMath.CreateMatrix4()
		matrix_invert.Invert(matrix)
		
		# get a matrix at the origin #
		matrix_origin = XSIMath.CreateMatrix4()
		
		# transformation matrix to go from current to the origin #
		matrix_to_origin = XSIMath.CreateMatrix4()
		matrix_to_origin.Mul(matrix_origin, matrix_invert)

		
		matrix_to_result = XSIMath.CreateMatrix4()
		matrix_to_result.Mul(matrix4, matrix_invert)
		
		# create a vector for the points #
		v = XSIMath.CreateVector3()
		
		# get all the position array #
		pa = list(self.node_con.ActivePrimitive.Geometry.Points.PositionArray)
		pa[0] = list(pa[0])
		pa[1] = list(pa[1])
		pa[2] = list(pa[2])
		
		# step through all the points #
		for p in xrange(len(pa[0])):
			
			# put the points in the vector #
			v.X = pa[0][p]
			v.Y = pa[1][p]
			v.Z = pa[2][p]
			
			# invert the points to remove the parent transform #
			# v.MulByMatrix4InPlace(matrix_to_origin)

			# multiply it by the transformation matrix #
			v.MulByMatrix4InPlace(matrix_to_result)
			# v.MulByMatrix4InPlace(matrix_delta)
			
			# put back the local transformation #
			# v.MulByMatrix4InPlace(matrix)

			# put the result back into the point list #
			pa[0][p] = v.X
			pa[1][p] = v.Y
			pa[2][p] = v.Z
			
		# put the array back on the curve #
		self.node_con.ActivePrimitive.Geometry.Points.PositionArray = pa
		

	def Scale(self, x, y, z):
		"""docstring for Scale"""
		
		# get all the position array #
		pa = list(self.node_con.ActivePrimitive.Geometry.Points.PositionArray)
		pa[0] = list(pa[0])
		pa[1] = list(pa[1])
		pa[2] = list(pa[2])
		
		# step through all the points #
		for p in xrange(len(pa[0])):
			pa[0][p] *= x
			pa[1][p] *= y
			pa[2][p] *= z
			
		# put the array back on the curve #
		self.node_con.ActivePrimitive.Geometry.Points.PositionArray = pa
		
		
	def Rotate(self, x, y, z):

		# get all the position array #
		pa = list(self.node_con.ActivePrimitive.Geometry.Points.PositionArray)
		pa[0] = list(pa[0])
		pa[1] = list(pa[1])
		pa[2] = list(pa[2])
		
		# convert angles to a transform #
		trans 	= XSIMath.CreateTransform()
		rot 	= XSIMath.CreateRotation(
			XSIMath.DegreesToRadians(x),
			XSIMath.DegreesToRadians(y),
			XSIMath.DegreesToRadians(z)
		)
		trans.Rotation = rot
		
		# step through all the points #
		for p in xrange(len(pa[0])):
			
			# create a transform for the point #
			t_points = XSIMath.CreateTransform()
			t_points.Translation = XSIMath.CreateVector3(pa[0][p], pa[1][p], pa[2][p])
			
			# multiply it by the rotation transform #
			t_points.MulInPlace(trans)
			
			# put the value back in the array #
			v_point = t_points.Translation
			pa[0][p] = v_point.X
			pa[1][p] = v_point.Y
			pa[2][p] = v_point.Z
		
		# put the array back on the curve #
		self.node_con.ActivePrimitive.Geometry.Points.PositionArray = pa

	def Draw(self):
		"""Draws the con based on the class attributes"""
		#---------------------------------------------------------------------
		# pre conditions
		
		match_text = re.match(r'^text:.+$', self.type, re.I)
		
		# make sure the curve definition exists in the point list #
		if not self.type in point_dict.keys() and not match_text:
			raise Exception(
				'No definition for con type "%s" found in point dictionary' % self.type
			)
		
		#---------------------------------------------------------------------
		# build the control
		
		# get the REST node #
		if not self.parent_node:
			self.parent_node = xsi.ActiveSceneRoot
		else:
			self.parent_node = dispatch(self.parent_node)
			
		# create a locator #
		node_rest = self.parent_node.AddNull(
			xsi.zMapName(self.basename, 'Home', self.symmetry)
		)
		# turn off the display #
		node_rest.primary_icon.Value = 0
		node_rest.Properties('Visibility').Parameters('viewvis').Value = False
		node_rest.Properties('Visibility').Parameters('rendvis').Value = False
		# set the transform #
		node_rest.Kinematics.Global.Transform = self.transform
		
		# scale the point array by the size #
		if not match_text:
			import copy
			pa = copy.deepcopy(point_dict.get(self.type).get('array'))
			for i in xrange(len(pa)):
				for r in xrange(len(pa[i])):
					pa[i][r] = pa[i][r] * self.size
		
		# determine if we are going to close the curve #
		closed = False
		if not match_text:
			if point_dict.get(self.type).has_key('closed'):
				closed = point_dict.get(self.type).get('closed')
		
		# draw the curve (CON) #
		node_con = None
		if not match_text:
			# curve controller #
			node_con = node_rest.AddNurbsCurve(
				pa, 
				None, 
				closed, 
				point_dict.get(self.type).get('degree'),
				c.siNonUniformParameterization,
				c.siSINurbs
			)
		else:
			# draw the text controller #
			node_con = node_rest.AddGeometry(
				'Text', 
				'NurbsCurve'
			)
			search 				= re.search(r'^text:(.+)$', self.type, re.I)
			node_con.text 		= "_RTF_{\\rtf1\\ansi\\deff0{\\fonttbl{\\f0\\fnil\\fprq5\\fcharset0 Arial;}}\r\n\\viewkind4\\uc1\\pard\\qc\\lang1033\\b\\f0\\fs20 %s\\b0\\par\r\n}\r\n" % search.groups(0)[0]
			node_con.fitsize 	= self.size
			# freeze to curves #
			xsi.FreezeObj(node_con)
			
		# rename #
		node_con.Name = xsi.zMapName(self.basename, 'Control', self.symmetry)
		# set the transform #
		node_con.Kinematics.Global.Transform = node_rest.Kinematics.Global.Transform
		
		# set the rotation order #
		ro = 0
		if   re.match(r'^xyz$', self.rotation_order, re.I): 		ro = 0
		elif re.match(r'^xzy$', self.rotation_order, re.I): 		ro = 1
		elif re.match(r'^yxz$', self.rotation_order, re.I): 		ro = 2
		elif re.match(r'^yzx$', self.rotation_order, re.I): 		ro = 3
		elif re.match(r'^zxy$', self.rotation_order, re.I): 		ro = 4
		elif re.match(r'^zyx$', self.rotation_order, re.I): 		ro = 5
		node_con.Kinematics.Local.Parameters('rotorder').Value = ro

		# add the HOOK #
		node_hook = node_con.AddNull(
			xsi.zMapName(self.basename, 'Hook', self.symmetry)
		)
		# turn off the display #
		node_hook.primary_icon.Value = 0
		node_hook.Properties('Visibility').Parameters('viewvis').Value = False
		node_hook.Properties('Visibility').Parameters('rendvis').Value = False
		# set the transform #
		node_hook.Kinematics.Global.Transform = node_rest.Kinematics.Global.Transform
		
		#---------------------------------------------------------------------
		# set the color
		 
		# a display property #
		disp = node_con.Properties('Display')
		if not node_con.Properties('zInit'):
			disp = node_con.AddProperty('Display Property', False)
			disp = dispatch(disp)

		# change the color #
		disp.wirecolorr.Value = self.red
		disp.wirecolorg.Value = self.green
		disp.wirecolorb.Value = self.blue
		
		#---------------------------------------------------------------------
		# set the output values
		self.node_rest 	= node_rest
		self.node_con 	= node_con 
		self.node_hook 	= node_hook
		
		
def zCon_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true

	oArgs = oCmd.Arguments
	oArgs.Add('con_type', c.siArgumentInput, 'box', c.siUInt)
	oArgs.Add('con_name', c.siArgumentInput, 'zCon', c.siString)
	# oArgs.AddWithHandler('parent', c.siArgHandlerSingleObj)
	
	return true

def zCon_Execute(con_type, con_name):

	# set the parent if missing #
	import win32com.server
	return win32com.server.util.wrap(
		zCon(con_type, con_name)
	)

#-----------------------------------------------------------------------------

def zConGUI_Init(ctxt):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true
	return true

def zConGUI_Execute():

	# get or create the gui property #
	prop = xsi.ActiveSceneRoot.Properties('zConGUI')
	if not prop:
		prop = xsi.ActiveSceneRoot.AddProperty('zConGUI')
		
	# if we have a selection, store the first item as the transform #
	if xsi.selection.Count:
		prop.Transform.Value = xsi.Selection(0).FullName
		
	# show the ppg #
	xsi.InspectObj(prop, '', '', c.siLockAndForceNew)
	
#-----------------------------------------------------------------------------
# Property
#-----------------------------------------------------------------------------
def zConGUI_Define(ctxt):
	prop = ctxt.Source
	
	prop.AddParameter2('Size', c.siFloat, 1, 0.001, 1000000, 0.001, 20.0, c.siClassifUnknown, c.siPersistable, '', False, False)
	prop.AddParameter3('ConType', c.siString, 'round_box', None, None, False) 
	prop.AddParameter3('ConName', c.siString, 'zCon') 
	prop.AddParameter3('Transform', c.siString, '') 
	prop.AddParameter3('Symmetry', c.siString, 'M') 
	prop.AddParameter3('ConR', c.siDouble, 0.25, None, None, False)
	prop.AddParameter3('ConG', c.siDouble, 0.25, None, None, False)
	prop.AddParameter3('ConB', c.siDouble, 0.5, None, None, False)

	prop.AddParameter3('RotOrder', c.siString, 'xyz', None, None, False)
	
	prop.AddParameter3('TransformSetup', c.siBool, False, None, None, False)
	prop.AddParameter3('TsTool', c.siUInt2, 1, 0, 10, False, True)
	prop.AddParameter3('TsTranslate', c.siString, 'local', 0, 10, False, True)
	prop.AddParameter3('TsRotate', c.siString, 'parent', 0, 10, False, True)
	prop.AddParameter3('TsAxisX', c.siBool, True, None, None, False, True)
	prop.AddParameter3('TsAxisY', c.siBool, True, None, None, False, True)
	prop.AddParameter3('TsAxisZ', c.siBool, True, None, None, False, True)
	
def zConGUI_DefineLayout(ctxt):
	lo = ctxt.Source
	lo.Clear()
	
	# build the available control list from the point dictionary #
	enum_type = []
	for key in point_dict.keys():
		name = key[0].upper() + key[1:]
		name = name.replace('_', ' ')
		enum_type.append(name)
		enum_type.append(key)

	# build a symmetry list #
	enum_sym = [
		'Middle', 'M',
		'Left', 'L',
		'Right', 'R',
		'Front', 'F',
		'Back', 'B',
		'Top', 'Tp',
		'Bottom', 'Bt'
	]

	lo.AddTab('zCon')
	
	lo.AddGroup('Controller Name')
	lo.AddItem('ConName', 'Name')
	lo.AddEnumControl('Symmetry', enum_sym, 'Symmetry', c.siControlCombo)
	lo.EndGroup()
	
	lo.AddGroup('Details')
	lo.AddEnumControl('ConType', enum_type, 'Controller Type', c.siControlCombo)
	lo.AddItem('Size')
	enum_ro = [
		'XYZ', 'xyz',
		'XZY', 'xzy',
		'YXZ', 'yxz',
		'YZX', 'yzx',
		'ZXY', 'zxy',
		'ZYX', 'zyx'
	]
	lo.AddEnumControl('RotOrder', enum_ro, 'Rotation Order')
	lo.AddColor('ConR', 'Color', False)
	lo.EndGroup()
	
	lo.AddGroup('Alignment')
	lo.AddRow()
	lo.AddItem('Transform')
	lo.AddButton('UseSel', 'Use Selection')
	lo.EndRow()
	lo.EndGroup()
	
	lo.AddRow()
	lo.AddButton('Close', 'Close')
	lo.AddSpacer()
	lo.AddButton('Create', 'Create Con')
	lo.EndRow()
	
	lo.AddTab('Transform Setup')
	
	enum_pos = [
		'View',    'view',
		'Global',  'global',
		'Local',   'local',
		'Parent',  'parent',
		'Ref',     'ref',
		'Plane',   'plane'
	]
	enum_rot = [
		'View',    'view',
		'Global',  'global',
		'Local',   'local',
		'Add',     'add',
		'Ref',     'ref',
		'Plane',   'plane'
	]
	lo.AddGroup()
	lo.AddItem('TransformSetup', 'Add Transform Setup')
	lo.AddGroup('Tool to Recall')
	lo.AddEnumControl('TsTool', ['Translate', 4, 'Rotate', 3, 'Last', 1], 'Tool')
	lo.EndGroup()
	lo.AddGroup('Reference Mode')
	lo.AddEnumControl('TsRotate', enum_rot, 'Rotate')
	lo.AddEnumControl('TsTranslate', enum_pos, 'Translate')
	lo.EndGroup()

	lo.AddGroup('Axis')
	lo.AddRow()
	lo.AddItem('TsAxisX', 'X')
	lo.AddItem('TsAxisY', 'Y')
	lo.AddItem('TsAxisZ', 'Z')
	lo.EndRow()
	lo.EndGroup()

	lo.EndGroup()
	
def zConGUI_TransformSetup_OnChanged():
	prop = PPG.Inspected(0)
	UpdateGUI(prop)
	
def zConGUI_TsTool_OnChanged():
	prop = PPG.Inspected(0)
	UpdateGUI(prop)
	
def UpdateGUI(prop):
	# turn on the items #
	if prop.TransformSetup.Value:
		prop.TsTool.ReadOnly = False
		
		# rotate #
		if prop.TsTool.Value == 3:
			prop.TsRotate.ReadOnly 		= False
			prop.TsTranslate.ReadOnly 	= True
			prop.TsAxisX.ReadOnly		= False
			prop.TsAxisY.ReadOnly		= False
			prop.TsAxisZ.ReadOnly		= False
			
		# translate #
		elif prop.TsTool.Value == 4:
			prop.TsRotate.ReadOnly 		= True
			prop.TsTranslate.ReadOnly 	= False
			prop.TsAxisX.ReadOnly		= False
			prop.TsAxisY.ReadOnly		= False
			prop.TsAxisZ.ReadOnly		= False
			
		# last #
		elif prop.TsTool.Value == 1:
			prop.TsRotate.ReadOnly 		= True
			prop.TsTranslate.ReadOnly 	= True
			prop.TsAxisX.ReadOnly		= True
			prop.TsAxisY.ReadOnly		= True
			prop.TsAxisZ.ReadOnly		= True
		
	# add is off #
	else:
		prop.TsTool.ReadOnly 		= True
		prop.TsRotate.ReadOnly 		= True
		prop.TsTranslate.ReadOnly 	= True
		prop.TsAxisX.ReadOnly		= True
		prop.TsAxisY.ReadOnly		= True
		prop.TsAxisZ.ReadOnly		= True
		
	# refresh the ppg #
	# PPG.Refresh()
	
def zConGUI_Close_OnClicked():
	PPG.Close()

def zConGUI_Create_OnClicked():
	prop = PPG.Inspected(0)
	prop = dispatch(prop)
	
	# create the con #
	con = xsi.zCon(prop.ConType.Value)
	con.basename	= prop.ConName.Value
	con.symmetry	= prop.Symmetry.Value
	con.size		= prop.Size.Value
	con.red			= prop.ConR.Value
	con.green		= prop.ConG.Value
	con.blue		= prop.ConB.Value
	
	# get the transform #
	if prop.Transform.Value:
		con.transform = xsi.ActiveSceneRoot.FindChild(prop.Transform.Value).Kinematics.Global.Transform
		
	# get the rotation order #
	con.rotation_order = prop.RotOrder.Value
	
	# draw the con #
	con.Draw()

	# add the transform setup #
	if prop.TransformSetup.Value:
		# last mode #
		if prop.TsTool.Value == 1:
			con.AddTransformSetupLast()
		# rotate #
		elif prop.TsTool.Value == 3:
			con.AddTransformSetupRot(
				prop.TsRotate.Value,
				prop.TsAxisX.Value,
				prop.TsAxisY.Value,
				prop.TsAxisZ.Value
			)
		# translate #
		elif prop.TsTool.Value == 4:
			con.AddTransformSetupPos(
				prop.TsTranslate.Value,
				prop.TsAxisX.Value,
				prop.TsAxisY.Value,
				prop.TsAxisZ.Value
			)


def zConGUI_UseSel_OnClicked():
	prop = PPG.Inspected(0)
	prop = dispatch(prop)
	
	prop.Transform.Value = xsi.Selection(0).FullName
