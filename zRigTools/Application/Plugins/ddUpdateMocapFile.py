#!/usr/bin/env python
# encoding: utf-8
"""
ddUpdateMocapFile.py

Created by andy on 2008-05-01.
Copyright (c) 2008 Zoogloo LLC. All rights reserved.
"""

import sys
import os
import re

# FILE_IN_NAME = '/Users/andy/Documents/work/Clients/D2/tcats/fromDD/Digi27_04-28-08/xsi/tcats_ref_Lionorun_d1_t1_Liono.xsi'
FILE_IN_NAME = '/Users/andy/Documents/work/Clients/D2/tcats/fromDD/Digi27_04-28-08/xsi/tcats_sc035X2_RW_d1_t1_Liono.2.xsi'
# FILE_OUT_NAME = '/Users/andy/Documents/work/Clients/D2/tcats/fromDD/Digi27_04-28-08/xsi/tcats_ref_Lionorun_d1_t1_Liono.Updated.xsi'
FILE_OUT_NAME = '/Users/andy/Documents/work/Clients/D2/tcats/fromDD/Digi27_04-28-08/xsi/sc035X2_01_liono_mocap_raw_v001.2.xsi'
def main():
	# make sure the file exists #
	if not os.path.exists(FILE_IN_NAME):
		print 'File doesn\'t exist:' + FILE_IN_NAME
		sys.exit(-1)
	# get the file handlers #
	fhi = open(FILE_IN_NAME, 'r')
	fho = open(FILE_OUT_NAME, 'w')
	
	# step through the lines #
	for line in fhi:
		fho.write(re.subn('Pelvis_M_Bone.kine.local.pos', 'Pelvis_M_Chain.kine.local.pos', line)[0])

	fhi.close()
	fho.close()
	

if __name__ == '__main__':
	main()

