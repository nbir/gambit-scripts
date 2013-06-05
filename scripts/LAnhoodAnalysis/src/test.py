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


from lib.findhome import *


def test_home():
#	Get list of users with min_tweet tweets
	user_ids = []
	with open('data/' + my.DATA_FOLDER + 'user_list__min_tw.csv', 'rb') as fp:
		cr = csv.reader(fp, delimiter=',')
		for row in cr:
			user_id = int(row[0])
			user_ids.append(user_id)
	print 'Read {0} user_ids'.format(len(user_ids))
	
	# Serial version
	for user_id in user_ids[:10]:
		_find_and_store_home(user_id)
	
	# Multi-threading version
	#pool = Pool(processes=my.PROCESSES)
	#pool.map(_find_and_store_home, user_ids)


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

	if ratio >= my.MIN_FRAC_INSIDE:
		points = [[float(ll[0]), float(ll[1])] for ll in records]
		fh = FindHome(points, my.DBSCAN_EPS, my.DBSCAN_MIN)
		print fh.getHome()
		print fh.getCenters()



