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
import src.calc_fun as calc

import csv
import anyjson
from pprint import *
import pickle

import numpy
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn import cluster
from sklearn.metrics import euclidean_distances
from sklearn.neighbors import kneighbors_graph

import lib.geo as geo
import lib.PiP_Edge as pip

def cluster_all():
	with open('data/' + my.DATA_FOLDER  + 'pickle/' + 'Xy.pickle', 'rb') as fp1:
		Xy = pickle.load(fp1)
	X = Xy['X']
	y = Xy['y']
	inst = calc.find_rnr_links()

	# Perform LSA on X
	n_comp = len(X)
	X = numpy.array(X)
	pca = PCA(copy=True, n_components=n_comp)
	pca.fit(X)
	X_LSA = pca.transform(X)
	
	#print X
	#print X_LSA

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


def _k_means(X, k=2):
# K-means
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

def compare_predictions(y, y_pred):
# Convert predictions to T/F list (correct/incorrect)
	y_pred = [1 if lbl==-1 else 0 for lbl in y_pred]
	# check using rival=1 & nonrival=0
	y = [1 if lbl=='rival' else 0 for lbl in y]
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

def save_predict_results(inst, truths):
# [[gang_id, gang_id, 0|1|-1]...]
#	1 - R>R, 0 - R>NR, -1 NR>R
	links = []
	for i in range(0, len(inst)):
		if inst[i][2] == 'rival':
			this_link = [inst[i][0], inst[i][1], truths[i]]
			links.append(this_link)
		if inst[i][2] == 'nonrival' and truths[i] == 0:
			this_link = [inst[i][0], inst[i][1], -1]
			links.append(this_link)
	pprint(links)

	if not os.path.exists('data/' + my.DATA_FOLDER + 'json/'):
		os.makedirs('data/' + my.DATA_FOLDER + 'json/')
	with open('data/' + my.DATA_FOLDER  + 'json/' + 'rivalry_pred.json', 'wb') as fp1:
		fp1.write(anyjson.dumps(links))

	inst = [[link[0], link[1], 1] if link[2]=='rival' else [link[0], link[1], 0] for link in inst if link[2]=='rival']
	#inst = [[link[0], link[1], 1] if link[2]=='rival' else [link[0], link[1], 0] for link in inst]		# All links
	with open('data/' + my.DATA_FOLDER  + 'json/' + 'rivalry_net.json', 'wb') as fp1:
		fp1.write(anyjson.dumps(inst))





