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

import anyjson
import psycopg2
from pprint import pprint


def out_all_homes_json():
#	Output JSON of all identified user homes
	con = psycopg2.connect(my.DB_CONN_STRING)
	cur = con.cursor()

	SQL = 'SELECT user_id, ST_X(geo), ST_Y(geo)\
				FROM {rel_name}'.format(rel_name=my.REL_HOME)
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


