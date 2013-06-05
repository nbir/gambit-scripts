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
import pickle
import lib.geo as geo
import lib.PiP_Edge as pip

def find_rnr_links():
# Calculate rivalry & non-ivalry links with min tweet bounds
#		returns	rivalry_list:[[gang_id, gang_id, rival/nonrival],...]

	rivalry_list = {}
	with open('data/' + my.DATA_FOLDER  + 'pickle/' + 'visit_mat.pickle', 'rb') as fp1:
		visit_mat = pickle.load(fp1)

	for gang_id in my.HBK_GANG_AND_RIVAL_IDS:
		for rival_id in [to_id for to_id in my.HBK_GANG_ID_LIST if to_id != gang_id]:
			if visit_mat[gang_id][rival_id] >= my.MIN_VISITS_IN_LINK and str(gang_id)+str(rival_id) not in rivalry_list and str(rival_id)+str(gang_id) not in rivalry_list:
				this_row = [gang_id, rival_id]
				this_row.append('rival') if rival_id in my.HBK_GANG_AND_RIVAL_IDS[gang_id] else this_row.append('nonrival')
				rivalry_list[str(gang_id)+str(rival_id)] = this_row

	rivalry_list = rivalry_list.values()
	rivals = [row for row in rivalry_list if row[2] == 'rival']
	nonrivals = [row for row in rivalry_list if row[2] == 'nonrival']
	rivalry_list = rivals + nonrivals
	return rivalry_list
