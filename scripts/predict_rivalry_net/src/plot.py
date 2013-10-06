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
import numpy as numpy
import lib.geo as geo
import matplotlib as mpl
import lib.PiP_Edge as pip
import matplotlib.pyplot as plt

from math import *
from pylab import *
from sklearn import svm
from pprint import pprint
from random import shuffle
from sklearn import cluster
from sklearn import naive_bayes
from sklearn import cross_validation
from sklearn.decomposition import PCA
from sklearn.neighbors import kneighbors_graph
from sklearn.metrics import euclidean_distances
from sklearn.preprocessing import StandardScaler
from matplotlib.collections import PolyCollection
from matplotlib.font_manager import FontProperties

import settings as my
sys.path.insert(0, os.path.abspath('..'))


#
# PLOT RIVALRY NET 
#
def _get_plot_lines(links, cmap=None):
	lines = []
	centers = _load_nhood_centers()
	for link in links:
		(a, b), [y, _] = link
		vertices = np.array([centers[a], centers[b]])
		lines.append([vertices, y])

	return lines

def plot_rivalry(folder, file_name):
	with open('data/' + my.DATA_FOLDER  + 'predict_rivalry/' + folder + file_name + '/' + 'links.pickle', 'rb') as fp1:
		links = pickle.load(fp1)
	with open('data/' + my.DATA_FOLDER  + 'predict_rivalry/' + folder + file_name + '/' + 'predicted_links.pickle', 'rb') as fp1:
		links_p = pickle.load(fp1)
	with open('data/' + my.DATA_FOLDER  + 'predict_rivalry/' + folder + file_name + '/' + 'info.txt', 'rb') as fp1:
		info = fp1.read()
	centers = _load_nhood_centers()
	names   = _load_nhood_names()
	with open('data/' + my.DATA_FOLDER + 'rivalry_baseline.pickle', 'rb') as fp:
		rivalry_baseline = pickle.load(fp)


	actual    = [(np.array([centers[a], centers[b]]), y) for a, b, y in links]
	baseline  = []
	predicted = []

	for i in range(len(links)):
		a, b, y = links_p[i]
		if y != links[i][2]:
			y += 2
		predicted.append((np.array([centers[a], centers[b]]), y))
		y = rivalry_baseline[a][b]
		#y = my.BASELINE_PREDICTION[(a, b)] if (a, b) in my.BASELINE_PREDICTION else my.BASELINE_PREDICTION[(b, a)]
		if y != links[i][2]:
			y += 2
		baseline.append((np.array([centers[a], centers[b]]), y))
	y_ 		= [y for v,y in actual]
	y_pred 	= [y for v,y in baseline]
	true 	= len([1 for i in range(len(y_)) if y_[i]==y_pred[i]])
	true_r 	= len([1 for i in range(len(y_)) if y_[i]==1 and y_[i]==y_pred[i]])
	miss 	= len(y_) - true
	acc 	= true / float(len(y_pred))
	acc_r 	= true_r / float(len([1 for i in range(len(y_)) if y_[i]==1]))
	base_info  = 'Links: ' + '{0}'.ljust(10).format(str(len(y_))) + '\n'
	base_info += 'Network acc.: ' + '{0}'.format(str(round(acc*100, 2)) + '%') + '\n'
	base_info += 'Rivalry acc.: ' + '{0}'.format(str(round(acc_r*100, 2)) + '%') + '\n'


	pols = []
	for pol in _load_nhood_polygons().values():
		pol = [[ll[1], ll[0]] for ll in pol]
		pols.append(pol)
	lngs = [ll[0] for ll in pol for pol in pols]
	lats = [ll[1] for ll in pol for pol in pols]
	print max(lngs), min(lngs), max(lats), min(lats)
	## MIGHT NEED TO SWAP x_dist and y_dist
	y_dist = geo.distance(geo.xyz(max(lats), max(lngs)), geo.xyz(max(lats), min(lngs)))
	x_dist = geo.distance(geo.xyz(max(lats), max(lngs)), geo.xyz(min(lats), max(lngs)))
	print x_dist, y_dist

	heat = [1,1,1,1,1,1,1,1,1,1,2,2,2,2,2,2,2,2,2,2,3,3,3,3,3,3,3,3,3,3,3]
	shuffle(heat)
	heat = np.array(heat)

	#fig = plt.figure(figsize=(1.5* 3*4, 1.5* 6))
	#plt.subplots_adjust(left=0.02, right=0.98, top=0.99, bottom=0.0)

	#
	# Map
	#
	'''
	markers = {
			29: (-118.21769714355469, 34.074559310537),
			25: (-118.20585250854492, 34.08948780782094),
			33: (-118.17117691040039, 34.08692882376708),
			42: (-118.15933227539062, 34.097306446504355),
			37: (-118.18439483642578, 34.08394324461533),
			47: (-118.19400787353516, 34.08422759002247),
			32: (-118.19211959838867, 34.080246667433315),
			36: (-118.20293426513672, 34.081099738028236),
			31: (-118.20653915405273, 34.0729952204399),
			41: (-118.20121765136719, 34.07143110146333),
			44: (-118.16946029663086, 34.06787617820785),
			26: (-118.19709777832031, 34.059628181822184),
			46: (-118.22164535522461, 34.05102381295824),
			50: (-118.2227611541748, 34.045476732062944),
			30: (-118.22190284729004, 34.041138377469416),
			49: (-118.21074485778809, 34.05130826886282),
			39: (-118.20259094238281, 34.0488192473379),
			52: (-118.19701194763184, 34.05166383740143),
			48: (-118.19486618041992, 34.050028209776336),
			40: (-118.1960678100586, 34.04327202221684),
			43: (-118.20293426513672, 34.043556504127444),
			35: (-118.2030200958252, 34.03843568373248),
			54: (-118.20405006408691, 34.03139405087606),
			45: (-118.20379257202148, 34.022786817002),
			23: (-118.2143497467041, 34.02392501371833),
			53: (-118.20671081542969, 34.02051037777654),
			38: (-118.19520950317383, 34.018803008289744),
			28: (-118.21610927581787, 34.04700577135851),
			51: (-118.2134485244751, 34.047432475078324),
			27: (-118.21108818054199, 34.04618791656029),
			34: (-118.2070541381836, 34.044658862517366)}
	fig = plt.figure(figsize=(1.5* 4, 1.5* 6))
	plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.0)
	ax = fig.add_subplot(111, aspect=1.2)
	coll = PolyCollection(pols, array=heat, cmap=mpl.cm.Accent, edgecolors='#111111', alpha=0.75)
	ax.add_collection(coll)
	ax.autoscale_view()
	ax.get_xaxis().set_ticklabels([])
	ax.get_yaxis().set_ticklabels([])
	count = 0
	id_map = {}
	for h_id in markers:
		count += 1
		id_map[h_id] = count
		x, y = markers[h_id]
		ax.text(x, y, str(count), backgroundcolor='#dddddd', color='#000000', fontsize=10, alpha=0.8, fontproperties=FontProperties(weight='bold'))
	ids = markers.keys()
	info1 = '\n'.join([str(str(id_map[i]) + ' : ' + names[i]) for i in ids[:8]])
	info2 = '\n'.join([str(str(id_map[i]) + ' : ' + names[i]) for i in ids[8:]])
	ax.text(0.05, 0.99, info1, ha='left', va='top', transform=ax.transAxes, fontsize=12)
	ax.text(0.6, 0.01, info2, ha='left', va='bottom', transform=ax.transAxes, fontsize=12)
	plt.savefig('data/' + my.DATA_FOLDER  + 'predict_rivalry/' + folder + file_name + '/' + '_map' + '.pdf')
	'''

	#
	# Actual
	#
	fig = plt.figure(figsize=(1.5* 4, 1.5* 6))
	plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.0)
	ax = fig.add_subplot(111, aspect=1.2) 
	#coll = PolyCollection(pols, array=heat, cmap=mpl.cm.Dark2, edgecolors='k', alpha=0.3)
	coll = PolyCollection(pols, facecolors='none', edgecolors='k', linewidths=1, alpha=0.3)
	ax.add_collection(coll)
	ax.autoscale_view()
	ax.get_xaxis().set_ticklabels([])
	ax.get_yaxis().set_ticklabels([])
	#ax.set_title('Actual')
	for vertices, y in actual:
		if y == 1:
			ax.plot(vertices[:,0], vertices[:,1], color=my.CMAP[y], alpha=0.95, linewidth=my.LINEWIDTH[y])
		else:
			ax.plot(vertices[:,0], vertices[:,1], color=my.CMAP[y], alpha=0.75, linewidth=1, linestyle=my.LINESTYLE[y])
	plt.savefig('data/' + my.DATA_FOLDER  + 'predict_rivalry/' + folder + file_name + '/' + '_actual' + '.pdf')

	#
	# Baseline
	#
	fig = plt.figure(figsize=(1.5* 4, 1.5* 6))
	plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.0)
	ax = fig.add_subplot(111, aspect=1.2) 
	#coll = PolyCollection(pols, array=heat, cmap=mpl.cm.Dark2, edgecolors='k', alpha=0.3)
	coll = PolyCollection(pols, facecolors='none', edgecolors='k', linewidths=1, alpha=0.3)
	ax.add_collection(coll)
	ax.autoscale_view()
	ax.get_xaxis().set_ticklabels([])
	ax.get_yaxis().set_ticklabels([])
	#ax.set_title('Baseline')
	ax.text(0.98, 0.05, base_info, horizontalalignment='right', verticalalignment='bottom', transform = ax.transAxes, fontsize=19)
	for vertices, y in baseline:
		if y == 1:
			ax.plot(vertices[:,0], vertices[:,1], color=my.CMAP[y], alpha=0.95, linewidth=my.LINEWIDTH[y])
		else:
			ax.plot(vertices[:,0], vertices[:,1], color=my.CMAP[y], alpha=0.9, linewidth=my.LINEWIDTH[y], linestyle=my.LINESTYLE[y])
	plt.savefig('data/' + my.DATA_FOLDER  + 'predict_rivalry/' + folder + file_name + '/' + '_baseline' + '.pdf')
	
	#
	# Predicted
	#
	fig = plt.figure(figsize=(1.5* 4, 1.5* 6))
	plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.0)
	ax = fig.add_subplot(111, aspect=1.2) 
	#coll = PolyCollection(pols, array=heat, cmap=mpl.cm.winter, edgecolors='k', alpha=0.2)
	coll = PolyCollection(pols, facecolors='none', edgecolors='k', linewidths=1, alpha=0.3)
	ax.add_collection(coll)
	ax.autoscale_view()
	ax.get_xaxis().set_ticklabels([])
	ax.get_yaxis().set_ticklabels([])
	#ax.set_title('Predicted')
	ax.text(0.98, 0.05, info, horizontalalignment='right', verticalalignment='bottom', transform = ax.transAxes, fontsize=19)
	for vertices, y in predicted:
		if y == 1:
			ax.plot(vertices[:,0], vertices[:,1], color=my.CMAP[y], alpha=0.95, linewidth=my.LINEWIDTH[y])
		else:
			ax.plot(vertices[:,0], vertices[:,1], color=my.CMAP[y], alpha=0.9, linewidth=my.LINEWIDTH[y], linestyle=my.LINESTYLE[y])
	plt.savefig('data/' + my.DATA_FOLDER  + 'predict_rivalry/' + folder + file_name + '/' + '_predicted' + '.pdf')
	
	#fig.suptitle('' + folder.upper() + ' (' + my.DATA_FOLDER[:-1].upper() + ')', fontsize=18)
	#plt.savefig('data/' + my.DATA_FOLDER  + 'predict_rivalry/' + folder + file_name + '/' + 'rivalry_net' + '.png')
	#plt.savefig('data/' + my.DATA_FOLDER  + 'predict_rivalry/' + folder + file_name + '/' + 'rivalry_net' + '.pdf')


#
# LOAD Functions
#
_load_nhoodIDs = lambda: [int(nid) for nid in anyjson.loads(
				open('data/' + my.DATA_FOLDER + 'hood_ids.txt', 'rb').read())]

_load_nhood_names = lambda: dict((int(loc['id']), str(loc['name'])) for loc in anyjson.loads(
				open('data/' + my.DATA_FOLDER + 'loc_data.json', 'rb').read()))

_load_nhood_polygons = lambda: dict((int(loc['id']), loc['polygon'][:-1]) for loc in anyjson.loads(
				open('data/' + my.DATA_FOLDER + 'loc_data.json', 'rb').read()))

_load_nhood_centers = lambda: dict((int(loc['id']), [sum([ll[1] for ll in loc['polygon']]) / len(loc['polygon']), 
				sum([ll[0] for ll in loc['polygon']]) / len(loc['polygon'])]) for loc in anyjson.loads(
				open('data/' + my.DATA_FOLDER + 'loc_data.json', 'rb').read()))

_load_nhood_features = lambda: pickle.load(open('data/' + my.DATA_FOLDER  + 'features.pickle', 'rb'))