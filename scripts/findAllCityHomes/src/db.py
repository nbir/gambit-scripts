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
import pickle
import anyjson
import psycopg2
from pprint import pprint


def create_home_db():
# Create t4_home relation
	con = psycopg2.connect(my.DB_CONN_STRING)
	cur = con.cursor()

	SQL = '''CREATE TABLE "{rel_home}" ( \
					"user_id" int PRIMARY KEY\
				);	\
	\
	SELECT AddGeometryColumn('public', '{rel_home}', 'geo', 0, 'POINT', 2);'''.format(rel_name=my.REL_HOME)

	cur.execute(SQL)
	con.commit()
	con.close()

	