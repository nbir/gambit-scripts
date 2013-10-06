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
	inn = dict([(to_id, len([1 for from_id in hood_ids \
					if from_id != to_id and visit_mat_frac[from_id][to_id] != 0])) \
						for to_id in hood_ids])
	outn = dict([(from_id, len([1 for to_id in hood_ids \
					if to_id != from_id and visit_mat_frac[from_id][to_id] != 0])) \
						for from_id in hood_ids])
	inn = [i for i in inn if inn[i] > my.MIN_LINKS_FRAC*max(inn.values())]
	outn = [i for i in outn if outn[i] > my.MIN_LINKS_FRAC*max(outn.values())]
	print hood_ids
	print inn
	print outn

	#for a in visit_mat_frac:
	#	print a, len([1 for b in visit_mat_frac if visit_mat_frac[a][b] != 0 and visit_mat_frac[b][a] !=0])
	
	# Calculate each feature
	OUTFLOW_INFLOW = dict([(h_id, _calc_inflowVsOutflow(h_id, visit_mat_frac)) for h_id in hood_ids])
	IN_DENSITY = dict([(h_id, _calc_inDensity(h_id, visit_mat_frac)) for h_id in hood_ids])
	OUT_DENSITY = dict([(h_id, _calc_outDensity(h_id, visit_mat_frac)) for h_id in hood_ids])
	POPULARITY = dict([(h_id, _calc_Popularity(h_id, visit_mat_frac)) for h_id in hood_ids])
	ENTROPY_OUT = dict([(h_id, _calc_EntropyOut(h_id, visit_mat_frac)) for h_id in hood_ids])
	ENTROPY_OUT_BYN = dict([(h_id, _calc_EntropyOut_byN(h_id, visit_mat_frac)) for h_id in hood_ids])
	ENTROPY_OUT_ALL = dict([(h_id, _calc_EntropyOutAll(h_id, visit_mat_frac)) for h_id in hood_ids])
	ENTROPY_IN = dict([(h_id, _calc_EntropyIn(h_id, visit_mat_frac)) for h_id in hood_ids])
	ENTROPY_IN_BYN = dict([(h_id, _calc_EntropyIn_byN(h_id, visit_mat_frac)) for h_id in hood_ids])
	ENTROPY_IN_ALL = dict([(h_id, _calc_EntropyInAll(h_id, visit_mat_frac)) for h_id in hood_ids])
	KL_DIVERGENCE = dict([(h_id, _calc_KLDivergence(h_id, visit_mat_frac)) for h_id in hood_ids])

	ENTROPY_OUT = _trim_ids(ENTROPY_OUT, outn)
	ENTROPY_IN = _trim_ids(ENTROPY_IN, inn)
	
	# Initialize features for plot
	features = {'OUTFLOW_INFLOW' : OUTFLOW_INFLOW,
		'IN_DENSITY' : IN_DENSITY,
		'OUT_DENSITY' : OUT_DENSITY,
		'POPULARITY' : POPULARITY,
		'ENTROPY_OUT' : ENTROPY_OUT,
		'ENTROPY_OUT_(/N)' : ENTROPY_OUT_BYN,
		'ENTROPY_OUT_ALL' : ENTROPY_OUT_ALL,
		'ENTROPY_IN' : ENTROPY_IN,
		'ENTROPY_IN_(/N)' : ENTROPY_IN_BYN,
		'ENTROPY_IN_ALL' : ENTROPY_IN_ALL,
		'KL_DIVERGENCE': KL_DIVERGENCE}

	#with open('data/' + my.DATA_FOLDER  + 'features_' + folder + '.pickle', 'wb') as fp1:
	#	pickle.dump(features, fp1)

	#feature_names = ['OUTFLOW_INFLOW', 'IN_DENSITY', 'OUT_DENSITY', 'POPULARITY', 'ENTROPY_OUT', 'ENTROPY_OUT_ALL', 'ENTROPY_IN', 'ENTROPY_IN_ALL']
	#feature_names = ['OUTFLOW_INFLOW', 'POPULARITY', 'ENTROPY_OUT', 'ENTROPY_OUT_(/N)', 'ENTROPY_IN', 'ENTROPY_IN_(/N)']
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
	fig = plt.figure(figsize=(2 * 6, 3 * y_dist * 6/x_dist))
	plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
	count = 0
	for name in feature_names:
		count += 1
		#x = [hood_info[h_id]['name'] for h_id in sorted(features[name], key=features[name].get)]
		#y = [features[name][h_id] for h_id in sorted(features[name], key=features[name].get)]
		heat = np.array([features[name][h_id] for h_id in pol_seq])

		#fig = plt.figure(figsize=(6, y_dist * 6/x_dist))
		ax = fig.add_subplot(3, 2, count, aspect='equal') 
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
	if not os.path.exists('data/' + my.DATA_FOLDER + 'nhood_rank/'):
		os.makedirs('data/' + my.DATA_FOLDER + 'nhood_rank/')
	plt.savefig('data/' + my.DATA_FOLDER + 'nhood_rank/' + file_name + '.png')

	# Plot seperate plots WEST LA
	'''feature_names = ['ENTROPY_OUT', 'ENTROPY_IN']
	markers = {
			2932: (-118.40034484863281, 33.95475186857191),
			2815: (-118.4487533569336, 33.9778158396608),
			2728: (-118.42403411865234, 33.989487811032085),
			2813: (-118.40034484863281, 33.88922749934701),
			2855: (-118.37081909179688, 33.86727982302171),
			2870: (-118.48514556884766, 34.022217712919684),
			2871: (-118.44806671142578, 34.036444170082454),
			2814: (-118.43570709228516, 34.01055023831342),
			2910: (-118.46351623535156, 33.994326938821324),
			2846: (-118.41716766357422, 33.97923933661636),
			2847: (-118.443603515625, 33.958738681008505),
			2743: (-118.40412139892578, 33.91686783484126),
			2727: (-118.3725357055664, 33.92228087152904),			
			2772: (-118.39656829833984, 33.86585445407186)}
	marker_seq = [2728,2871, 2814, 2910, 2727, 2932, 2815, 2813, 2855, 2870, 2846, 2847, 2743, 2772]

	if not os.path.exists('data/' + my.DATA_FOLDER + 'nhood_rank/' + file_name + '/'):
		os.makedirs('data/' + my.DATA_FOLDER + 'nhood_rank/' + file_name + '/')

	for name in feature_names:
		fig = plt.figure(figsize=(6, y_dist * 6/x_dist))
		plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
		ax = fig.add_subplot(111, aspect='equal') 

		heat = np.array([features[name][h_id] for h_id in pol_seq])
		coll = PolyCollection(pols, array=heat, cmap=mpl.cm.OrRd, edgecolors='k', alpha=0.75)
		ax.add_collection(coll)
		ax.autoscale_view()
		ax.get_xaxis().set_ticklabels([])
		ax.get_yaxis().set_ticklabels([])
		fig.colorbar(coll, ax=ax)

		text = ''
		count = 0
		for h_id in marker_seq:
			count += 1
			x, y = markers[h_id]
			ax.text(x, y, str(count), backgroundcolor='#dddddd', color='#000000', fontsize=15)
			text += str(count) + ' : ' + hood_info[h_id]['name'] + '\n'
		ax.text(0.02, 0.01, text, ha='left', va='bottom', transform=ax.transAxes, fontsize=15)

		plt.savefig('data/' + my.DATA_FOLDER + 'nhood_rank/' + file_name + '/' + name + '.pdf')
	'''
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
_calc_inflowVsOutflow = lambda h_id, mat: sum([mat[from_id][h_id] for from_id in mat if from_id != h_id]) - \
									sum([mat[h_id][to_id] for to_id in mat[h_id] if to_id != h_id])
					
_calc_inDensity = lambda h_id, mat: len([mat[from_id][h_id] for from_id in mat if from_id != h_id and mat[from_id][h_id] != 0]) / float(len(mat)) 
_calc_outDensity = lambda h_id, mat: len([mat[h_id][to_id] for to_id in mat[h_id] if to_id != h_id and mat[h_id][to_id] != 0]) / float(len(mat))
_calc_Popularity = lambda h_id, mat: len([mat[from_id][h_id] for from_id in mat if from_id != h_id and mat[from_id][h_id] != 0]) + len([mat[h_id][to_id] for to_id in mat[h_id] if to_id != h_id and mat[h_id][to_id] != 0])

_calc_EntropyOut = lambda h_id, mat: -1 * sum([mat[h_id][to_id] * log(mat[h_id][to_id]) \
											for to_id in mat[h_id] if to_id != h_id \
											and mat[h_id][to_id] != 0])

_calc_EntropyOut_byN = lambda h_id, mat: -1 * sum([mat[h_id][to_id] * log(mat[h_id][to_id]) \
											for to_id in mat[h_id] if to_id != h_id \
											and mat[h_id][to_id] != 0]) \
											/ (1 + len([1 for to_id in mat[h_id] if to_id != h_id \
											and mat[h_id][to_id] != 0 and mat[to_id][h_id] != 0]))

_calc_EntropyOutAll = lambda h_id, mat: -1 * sum([mat[h_id][to_id] * log(mat[h_id][to_id]) for to_id in mat[h_id] if mat[h_id][to_id] != 0])

_calc_EntropyIn = lambda h_id, mat: -1 * sum([mat[from_id][h_id] * log(mat[from_id][h_id]) \
											for from_id in mat if from_id != h_id \
											and mat[from_id][h_id] != 0])

_calc_EntropyIn_byN = lambda h_id, mat: -1 * sum([mat[from_id][h_id] * log(mat[from_id][h_id]) \
											for from_id in mat if from_id != h_id \
											and mat[from_id][h_id] != 0]) \
											/ (1 + len([1 for from_id in mat if from_id != h_id \
											and mat[from_id][h_id] != 0 and mat[h_id][from_id] != 0]))

_calc_EntropyInAll = lambda h_id, mat: -1 * sum([mat[from_id][h_id] * log(mat[from_id][h_id]) for from_id in mat if mat[from_id][h_id] != 0])

#_calc_KLDivergence = lambda a, mat: sum([mat[a][b] * log(mat[a][b] / mat[b][a]) \
_calc_KLDivergence = lambda a, mat: sum([mat[b][a] * log(mat[b][a] / mat[a][b]) \
											for b in mat if a != b \
											and mat[a][b] != 0 and mat[b][a] != 0])


_conv_SplitLabels = lambda labels: [label.replace('-', ' ').replace(' ', '\n', 1) for label in labels]

_minmax_norm = lambda vec: [(x-min(vec)) / (max(vec)-min(vec)) for x in vec]

def _trim_ids(feat, ids):
	for i in feat:
		if i not in ids:
			feat[i] = 0
	return feat
