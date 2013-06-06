# Gambit scripts
#
# Copyright (C) USC Information Sciences Institute
# Author: Nibir Bora <nbora@usc.edu>
# URL: <http://cbg.isi.edu/>
# For license information, see LICENSE

import os
import sys
import csv
import anyjson
import psycopg2

from lib.findhome import *
from multiprocessing import Pool
from pprint import pprint as pprint

import settings as my
sys.path.insert(0, os.path.abspath('..'))


#
# DATABASE
#
def create_home_db():
	'''Create t4_home relation'''
	SQL = '''CREATE TABLE "{rel_home}" ( \
			"user_id" int PRIMARY KEY\
		); \
		\
		SELECT AddGeometryColumn('public', '{rel_home}', 'geo', 0, 'POINT', 2);'''.format(rel_home=my.REL_HOME)

	con = psycopg2.connect(my.DB_CONN_STRING)
	cur = con.cursor()
	cur.execute(SQL)
	con.commit()
	con.close()

#
# USERS
#
def get_min_tweet_users():
	'''Get list of users with min_tweet tweets'''
	h_start, h_end = my.HH_START, my.HH_END
	hour_list = range(h_start, h_end+1) if h_start < h_end else range(h_start, 24) + range(0, h_end+1)
	print 'Night time hours in {hours}'.format(hours=hour_list)

	SQL = 'SELECT user_id, COUNT(id) as count \
		FROM {rel_tweet} \
		WHERE extract(hour FROM timestamp AT TIME ZONE \'{timezone}\') IN %s '.format(rel_tweet=my.REL_TWEET, 
										rel_home=my.REL_HOME, rel_nhood=my.REL_NHOOD, timezone=my.TIMEZONE) \
		+ my.QUERY_CONSTRAINT + \
		'GROUP BY user_id \
		ORDER BY count DESC'

	con = psycopg2.connect(my.DB_CONN_STRING)
	cur = con.cursor()
	cur.execute(SQL, (tuple(hour_list),))
	recs = cur.fetchall()
	con.close()

	fp = open('data/' + my.DATA_FOLDER + 'user_list__min_tw.csv', 'wb')
	cw = csv.writer(fp, delimiter=',')
	n_users = 0
	for rec in recs:
		user_id, count = rec
		user_id, count = int(user_id), int(count)
		if count > my.MIN_NIGHT_TW and count < my.MAX_NIGHT_TW:
			cw.writerow([user_id, count])
			n_users += 1
	fp.close()
	print '{n_users} users with minimum night tweets'.format(n_users=n_users)


#
# HOMES
#
def find_user_homes():
	'''Find home locations for all user_id in user_list__min_tw.csv'''
	with open('data/' + my.DATA_FOLDER + 'user_list__min_tw.csv', 'rb') as fp:
		cr = csv.reader(fp, delimiter=',')
		user_ids = [int(row[0]) for row in cr]
	print '{0} user_ids read from file'.format(len(user_ids))
	
	# Get list of user_id who's home has been computed
	con = psycopg2.connect(my.DB_CONN_STRING)
	cur = con.cursor()
	SQL = 'SELECT user_id FROM {rel_home}'.format(rel_home=my.REL_HOME)
	cur.execute(SQL)
	recs = cur.fetchall()
	con.close()
	user_ids_exist = [int(rec[0]) for rec in recs]
	print '{0} user_ids previously calculated'.format(len(user_ids_exist))

	user_ids = [uid for uid in user_ids if uid not in user_ids_exist]
	print '{0} user_ids to find home'.format(len(user_ids))
	
	# Serial processing version
	#for user_id in user_ids[:100]:
	#	_find_and_store_home(user_id)

	# Multi-threaded version
	pool = Pool(processes=my.PROCESSES)
	pool.map(_find_and_store_home, user_ids)

def _find_and_store_home(user_id):
	'''MapReduce: Map Function. Finds home and stores to db for one user_id'''
	print user_id
	h_start, h_end = my.HH_START, my.HH_END
	hour_list = range(h_start, h_end+1) if h_start < h_end else range(h_start, 24) + range(0, h_end+1)

	SQL = 'SELECT ST_X(geo), ST_Y(geo) \
		FROM {rel_tweet} \
		WHERE user_id = %s \
		AND extract(hour FROM timestamp AT TIME ZONE \'{timezone}\') IN %s '.format(rel_tweet=my.REL_TWEET, 
										rel_home=my.REL_HOME, rel_nhood=my.REL_NHOOD, timezone=my.TIMEZONE) \
		+ my.QUERY_CONSTRAINT \
		+ 'ORDER BY timestamp'

	con = psycopg2.connect(my.DB_CONN_STRING)
	cur = con.cursor()
	cur.execute(SQL, (user_id, tuple(hour_list)))
	records = cur.fetchall()
	n_tweets = len(records)
	con.close()
	
	points = [[float(ll[0]), float(ll[1])] for ll in records]
	min_samples = max(my.DBSCAN_MIN_ABS, int(my.DBSCAN_MIN_FRAC * n_tweets))
	fh = FindHome(points, my.DBSCAN_EPS, min_samples)
	home = fh.getHome()
	
	if home:
		try:
			p = {
				"type"			: "Point",
				"coordinates"	: home
				}
			SQL = 'INSERT INTO {rel_home} VALUES (%s, ST_GeomFromGeoJSON(%s))'.format(rel_home=my.REL_HOME)

			con = psycopg2.connect(my.DB_CONN_STRING)
			cur = con.cursor()
			rec = (user_id, anyjson.dumps(p))
			cur.execute(SQL, rec)
			con.commit()
			con.close()
		except:
			print '{user_id}:\tCouldn\'t save to database!'.format(user_id=user_id)
	

#
# JSON HOME LOCATIONS
#
def out_all_homes_json():
	'''Output JSON of all identified user homes'''
	SQL = 'SELECT user_id, ST_X(geo), ST_Y(geo)\
		FROM {rel_home}'.format(rel_home=my.REL_HOME)

	con = psycopg2.connect(my.DB_CONN_STRING)
	cur = con.cursor()
	cur.execute(SQL)
	recs = cur.fetchall()
	con.close()

	homes = {}
	for rec in recs:
		user_id, lat, lng = rec
		user_id, lat, lng = int(user_id), float(lat), float(lng)
		homes[user_id] = [lat, lng]
		
	with open('data/' + my.DATA_FOLDER + 'user_home_all.json', 'wb') as fp:
		fp.write(anyjson.dumps(homes))
