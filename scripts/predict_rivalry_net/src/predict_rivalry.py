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

from sklearn import svm
from sklearn import tree
from sklearn import cluster
from sklearn import naive_bayes
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors.nearest_centroid import NearestCentroid

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
# PREDICT RIVALRY
#
def predict_rivalry(folder, file_name):
	if not os.path.exists('data/' + my.DATA_FOLDER + 'predict_rivalry/' + folder + file_name + '/'):
		os.makedirs('data/' + my.DATA_FOLDER + 'predict_rivalry/' + folder + file_name + '/')
	ids 	= _trim_user_list()
	mat 	= _load_matrix(folder, file_name)
	links 	= _trim_links(mat, ids, folder, file_name)
	Xy 		= make_feature_mat(mat, links, folder, file_name)
	path = 'data/' + my.DATA_FOLDER + 'dataset/' + folder
	if not os.path.exists(path): os.makedirs(path)
	with open(path + file_name + '.pickle', 'wb') as fp:
		pickle.dump(Xy, fp)
	with open(path + file_name + '.json', 'wb') as fp:
		fp.write(anyjson.dumps(Xy))
	#cluster_all(Xy)
	y_pred  = classify_all(Xy, folder, file_name)
	links_p = _make_predicted_links(links, y_pred, folder, file_name)

	#lines = _get_plot_lines(links)
	#_plot_prediction(lines, lines)

	#rivalry_lines = _get_rivalry_lines(ids)

	#_plot_prediction()


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

def _trim_links(mat, ids=None, folder='dummy', file_name='dummy'):
	links = {}
	if not ids:
		ids = _load_nhoodIDs()
	rivalry_mat = _load_matrix('', 'rivalry_mat')

	for from_id in ids:
		for to_id in ids:
			if from_id != to_id \
			and (from_id, to_id) not in links and (to_id, from_id) not in links \
			and mat[from_id][to_id] + mat[to_id][from_id] > my.MIN_LINK_SUM:
				links[(from_id, to_id)] = [rivalry_mat[from_id][to_id], mat[from_id][to_id] + mat[to_id][from_id]]

	links 	= sorted(links.items(), key=lambda x: x[1][0])
	r 		= [[i, val] for i, val in links if val[0]==1]
	nr 		= [[i, val] for i, val in links if val[0]==0]
	r 		= sorted(r, key=lambda x: x[1][1], reverse=True)
	nr 		= sorted(nr, key=lambda x: x[1][1], reverse=True)

	if len(nr) > len(r):
		nr = nr[:len(r)]
	elif len(r) > len(nr):
		r = r[:len(nr)]
	
	links = r + nr
	links = [(a, b, y) for (a, b), [y, val] in links]
	print 'Number of link = {0}'.format(len(links))
	#pprint(links)
	with open('data/' + my.DATA_FOLDER  + 'predict_rivalry/' + folder + file_name + '/' + 'links.pickle', 'wb') as fp1:
		pickle.dump(links, fp1)
	return links

def _make_predicted_links(links, y_pred, folder, file_name):
	links = [(links[i][0], links[i][1], y_pred[i]) for i in range(len(links))]
	with open('data/' + my.DATA_FOLDER  + 'predict_rivalry/' + folder + file_name + '/' + 'predicted_links.pickle', 'wb') as fp1:
		pickle.dump(links, fp1)
	#pprint(links)
	return links

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


#
# FEATURES 
#
def make_feature_mat(mat, links, folder, file_name):
	X 		= []
	y 		= []
	centers = _load_nhood_centers()
	pols 	= _load_nhood_polygons()
	mat_f	= _calc_mat_frac(mat)

	for a, b, label in links:
		instance = [
			int(geo.distance(geo.xyz(centers[a][0], centers[a][1]), geo.xyz(centers[b][0], centers[b][1]))), # CENTROID_DIST
			_closest_dist(pols[a], pols[b]), # CLOSEST_DIST
			max(_territory_span(pols[a]), _territory_span(pols[b])), # MAX_TTY_SPAN
			abs(_territory_span(pols[a]) - _territory_span(pols[b])), #TTY_SPAN_DIFF
			pow(max(_territory_span(pols[a]), _territory_span(pols[b])), 2), # SPAN_SQ
			
			mat_f[a][b] + mat_f[b][a], # TOTAL_VISITS
			(mat_f[a][b] + mat_f[b][a])/2, # AVG_VISITS
			
			_in_density(a, mat_f) + _in_density(b, mat_f), # IN_DENSITY_ApB
			abs(_in_density(a, mat_f) - _in_density(b, mat_f)), # IN_DENSITY_AmB
			_out_density(a, mat_f) + _out_density(b, mat_f), # OUT_DENSITY_ApB
			abs(_out_density(a, mat_f) - _out_density(b, mat_f)), # OUT_DENSITY_AmB

			_in_entropy(a, mat_f) + _in_entropy(b, mat_f),
			_out_entropy(a, mat_f) + _out_entropy(b, mat_f),

			_in_cross_entropy(a, b, mat_f), # IN_CROSS_ENTROPY
			_out_cross_entropy(a, b, mat_f), # OUT_CROSS_ENTROPY
			]
		X.append(instance)
		y.append(label)

	Xy = {'X': X, 'y': y}
	with open('data/' + my.DATA_FOLDER  + 'predict_rivalry/' + folder + file_name + '/' + 'Xy.pickle', 'wb') as fp1:
		pickle.dump(Xy, fp1)
	return Xy

_calc_mat_frac = lambda mat: dict([(from_id, 
										dict([(to_id, mat[from_id][to_id] / float(sum(mat[from_id].values()))) \
										if sum(mat[from_id].values()) != 0 else (to_id, 0) \
										for to_id in mat[from_id]])) \
										for from_id in mat])

def _closest_dist(pol_a, pol_b):
	'''Find the closest distance between pol_a and pol_b.
	Closest among set of end points of line segments in pol_a and pol_b'''
	min_dist = 15000
	for a in pol_a:
		for b in pol_b:
			try:
				dist = int(geo.distance(geo.xyz(a[0], a[1]), geo.xyz(b[0], b[1])))
				min_dist = dist if dist < min_dist else min_dist
			except:
				print 'Error calculating distance!'
	return min_dist

def _territory_span(pol):
	'''Find the spanning distance of the territory.
	i.e. the maximum distance between any two end points of line segments in pol'''
	max_dist = 0
	for a in pol:
		for b in pol:
			try:
				dist = int(geo.distance(geo.xyz(a[0], a[1]), geo.xyz(b[0], b[1])))
				max_dist = dist if dist > max_dist else max_dist
			except:
				print 'Error calculating distance!'
	return max_dist

_in_density = lambda h_id, mat: len([mat[from_id][h_id] for from_id in mat \
										if from_id != h_id and mat[from_id][h_id] != 0]) \
										/ float(len(mat)) 

_out_density = lambda h_id, mat: len([mat[h_id][to_id] for to_id in mat[h_id] \
										if to_id != h_id and mat[h_id][to_id] != 0]) \
										/ float(len(mat))

_in_cross_entropy = lambda p, q, mat: -1 * sum(mat[from_id][p] * log(mat[from_id][q]) \
										for from_id in mat \
										if from_id != p and from_id != q and mat[from_id][q] != 0)

_out_cross_entropy = lambda p, q, mat: -1 * sum(mat[p][to_id] * log(mat[q][to_id]) \
										for to_id in mat \
										if to_id != p and to_id != q and mat[q][to_id] != 0)

_in_entropy = lambda p, mat: -1 * sum([mat[from_id][p] * log(mat[from_id][p]) \
								for from_id in mat \
								if from_id != p and mat[from_id][p] != 0])

_out_entropy = lambda p, mat: -1 * sum([mat[p][to_id] * log(mat[p][to_id]) \
								for to_id in mat[p] \
								if to_id != p and mat[p][to_id] != 0])


#
# PLOT FEATURES
#
def plot_features(folder, file_name):
	''''''
	path = 'data/' + my.DATA_FOLDER + 'dataset/' + folder
	with open(path + file_name + '.pickle', 'rb') as fp:
		Xy = pickle.load(fp)

	X = Xy['X']
	y = Xy['y']
	M = len(X[0])
	N = len(X)

	path = 'data/' + my.DATA_FOLDER + 'features/' + folder + file_name + '/'
	if not os.path.exists(path): os.makedirs(path)

	for i in range(M):
		f = []
		for j in range(N): f.append(X[j][i])
		f = _norm(f)
		
		r = []
		nr = []
		for k in range(N):
			if y[k] == 0: nr.append(f[k])
			else: r.append(f[k])
		
		feat_names = ['CENTROID_DIST', 'CLOSEST_DIST', 'MAX_TTY_SPAN', 'TTY_SPAN_DIFF', 'SPAN_SQ', 'TOTAL_ACTIVITY', 'AVG_ACTIVITY', 'IN_DENSITY_AplusB', 'IN_DENSITY_AminusB', 'OUT_DENSITY_AplusB', 'OUT_DENSITY_AminusB', 'IN_CROSS_ENTROPY', 'OUT_CROSS_ENTROPY']

		num_bins = 10
		fig = plt.figure(figsize=(10,4))
		fig.set_tight_layout(True)
		ax = fig.add_subplot(121)
		ax.hist(nr, num_bins, facecolor='blue', alpha=0.5)
		ax = fig.add_subplot(122)
		ax.hist(r, num_bins, facecolor='red', alpha=0.5)
		plt.savefig(path + 'hist_' + feat_names[i] + '.pdf')

		fig = plt.figure(figsize=(4,4))
		fig.set_tight_layout(True)
		ax = fig.add_subplot(111)
		ax.boxplot([nr, r], positions=[1,2], widths=0.5)
		ax.set_title(feat_names[i].replace('_', ' ').replace('minus', '-').replace('plus', '+'))
		plt.savefig(path + 'box_' + feat_names[i] + '.pdf')

def _norm(x):
	mx = float(max(x))
	mn = float(min(x))
	diff = mx - mn
	if diff == 0:
		return x
	x_ = [(e-mn)/diff for e in x]
	return x_


#
# CLUSTERING
#
def cluster_all(Xy):
	X = Xy['X']
	y = Xy['y']
	
	n_comp = len(X)
	X = numpy.array(X)
	pca = PCA(copy=True, n_components=n_comp)
	pca.fit(X)
	X_LSA = pca.transform(X)

	y_pred = _k_means(X, 2)
	compare_predictions(y, y_pred)
	y_pred = _k_means(X_LSA, 2)
	compare_predictions(y, y_pred)

	y_pred = _ward(X, 2)
	compare_predictions(y, y_pred)
	y_pred = _ward(X_LSA, 2)
	compare_predictions(y, y_pred)

	y_pred = _spectral(X, 2)
	compare_predictions(y, y_pred)
	y_pred = _spectral(X_LSA, 2)
	compare_predictions(y, y_pred)

	y_pred = _dbscan(X)
	compare_predictions(y, y_pred)
	#save_predict_results(inst, compare_predictions(y, y_pred))
	y_pred = _dbscan(X_LSA)
	compare_predictions(y, y_pred)

def compare_predictions(y, y_pred):
	'''Convert predictions to T/F list (correct/incorrect)'''
	print y 
	print y_pred.tolist()
	y_pred = [1 if lbl==-1 else 0 for lbl in y_pred]
	# check using rival=1 & nonrival=0
	#y = [1 if lbl=='rival' else 0 for lbl in y]
	tp = 0
	for i in range(0, len(y)):
		tp = tp+1 if y[i]==y_pred[i] else tp
	acc1 = round((float(tp)/len(y)) * 100, 2)
	
	# check using rival=0 & nonrival=1
	y = [1 if lbl==0 else 0 for lbl in y]
	tp2 = 0
	for i in range(0, len(y)):
		tp2 = tp2+1 if y[i]==y_pred[i] else tp2
	acc2 = round((float(tp2)/len(y)) * 100, 2)
	#max accuracy among both
	acc = max(acc1, acc2)
	print acc

	if acc1>acc2:	# reverse to first mapping
		y = [1 if lbl==0 else 0 for lbl in y]
	truths = [1 if y[i]==y_pred[i] else 0 for i in range(0, len(y))]
	#print truths
	#print round(len([val for val in truths if val==1])/float(len(y)), 2)
	return truths


def _k_means(X, k=2):
	two_means = cluster.KMeans(n_clusters=k)
	two_means.fit(X)
	y_pred = two_means.labels_.astype(numpy.int)
	return y_pred

def _ward(X, k=2):
	connectivity = kneighbors_graph(X, n_neighbors=10)
	connectivity = 0.5 * (connectivity + connectivity.T)
	ward_five = cluster.Ward(n_clusters=k, connectivity=connectivity)
	ward_five.fit(X)
	y_pred = ward_five.labels_.astype(numpy.int)
	return y_pred

def _spectral(X, k=2):
	spectral = cluster.SpectralClustering(n_clusters=2, eigen_solver='arpack', affinity="nearest_neighbors")
	spectral.fit(X)
	y_pred = spectral.labels_.astype(numpy.int)
	return y_pred

def _dbscan(X):
	dbscan = cluster.DBSCAN(eps=1500, min_samples=20)
	dbscan.fit(X)
	y_pred = dbscan.labels_.astype(numpy.int)
	return y_pred


#
# CLASSIFICATION
#
def classify_all(Xy, folder, file_name):
	X = np.array(Xy['X'])
	y = np.array(Xy['y'])
	info = 'Links: '.rjust(25) + '{0}        '.format(str(len(y)) + '    ') + '\n'
	'''
	clf 	= naive_bayes.GaussianNB()
	cv 		= cross_validation.LeaveOneOut(n=len(y))
	scores 	= cross_validation.cross_val_score(clf, X, y, cv=cv)
	true 	= sum(scores)
	acc 	= sum(scores)/len(scores)'''

	cv 		= cross_validation.LeaveOneOut(n=len(y))
	y_pred 	= [0] * len(y)
	for train, test in cv:
		X_train, X_test, y_train, y_test = X[train], X[test], y[train], y[test]
		clf 	= naive_bayes.GaussianNB()
		#clf 	= svm.LinearSVC()
		#clf = tree.DecisionTreeClassifier()
		#clf = RandomForestClassifier(n_estimators=10)
		#clf = NearestCentroid()

		clf.fit(X_train, y_train)
		pred 	= clf.predict(X_test)[0]
		ind 	= test[0]
		y_pred[ind] = pred
	y 		= y.tolist()
	true 	= len([1 for i in range(len(y)) if y[i]==y_pred[i]])
	true_r 	= len([1 for i in range(len(y)) if y[i]==1 and y[i]==y_pred[i]])
	miss 	= len(y) - true
	acc 	= true / float(len(y_pred))
	acc_r 	= true_r / float(len([1 for i in range(len(y)) if y[i]==1]))
	print true, acc, true_r, acc_r, miss
	info += 'Network acc.: '.rjust(25) + '{0}'.ljust(6).format(str(round(acc*100, 2)) + '%') + '\n'
	info += 'Rivalry acc.: '.rjust(25) + '{0}'.ljust(6).format(str(round(acc_r*100, 2)) + '%') + '\n'
	#info += 'Mis-predictions: '.rjust(25) + '{0}'.ljust(6).format(str(miss) + '     ') + '\n'

	clf = naive_bayes.GaussianNB()
	#clf 	= svm.SVC()
	#clf = tree.DecisionTreeClassifier()
	#clf = RandomForestClassifier(n_estimators=10)
	#clf = NearestCentroid()

	clf.fit(X, y)
	acc = clf.score(X, y)
	print acc

	print info
	with open('data/' + my.DATA_FOLDER  + 'predict_rivalry/' + folder + file_name + '/' + 'info.txt', 'wb') as fp1:
		fp1.write(info)

	print '----------'
	return y_pred


