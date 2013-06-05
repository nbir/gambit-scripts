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
from lib.findhome import *

import csv
import psycopg2
import anyjson
from multiprocessing import Pool

from pprint import pprint as pprint


def find_user_homes():
	#	Get list of users with min_tweet tweets
	user_ids = []
	with open('data/' + my.DATA_FOLDER + 'user_list__min_tw.csv', 'rb') as fp:
		cr = csv.reader(fp, delimiter=',')
		user_ids = [int(row[0]) for row in cr]
	print '{0} user_ids read from file'.format(len(user_ids))
	
	# Get list of user_id who's home has been computed
	con = psycopg2.connect(my.DB_CONN_STRING)
	cur = con.cursor()
	SQL = 'SELECT user_id FROM {rel_name}'.format(rel_name=my.REL_HOME)
	cur.execute(SQL)
	recs = cur.fetchall()
	con.close()
	user_ids_exist = [int(rec[0]) for rec in recs]
	print '{0} user_ids previously calculated'.format(len(user_ids_exist))

	# Final user_id list
	user_ids = [uid for uid in user_ids if uid not in user_ids_exist]
	print '{0} user_ids to find home'.format(len(user_ids))
	
	# Serial version
	#for user_id in user_ids[:100]:
	#	_find_and_store_home(user_id)
	
	# Multi-threading version
	pool = Pool(processes=my.PROCESSES)
	pool.map(_find_and_store_home, user_ids)


def _find_and_store_home(user_id):
# MapReduce: Map Function. Finds home and stores to db for one user_id
	print user_id
	
	# Calculate hour range (conv: LOCAL to UTC)
	h_start, h_end = (my.HH_START - my.TZ_OFFSET) % 24, (my.HH_END - my.TZ_OFFSET) % 24
	if h_start < h_end:
		hour_list = range(h_start, h_end+1)
	else:
		hour_list = range(h_start, 24) + range(0, h_end+1)

	# DB connection
	con = psycopg2.connect(my.DB_CONN_STRING)
	cur = con.cursor()

	# Tweets only inside bound_pol
	SQL = 'SELECT ST_X(geo), ST_Y(geo) \
			FROM t3_tweet_6 \
			WHERE user_id = %s \
			AND extract(hour from timestamp) in %s '\
			+ my.QUERY_CONSTRAINT \
			+ 'ORDER BY timestamp'
	cur.execute(SQL, (user_id, tuple(hour_list)))
	records = cur.fetchall()
	n_tweets = len(records)
	con.close()
	
	min_samples = max(my.DBSCAN_MIN_ABS, int(my.DBSCAN_MIN_FRAC * n_tweets))

	# Trim if there are too many points
	#if n_tweets > my.MAX_TW_TO_CLUSTER:
	#	records = records[:my.MAX_TW_TO_CLUSTER]

	points = [[float(ll[0]), float(ll[1])] for ll in records]
	
	fh = FindHome(points, my.DBSCAN_EPS, min_samples)
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
			SQL = 'INSERT INTO {rel_hame} VALUES (%s, ST_GeomFromGeoJSON(%s))'.format(rel_name=my.REL_HOME)
			cur.execute(SQL, rec)
			con.commit()
			con.close()
		except:
			print '{user_id}:\tCouldn\'t save to database!'.format(user_id=user_id)
	
