# Gambit scripts
#
# Copyright (C) USC Information Sciences Institute
# Author: Nibir Bora <nbora@usc.edu>
# URL: <http://cbg.isi.edu/>
# For license information, see LICENSE

import os
import sys
import csv
import math
import nltk
import shutil
import anyjson
import psycopg2
import itertools
import numpy as np
import cPickle as pickle
import jsbeautifier as jsb
import multiprocessing as mp
import matplotlib.pyplot as plt

from datetime import *
from pprint import pprint
from pymining import itemmining
from nltk.corpus import stopwords
from nltk.probability import FreqDist

import settings as my
sys.path.insert(0, os.path.abspath('..'))


#
# GET DATA
#
def get_data():
	''''''
	date_from = datetime.strptime(my.DATE_FROM, my.DATE_FORMAT).date()
	date_to = datetime.strptime(my.DATE_TO, my.DATE_FORMAT).date()
	print date_from, '-', date_to
	td = timedelta(days=1)

	dates = []
	while date_from < date_to:
		dates.append(date_from.isoformat())
		date_from = date_from + td
	print len(dates), 'dates'

	with open('data/' + my.DATA_FOLDER + 'grid.json', 'rb') as fp:
		grid = anyjson.loads(fp.read())

	global cells, rows, columns
	cells = grid['cells']
	rows = grid['rows']
	columns = grid['columns']
	global xticks, yticks
	xticks = grid['xticks']
	yticks = grid['yticks']
	
	global grid_lookup
	grid_lookup = {}
	for id in grid['grid']:
		y, x, _, _ = grid['grid'][id]
		grid_lookup[(y, x)] = int(id)

	#_dates = []
	#for date in dates[:5]:
	#	_dates.append(_get_data(date))

	pool = mp.Pool(my.PROCESSES)
	_dates = pool.map(_get_data, dates)

	#_dates = format(None, _dates)
	
	with open('data/' + my.DATA_FOLDER + 'dates.json', 'wb') as fp:
		fp.write( jsb.beautify( anyjson.dumps(_dates) ) )


def _get_data(date):
	'''Map function'''
	print 'Started', date
	SQL = '''SELECT ST_X(geo), ST_Y(geo) 
			FROM {rel_tweet} 
			WHERE timestamp::date = '{date}' 
			'''.format( rel_tweet=my.REL_TWEET, date=date)

	con = psycopg2.connect(my.DB_CONN_STRING)
	cur = con.cursor()
	cur.execute(SQL)
	recs = cur.fetchall()
	con.close()
	print len(recs), 'records retrieved for date', date

	if len(recs) < my.MIN_TWEETS:
		return None
	else:
		#pool = mp.Pool(my.PROCESSES)
		#grids = pool.map(_get_grid, recs)
		
		grids = []
		for rec in recs:
			grids.append(_get_grid(rec))

		data = np.zeros(cells, dtype=int)
		for g in grids:
			if g: data[g] += 1
		data = data.reshape((rows, columns)).tolist()

		path = 'data/' + my.DATA_FOLDER + 'grid_data/'
		if not os.path.exists(path): os.makedirs(path)
		with open(path + date + '.json', 'wb') as fp:
			fp.write( jsb.beautify( anyjson.dumps(data) ) )

		return date


def _get_grid(rec):
	''''''
	lat, lng = rec

	for y in yticks:
		if lat >= y: break
	
	for x in xticks:
		if x > lng: break
	x = xticks[xticks.index(x) - 1] 

	#print rec, y, x, grid_lookup[(y, x)]
	if (y, x) in grid_lookup:
		return grid_lookup[(y, x)]
	else:
		return None
