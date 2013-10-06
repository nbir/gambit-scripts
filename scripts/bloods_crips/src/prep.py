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
import lib.geo as geo
from pprint import pprint
from xml.etree import ElementTree

import settings as my
sys.path.insert(0, os.path.abspath('..'))

#
# KML
#
def parse_kml():
	"""Parse kml file with all gang boundaries"""
	geo_data = {}
	loc_data = []
	loc_desc = {}
	hood_ids = []
	kml = 'data/' + my.DATA_FOLDER + my.GANGS_KML
	tree = ElementTree.parse(kml)
	items = tree.findall('.//{http://earth.google.com/kml/2.2}Placemark')
	id = 0
	for item in items:
		id += 1
		name = item.find('.//{http://earth.google.com/kml/2.2}name').text
		desc = item.find('.//{http://earth.google.com/kml/2.2}description').text
		cord = item.find(
				'.//{http://earth.google.com/kml/2.2}coordinates').text
		cord = cord.strip().split('\n')
		pol = []
		for ll in cord:
			ll = ll.split(',')
			lng = float(ll[0])
			lat = float(ll[1])
			pol.append([lat, lng])
		
		geo = {
			"type" : "Polygon",
			"coordinates" : [pol]
			}
		geo_ = {
			"id" : id,
			"name" : name,
			"geo" : geo
			}
		geo_data[id] = geo_
		loc = {
			"id" : id,
			"name" : name,
			"polygon" : pol
			}
		loc_data.append(loc)
		loc_desc[id] = desc
		hood_ids.append(str(id))

	with open('data/' + my.DATA_FOLDER + 'geo_data.json', 'wb') as fp:
		fp.write(anyjson.dumps(geo_data))
	with open('data/' + my.DATA_FOLDER + 'loc_data.json', 'wb') as fp:
		fp.write(anyjson.dumps(loc_data))
	with open('data/' + my.DATA_FOLDER + 'loc_desc.json', 'wb') as fp:
		fp.write(anyjson.dumps(loc_desc))
	with open('data/' + my.DATA_FOLDER + 'hood_ids.json', 'wb') as fp:
		fp.write(anyjson.dumps(hood_ids))

def show_names():
	"""Show names of all gangs"""
	loc_data = anyjson.loads(
		open('data/' + my.DATA_FOLDER + 'loc_data.json', 'rb').read())
	names = []
	for loc in loc_data:
		name = loc['name'].replace('W/S ','')\
						.replace('E/S ','')\
						.replace('S/S ','')
		names.append([loc['id'], name])
	names = sorted(names, key=lambda x: x[1])
	for id, name in names:
		print '{id}\t{name}'.format(id=id, name=name)
	print '\n\t{}'.format(len(names))

def in_rivalries():
	"""Console input rivalries for each gang"""
	rivs = {}
	with open('data/' + my.DATA_FOLDER + 'loc_desc.json', 'rb') as fp:
		loc_desc = anyjson.loads(fp.read())
	for id, desc in loc_desc.items():
		print '{id}\t{desc}\n'.format(id=id, 
									desc=desc.replace(',', ',\n')\
											.replace('.', '.\n')\
											.replace('and', 'and\n'))
		riv = raw_input('Rivalries? : ')
		if riv == '-1':
			break
		riv = riv.split()
		print riv
		rivs[id] = riv
		os.system('clear')
	pprint(rivs)
	with open('data/' + my.DATA_FOLDER + 'rivalries.json', 'wb') as fp:
		fp.write(anyjson.dumps(rivs))

def out_rivalry_mat():
	'''Save rivalry matrix in json format'''
	with open('data/' + my.DATA_FOLDER + 'rivalries.json', 'rb') as fp:
		rivs = anyjson.loads(fp.read())
	ids = [int(i) for i in rivs]
	mat = dict((a, dict((b, 0) for b in ids)) for a in ids)

	for a in rivs:
		for b in rivs[a]:
			a = int(a)
			b = int(b)
			if a != b:
				mat[a][b] = 1
				mat[b][a] = 1

	with open('data/' + my.DATA_FOLDER  + 'rivalry_mat' + '.pickle', 'wb') as fp:
		pickle.dump(mat, fp)
	with open('data/' + my.DATA_FOLDER  + 'rivalry_mat' + '.json', 'wb') as fp:
		fp.write(anyjson.dumps(mat))


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
	with open('data/' + my.DATA_FOLDER + 'geo_data.json', 'rb') as fp1:
		geo_data = anyjson.loads(fp1.read())
	con = psycopg2.connect(my.DB_CONN_STRING)
	cur = con.cursor()
	
	for id, geo_ in geo_data.items():
		name = geo_['name']
		region = name.split()[0]
		geo = geo_['geo']

		SQL = '''INSERT INTO {rel_nhood} 
				VALUES (%s, %s, %s, ST_GeomFromGeoJSON(%s))
				'''.format(rel_nhood=my.REL_NHOOD);
		r = (id, name, region, anyjson.dumps(geo))
		cur.execute(SQL, r)
	con.commit()
	con.close()


#
# BASELINE RIVALRIES
#
def calc_baseline_riv():
	"""Calculate baseline rivalries for all gangs"""
	with open('data/' + my.DATA_FOLDER + 'loc_data.json', 'rb') as fp:
		loc_data = anyjson.loads(fp.read())
	pols = dict((int(loc['id']), loc['polygon'][:-1]) for loc in loc_data)
	root = {}
	for loc in loc_data:
		id = loc['id']
		name = loc['name'].lower()
		if 'blood' in name or 'piru' in name:
			root[id] = 'blood'
		elif 'crip' in name:
			root[id] = 'crip'
		else:
			root[id] = 'unknown'
	ids = [i for i in pols]
	mat = dict((a, dict((b, 0) for b in ids)) for a in ids)

	c = 0
	for a in ids:
		for b in ids:
			if root[a] != root[b]:
				close = _closest_dist(pols[a], pols[b])
				span = _territory_span(pols[a])
				if close < span/2:
					c += 1
					mat[a][b] = 1
					mat[b][a] = 1
	print '{c} links marked as rivalries.'.format(c=c)

	with open('data/' + my.DATA_FOLDER  + 'rivalry_baseline' + '.pickle', 'wb') as fp:
		pickle.dump(mat, fp)
	with open('data/' + my.DATA_FOLDER  + 'rivalry_baseline' + '.json', 'wb') as fp:
		fp.write(anyjson.dumps(mat))



def _closest_dist(pol_a, pol_b):
	'''Find the closest distance between pol_a and pol_b.
	Closest among set of end points of line segments in pol_a and pol_b'''
	min_dist = 15000
	for a in pol_a:
		for b in pol_b:
			try:
				dist = int(geo.distance(geo.xyz(a[0], a[1]), geo.xyz(b[0], b[1])))
				min_dist = dist if dist < min_dist else min_dist
			except:
				print 'Error calculating distance!'
	return min_dist

def _territory_span(pol):
	'''Find the spanning distance of the territory.
	i.e. the maximum distance between any two end points of line segments in pol'''
	max_dist = 0
	for a in pol:
		for b in pol:
			try:
				dist = int(geo.distance(geo.xyz(a[0], a[1]), geo.xyz(b[0], b[1])))
				max_dist = dist if dist > max_dist else max_dist
			except:
				print 'Error calculating distance!'
	return max_dist
