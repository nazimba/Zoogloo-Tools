'''
Envelope To Maya

XSI Plugin to extract xsi envelope weights to a maya mel file.  

The reulting mel code can be run inside maya as 'source "<output_filename>.mel";'

Copyright 2006 Zoogloo LLC. All rights reserved.
This plugin is provided AS IS and WITHOUT WARRANTY
'''
import win32com.client
import win32com
from win32com.client import constants
from win32com.client import constants as c

xsi = Application

null = None
false = 0
true = 1

def XSILoadPlugin( in_reg ):
	in_reg.Author = "Andy Buecker"
	in_reg.Name = "Envelope To Maya"
	in_reg.Email = "andy@zoogloo.net"
	in_reg.URL = ""
	in_reg.Major = 1
	in_reg.Minor = 0

	
	# in_reg.RegisterCommand("EnvelopeToMel","EnvToMel")
	# in_reg.RegisterCommand("Envelope To Mel","EnvToMelGUI")
	
	xsi.logmessage( "\n------------------------------------------\n  Envelope to Maya Plugin for XSI.\n  Copyright 2006 Zoogloo LLC.\n  All rights Reserved.\n------------------------------------------\n" )
	
	#RegistrationInsertionPoint - do not remove this line

	return true

def XSIUnloadPlugin( in_reg ):
	strPluginName = in_reg.Name
	Application.LogMessage(str(strPluginName) + str(" has been unloaded."))
	return true

def EnvelopeToMel_Init( ctxt ):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true

	oArgs = oCmd.Arguments
	oArgs.Add("filename",constants.siArgumentInput)
	oArgs.Add("appendEnv",constants.siArgumentInput, True, c.siBool )
	return true

def EnvelopeToMel_Execute( filename, appendEnv ):

	Application.LogMessage("EnvToMaya_Execute called")

	# get only geometry from selection #
	col_geo = win32com.client.Dispatch( 'XSI.Collection' )
	for item in xsi.selection:
		xsi.logmessage( item.type )
		
		if item.type == 'polymsh' or item.type == 'surfmsh':
		
			if item.Envelopes.Count: col_geo.Add( item )
	
	xsi.logmessage( 'Found: %s' % col_geo.Count )
	
	# open a file handle #
	from string import join
	file = open( filename, "w" )
	file.write( 'while( true ) {\n' )
	
	# step through the geo #
	env_dict = {}
	for obj in col_geo:
	
		# create a string list of deformer names #
		def_list = []
		
		# initialize a progress bar #
		pb = XSIUIToolkit.ProgressBar
		pb.Maximum = obj.Envelopes(0).Deformers.Count
		pb.Step = 1
		pb.Caption = 'Envelope: %s' % obj.name
		if xsi.Interactive: pb.Visible = True
		
		# step through each envelope on each object #
		xsi.logmessage( obj.name )
		for env in obj.Envelopes:
		
			# create a list string percentages #
			perc_list = []
			
			# step through each deformer #
			for dfm in env.Deformers:
			
				# skip over effectors #
				if dfm.type == 'eff': continue
				
				# append the deformer name to the def_list #
				if appendEnv:
					def_list.append( dfm.name + "ENV" )
				else:
					def_list.append( dfm.name )
				
			# write the skincluster and deformers to disk #
			file.write( 'if ( `objExists "%s"` ) {\n' % obj.name )
			file.write( 'string $skin[]=`skinCluster -ibp -tsb "%s" "%s"`;\n' % ( join( def_list, '" "' ), obj.name ) )
			file.write( 'progressWindow -title "Importing Envelope: %s" -progress 0 -maxValue %s -status "Removing All Weights" -isInterruptable true;\n' % ( obj.Name, len( def_list ) ) )
		
			# zero all the weights in Maya #
			for df in def_list:
				file.write( 'skinPercent -normalize false -tv "%s" 0 $skin[0] "%s.vtx[0:%s]";\n' % ( df, obj.name, obj.ActivePrimitive.Geometry.Points.Count-1 ) )
				
			
			#
			pb.Maximum = len( def_list )
			
			# step through each deformer again #
			for dfm in env.Deformers:
			
				# skip over effectors #
				if dfm.type == 'eff': continue
				
				# increment the progressbar #
				if pb.CancelPressed: return
				pb.StatusText = '%s : Deformer' % dfm.name
				pb.Increment()
				
				# incremente the Maya progress bar #
				file.write( "if ( `progressWindow -q -ic` ) break;\n" )
				file.write( 'progressWindow -e -step 1 -status "Deformer: %s";\n' % dfm.name )
				
				# get the weights for the deformer #
				weights = env.GetDeformerWeights( dfm )
				
				# step through the weights and write to disk #
				for w in range( len( weights ) ):
					if weights[w] != 0:
						if appendEnv:
							file.write(
								'skinPercent -normalize false -transformValue "%(joint)s" %(value)s $skin[0] "%(obj)s.vtx[%(cv)s]";\n' % {
									"joint": dfm.name + "ENV",
									"value" : weights[w]/100,
									"obj": obj.name,
									"cv": w
									}
								)
						else:
							file.write(
								'skinPercent -normalize false -transformValue "%(joint)s" %(value)s $skin[0] "%(obj)s.vtx[%(cv)s]";\n' % {
									"joint": dfm.name,
									"value" : weights[w]/100,
									"obj": obj.name,
									"cv": w
									}
								)
							
			file.write( '}\n')
			
		# cleanup the Maya progress window #
		file.write( 'progressWindow -endProgress;\n' )
		
	# close the file handle #
	file.write( 'break;\n' )
	file.write( '}\n' )
	file.write( 'progressWindow -endProgress;\n' )
	file.close()
		
	return true

def EnvelopeToMelGUI_Init( ctxt ):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true

	return true

def EnvelopeToMelGUI_Execute( ):

	#
	if not Application.Interactive:
		xsi.logmessage( 'XSI is not interactive.  Unable to use GUI', c.siError )
		return
		
	# get a file browser #
	fb = XSIUIToolkit.FileBrowser
	fb.DialogTitle = "Export Envelope To Mel"
	fb.FileBaseName = "envelope"
	fb.Filter = "Mel (*.mel)|*.mel|All Files (*.*)|*.*||"
	
	fb.ShowSave()
	
	if not fb.FilePathName: 
		xsi.logmessage( 'No filename selected.', c.siWarning )
		return

	xsi.logmessage( "Exporting Env to: %s" % fb.FilePathName )		
	xsi.EnvToMel( fb.FilePathName )
	#xsi.EnvToMel( fb.FilePathName, False )
	
	return true
