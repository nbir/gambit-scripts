# Gambit scripts
#
# Copyright (C) USC Information Sciences Institute
# Author: Nibir Bora <nbora@usc.edu>
# URL: <http://cbg.isi.edu/>
# For license information, see LICENSE


import sys
import os
sys.path.insert(0, os.path.abspath('..'))
import settings as my

import csv
import anyjson
import lib.geo as geo
import lib.PiP_Edge as pip

import bin.load_fun as load
import bin.prep_fun as prep
import bin.calc_fun as calc


def lists_print(lists):
	lens = []
	for row in lists:
		for i in range(0, len(row)):
			lens[i] = 0 if i not in lens
			lens[i] = len(str(row[i])) if len(str(row[i])) > lens[i] else lens[i]

	fs = ''
	for el in lens:
		fs += '%s'
	for row in lists:
		print 
