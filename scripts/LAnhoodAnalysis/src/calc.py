# Gambit scripts
#
# Copyright (C) USC Information Sciences Institute
# Author: Nibir Bora <nbora@usc.edu>
# URL: <http://cbg.isi.edu/>
# For license information, see LICENSE

import os
import sys
sys.path.insert(0, os.path.abspath('..'))
import settings as my
import lib.geo as geo

import csv
import pickle
import anyjson
import psycopg2
from multiprocessing import Pool
from pprint import pprint as pprint

from datetime import *
from pytz import timezone, utc

import math
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from pylab import *


#TODO ALL

# VISITS

def calc_visits():
	visit_mat = None
	visit_mat__dist_norm = None

	# Create visits/ directory
	if not os.path.exists('data/' + my.DATA_FOLDER + 'visits/'):
		os.makedirs('data/' + my.DATA_FOLDER + 'visits/')

	# Try to load visit matrix if exist
	if os.path.exists('data/' + my.DATA_FOLDER + 'visits/visit_mat.pickle'):
		with open('data/' + my.DATA_FOLDER  + 'visits/' + 'visit_mat.pickle', 'rb') as fp1:
			visit_mat = pickle.load(fp1)
	if os.path.exists('data/' + my.DATA_FOLDER + 'visits/visit_mat__dist_norm.pickle'):
		with open('data/' + my.DATA_FOLDER  + 'visits/' + 'visit_mat__dist_norm.pickle', 'rb') as fp1:
			visit_mat__dist_norm = pickle.load(fp1)

	# Calculate visit matrix
	if not visit_mat:
		visit_mat = _calc_visitMat()
		_save_visitMat(visit_mat, 'visit_mat')
	if not visit_mat__dist_norm:
		visit_mat__dist_norm = _calc_visitMatDistNorm()
		_save_visitMat(visit_mat__dist_norm, 'visit_mat__dist_norm')

	# Apply normalizations
	visit_mat__twfreq_norm = _apply_TwFreqNorm(visit_mat)
	visit_mat__dtf_norm = _apply_TwFreqNorm(visit_mat__dist_norm, visit_mat)
	_save_visitMat(visit_mat__twfreq_norm, 'visit_mat__twfreq_norm')
	_save_visitMat(visit_mat__dtf_norm, 'visit_mat__dtf_norm')


	see_visitMat(visit_mat)
	see_visitMat(visit_mat__twfreq_norm)
	see_visitMat(visit_mat__dist_norm)
	see_visitMat(visit_mat__dtf_norm)

	#_plot_visitPairs(_calc_visitPairs(visit_mat), 'no_norm/')
	#_plot_visitPairs(_calc_visitPairs(visit_mat), 'twfreq_norm/')

	calc_hoodVisits(visit_mat, 'no_norm')
	calc_hoodVisits(visit_mat__twfreq_norm, 'tf_norm')
	calc_hoodVisits(visit_mat__dist_norm, 'dist_norm')
	calc_hoodVisits(visit_mat__dtf_norm, 'dtf_norm')


################################################################################
# VISIT PAIRS

def _calc_visitPairs(visit_mat):
# Calculate visits from_id->to_id as a fraction of all of from_id's tweets
	visit_pairs = {}

	for from_id in visit_mat:
		for to_id in visit_mat:
			if from_id != to_id:
				visit_pairs[(from_id, to_id)] = round(visit_mat[from_id][to_id] / \
																				float(sum(visit_mat[from_id].values()) - visit_mat[from_id][from_id]), 5)

	return visit_pairs

def _plot_visitPairs(visit_pairs, folder_name='visit_pairs/', file_name = '_dummy'):
	ids = list(set([pair[0] for pair in visit_pairs] + [pair[1] for pair in visit_pairs]))

	ab_list = []
	ba_list = []
	labels = []
	diff = []
	
	for a in ids:
		for b in ids:
			if (a, b) in visit_pairs:
				ab = visit_pairs[(a, b)]
				ba = visit_pairs[(b, a)]
				del visit_pairs[(a, b)]
				del visit_pairs[(b, a)]
				if not (ab == 0 and ba == 0):
					#ab_list.append(abs(math.log(ab)) if ab !=0 else 0.0)
					#ba_list.append(abs(math.log(ba)) if ba !=0 else 0.0)
					ab_list.append(ab)
					ba_list.append(ba)
					labels.append(str(a) + '\n' + str(b))
					diff.append(abs(ab-ba))

	ind = np.arange(len(labels)) * 10
	width = 4
	fig = plt.figure(figsize=(25,len(labels)))
	ax = fig.add_subplot(111)

	colors = ["#4DAF4A","#3B3B3B","#984EA3","#E41A1C","#A65628","#FA71AF","#FF7F00","#377EB8"]
	rects1 = ax.barh(ind, ab_list, width, color=colors, alpha=0.85, edgecolor=colors)
	rects2 = ax.barh(ind+width, ba_list, width, color=colors, alpha=0.5, edgecolor=colors)
	ax.set_yticks(ind+width)
	ytickNames = plt.setp(ax, yticklabels=labels)

	if not os.path.exists('data/' + my.DATA_FOLDER + 'visits/' + folder_name):
		os.makedirs('data/' + my.DATA_FOLDER + 'visits/' + folder_name)
	plt.savefig('data/' + my.DATA_FOLDER + 'visits/' + folder_name + file_name + '.png')

	diff = np.array(diff)
	print diff.max(), diff.min(), diff.mean(), diff.std(), diff.var()

################################################################################
# HOODwise VISITS

def calc_hoodVisits(visit_mat, file_name='_dummy'):
	hood_visits = {}
	hood_to_ids = {}
	centroids = _load_nhoodCentroids()
	
	for from_id in _load_nhoodIDs():
		dists = _calc_distToHoods(from_id, centroids)
		closest_nid = sorted(dists, key=dists.get)
		hood_visits[from_id] = [visit_mat[from_id][to_id] for to_id in closest_nid]
		hood_to_ids[from_id] = closest_nid
		
	_plot_hoodVisits(hood_visits, hood_to_ids, file_name)

def _plot_hoodVisits(hood_visits, hood_to_ids=[], file_name='_dummy'):
# Plots hood visits for all hoods in regions
	width = 6
	color = '#984EA3'
	max_y = max([max(l) for l in hood_visits.values()]) 
	ind = np.arange(len(hood_visits.values()[1])) * 10
	count = 0

	fig = plt.figure(figsize=(len(hood_visits.values()[1])+1, len(hood_visits)*1.5))
	plt.subplots_adjust(left=0.04, right=0.96, top=0.96, bottom=0.04)

	for nid in hood_visits:
		count += 1
		ax = fig.add_subplot(len(hood_visits), 1, count)
		ax.set_autoscaley_on(False)
		ax.set_ylim([0, max_y])
		ax.set_autoscalex_on(False)

		ax.set_xticks(ind+(width/2))
		plt.setp(ax, xticklabels=hood_to_ids[nid], yticklabels=[])
		
		ax.bar(ind, hood_visits[nid], width, color=color, alpha=0.75, edgecolor=color)
		ax.set_ylabel(str(nid))


	if not os.path.exists('data/' + my.DATA_FOLDER + 'visits/' + 'hood_visits/'):
		os.makedirs('data/' + my.DATA_FOLDER + 'visits/' + 'hood_visits/')
	plt.savefig('data/' + my.DATA_FOLDER + 'visits/' + 'hood_visits/' + file_name + '.png')


def _load_nhoodCentroids():
# Load hood centroids for all nhods
	con = psycopg2.connect(my.DB_CONN_STRING)
	cur = con.cursor()

	SQL = '''SELECT id, ST_AsGeoJSON(ST_Centroid(pol)) \
				FROM {rel_nhood} \
				WHERE id IN %s'''.format(rel_nhood=my.REL_NHOOD)

	cur.execute(SQL, (tuple(_load_nhoodIDs()),))
	records = cur.fetchall()
	con.close()

	centroids = dict([(rec[0], anyjson.loads(rec[1])['coordinates']) for rec in records])
	return centroids

def _calc_distToHoods(from_id, centroids):
# Calculate distance to all centroids from the centroid of from_id
	dists = {}

	for to_id in centroids:
		if to_id != from_id:
			dists[to_id] = int(geo.distance(geo.xyz(centroids[from_id][0], centroids[from_id][1]), \
										geo.xyz(centroids[to_id][0], centroids[to_id][1])))
	return dists
