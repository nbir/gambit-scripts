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
import psycopg2
import matplotlib
import numpy as np
import lib.geo as geo
import matplotlib.pyplot as plt

from math import *
from pylab import *
from pprint import pprint
from matplotlib.collections import PolyCollection

import settings as my
sys.path.insert(0, os.path.abspath('..'))


def calc_featAndPlot(folder='visits', file_name='visit_mat'):
# Calculate features for each neighborhoods
# and plot rankings
	hood_ids = _load_nhoodIDs()
	hood_info = _load_hoodInfo()
	visit_mat = _load_visitMat(folder, file_name)
	visit_mat_frac = _calc_visitMatFrac(visit_mat)

	# Calculate each feature
	OUTFLOW_INFLOW = dict([(h_id, _calc_inflowVsOutflow(h_id, visit_mat_frac)) for h_id in hood_ids])
	IN_DENSITY = dict([(h_id, _calc_inDensity(h_id, visit_mat_frac)) for h_id in hood_ids])
	OUT_DENSITY = dict([(h_id, _calc_outDensity(h_id, visit_mat_frac)) for h_id in hood_ids])
	POPULARITY = dict([(h_id, _calc_Popularity(h_id, visit_mat_frac)) for h_id in hood_ids])
	ENTROPY_OUT = dict([(h_id, _calc_EntropyOut(h_id, visit_mat_frac)) for h_id in hood_ids])
	ENTROPY_OUT_ALL = dict([(h_id, _calc_EntropyOutAll(h_id, visit_mat_frac)) for h_id in hood_ids])
	ENTROPY_IN = dict([(h_id, _calc_EntropyIn(h_id, visit_mat_frac)) for h_id in hood_ids])
	ENTROPY_IN_ALL = dict([(h_id, _calc_EntropyInAll(h_id, visit_mat_frac)) for h_id in hood_ids])

	# Initialize features for plot
	features = {'OUTFLOW_INFLOW' : OUTFLOW_INFLOW,
	'IN_DENSITY' : IN_DENSITY,
	'OUT_DENSITY' : OUT_DENSITY,
	'POPULARITY' : POPULARITY,
	'ENTROPY_OUT' : ENTROPY_OUT,
	'ENTROPY_OUT_ALL' : ENTROPY_OUT_ALL,
	'ENTROPY_IN' : ENTROPY_IN,
	'ENTROPY_IN_ALL' : ENTROPY_IN_ALL}

	with open('data/' + my.DATA_FOLDER  + 'features_' + folder + '.pickle', 'wb') as fp1:
		pickle.dump(features, fp1)

	feature_names = ['OUTFLOW_INFLOW', 'IN_DENSITY', 'OUT_DENSITY', 'POPULARITY', 'ENTROPY_OUT', 'ENTROPY_OUT_ALL', 'ENTROPY_IN', 'ENTROPY_IN_ALL']
	colors = ["#4DAF4A","#3B3B3B","#984EA3","#E41A1C","#A65628","#FA71AF","#FF7F00","#377EB8"]

	# Plot all feature ranks
	'''width = 6
	ind = np.arange(len(hood_ids)) * 10
	count = 0
	fig = plt.figure(figsize=(len(features)*2.5, len(hood_ids)*0.75))
	plt.subplots_adjust(left=0.02, right=0.96, top=0.88, bottom=0.02)

	for name in feature_names:
		x = [hood_info[h_id]['name'] for h_id in sorted(features[name], key=features[name].get)]
		y = [features[name][h_id] for h_id in sorted(features[name], key=features[name].get)]
		count += 2
		color = colors.pop()

		ax = fig.add_subplot(1, len(features)*2, count)
		ax.set_yticks(ind+(width/2))
		plt.setp(ax, xticklabels=[])
		plt.setp(ax, yticklabels=_conv_SplitLabels(x))
		#ax.tick_params(axis='x', labelsize=10)
		ax.barh(ind, y, width, color=color, alpha=0.75, edgecolor=color)
		ax.set_title(name + '\n\n')

	fig.suptitle('Neighborhood ranks: ' + folder.upper() + ' (' + my.DATA_FOLDER[:-1].upper() + ')', fontsize=18)
	plt.savefig('data/' + my.DATA_FOLDER + folder + '/' + 'hood_ranks__' + my.DATA_FOLDER[:-1] + '.png')
	'''

	# Plot map: polygons init
	pols = []
	pol_seq = []
	for h_id in hood_info:
		pol = hood_info[h_id]['polygon'][:-1]
		pol = [[ll[1], ll[0]] for ll in pol]
		pols.append(pol)
		pol_seq.append(h_id)
	lngs = [ll[0] for ll in pol for pol in pols]
	lats = [ll[1] for ll in pol for pol in pols]
	#print max(lngs), min(lngs), max(lats), min(lats)
	## MIGHT NEED TO SWAP x_dist and y_dist
	y_dist = geo.distance(geo.xyz(max(lats), max(lngs)), geo.xyz(max(lats), min(lngs)))
	x_dist = geo.distance(geo.xyz(max(lats), max(lngs)), geo.xyz(min(lats), max(lngs)))
	#print x_dist, y_dist

	# Plot map: each feature
	fig = plt.figure(figsize=(2 * 6, 4 * y_dist * 6/x_dist))
	plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
	count = 0
	for name in feature_names:
		count += 1
		#x = [hood_info[h_id]['name'] for h_id in sorted(features[name], key=features[name].get)]
		#y = [features[name][h_id] for h_id in sorted(features[name], key=features[name].get)]
		heat = np.array([features[name][h_id] for h_id in pol_seq])

		#fig = plt.figure(figsize=(6, y_dist * 6/x_dist))
		ax = fig.add_subplot(4, 2, count, aspect='equal') 
		#ax = fig.add_subplot(4, 2, count, aspect=y_dist/x_dist) 
		coll = PolyCollection(pols, array=heat, cmap=mpl.cm.OrRd, edgecolors='k', alpha=0.75)
		## mpl.cm.datad for list of colormaps
		ax.add_collection(coll)
		ax.autoscale_view()
		ax.get_xaxis().set_ticklabels([])
		ax.get_yaxis().set_ticklabels([])
		fig.colorbar(coll, ax=ax)
		#ax.set_title(my.DATA_FOLDER[:-1].upper() + '(' + folder.upper() + '): ' + name)
		ax.set_title(name)
	
	fig.suptitle('Neighborhood ranks: ' + folder.upper() + ' (' + my.DATA_FOLDER[:-1].upper() + ')', fontsize=18)
	plt.savefig('data/' + my.DATA_FOLDER + folder + '/' + 'hood_rank_map__' + my.DATA_FOLDER[:-1] + '.png')


#
# LOAD functions
#
_load_nhoodIDs = lambda: [int(nid) for nid in anyjson.loads(open('data/' + my.DATA_FOLDER + 'hood_ids.txt', 'rb').read())]
_load_hoodInfo = lambda: dict([(int(loc['id']), loc) for loc in anyjson.loads(open('data/' + my.DATA_FOLDER + 'loc_data.json', 'rb').read())])
_load_visitMat = lambda folder, file_name: pickle.load(open('data/' + my.DATA_FOLDER  + folder + '/' + file_name + '.pickle', 'rb'))

_calc_visitMatFrac = lambda visit_mat: dict([(from_id, dict([(to_id, visit_mat[from_id][to_id] / float(sum(visit_mat[from_id].values()))) \
					if sum(visit_mat[from_id].values()) != 0 else (to_id, 0) for to_id in visit_mat[from_id]])) for from_id in visit_mat])


#
# CALC FEATURES
#
_calc_inflowVsOutflow = lambda h_id, visit_mat: sum([visit_mat[from_id][h_id] for from_id in visit_mat if from_id != h_id]) - \
									sum([visit_mat[h_id][to_id] for to_id in visit_mat[h_id] if to_id != h_id])
					
_calc_inDensity = lambda h_id, visit_mat: len([visit_mat[from_id][h_id] for from_id in visit_mat if from_id != h_id and visit_mat[from_id][h_id] != 0]) / float(len(visit_mat)) 
_calc_outDensity = lambda h_id, visit_mat: len([visit_mat[h_id][to_id] for to_id in visit_mat[h_id] if to_id != h_id and visit_mat[h_id][to_id] != 0]) / float(len(visit_mat))
_calc_Popularity = lambda h_id, visit_mat: len([visit_mat[from_id][h_id] for from_id in visit_mat if from_id != h_id and visit_mat[from_id][h_id] != 0]) + len([visit_mat[h_id][to_id] for to_id in visit_mat[h_id] if to_id != h_id and visit_mat[h_id][to_id] != 0])
_calc_EntropyOut = lambda h_id, visit_mat: -1 * sum([visit_mat[h_id][to_id] * log(visit_mat[h_id][to_id]) for to_id in visit_mat[h_id] if to_id != h_id and visit_mat[h_id][to_id] != 0])
_calc_EntropyOutAll = lambda h_id, visit_mat: -1 * sum([visit_mat[h_id][to_id] * log(visit_mat[h_id][to_id]) for to_id in visit_mat[h_id] if visit_mat[h_id][to_id] != 0])
_calc_EntropyIn = lambda h_id, visit_mat: -1 * sum([visit_mat[from_id][h_id] * log(visit_mat[from_id][h_id]) for from_id in visit_mat if from_id != h_id and visit_mat[from_id][h_id] != 0])
_calc_EntropyInAll = lambda h_id, visit_mat: -1 * sum([visit_mat[from_id][h_id] * log(visit_mat[from_id][h_id]) for from_id in visit_mat if visit_mat[from_id][h_id] != 0])


_conv_SplitLabels = lambda labels: [label.replace('-', ' ').replace(' ', '\n', 1) for label in labels]
