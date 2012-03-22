'''
XSI Plugin containing various enveloping tools: EnvToMelGUI, SwapDeformer, NormalizeEnvelope.
'''
import win32com.client
import win32com
from win32com.client import constants
from win32com.client import constants as c

xsi = Application
dispatch = win32com.client.dynamic.Dispatch

null = None
false = 0
true = 1

def XSILoadPlugin( in_reg ):
	in_reg.Author = "andy"
	in_reg.Name = "EnvelopeTools"
	in_reg.Email = ""
	in_reg.URL = ""
	in_reg.Major = 1
	in_reg.Minor = 0

	
	in_reg.RegisterCommand("EnvToMel","EnvToMel")
	
	in_reg.RegisterCommand("EnvToMelGUI","EnvToMelGUI")
	
	in_reg.RegisterCommand("SwapDeformer","SwapDeformer")
	
	in_reg.RegisterCommand("NormalizeEnvelope","NormalizeEnvelope")
	
	# in_reg.RegisterMenu(c.siMenuMainTopLevelID, 'zgTools')
	#RegistrationInsertionPoint - do not remove this line

	return true
def zgTools_Init(ctxt):
	menu = ctxt.Source
	env = menu.AddItem('Envelope Tools', c.siMenuItemSubmenu)
	env = dispatch(env)
	env.AddCommandItem('Swap Deformer', 'SwapDeformer')
	env.AddCommandItem('Normalize', 'NormalizeEnvelope')
	env.AddCommandItem('Env To Mel', 'EnvToMelGUI')
	
def XSIUnloadPlugin( in_reg ):
	strPluginName = in_reg.Name
	Application.LogMessage(str(strPluginName) + str(" has been unloaded."))
	return true

def EnvToMel_Init( ctxt ):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true

	oArgs = oCmd.Arguments
	oArgs.Add("filename",constants.siArgumentInput)
	oArgs.Add("appendEnv",constants.siArgumentInput, True, c.siBool )
	return true

def EnvToMel_Execute( filename, appendEnv ):

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

def EnvToMelGUI_Init( ctxt ):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true

	return true

def EnvToMelGUI_Execute( ):

	#
	if not Application.Interactive:
		xsi.logmessage( 'XSI is not interactive.  Unable to use GUI', c.siError )
		return
		
	# get a file browser #
	fb = XSIUIToolkit.FileBrowser
	fb.DialogTitle = "Export Envelope To Mel"
	fb.InitialDirectory = "E:/Clients/GKR/HappyFeet/assets/BigRig/envelopes" 
	fb.FileBaseName = "envelope"
	fb.Filter = "Mel (*.mel)|*.mel|All Files (*.*)|*.*||"
	
	fb.ShowSave()
	
	if not fb.FilePathName: 
		xsi.logmessage( 'No filename selected.', c.siWarning )
		return

	xsi.logmessage( "Exporting Env to: %s" % fb.FilePathName )		
	#xsi.EnvToMel( fb.FilePathName )
	xsi.EnvToMel( fb.FilePathName, False )
	
	return true

def SwapDeformer_Init( ctxt ):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true

	return true

def SwapDeformer_Execute(  ):

	Application.LogMessage("SwapDeformer_Execute called")
	
	# make sure a mesh with an envelope is selected #
	if xsi.selection.Count == 0:
		xsi.logmessage( 'No Mesh Selected', c.siError )
		return False
	
	# create a collection to hold the envelopes #	
	env_col = win32com.client.Dispatch( 'XSI.Collection' )
	
	for obj in xsi.selection:
		if obj.Envelopes.Count != 0:
			env_col.Add( obj )

	xsi.logmessage( env_col.Count )
	
	if env_col.Count == 0:
		xsi.logmessage( 'No Meshes with Envelopes found.', c.siError )
		return False
	
	# pick the deformer to replace #
	pkr = xsi.PickElement( None, 'Pick Deformer to Replace' )
	
	# catch right clicks #
	if pkr[0] == 0:
		return False
	dfm_old = pkr[2]
	xsi.logmessage( 'Deformer Old: %s' % dfm_old.FullName )
	
	# otherwise make sure the deformer is part of the envelope #
	dfms = None
	for obj in env_col:
		dfms = obj.Envelopes(0).Deformers
		dfms_list = dfms.GetAsText().split(',')
		if not dfm_old.FullName in dfms_list:
			xsi.logmessage( 'Deformer %s not in envelope' % dfm_old.FullName, c.siError )
			return False
			
		
		#xsi.logmessage( `dfms_list` )
		
	# pick the new deformer #
	pkr = xsi.PickElement( None, 'Pick New Deformer' )
	
	# catch right clicks #
	if pkr[0] == 0:
		return False
	dfm_new = pkr[2]
		
	
	# step through each object in the env col #
	for obj in env_col:
	
		# get the envelope #
		env = obj.Envelopes(0)
		
		# get the deformers #
		dfms = env.Deformers
		
		# get a list of all the weights #
		all_weights = env.Weights.Array
		
		# get the old and new deformer id #
		dfmOldID = None
		dfmNewID = None
		xsi.logmessage( 'TEst: %s == %s' %  (dfm_old.FullName, xsi.PyFix( dfms(0) ).FullName ) )
		for i in xrange( dfms.Count ):
			# stop if we've found both id's #
			if dfmOldID and dfmNewID: break
			
			# fix the dispatch #
			defObj = xsi.PyFix( dfms(i) )
			#xsi.logmessage( '> %s == %s ? %s' % ( dfm_old.FullName, defObj.FullName, dfm_old.FullName == defObj.FullName ) )
			if dfm_old.FullName == defObj.FullName: dfmOldID = i
			if dfm_new.FullName == defObj.FullName: dfmNewID = i
			
		xsi.logmessage( 'oldID: %s' % dfmOldID )
		xsi.logmessage( 'newID: %s' % dfmNewID )

		# convert the weights into arrays and add them together #
		import numpy
		xsi.logmessage( '>>: %s' % len( all_weights ) )
		oldWeights = numpy.array( all_weights[ dfmOldID ] )
		newWeights = numpy.array( all_weights[ dfmNewID ] )
		addWeights = oldWeights + newWeights
		
		# convert the tuple to a list #
		newWeights = list( all_weights )
		
		# populate the cached weight array with the new values #
		newWeights[ dfmNewID ] = tuple( addWeights )
		newWeights[ dfmOldID ] = tuple( [0] * len( newWeights[0] ) )
			
		# reapply the weights #
		env.Weights.Array = newWeights
		
		# step through each point and copy the values #
		return
		
		# skip the deformer if it isn't in the deformer list #
		dfms_list = dfms.GetAsText().split(',')
		if not dfm_old.FullName in dfms_list:
			xsi.logmessage( 'Deformer %s not in envelope. Skipping' % dfm_old.FullName, c.siWarning )
			continue

	
		# get the weight list for the old deformer #
		weights = env.GetDeformerWeights( dfm_old )
		
		# get the old deformers color #
		color = env.GetDeformerColor( dfm_old )
		
		# remove weight on the olde deformer #
		zero_weights = [0] * len( weights )
	
		# set the weights of the new deformer #
		env.SetDeformerWeights( dfm_old, zero_weights )
		
		# remove the old deformer #
		Application.RemoveFlexEnvDeformer('%s;%s' % ( obj.FullName, dfm_old.FullName ), False)
		
		# add the new deformer to the envelope if it doesn't exist #
		if not dfm_new.FullName in dfms_list:
			xsi.ApplyFlexEnv('%s;%s' % ( obj.FullName, dfm_new.FullName ), 0, 0)
			
		# set the weights of the new deformer #
		env.SetDeformerWeights( dfm_new, list(weights) )
		
		# set the color for the new deformer #
		env.SetDeformerColor( dfm_new, color )
		
		
		
	
	return true

def NormalizeEnvelope_Init( ctxt ):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true

	return true

def NormalizeEnvelope_Execute(  ):

	Application.LogMessage("NormalizeEnvelope_Execute called")
	
	# step through selected objects #
	for obj in xsi.selection:
	
		xsi.logmessage( 'Normalizing: %s' % obj.Name )
		
		# step through envelopes on obj #
		for env in obj.Envelopes:
		
			dirty = False
			
			weights = list( env.Weights.Array )
			
#			xsi.logmessage( 'Transposing' )
			
			
			# covnert the weights to an array #
			import numpy
			pd = numpy.array( weights )
#			print pd.shape
			
			# transpose the array so it's by point first #
			pd = numpy.transpose( pd )
			
			# step through each point #
			for p in xrange( len(pd) ):
				
				# get the sum of the weights #
				total_orig = numpy.sum( pd[p] )				
				
				# normalize the row if it isn't #
				tol = float(0.002)
				import math
				if math.fabs( 100 - total_orig ) > tol:
#				if total_orig.round(6) != float(100):
				
					xsi.logmessage( 'Normalizing Point %s (%s)' % ( p, total_orig.round(6) ) )
				
					dirty = True
					
					# normalize the array - row * perc ratio #
					pd[p] = pd[p]*(100/total_orig)
			
			# retranspose the array back to by deformer #
			pd = numpy.transpose( pd )
#			print pd.shape
				
			# put the weights back on the object #
			if dirty:
				xsi.logmessage( '  .. Setting the envelope weights' )
				#env.Weights = numpy.zeros( (len(weights), len(weights[0])) ).tolist()
				
				for d in xrange( env.Deformers.Count ):
					dfm = win32com.client.dynamic.Dispatch( env.Deformers(d) )
					xsi.logmessage( ' Weighting Def: %s' % dfm.Name )
					try:
						env.SetDeformerWeights( dfm, pd[d] )
					except:
						xsi.logmessage( 'Unable to Set Weight for deformer: %s' % dfm.Name, c.siWarning )
			else:
				xsi.logmessage( '  ..All ready Normalized' )
	return true

