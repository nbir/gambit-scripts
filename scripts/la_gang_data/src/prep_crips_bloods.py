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
from xml.etree import ElementTree

import settings as my
sys.path.insert(0, os.path.abspath('..'))


def parse_kml():
	geo_data = {}
	loc_data = []
	kml = 'data/' + my.DATA_FOLDER + 'kml/' + 'LosAngelesCountyGangs.kml'
	tree = ElementTree.parse(kml)
	items = tree.findall('.//{http://earth.google.com/kml/2.2}Placemark')
	id = 0
	for item in items:
		id += 1
		name = item.find('.//{http://earth.google.com/kml/2.2}name').text
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
		geo_data[id] = geo
		loc = {
			"id" : id,
			"name" : name,
			"polygon" : pol,
			}
		loc_data.append(loc)
	with open('data/' + my.DATA_FOLDER + 'geo_data.json', 'wb') as fp:
		fp.write(anyjson.dumps(geo_data))
	with open('data/' + my.DATA_FOLDER + 'loc_data.json', 'wb') as fp:
		fp.write(anyjson.dumps(loc_data))


