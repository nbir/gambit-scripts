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
import traceback
import itertools
import matplotlib
import numpy as np
import jsbeautifier as jsb
import lib.PiP_Edge as pip
import matplotlib.pyplot as plt

from time import sleep
from osgeo import ogr, osr
from random import uniform
from multiprocessing import Pool
from matplotlib.collections import PolyCollection

import settings as my
sys.path.insert(0, os.path.abspath('..'))



#
# GRID
#
def make_grid():
	'''Plot all geo-tagged tweets on map'''
	lat1, lng1, lat2, lng2 = my.BBOX
	xticks = np.arange(lng1, lng2, my.GRID_LNG_DELTA).tolist()
	xticks.append(lng2)
	yticks = np.arange(lat1, lat2, my.GRID_LAT_DELTA).tolist()
	yticks.append(lat2)
	print len(xticks), 'x', len(yticks)

	fig=plt.figure(figsize=(36,26))
	fig.set_tight_layout(True)
	ax=fig.add_subplot(111)
	ax.set_xlim(lng1, lng2)
	ax.set_ylim(lat1, lat2)
	ax.set_xticks(xticks)
	ax.set_yticks(yticks)
	ax.grid(ls='-', lw=.2)
	plt.setp(plt.xticks()[1], rotation=90)

	bg = matplotlib.image.imread('data/' + my.DATA_FOLDER + 'map/' + 'map.png')
	ax.imshow(bg, aspect='auto', extent=(lng1, lng2, lat1, lat2), alpha=0.9)

	plt.savefig('data/' + my.DATA_FOLDER + 'map/' + 'grid' + '.png')

	yticks.reverse()

	grid = {
		'bbox' : my.BBOX,
		'lat_delta' : my.GRID_LAT_DELTA,
		'lng_delta' : my.GRID_LNG_DELTA,
		'xticks' : [round(i, 3) for i in xticks],
		'yticks' : [round(i, 3) for i in yticks],
		'rows' : len(yticks) - 1,
		'columns' : len(xticks) - 1,
		'cells' : (len(yticks) - 1) * (len(xticks) - 1),
		'grid' : {},
		#'grid_lookup' : {}
	}

	i = 0
	for r in range(len(yticks) - 1):
		#grid['grid_lookup'][round(yticks[r+1], 3)] = {}
		for c in range(len(xticks) - 1):
			grid['grid'][i] = (	round(yticks[r+1], 3), 
								round(xticks[c], 3), 
								round(yticks[r], 3), 
								round(xticks[c+1], 3))
			#grid['grid_lookup'][round(yticks[r+1], 3)][round(xticks[c], 3)] = i
			i += 1	

	with open('data/' + my.DATA_FOLDER + 'grid.json', 'wb') as fp:
		fp.write(jsb.beautify(anyjson.dumps(grid)))


def make_grid_lookup():
	global pols
	pols = {}
	with open('data/' + my.DATA_FOLDER + 'city_tracts.json', 'rb') as fp:
		polygons = anyjson.loads(fp.read())
	for gid, json_poly in polygons.iteritems():
		json_poly_str = anyjson.dumps(json_poly)
		pols[gid] = ogr.CreateGeometryFromJson(json_poly_str)

	grid_pols = []
	global grid_json_pols
	grid_json_pols = {}
	with open('data/' + my.DATA_FOLDER + 'grid.json', 'rb') as fp:
		grid = anyjson.loads(fp.read())
	for id in grid['grid']:
		lat1, lng1, lat2, lng2 = grid['grid'][id]
		#grid_lookup[(y, x)] = int(id)
		json_poly = {
			'type': 'Polygon',
			'coordinates': [[
				[lng1, lat1], 
				[lng1, lat2], 
				[lng2, lat2], 
				[lng2, lat1], 
				[lng1, lat1] ]]
			}
		grid_json_pols[id] = json_poly
		json_poly_str = anyjson.dumps(json_poly)
		pol = ogr.CreateGeometryFromJson(json_poly_str)
		grid_pols.append([id, pol])

	print len(pols), 'tracts.', len(grid_pols), 'grid cells.'

	#grid_lookup = {}
	#for ip in grid_pols:
	#	op = _grid_tract(ip)
	#	grid_lookup[op[0]] = op[1]
	pool = Pool(my.PROCESSES)
	matches = pool.map(_grid_tract, grid_pols)
	grid_lookup = dict(matches)

	with open('data/' + my.DATA_FOLDER + 'grid_lookup.json', 'wb') as fp:
		fp.write(jsb.beautify(anyjson.dumps(grid_lookup)))

def _grid_tract(ip):
	id, grid_pol = ip
	matches = []

	for gid, pol in pols.iteritems():
		if pol.Intersects(grid_pol):
			try:
				matches.append([gid, pol.Intersection(grid_pol).GetArea()])
			except:
				 traceback.print_exc()

	if len(matches) < 1:
		print grid_pol.GetArea(), grid_json_pols[id]
		return (id, 0)
	elif len(matches) == 1:
		match = matches.pop()
		print '1'
	else:
		matches = sorted(matches, key=lambda x: x[1])
		print len(matches)
		match = matches.pop()

	return (id, match[0])


def plot_grid_lookup():
	with open('data/' + my.DATA_FOLDER + 'grid.json', 'rb') as fp:
		grid = anyjson.loads(fp.read())
	rows = grid['rows']
	columns = grid['columns']

	with open('data/' + my.DATA_FOLDER + 'grid_lookup.json', 'rb') as fp:
		grid_lookup = anyjson.loads(fp.read()).items()
	grid_lookup = sorted(grid_lookup, key=lambda x: int(x[0]))
	grid_lookup = [0 if g==0 else 1 for _, g in grid_lookup]
	print len(grid_lookup), sum(grid_lookup)
	grid_lookup = np.array(grid_lookup).reshape(rows, columns)

	gids = ()
	skip_pols = []
	with open('data/' + my.DATA_FOLDER + 'city_tracts.json', 'rb') as fp:
		polygons = anyjson.loads(fp.read())
	for g, json_poly in polygons.iteritems():
		pol = json_poly['coordinates'][0]
		skip_pols.append(pol)

	lat1, lng1, lat2, lng2 = my.BBOX
	xticks = np.arange(lng1, lng2, my.GRID_LNG_DELTA).tolist()
	xticks.append(lng2)
	yticks = np.arange(lat1, lat2, my.GRID_LAT_DELTA).tolist()
	yticks.append(lat2)

	fig=plt.figure(figsize=(36,26))
	fig.set_tight_layout(True)
	ax=fig.add_subplot(111)
	ax.set_xlim(lng1, lng2)
	ax.set_ylim(lat1, lat2)
	ax.set_xticks(xticks)
	ax.set_yticks(yticks)
	ax.grid(ls='-', lw=.2)
	plt.setp(plt.xticks()[1], rotation=90)
	ax.imshow(grid_lookup, 
			cmap=plt.cm.Reds, 
			extent=(lng1,lng2,lat1,lat2), 
			interpolation='nearest', 
			alpha=0.35)

	coll = PolyCollection(	skip_pols, edgecolors='#333333', lw=0.5, 
							facecolors='none')
	ax.add_collection(coll)

	plt.savefig('data/' + my.DATA_FOLDER + 'map/' + 'grid_lookup' + '.png')

	


#
# VISITS
#
def calc_visit_mat():
	#_calc_visit_mat('tweets.json')
	_calc_visit_mat('artificial_tweets.json')

def _calc_visit_mat(filename):
	global gids
	with open('data/' + my.DATA_FOLDER + 'city_tracts.json', 'rb') as fp:
		gids = anyjson.loads(fp.read()).keys()
	gids = sorted(gids)
	print len(gids), 'gids'
	path = 'data/' + my.DATA_FOLDER + 'data/'
	with open(path + 'gids.json', 'wb') as fp:
		fp.write( anyjson.dumps(gids) )

	global rows, columns, xticks, yticks
	with open('data/' + my.DATA_FOLDER + 'grid.json', 'rb') as fp:
		grid = anyjson.loads(fp.read())
	rows = grid['rows']
	columns = grid['columns']
	xticks = grid['xticks']
	yticks = grid['yticks']
	
	global grid_lookup
	grid_lookup = {}
	with open('data/' + my.DATA_FOLDER + 'grid_lookup.json', 'rb') as fp:
		_grid_lookup = anyjson.loads(fp.read())
	for id in grid['grid']:
		y, x, _, _ = grid['grid'][id]
		gid = _grid_lookup[id]
		if gid == 0:
			grid_lookup[(y, x)] = -1
		else:
			grid_lookup[(y, x)] = gids.index(gid)

	with open('data/' + my.DATA_FOLDER + 'tract_users.json', 'rb') as fp:
		tract_users = anyjson.loads(fp.read())
	ip = [ (g, filename, tract_users[g]) for g in gids]

	#visits = []
	#for i in ip:
	#	visits.append( _calc_visits(i) )
	pool = Pool(my.PROCESSES)
	visits = pool.map(_calc_visits, ip)
	visits = dict(visits)

	visit_mat = []
	for g in gids:
		visit_mat.append(visits[g])

	with open(path + 'visit_mat_' + filename, 'wb') as fp:
		fp.write( jsb.beautify( anyjson.dumps(visit_mat) ) )

def _calc_visits(ip):
	gid, filename, user_ids = ip
	if len(user_ids) == 0:
		visits = [0] * len(gids)
		return (gid, visits)

	tweets = []
	for user_id in user_ids:
		tweets.extend( _load_artificial_tweets(user_id) )

	"""con = psycopg2.connect(my.DB_CONN_STRING)
	cur = con.cursor()
	SQL = '''SELECT ST_X(geo), ST_Y(geo) \
			FROM  {rel_tweet} \
				WHERE user_id IN ({user_ids}) \
			'''.format( rel_tweet=my.REL_TWEET,
						user_ids=','.join( str(u) for u in user_ids ))
	cur.execute(SQL)
	tweets = cur.fetchall()
	con.close()"""

	target_idx = [_get_grid(rec) for rec in tweets]
	target_idx = filter(None, target_idx)
	target_idx = filter(lambda x: 1 if x != -1 else 0, target_idx)
	visits = [0] * len(gids)
	for i in target_idx:
		visits[i] += 1

	print gid, len(visits), len(tweets), 'done'
	return (gid, visits)

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

def _load_artificial_tweets(user_id):
	path = 'data/' + my.DATA_FOLDER + 'data/' + 'artificial_tweets/'
	with open(path + str(user_id) + '.json', 'rb') as fp:
		tweets = anyjson.loads(fp.read())
	return tweets



#
# RACE VISITS
#
def find_race_visits():
	with open('data/' + my.DATA_FOLDER + 'data/' + 'gids.json', 'rb') as fp:
		gids = anyjson.loads(fp.read())
	with open('data/' + my.DATA_FOLDER + 'tract_race.json', 'rb') as fp:
		tract_race = anyjson.loads(fp.read())

	race_idx = {'w': [], 'b': [], 'a': [], 'h': [], 'o': []}
	for race in race_idx.keys():
		this_race_tracts = [g for g, r in tract_race.iteritems() if r==race]
		race_idx[race] = [gids.index(g) for g in this_race_tracts if g in gids]
	print dict((r, len(i)) for r, i in race_idx.iteritems())

	path = 'data/' + my.DATA_FOLDER + 'data/'
	with open(path + 'visit_mat_tweets' + '.json', 'rb') as fp:
		visit_mat = anyjson.loads(fp.read())
	with open(path + 'visit_mat_artificial_tweets' + '.json', 'rb') as fp:
		visit_mat_arti = anyjson.loads(fp.read())

	lookup = {'w': 0, 'b': 1, 'a': 2, 'h': 3, 'o': 4}
	colors = [ my.COLOR[r] for r in ['w', 'b', 'a', 'h', 'o'] ]
	
	for race in ['w', 'b', 'a', 'h']:
		sizes = [0]*5
		sizes_arti = [0]*5

		for idx_from in race_idx[race]:
			for race_to in ['w', 'b', 'a', 'h']:
				for idx_to in race_idx[race_to]:
					if idx_from != idx_to:
						sizes[ lookup[race_to] ] += visit_mat[idx_from][idx_to]
						sizes_arti[ lookup[race_to] ] += \
										visit_mat_arti[idx_from][idx_to]
		sizes = [round(float(s)/sum(sizes), 4) for s in sizes]
		sizes_arti = [round(float(s)/sum(sizes_arti), 4) for s in sizes_arti]
		print sizes
		print sizes_arti

		# Plot
		#
		fig=plt.figure()
		fig.set_tight_layout(True)
		ax=fig.add_subplot(111)

		ind = np.arange(5)
		width = 0.35
		rects1 = ax.bar(ind, sizes, width, color=colors)
		rects2 = ax.bar(ind+width, sizes_arti, width, color=colors, edgecolor=colors, alpha=0.45)
		ax.set_ylabel('Visit fraction')
		ax.set_ylim(0,1)
		ax.set_title('Race visits by ' + race.upper())
		ax.set_xticks(ind+width)
		ax.set_xticklabels( ('W', 'B', 'A', 'H', 'O') )
		ax.legend(	(rects1[lookup[race]], rects2[lookup[race]]),
					('Actual', 'Artificial') )

		path = 'data/' + my.DATA_FOLDER + 'visits/'
		if not os.path.exists(path): os.makedirs(path)
		plt.savefig(path + 'race_visits_' + race + '.pdf')



