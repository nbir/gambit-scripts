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
import numpy as np
import lib.geo as geo
import lib.PiP_Edge as pip
import matplotlib.pyplot as plt

from pprint import pprint

import settings as my
sys.path.insert(0, os.path.abspath('..'))


_load_nhoodIDs = lambda: [int(nid) for nid in anyjson.loads(
				open('data/' + my.DATA_FOLDER + 'hood_ids.txt', 'rb').read())]

_load_nhood_names = lambda: dict((int(loc['id']), str(loc['name'])) for loc in anyjson.loads(
				open('data/' + my.DATA_FOLDER + 'loc_data.json', 'rb').read()))

#
# RIVAL / NONRIVAL VISIT SETS
#

def calc_rnr_visits():
	'''Calculate rival vs. non-rival visits'''
	rivalry_mat 			= _load_matrix('', 'rivalry_mat')
	activity_mat 			= _load_matrix('activity/', 'activity_mat')
	activity_mat__dist_norm = _load_matrix('activity/', 'activity_mat__dist_norm')
	activity_mat__dtf_norm 	= _load_matrix('activity/', 'activity_mat__dtf_norm')
	activity_mat__din_norm 	= _load_matrix('activity/', 'activity_mat__din_norm')
	activity_mat__dtfin_norm= _load_matrix('activity/', 'activity_mat__dtfin_norm')

	visit_mat 				= _load_matrix('visits/', 'visit_mat')
	visit_mat__dist_norm 	= _load_matrix('visits/', 'visit_mat__dist_norm')
	visit_mat__dtf_norm 	= _load_matrix('visits/', 'visit_mat__dtf_norm')
	visit_mat__din_norm 	= _load_matrix('visits/', 'visit_mat__din_norm')
	visit_mat__dtfin_norm 	= _load_matrix('visits/', 'visit_mat__dtfin_norm')
	
	visitor_mat 			= _load_matrix('visitors/', 'visitor_mat')
	ids = _trim_user_list()

	order = _calc_rnr_visits(visit_mat, rivalry_mat, ids=ids, file_name='visits')
	_calc_rnr_visits(visit_mat__dist_norm, rivalry_mat, ids=ids, order=order, file_name='visits__dist_norm')
	_calc_rnr_visits(visit_mat__dtf_norm, rivalry_mat, ids=ids, order=order, file_name='visits__dtf_norm')
	_calc_rnr_visits(visit_mat__din_norm, rivalry_mat, ids=ids, order=order, file_name='visits__din_norm')
	_calc_rnr_visits(visit_mat__dtfin_norm, rivalry_mat, ids=ids, order=order, file_name='visits__dtfin_norm')

	_calc_rnr_visits(activity_mat, rivalry_mat, ids=ids, order=order, file_name='activity')
	_calc_rnr_visits(activity_mat__dist_norm, rivalry_mat, ids=ids, order=order, file_name='activity__dist_norm')
	_calc_rnr_visits(activity_mat__dtf_norm, rivalry_mat, ids=ids, order=order, file_name='activity__dtf_norm')#
	_calc_rnr_visits(activity_mat__din_norm, rivalry_mat, ids=ids, order=order, file_name='activity__din_norm')#
	_calc_rnr_visits(activity_mat__dtfin_norm, rivalry_mat, ids=ids, order=order, file_name='activity__dtfin_norm')#
	
	order = _calc_rnr_visits(visitor_mat, rivalry_mat, ids=ids, order=order, file_name='visitors')

def _trim_user_list():
	'''Trim nhood id list for min # of users & min # of tweet'''
	ids  = _load_nhoodIDs()
	ids_ = _load_nhoodIDs()
	visitor_mat = _load_matrix('visitors/', 'visitor_mat')
	for from_id in ids:
		visitors = max(visitor_mat[from_id].values())
		if visitors < my.MIN_USERS:
			ids_.remove(from_id)

	ids = [i for i in ids_]
	activity_mat = _load_matrix('activity/', 'activity_mat')
	for from_id in ids:
		activity = sum(activity_mat[from_id].values()) - activity_mat[from_id][from_id]
		if activity < my.MIN_TWEETS:
			ids_.remove(from_id)
		
	return ids_

def _calc_rnr_visits(visit_mat, rivalry_mat, ids=None, order=None, file_name='dummy'):
	visits = {}
	visit_fracs = {}
	if not ids:
		ids = _load_nhoodIDs()
	for from_id in ids:
		tot_visits = sum(visit_mat[from_id].values()) - visit_mat[from_id][from_id]
		if tot_visits != 0:
			visits[from_id] = [0, 0]			# [0:non-rival, 1:rival]
			visit_fracs[from_id] = [0.0, 0.0]
			for to_id in [to_id for to_id in _load_nhoodIDs() if to_id != from_id]:
				if rivalry_mat[from_id][to_id] == 0:
					visits[from_id][0] += visit_mat[from_id][to_id]
					visit_fracs[from_id][0] += round(visit_mat[from_id][to_id] / float(tot_visits), 4)
				else:
					visits[from_id][1] += visit_mat[from_id][to_id]
					visit_fracs[from_id][1] += round(visit_mat[from_id][to_id] / float(tot_visits), 4) 

	if order:
		visit_fracs = [(i, visit_fracs[i]) for i in order]
	else:
		visit_fracs = sorted(visit_fracs.items(), key=lambda a: a[1][1], reverse=True)
	ids = [tup[0] for tup in visit_fracs]
	nrs	= [tup[1][0] for tup in visit_fracs]
	rs	= [tup[1][1] for tup in visit_fracs]

	# Plot bars
	fig    = plt.figure(figsize=(8,5))
	ax     = fig.add_subplot(111)
	plt.subplots_adjust(left=0.075, right=0.96, top=0.92, bottom=0.3)
	ax.set_ylim([0,1])
	ax.set_xlim([0,len(ids)*3])
	width  = 2.4
	ind    = np.arange(0, len(ids)*3, 3)
	bar_r  = plt.bar(ind, rs, width, color='#FA71AF', edgecolor='#FA71AF', alpha=0.75)
	bar_nr = plt.bar(ind, nrs, width, color='#377EB8', edgecolor='#377EB8', alpha=0.75, bottom=rs)
	loc_n  = _load_nhood_names()
	labels = [loc_n[i].strip().replace('Street', 'St.') for i in ids]
	ax.set_xticks(ind + width/2)
	ax.set_xticklabels(labels, rotation='vertical', fontsize=11)
	title  = file_name.replace('_', ' ').upper()
	ax.set_title(title, fontsize=11)

	# Attach absolute counts
	for i in range(len(bar_r)):
		br  = bar_r[i]
		height = br.get_height()
		ax.text(br.get_x() + br.get_width()/2., height-0.02, str(int(visits[ids[i]][1])) if visits[ids[i]][1] != 0 else '',
			ha='left', va='top', rotation='vertical', fontsize=10)
		ax.text(br.get_x() + br.get_width()/2., height+0.02, str(int(visits[ids[i]][0])) if visits[ids[i]][0] != 0 else '',
			ha='right', va='bottom', rotation='vertical', fontsize=10)

	if not os.path.exists('data/' + my.DATA_FOLDER + 'rnr_plots/'):
		os.makedirs('data/' + my.DATA_FOLDER + 'rnr_plots/')
	plt.savefig('data/' + my.DATA_FOLDER + 'rnr_plots/' + file_name + '.png')
	print 'Stored chart: %s' % file_name

	return ids 	# ordering

def _load_matrix(folder, file_name):
	if os.path.exists('data/' + my.DATA_FOLDER + folder + file_name + '.pickle'):
		with open('data/' + my.DATA_FOLDER  + folder + file_name + '.pickle', 'rb') as fp1:
			visit_mat = pickle.load(fp1)
		return visit_mat
	else:
		return None


def _show_matrix(mat):
	line_str = '%5s |' + ' %5s' * (len(mat))
	print '\n' + '_'*7 + '______' * (len(mat))
	print line_str % tuple(['A->B'] + mat.keys())
	print '_'*7 + '______' * (len(mat))
	for nid in mat:
		x = [nid]
		vals = [str(val)[0:5] for val in mat[nid].values()]
		x.extend(vals)
		print line_str % tuple(x)
	print '_'*7 + '______' * (len(mat))