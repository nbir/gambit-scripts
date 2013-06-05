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
import time
import psycopg2
import anyjson
from multiprocessing import Pool

from datetime import *
from pytz import timezone, utc
from pprint import pprint as pprint

import numpy as np
from scipy.spatial import distance
from sklearn.cluster import DBSCAN

import matplotlib
import matplotlib.pyplot as plt
from pylab import *

def find_user_homes():
#	Get list of users with min_tweet tweets
	user_ids = []
	with open('data/' + my.DATA_FOLDER + 'user_list__min_tw.csv', 'rb') as fp:
		cr = csv.reader(fp, delimiter=',')
		for row in cr:
			user_id = int(row[0])
			user_ids.append(user_id)
	print 'Read {0} user_ids'.format(len(user_ids))
	
	# Serial version
	#for user_id in user_ids:
	#	_find_and_store_home(user_id)
	
	# Multi-threading version
	pool = Pool(processes=my.PROCESSES)
	pool.map(_find_and_store_home, user_ids)


def _find_and_store_home(user_id):
# MapReduce: Map Function. Finds home and stores to db for one user_id
	
	# Calculate hour range (conv: LOCAL to UTC)
	h_start, h_end = (my.HH_START - my.TZ_OFFSET) % 24, (my.HH_END - my.TZ_OFFSET) % 24
	if h_start < h_end:
		hour_list = range(h_start, h_end+1)
	else:
		hour_list = range(h_start, 24) + range(0, h_end+1)

	# Tweets only from bound_pol
	with open('data/' + my.DATA_FOLDER + 'bound_pol.txt', 'rb') as fpr:
		bound_pol = fpr.read().strip()

	# DB connection
	con = psycopg2.connect(my.DB_CONN_STRING)
	cur = con.cursor()

	# All tweets count
	SQL = 'SELECT count(*) \
			FROM t3_tweet_6 \
			WHERE user_id = %s \
			AND extract(hour from timestamp) in %s' \
			+ my.QUERY_CONSTRAINT
	cur.execute(SQL, (user_id, tuple(hour_list)))
	records = cur.fetchall()
	total_tw = int(records[0][0])

	# Tweets only inside bound_pol
	SQL = 'SELECT ST_X(geo), ST_Y(geo) \
			FROM t3_tweet_6 \
			WHERE user_id = %s \
			AND extract(hour from timestamp) in %s \
			AND geo && ST_GeomFromGeoJSON(%s) '\
			+ my.QUERY_CONSTRAINT \
			+ 'ORDER BY timestamp'
	cur.execute(SQL, (user_id, tuple(hour_list), bound_pol))
	records = cur.fetchall()
	inside_tw = len(records)
	con.close()
	
	# Check tweet ratio INSIDE:TOTAL
	ratio = round(float(inside_tw) / total_tw, 2)
	print '{user_id}:'.format(user_id=user_id).rjust(25) + '\t{ins}/{tot} = {ratio} inside:total ratio.'.format(ratio=ratio, ins=inside_tw, tot=total_tw)

	# Trim if there are too many points
	if inside_tw > my.MAX_TW_TO_CLUSTER:
		records = records[:my.MAX_TW_TO_CLUSTER]

	# Find home only if INSIDE:TOTAL meets minimum requirement
	if ratio >= my.MIN_FRAC_INSIDE:
		points = [[float(ll[0]), float(ll[1])] for ll in records]
		fh = FindHome(points, my.DBSCAN_EPS, my.DBSCAN_MIN)
		home = fh.getHome()
		
		if home:
			# Store to database
			try:
				con = psycopg2.connect(my.DB_CONN_STRING)
				cur = con.cursor()
				p = {
						"type"				: "Point",
						"coordinates"	:	home
						}
				rec = (user_id, anyjson.dumps(p))
				SQL = 'INSERT INTO t4_home VALUES (%s, ST_GeomFromGeoJSON(%s))';
				cur.execute(SQL, rec)
				con.commit()
				con.close()
			except:
				print '%s:\tCouldn\'t save to database!' % user_id

	
################################################################################
# Load lost of all nhoods in region
_load_nhoodIDs = lambda: [int(nid) for nid in anyjson.loads(open('data/' + my.DATA_FOLDER + 'hood_ids.txt', 'rb').read())]


def find_daily_disp():
#	Find daily max displacement for users
# Also generated displacement plots for each user
	if my.USER_IDS_FROM_DB:
		con = psycopg2.connect(my.DB_CONN_STRING)
		cur = con.cursor()
		SQL = 'SELECT user_id \
					FROM t4_home \
					WHERE ST_Within (geo, ST_UNION( \
						ARRAY(SELECT pol FROM t4_nhood \
							WHERE id in %s)))'
		cur.execute(SQL, (tuple(_load_nhoodIDs()), ))
		records = cur.fetchall()
		con.close()
		user_ids = [int(rec[0]) for rec in records]

	else:
		with open('data/' + my.DATA_FOLDER + 'user_list.csv', 'rb') as fpr:
			cr = csv.reader(fpr, delimiter=',')
			user_ids = [int(row[0]) for row in cr]

	print 'Read {0} user_ids'.format(len(user_ids))

	with open('data/' + my.DATA_FOLDER + 'user_list.json', 'wb') as fpw:
		fpw.write(anyjson.dumps(user_ids))

	#for user_id in user_ids:
	#	_find_daily_disp(user_id)
	#	break

	pool = Pool(processes=my.PROCESSES)
	pool.map(_find_daily_disp, user_ids)

def _find_daily_disp(user_id):
	## Displacement csv
	with open('data/' + my.DATA_FOLDER + 'city_bound_pol.txt', 'rb') as fpr:
		bound_pol = fpr.read().strip()

	con = psycopg2.connect(my.DB_CONN_STRING)
	cur = con.cursor()
	SQL = 'SELECT ST_X(geo), ST_Y(geo) \
			FROM t4_home \
			WHERE user_id = %s '
	cur.execute(SQL, (user_id,))
	records = cur.fetchall()

	if len(records) > 0:
		home = records[0]
		#print home

		SQL = 'SELECT ST_X(geo), ST_Y(geo), timestamp \
				FROM t3_tweet_6 \
				WHERE user_id = %s \
				AND geo && ST_GeomFromGeoJSON(%s) '\
				+ my.QUERY_CONSTRAINT \
				+ 'ORDER BY timestamp'
		cur.execute(SQL, (user_id, bound_pol))
		records = cur.fetchall()
		con.close()

		user_disp = {}
		x, y = [], []

		for rec in records:
			lat, lng, ts = rec
			x.append(lng-home[1])
			y.append(lat-home[0])
			
			ts = ts.replace(tzinfo=utc).astimezone(timezone(my.TIMEZONE))
			ds = ts.date().isoformat()

			if ds not in user_disp:
				user_disp[ds] = 0
			try:
				dist = int(round(geo.distance(geo.xyz(home[0], home[1]), geo.xyz(lat, lng))))
			except:
				dist = 0
			if dist > user_disp[ds]:
				user_disp[ds] = dist
			#print dist

		if not os.path.exists('data/' + my.DATA_FOLDER + 'user_disp/'):
			os.makedirs('data/' + my.DATA_FOLDER + 'user_disp/')
		with open('data/' + my.DATA_FOLDER + 'user_disp/' + str(user_id) + '.csv', 'wb') as fpw:
			cw = csv.writer(fpw, delimiter=',')
			for ds in user_disp:
				cw.writerow([user_id, user_disp[ds], ds])


		## Displacement plot
		fig = plt.figure(figsize=(5,5))
		ax = fig.add_subplot(111)
		plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
		ax.set_autoscaley_on(False)
		ax.set_ylim([-0.5,0.5])
		ax.set_xlim([-0.5,0.5])
		ax.set_yticks([0.0])
		ax.set_xticks([0.0])
		ax.set_yticklabels([])
		ax.set_xticklabels([])
		ax.grid(True)
		ax.plot(x, y, 'b+')
		ax.plot([0], [0], 'r^')
		ax.text(-0.45, -0.45, str(user_id), fontsize=10)
		if not os.path.exists('data/' + my.DATA_FOLDER + 'plot_disp/'):
			os.makedirs('data/' + my.DATA_FOLDER + 'plot_disp/')
		plt.savefig('data/' + my.DATA_FOLDER + 'plot_disp/' + str(user_id) + '.png')

	else:
		con.close()
		print 'Missed 1 user_id!'

def join_daily_disp():
# Join max displacement for all users into one file
	fpw = open('data/' + my.DATA_FOLDER + 'user_disp.csv', 'wb')
	cw = csv.writer(fpw, delimiter=',')

	doc_path = 'data/' + my.DATA_FOLDER + 'user_disp/'
	doc_names = os.listdir(doc_path)
	if '.DS_Store' in doc_names:
		doc_names.remove('.DS_Store')
	
	for doc in doc_names:
		with open(doc_path + doc, 'rb') as fp1:
			cr = csv.reader(fp1, delimiter=',')
			for row in cr:
				user_id, dist, date = int(row[0]), int(row[1]), row[2]
				cw.writerow([user_id, dist, date])
	fpw.close()



