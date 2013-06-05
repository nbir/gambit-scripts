# Gambit scripts
#
# Copyright (C) USC Information Sciences Institute
# Author: Nibir Bora <nbora@usc.edu>
# URL: <http://cbg.isi.edu/>
# For license information, see LICENSE

import os
import sys
import csv
import math
import pickle
import anyjson
import psycopg2
import matplotlib
import numpy as np
import lib.geo as geo
import matplotlib.pyplot as plt

from pylab import *
from datetime import *
from pprint import pprint
from pytz import timezone, utc
from multiprocessing import Pool

import settings as my
sys.path.insert(0, os.path.abspath('..'))


#
# ACTIVITY POINTS
#
def calc_activity():
	'''Calculate activity matrix'''
	if not os.path.exists('data/' + my.DATA_FOLDER + 'activity/'):
		os.makedirs('data/' + my.DATA_FOLDER + 'activity/')
	activity_mat = _load_matrix('activity', 'activity_mat')
	activity_mat__dist_norm = _load_matrix('activity', 'activity_mat__dist_norm')

	if not activity_mat:
		activity_mat = _calc_activity_mat()
		_save_matrix('activity', 'activity_mat', activity_mat)
	if not activity_mat__dist_norm:
		activity_mat__dist_norm = _calc_activity_mat(dist_norm=True)
		_save_matrix('activity', 'activity_mat__dist_norm', activity_mat__dist_norm)
	_show_matrix(activity_mat)
	_show_matrix(activity_mat__dist_norm)

def _calc_activity_mat(dist_norm=False):
	'''Calculate activity matrix for all neighborhoods in region'''
	mat = {}
	con = psycopg2.connect(my.DB_CONN_STRING)
	cur = con.cursor()

	if not dist_norm:
		SQL = 'SELECT nh.id, count(*) \
			FROM (SELECT * FROM {rel_tweet} \
				WHERE user_id IN \
					(SELECT user_id FROM {rel_home} \
					WHERE ST_WithIN(geo, \
						(SELECT pol FROM {rel_nhood} \
						WHERE id = %s)))) AS tw, \
				(SELECT * FROM {rel_nhood} \
				WHERE id IN %s) AS nh \
			WHERE ST_WithIN(tw.geo, nh.pol) \
			GROUP BY nh.id'.format(rel_tweet=my.REL_TWEET, rel_home=my.REL_HOME, rel_nhood=my.REL_NHOOD)
		
		for from_id in _load_nhoodIDs():
			mat[from_id] = dict([(to_id, 0) for to_id in _load_nhoodIDs()])
			cur.execute(SQL, (from_id, tuple(_load_nhoodIDs())))
			records = cur.fetchall()
			for rec in records:
				mat[from_id][rec[0]] = rec[1]

	else:
		SQL = 'SELECT nh.id, ST_Distance_Sphere(ST_MakePoint(ST_Y(tw.geo), ST_X(tw.geo)), \
				ST_MakePoint(ST_Y(h.geo), ST_X(h.geo))) AS dist \
			FROM (SELECT * FROM {rel_tweet} \
				WHERE user_id IN \
					(SELECT user_id FROM {rel_home} \
					WHERE ST_WithIN(geo, \
						(SELECT pol FROM {rel_nhood} \
						WHERE id = %s)))) AS tw, \
				(SELECT * FROM {rel_nhood} \
				WHERE id IN %s) AS nh, \
				(SELECT * FROM {rel_home} \
					WHERE ST_WithIN(geo, \
						(SELECT pol FROM {rel_nhood} \
						WHERE id = %s))) as h \
			WHERE ST_WithIN(tw.geo, nh.pol) \
			AND h.user_id = tw.user_id'.format(rel_tweet=my.REL_TWEET, rel_home=my.REL_HOME, rel_nhood=my.REL_NHOOD)
		norm = _calc_dist_norm()

		for from_id in _load_nhoodIDs():
			mat[from_id] = dict([(to_id, 0) for to_id in _load_nhoodIDs()])
			cur.execute(SQL, (from_id, tuple(_load_nhoodIDs()), from_id))
			records = cur.fetchall()
			visit_dists = [rec for rec in records]

			visits = dict((v, 0) for v in list(set([vd[0] for vd in visit_dists])))
			for vd in visit_dists:
				if int(vd[1]) > 0 and int(vd[1]/100 + 1) < 150:
					visits[vd[0]] += 1.0 / norm[int(round(vd[1]/100 + 1))]

			for to_id in visits:
				mat[from_id][to_id] = int(visits[to_id])

	con.close()
	return mat


#
# VISITS
#
def calc_visits():
	'''Calculate visit matrix'''
	if not os.path.exists('data/' + my.DATA_FOLDER + 'visits/'):
		os.makedirs('data/' + my.DATA_FOLDER + 'visits/')
	visit_mat = _load_matrix('visits', 'visit_mat')
	visit_mat__dist_norm = _load_matrix('visits', 'visit_mat__dist_norm')
	
	if not visit_mat:
		visit_mat = _calc_visit_mat()
		_save_matrix('visits', 'visit_mat', visit_mat)
	if not visit_mat__dist_norm:
		visit_mat__dist_norm = _calc_visit_mat(dist_norm=True)
		_save_matrix('visits', 'visit_mat__dist_norm', visit_mat__dist_norm)
	_show_matrix(visit_mat)
	_show_matrix(visit_mat__dist_norm)
	
def _calc_visit_mat(dist_norm=False):
	'''Calculate visit matrix for all neighborhoods in region'''
	mat = {}
	con = psycopg2.connect(my.DB_CONN_STRING)
	cur = con.cursor()
	
	if not dist_norm:
		SQL = 'SELECT pts.id, count(*) \
			FROM (SELECT nh.id, user_id, (timestamp AT TIME ZONE \'{timezone}\')::date AS ds, count(*) \
				FROM (SELECT * FROM {rel_tweet} \
					WHERE user_id IN  \
						(SELECT user_id FROM {rel_home} \
						WHERE ST_WithIN(geo, \
							(SELECT pol FROM {rel_nhood} \
							WHERE id = %s)))) AS tw, \
					(SELECT * FROM {rel_nhood} \
					WHERE id IN %s) AS nh \
				WHERE ST_WithIN(tw.geo, nh.pol) \
				GROUP BY nh.id, user_id, ds) AS pts \
			GROUP BY (pts.id)'.format(rel_tweet=my.REL_TWEET, rel_home=my.REL_HOME, rel_nhood=my.REL_NHOOD, timezone=my.TIMEZONE)

		for from_id in _load_nhoodIDs():
			mat[from_id] = dict([(to_id, 0) for to_id in _load_nhoodIDs()])
			cur.execute(SQL, (from_id, tuple(_load_nhoodIDs())))
			records = cur.fetchall()
			for rec in records:
				mat[from_id][rec[0]] = rec[1]

	else:
		SQL = 'SELECT id, dist \
			FROM (SELECT nh.id, tw.user_id, (timestamp AT TIME ZONE \'{timezone}\')::date AS ds, \
					max(ST_Distance_Sphere(ST_MakePoint(ST_Y(tw.geo), ST_X(tw.geo)), ST_MakePoint(ST_Y(h.geo), ST_X(h.geo)))) as dist, count(*) \
				FROM (SELECT * FROM {rel_tweet} \
					WHERE user_id IN  \
						(SELECT user_id FROM {rel_home} \
						WHERE ST_WithIN(geo, \
							(SELECT pol FROM {rel_nhood} \
							WHERE id = %s)))) AS tw, \
					(SELECT * FROM {rel_nhood} \
					WHERE id IN %s) AS nh, \
					(SELECT * FROM {rel_home} \
						WHERE ST_WithIN(geo,  \
							(SELECT pol FROM {rel_nhood} \
							WHERE id = %s))) as h \
				WHERE ST_WithIN(tw.geo, nh.pol) \
				AND h.user_id = tw.user_id \
				GROUP BY nh.id, tw.user_id, ds) AS foo'.format(rel_tweet=my.REL_TWEET, rel_home=my.REL_HOME, rel_nhood=my.REL_NHOOD, timezone=my.TIMEZONE)
		norm = _calc_dist_norm()
		
		for from_id in _load_nhoodIDs():
			mat[from_id] = dict([(to_id, 0) for to_id in _load_nhoodIDs()])
			cur.execute(SQL, (from_id, tuple(_load_nhoodIDs()), from_id))
			records = cur.fetchall()
			visit_dists = [rec for rec in records]

			visits = dict((v, 0) for v in list(set([vd[0] for vd in visit_dists])))
			for vd in visit_dists:
				if int(vd[1]) > 0 and int(vd[1]/100 + 1) < 150:
					visits[vd[0]] += 1.0 / norm[int(round(vd[1]/100 + 1))]

			for to_id in visits:
				mat[from_id][to_id] = int(visits[to_id])

	con.close()
	return mat


#
# VISITORS
#
def calc_visitors():
	'''Calculate visitor matrix'''
	if not os.path.exists('data/' + my.DATA_FOLDER + 'visitors/'):
		os.makedirs('data/' + my.DATA_FOLDER + 'visitors/')
	visitor_mat = _load_matrix('visitors', 'visitor_mat')
	visitor_mat__dist_norm = _load_matrix('visitors', 'visitor_mat__dist_norm')
	
	if not visitor_mat:
		visitor_mat = _calc_visitor_mat()
		_save_matrix('visitors', 'visitor_mat', visitor_mat)
	_show_matrix(visitor_mat)


def _calc_visitor_mat():
	'''Calculate visitor matrix for all neighborhoods in region'''
	mat = {}
	SQL = 'SELECT nh.id, count(DISTINCT user_id) \
		FROM (SELECT * FROM {rel_tweet} \
			WHERE user_id IN \
				(SELECT user_id FROM {rel_home} \
				WHERE ST_WithIN(geo, \
					(SELECT pol FROM {rel_nhood} \
					WHERE id = %s)))) AS tw, \
			(SELECT * FROM {rel_nhood} \
			WHERE id IN %s) AS nh \
		WHERE ST_WithIN(tw.geo, nh.pol) \
		GROUP BY nh.id'.format(rel_tweet=my.REL_TWEET, rel_home=my.REL_HOME, rel_nhood=my.REL_NHOOD)
	con = psycopg2.connect(my.DB_CONN_STRING)
	cur = con.cursor()

	for from_id in _load_nhoodIDs():
		mat[from_id] = dict([(to_id, 0) for to_id in _load_nhoodIDs()])
		cur.execute(SQL, (from_id, tuple(_load_nhoodIDs())))
		records = cur.fetchall()
		for rec in records:
			mat[from_id][rec[0]] = rec[1]
	
	con.close()
	return mat


################################################################################
#
# NORMALIZE
#
def _calc_dist_norm():
	'''Calculate distance norm function [1-CDF]'''
	frac = dict([(i, 0) for i in range(1, 151)])
	count = 1
	with open('data/' + my.DATA_FOLDER + 'user_disp.csv', 'rb') as fp:
		csv_reader = csv.reader(fp, delimiter=',')
		for row in csv_reader:
			dist_i = int(int(row[1])/100)+1
			if dist_i > 0 and dist_i <= 150:
				frac[dist_i] += 1
				count += 1

	cdf = {}
	for i in range(1, 151):
		cdf[i] = sum([frac[j] for j in range(1, i+1)])/float(count)
	
	norm = {}
	for i in range(1, 151):
		norm[i] = 1-cdf[i]		# dist_norm_3
	
	return norm

# Tweet frequency normalization
def _apply_TwFreqNorm(visit_mat, visit_mat__norm=None):
	if visit_mat__norm:
		norm = _calc_TwFreqNorm(visit_mat__norm)
	else:
		norm = _calc_TwFreqNorm(visit_mat)

	visit_mat__out = dict([(from_id, dict()) for from_id in visit_mat])

	for from_id in visit_mat:
		for to_id in visit_mat:
			if norm[from_id] != 0:
				visit_mat__out[from_id][to_id] = visit_mat[from_id][to_id] / norm[from_id]
			else:
				visit_mat__out[from_id][to_id] = 0

	return visit_mat__out

def _calc_TwFreqNorm(visit_mat):
	norm = dict([(nid, sum(visit_mat[nid].values())) for nid in visit_mat])
	norm = dict([(nid, norm[nid]/float(sum(norm.values()))) for nid in norm])

	return norm


################################################################################
#
# UTILITY FUNCTIONS
#
_load_nhoodIDs = lambda: [int(nid) for nid in anyjson.loads(
				open('data/' + my.DATA_FOLDER + 'hood_ids.txt', 'rb').read())]

def _load_matrix(folder, file_name):
	if os.path.exists('data/' + my.DATA_FOLDER + folder + '/' + file_name + '.pickle'):
		with open('data/' + my.DATA_FOLDER  + folder + '/' + file_name + '.pickle', 'rb') as fp1:
			visit_mat = pickle.load(fp1)
		return visit_mat
	else:
		return None

def _save_matrix(folder, file_name, mat):
	with open('data/' + my.DATA_FOLDER  + folder + '/' + file_name + '.pickle', 'wb') as fp1:
		pickle.dump(mat, fp1)

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



'''def _save_visitMatJSONs():
# Stores all visit matrices in JSON format
# Reads from visit matrix pickles
	if not os.path.exists('data/' + my.DATA_FOLDER + 'visits/' + 'json/'):
		os.makedirs('data/' + my.DATA_FOLDER + 'visits/' + 'json/')

	_save_visitMatJSON('visit_mat')
	_save_visitMatJSON('visit_mat__twfreq_norm')
	_save_visitMatJSON('visit_mat__dist_norm')
	_save_visitMatJSON('visit_mat__dtf_norm')
'''
def _save_visitMatJSON(file_name):
	with open('data/' + my.DATA_FOLDER  + 'visits/' + file_name + '.pickle', 'rb') as fp1:
		visit_mat = pickle.load(fp1)
	with open('data/' + my.DATA_FOLDER  + 'visits/json/' + file_name + '.json', 'wb') as fp1:
		fp1.write(anyjson.dumps(visit_mat))




