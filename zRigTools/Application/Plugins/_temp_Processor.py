#!/usr/bin/env python
# encoding: utf-8
"""
_temp_Processor.py

Created by andy on 2008-07-01.
Copyright (c) 2008 Zoogloo LLC. All rights reserved.
"""

import sys
import os


def main(test=True):
	import glob
	path = '/Volumes/show/tcats/xsi/liono_corrective/zPoseShapesV2_TY'
	# rename the directory #
	for zpshp in glob.glob(path + '/*_R.zpshp'):
		print zpshp
		# get the contents #
		from zPoseShapeContents import zPoseShapeContents
		ps = zPoseShapeContents(zpshp)
		ps.Load()
		import elementtree.ElementTree as ET
		xml = ET.parse(zpshp + '/' + ps.pose.file)
		for elem in xml.findall('/object'):
			import re
			if re.match(r'fing', elem.attrib['name'], re.I) or \
			re.match(r'thumb', elem.attrib['name'], re.I):
				old_name = elem.attrib['name']
				if re.match(r'.+_L_.+', elem.attrib['name']):
					elem.attrib['name'] = old_name.replace('_L_', '_R_')
				elif re.match(r'.+_R_.+', elem.attrib['name']):
					elem.attrib['name'] =  old_name.replace('_R_', '_L_')
				print '%s -> %s' % (old_name, elem.attrib['name'])
		
		# rename #
		os.unlink(zpshp + '/' + ps.pose.file)
		xml.write(zpshp + '/' + ps.pose.file.replace('_L', '_R'))
		ps.pose.file = ps.pose.file.replace('_L', '_R')	
		ps.Save()
		# new_path = zpshp.replace(' copy', '').replace('_L', '_R')
		# print new_path
		# if not test: os.rename(zpshp, new_path)
		# 
		# # get the contents #
		# contents = zpshp + '/contents.xml'
		# from zPoseShapeContents import zPoseShapeContents
		# ps = zPoseShapeContents(zpshp)
		# ps.Load()
		# ps.UpdateInfo()
		# 
		# # rename the objs #
		# for obj in ps.objs.children:
		# 	old_obj = path + '/obj_orignal/' + obj.file
		# 	obj.file = obj.file.replace('_L', '_R')
		# 	if not test: os.rename(old_obj, path + '/obj_orignal/' + obj.file)
		# 	
		# # rename the pose #
		# old_pose = ps.pose.file
		# ps.pose.file = old_pose.replace('_L', '_R')
		# if not test:
		# 	os.rename(path + old_pose,)
		# 
		# # save the new contents #
		# if not test:
		# 	ps.Save()

if __name__ == '__main__':
	main()

