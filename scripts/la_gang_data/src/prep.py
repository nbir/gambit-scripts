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
from lib import ogr2ogr
from pykml import parser
from pprint import pprint

import settings as my
sys.path.insert(0, os.path.abspath('..'))


def shp_to_kml():
	"""Convert all shp files to kml files."""	
	folders = os.listdir('data/' + my.DATA_FOLDER + '/shp/')
	if '.DS_Store' in folders:
		folders.remove('.DS_Store')
	#print folders
	for folder in folders:
		print '\n' + folder + '\n'
		path = 'data/' + my.DATA_FOLDER + 'shp/' + folder + '/'
		kml_path = 'data/' + my.DATA_FOLDER + 'kml/' + \
					folder.replace(' Division Gangs', '') + '/'
		if not os.path.exists(kml_path):
			os.makedirs(kml_path)

		files = os.listdir(path)
		if '.DS_Store' in files:
			files.remove('.DS_Store')
		files_ = []
		for file in files:
			file = file.split('.')
			files_.append(file[0])
		files_ = list(set(files_))
		#pprint(files_)

		for file in files_:
			shp = path + file + '.shp'
			kml = kml_path + file.replace('_', ' ') + '.kml'
			ogr2ogr.main(["","-f", "KML", kml, shp])

def kml_to_geoJSON():
	"""Converts all kml files to geoJSON formated json files"""
	folders = os.listdir('data/' + my.DATA_FOLDER + '/kml/')
	if '.DS_Store' in folders:
		folders.remove('.DS_Store')
	#print folders
	for folder in folders:
		print '\n' + folder + '\n'
		path = 'data/' + my.DATA_FOLDER + 'kml/' + folder + '/'
		json_path = 'data/' + my.DATA_FOLDER + 'json/' + \
					folder.replace(' Division Gangs', '') + '/'
		if not os.path.exists(json_path):
			os.makedirs(json_path)

		files = os.listdir(path)
		if '.DS_Store' in files:
			files.remove('.DS_Store')
		files_ = []
		for file in files:
			file = file.split('.')
			files_.append(file[0])
		files_ = list(set(files_))
		#pprint(files_)

		for file in files_:
			kml = path + file + '.kml'
			json = json_path + file + '.json'
			#print json
			if 'Crips' in file or 'Bloods' in file:
				print file
			raw = open(kml, 'rb').read()
			root = parser.fromstring(raw)
			try:
				cord = root.Document.Folder.Placemark.Polygon.outerBoundaryIs.LinearRing.coordinates
			except:
				cord = root.Document.Folder.Placemark.MultiGeometry.Polygon.outerBoundaryIs.LinearRing.coordinates
			cord = str(cord)
			cord = cord.split(' ')
			pol = []
			for ll in cord:
				ll = ll.split(',')
				lng = float(ll[0])
				lat = float(ll[1])
				pol.append([lat, lng])
			geo = {
				"type"			: "Polygon",
				"coordinates"	:	[pol]
				}
			open(json, 'wb').write(anyjson.dumps(geo))
		

def combine_json():
	"""Combine all geoJSON files into one file"""
	ttys = []
	folders = os.listdir('data/' + my.DATA_FOLDER + '/json/')
	if '.DS_Store' in folders:
		folders.remove('.DS_Store')
	#print folders
	for folder in folders:
		#print '\n' + folder + '\n'
		path = 'data/' + my.DATA_FOLDER + 'json/' + folder + '/'
		files = os.listdir(path)
		if '.DS_Store' in files:
			files.remove('.DS_Store')
		files_ = []
		for file in files:
			file = file.split('.')
			files_.append(file[0])
		files_ = list(set(files_))
		#pprint(files_)

		for file in files_:
			json = path + file + '.json'
			raw = open(json, 'rb').read()
			geo = anyjson.loads(raw)
			this = {
				'geo' : geo,
				'name' : file,
				'division' : folder
			}
			ttys.append(this)

	print len(ttys)
	with open('data/' + my.DATA_FOLDER + 'loc_data.json', 'wb') as fp:
		fp.write(anyjson.dumps(ttys))



