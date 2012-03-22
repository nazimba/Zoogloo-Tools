'''
XSI Plugin to add and env node to a seleted item.

>>> Application.zAddEnvNode()
'''

try:
	import win32com.client
	from win32com.client import constants
	from win32com.client import constants as c
	from win32com.client.dynamic import Dispatch as dispatch

	xsi = Application
	log = xsi.logmessage
except:
	pass

null = None
false = 0
true = 1

def XSILoadPlugin( in_reg ):
	in_reg.Author = "andy"
	in_reg.Name = "zAddEnvNode"
	in_reg.Email = ""
	in_reg.URL = ""
	in_reg.Major = 1
	in_reg.Minor = 0

	in_reg.RegisterCommand("zAddEnvNode","zAddEnvNode")
	#RegistrationInsertionPoint - do not remove this line

	return true

def XSIUnloadPlugin( in_reg ):
	strPluginName = in_reg.Name
	Application.LogMessage(str(strPluginName) + str(" has been unloaded."),constants.siVerbose)
	return true

def zAddEnvNode_Init( in_ctxt ):
	oCmd = in_ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true

	return true

def zAddEnvNode_Execute():

	# make sure something is selected #
	if not xsi.selection:
		log('Nothing Selected.', c.siError)
		
	# step through each item #
	for item in xsi.selection:
		
		# generate the new name #
		split = item.name.split('_')
		envName = ''
		dynName = ''
		jglName = ''
		for s in xrange(len(split)):
			if s == len(split)-1:
				dynName += 'DfmPrnt'  # move to preferences
				jglName += 'DfmShdw'  # move to preferences
				envName += 'Env'  # move to preferences
			else:
				dynName += '%s_' % split[s]
				jglName += '%s_' % split[s]
				envName += '%s_' % split[s]
		log('Adding Env/Dynamic Stack to node "%s"' % (item))
		
		# create a node #
		dyn = xsi.ActiveSceneRoot.AddNull(dynName)
		jgl = dyn.AddNull(jglName)
		env = jgl.AddNull(envName)
		# match transform #
		dyn.kinematics.Global.Transform = item.kinematics.Global.Transform
		jgl.kinematics.Global.Transform = item.kinematics.Global.Transform
		env.kinematics.Global.Transform = item.kinematics.Global.Transform
		# constrain #
		dyn.kinematics.AddConstraint('Pose', item, False)
		# change the display #
		dyn.primary_icon.Value = 0
		dyn.Properties('Visibility').Parameters('viewvis').Value = False
		dyn.Properties('Visibility').Parameters('rendvis').Value = False
		jgl.primary_icon.Value = 0
		jgl.Properties('Visibility').Parameters('viewvis').Value = False
		jgl.Properties('Visibility').Parameters('rendvis').Value = False
		env.primary_icon.Value = 0
		env.Properties('Visibility').Parameters('viewvis').Value = False
		env.Properties('Visibility').Parameters('rendvis').Value = False

	# return the env #
	return [dyn,jgl,env]

