# Gambit scripts
#
# Copyright (C) USC Information Sciences Institute
# Author: Nibir Bora <nbora@usc.edu>
# URL: <http://cbg.isi.edu/>
# For license information, see LICENSE

import os
import sys
import csv
import pickle
import anyjson
import lib.geo as geo
import lib.PiP_Edge as pip

from pprint import pprint

import settings as my
sys.path.insert(0, os.path.abspath('..'))


_load_nhoodIDs = lambda: [int(nid) for nid in anyjson.loads(
				open('data/' + my.DATA_FOLDER + 'hood_ids.txt', 'rb').read())]

#
# JSON - OUTPUT
#
def out_rivalry_mat():
	'''Save rivalry matrix in json format'''
	mat = {}
	for from_id in _load_nhoodIDs():
		mat[from_id] = dict((to_id, 0) for to_id in _load_nhoodIDs())
		for to_id in my.RIVALS[from_id]:
			mat[from_id][to_id] = 1

	with open('data/' + my.DATA_FOLDER  + 'rivalry_mat' + '.pickle', 'wb') as fp1:
		pickle.dump(mat, fp1)
	with open('data/' + my.DATA_FOLDER  + 'rivalry_mat' + '.json', 'wb') as fp1:
		fp1.write(anyjson.dumps(mat))


