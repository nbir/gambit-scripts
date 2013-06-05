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

import csv
import psycopg2

def get_min_tweet_users():
#	Get list of users with min_tweet tweets
	fp = open('data/' + my.DATA_FOLDER + 'user_list__min_tw.csv', 'wb')
	cw = csv.writer(fp, delimiter=',')

	con = psycopg2.connect(my.DB_CONN_STRING)
	cur = con.cursor()

	hour_list = []
	h_start, h_end = (my.HH_START - my.TZ_OFFSET) % 24, (my.HH_END - my.TZ_OFFSET) % 24
	if h_start < h_end:
		hour_list = range(h_start, h_end+1)
	else:
		hour_list = range(h_start, 24) + range(0, h_end+1)
	print 'Night time hours in {}'.format(hour_list)

	with open('data/' + my.DATA_FOLDER + 'bound_pol.txt', 'rb') as fpr:
		bound_pol = fpr.read().strip()
	#print 'Bound Pol: {}'.format(bound_pol)

	SQL = 'SELECT user_id, count(id) as count \
				FROM t3_tweet_6 \
				WHERE extract(hour from timestamp) in %s \
				AND geo && ST_GeomFromGeoJSON(%s) '\
				+ my.QUERY_CONSTRAINT + \
				'GROUP BY user_id \
				ORDER BY count DESC'

	cur.execute(SQL, (tuple(hour_list), bound_pol))
	recs = cur.fetchall()
	con.close()

	n_users = 0
	for rec in recs:
		user_id, count = rec
		user_id, count = int(user_id), int(count)
		if count > my.MIN_NIGHT_TW and count < my.MAX_NIGHT_TW:
			cw.writerow([user_id, count])
			n_users += 1

	fp.close()
	print '{} users with minimum night tweets'.format(n_users)

	



