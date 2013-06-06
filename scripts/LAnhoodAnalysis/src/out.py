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
import numpy
import anyjson
import psycopg2
import matplotlib
import matplotlib.pyplot as plt

from pylab import *
from PIL import Image
from pprint import pprint
from datetime import datetime
from scipy.optimize import leastsq
from matplotlib.ticker import FuncFormatter
from matplotlib.backends.backend_pdf import PdfPages

import settings as my
sys.path.insert(0, os.path.abspath('..'))

#
# REGION HOMES, POINTS JSON
#
def out_homes_and_points_json():
	'''Output: JSON of all homes and latlng in region'''
	with open('data/' + my.DATA_FOLDER + 'user_list.json', 'rb') as fpr:
		user_ids = anyjson.loads(fpr.read())
	user_ids = [int(user_id) for user_id in user_ids]
	print 'Read {0} user_ids'.format(len(user_ids))

	SQL = 'SELECT user_id, ST_X(geo), ST_Y(geo)\
		FROM {rel_home} \
		WHERE user_id IN %s'.format(rel_home=my.REL_HOME)

	con = psycopg2.connect(my.DB_CONN_STRING)
	cur = con.cursor()
	cur.execute(SQL, (tuple(user_ids), ))
	recs = cur.fetchall()
	homes = [[rec[1], rec[2]] for rec in recs]

	SQL = 'SELECT ST_X(geo), ST_Y(geo)\
		FROM {rel_tweet} \
		WHERE user_id IN %s'.format(rel_tweet=my.REL_TWEET)
	#	AND geo && ST_GeomFromGeoJSON(%s)'.format(rel_tweet=my.REL_TWEET)
	#cur.execute(SQL, (tuple(user_ids), bound_pol))
	cur.execute(SQL, (tuple(user_ids), ))
	recs = cur.fetchall()
	points = [[rec[0], rec[1]] for rec in recs]
	con.close()
	print 'Fetched {n_h} homes, {n_l} latlngs.'.format(n_h=len(homes), n_l=len(points))

	if not os.path.exists('data/' + my.DATA_FOLDER + 'region/'):
		os.makedirs('data/' + my.DATA_FOLDER + 'region/')
	with open('data/' + my.DATA_FOLDER + 'region/' + 'homes.json', 'wb') as fp:
		fp.write(anyjson.dumps(homes))
	with open('data/' + my.DATA_FOLDER + 'region/' + 'points.json', 'wb') as fp:
		fp.write(anyjson.dumps(points))


def out_hoodwise_latlng_json():
	'''Output: JSON of latlng by users of each nhood in region'''
	nhood_points = {}
	h_ids = tuple([int(nid) for nid in anyjson.loads(open('data/' + my.DATA_FOLDER + 'hood_ids.txt', 'rb').read())])
	with open('data/' + my.DATA_FOLDER + 'bound_pol.txt', 'rb') as fpr:
		bound_pol = fpr.read().strip()
	con = psycopg2.connect(my.DB_CONN_STRING)
	cur = con.cursor()
	for h_id in h_ids:
		print h_id
		SQL = 'SELECT user_id \
			FROM {rel_home} \
			WHERE ST_Within (geo, \
				(SELECT pol FROM {rel_nhood} \
					WHERE id=%s))'.format(rel_home=my.REL_HOME, rel_nhood=my.REL_NHOOD)
		
		cur.execute(SQL, (h_id, ))
		recs = cur.fetchall()
		user_ids = [rec[0] for rec in recs]
		if len(user_ids) > 0:
			SQL = 'SELECT ST_X(geo), ST_Y(geo)\
				FROM {rel_tweet} \
				WHERE user_id IN %s \
				AND geo && ST_GeomFromGeoJSON(%s)'.format(rel_tweet=my.REL_TWEET)

			cur.execute(SQL, (tuple(user_ids), bound_pol))
			recs = cur.fetchall()
			if len(recs) > 0:
				nhood_points[h_id] = [[rec[0], rec[1]] for rec in recs]
				print len(user_ids), len(nhood_points[h_id])
	con.close()

	if not os.path.exists('data/' + my.DATA_FOLDER + 'region/'):
		os.makedirs('data/' + my.DATA_FOLDER + 'region/')
	with open('data/' + my.DATA_FOLDER + 'region/' + 'nhood_points.json', 'wb') as fp:
		fp.write(anyjson.dumps(nhood_points))


