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
from pprint import *

import numpy
from sklearn.decomposition import PCA

import lib.geo as geo
import lib.PiP_Edge as pip

import src.calc_fun as calc
import src.load_fun as load


REPLACE_ZEROS = lambda l: ['.' if x==0 else x for x in l]


def trim_visit_mat():
# Trim visit matrix for min tweet bound
	with open('data/' + my.DATA_FOLDER  + 'pickle/' + 'visit_mat.pickle', 'rb') as fp1:
		visit_mat = pickle.load(fp1)

	rivalry_links = calc.find_rnr_links()
	gang_id_list = sorted(list(set([link[0] for link in rivalry_links] + [link[1] for link in rivalry_links])))

	new_visit_mat = {}
	rivalry_mat = {}
	for from_id in gang_id_list:
		new_visit_mat[from_id] = {} 
		rivalry_mat[from_id] = {}
		for to_id in gang_id_list:
			new_visit_mat[from_id][to_id] = visit_mat[from_id][to_id]
			rivalry_mat[from_id][to_id] = my.RIVALRY_MATRIX[from_id][to_id]

	for gang_id in new_visit_mat:
		print '%4s '*len(new_visit_mat) % tuple(REPLACE_ZEROS(new_visit_mat[gang_id].values()))
	print '\n\n'
	for gang_id in rivalry_mat:
		print '%4s '*len(rivalry_mat) % tuple(REPLACE_ZEROS(rivalry_mat[gang_id].values()))

	X = numpy.array([[new_visit_mat[gang_id][to_id] for to_id in new_visit_mat[gang_id]] for gang_id in new_visit_mat])
	pca = PCA(copy=True, n_components=len(new_visit_mat))
	pca.fit(X)
	X = pca.transform(X).tolist()
	print X

def make_feature_mat():
	with open('data/' + my.DATA_FOLDER  + 'pickle/' + 'visit_mat.pickle', 'rb') as fp1:
		visit_mat = pickle.load(fp1)
	with open('data/' + my.DATA_FOLDER  + 'pickle/' + 'visit_mat_norm.pickle', 'rb') as fp1:
		visit_mat_norm = pickle.load(fp1)
	rivalry_links = calc.find_rnr_links()
	tty_centers = load.loadLocCenters()
	tty_polys, hbk_poly = load.loadLocPoly()
	hbk_user_home_loc = load.loadAllHomeLoc(hbk_poly)
	hbk_users_in_gang_t = load.loadUsersInGangTty(tty_polys, hbk_user_home_loc)
	user_counts = dict([(gang_id, len(hbk_users_in_gang_t[gang_id])) for gang_id in hbk_users_in_gang_t])
	user_counts = dict([(gang_id, user_counts[gang_id]) if gang_id in user_counts else (gang_id, 0) for gang_id in my.HBK_GANG_ID_LIST])

	X = []
	y = []
	for link in rivalry_links:
		[a, b, label] = link
		instance = []

		# CENTROID_DIST
		instance.append(int(geo.distance(geo.xyz(tty_centers[a][0], tty_centers[a][1]), geo.xyz(tty_centers[b][0], tty_centers[b][1]))))
		# CLOSEST_DIST
		instance.append(_closest_dist(tty_polys[a], tty_polys[b]))
		# MAX_TTY_SPAN
		span = max(_territory_span(tty_polys[a]), _territory_span(tty_polys[b]))
		instance.append(span)
		# SPAN_SQ
		instance.append((span*span)/10000)

		# VISITS_AB
		instance.append(visit_mat_norm[a][b])
		# VISITS_BA
		instance.append(visit_mat_norm[b][a])
		# TOTAL_VISITS
		instance.append(visit_mat_norm[a][b] + visit_mat_norm[b][a])
		# AVG_VISITS
		instance.append((visit_mat_norm[a][b] + visit_mat_norm[b][a])/2)
		# TOTAL_USERS
		instance.append(user_counts[a] + user_counts[b])
		# AVG_USERS
		instance.append((user_counts[a] + user_counts[b])/2)

		X.append(instance)
		y.append(label)		# class label

	for row in X:
		print '%8s '*len(row) % tuple(row)

	Xy = {'X': X, 'y': y}
	with open('data/' + my.DATA_FOLDER  + 'pickle/' + 'Xy.pickle', 'wb') as fp1:
		pickle.dump(Xy, fp1)


def _closest_dist(pol_a, pol_b):
# Find the closest distance between pol_a and pol_b.
# Closest among set of end points of line segments in pol_a and pol_b
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
# Find the spanning distance of the territory.
# i.e. the maximum distance between any two end points of line segments in pol
	max_dist = 0
	for a in pol:
		for b in pol:
			try:
				dist = int(geo.distance(geo.xyz(a[0], a[1]), geo.xyz(b[0], b[1])))
				max_dist = dist if dist > max_dist else max_dist
			except:
				print 'Error calculating distance!'
	return max_dist
