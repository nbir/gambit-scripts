# Gambit scripts
#
# Copyright (C) USC Information Sciences Institute
# Author: Nibir Bora <nbora@usc.edu>
# URL: <http://cbg.isi.edu/>
# For license information, see LICENSE

import os
import sys
import csv
import pickle
import anyjson
import psycopg2
from pprint import pprint

import settings as my
sys.path.insert(0, os.path.abspath('..'))

#
# DB - NHOOD
#
def create_hood_db():
	'''Create table t4_hood relation'''
	SQL = '''CREATE TABLE "{rel_nhood}" ( \
			"id" int PRIMARY KEY,\
			"name" varchar(64),\
			"region" varchar(5)\
		);	\
		\
		SELECT AddGeometryColumn('public', '{rel_nhood}', 'pol', 0, 'POLYGON', 2);'''.format(rel_nhood=my.REL_NHOOD)

	con = psycopg2.connect(my.DB_CONN_STRING)
	cur = con.cursor()
	cur.execute(SQL)
	con.commit()
	con.close()

def store_hoods_db():
	'''Store all nhood information to database'''
	with open('data/' + my.DATA_FOLDER + 'all-hoods.json', 'rb') as fp1:
		all_hoods = anyjson.deserialize(fp1.read())

	con = psycopg2.connect(my.DB_CONN_STRING)
	cur = con.cursor()
	for hood in all_hoods:
		h_id, name, region = int(hood['id']), hood['name'], hood['region']
		pol = []
		for ll in hood['polygon']:
			pol.append([float(ll[0]), float(ll[1])])
		p = {
			"type"			: "Polygon",
			"coordinates"	:	[pol]
			}
		SQL = 'INSERT INTO {rel_nhood} VALUES (%s, %s, %s, ST_GeomFromGeoJSON(%s))'.format(rel_nhood=my.REL_NHOOD);

		r = (h_id, name, region, anyjson.dumps(p))
		cur.execute(SQL, r)
	con.commit()
	con.close()

def check_hoods_db():
	'''Checks nhood relation. Print tuples'''
	SQL = 'select ST_AsGeoJSON (pol) from t4_nhood limit 1'

	con = psycopg2.connect(my.DB_CONN_STRING)
	cur = con.cursor()
	cur.execute(SQL)
	recs = cur.fetchall()
	con.close()

	for r in recs:
		print r
		r = anyjson.loads(r[0])
		print r['coordinates'][0]


#
# DB - HOME
#
def create_home_db():
	'''Create t4_home relation'''
	SQL = '''CREATE TABLE "{rel_home}" ( \
			"user_id" int PRIMARY KEY\
		);	\
		\
		SELECT AddGeometryColumn('public', '{rel_home}', 'geo', 0, 'POINT', 2);'''.format(rel_home=my.REL_HOME)

	con = psycopg2.connect(my.DB_CONN_STRING)
	cur = con.cursor()
	cur.execute(SQL)
	con.commit()
	con.close()


#
# Hollenbeck homes / nhoods
#
def store_hbk_homes_db():
	'''Store Hollenbeck homes into db'''
	con = psycopg2.connect(my.DB_CONN_STRING)
	cur = con.cursor()

	with open('data/' + my.DATA_FOLDER + 'user_list.csv', 'rb') as fpr:
		cr = csv.reader(fpr, delimiter=',')
		user_ids = [int(row[0]) for row in cr]
		
	with open('data/' + my.DATA_FOLDER + 'user_home.csv', 'rb') as fpr:
		cr = csv.reader(fpr, delimiter=',')
		for row in cr:
			user_id, lat, lng = row
			user_id, lat, lng = int(user_id), float(lat), float(lng)
			if user_id in user_ids:
				SQL = 'SELECT * FROM {rel_home} WHERE user_id = %s'.format(rel_home=my.REL_HOME)
				cur.execute(SQL, (user_id, ))
				recs = cur.fetchall()
				if len(recs) == 0:
					try:
						p = {
							"type"			: "Point",
							"coordinates"	: [lat,lng]
							}
						SQL = 'INSERT INTO {rel_home} VALUES (%s, ST_GeomFromGeoJSON(%s))'.format(rel_home=my.REL_HOME);

						rec = (user_id, anyjson.dumps(p))
						cur.execute(SQL, rec)
					except:
						print '%s:\tCouldn\'t save to database!' % user_id

	con.commit()
	con.close()

def store_hbk_hoods_db():
	'''Store HBK nhood information to database'''
	loc_data__out = []
	with open('data/' + my.DATA_FOLDER + 'hbk_loc_data.json', 'rb') as fp1:
		all_hoods = anyjson.deserialize(fp1.read())

	con = psycopg2.connect(my.DB_CONN_STRING)
	cur = con.cursor()

	for hood in all_hoods:
		h_id, name, region = int(hood['id']), str(hood['name']).replace('HBK', '').replace('.kml', '').replace('_', ' ') , 'HBK'
		if h_id == 24:	# Skip Arroyo Seco
			continue

		pol = []
		for ll in hood['polygon']:
			if ll[0] < 0:
				pol.append([float(ll[1]), float(ll[0])])
			else:
				pol.append([float(ll[0]), float(ll[1])])
		
		p = {
			"type"			: "Polygon",
			"coordinates"	:	[pol]
			}
		r = (h_id, name, region, anyjson.dumps(p))

		print h_id, name
		loc_data__out.append({
			'id'	: h_id,
	    	'name'	: name,
	    	'polygon': pol
			})
		
		SQL = 'INSERT INTO t4_nhood VALUES (%s, %s, %s, ST_GeomFromGeoJSON(%s))';
		cur.execute(SQL, r)
	con.commit()
	con.close()

	with open('data/' + my.DATA_FOLDER  + 'hbk_loc_data__out' + '.json', 'wb') as fp1:
		fp1.write(anyjson.dumps(loc_data__out))
	

	