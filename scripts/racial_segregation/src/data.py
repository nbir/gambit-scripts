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
import itertools
import numpy as np
import jsbeautifier as jsb
import lib.PiP_Edge as pip
import matplotlib.pyplot as plt

from time import sleep
from osgeo import ogr, osr
from random import uniform
from multiprocessing import Pool

import settings as my
sys.path.insert(0, os.path.abspath('..'))


#
# POPULATION
#
def get_tract_population():
	''''''
	fpw = open('data/' + my.DATA_FOLDER + 'tract_population.csv', 'wb')
	cw = csv.writer(fpw, delimiter=',')
	cw.writerow(['GISJOIN', 'WHITE', 'BLACK', 'ASIAN', 'HISPANIC', 'OTHERS'])

	population = {}
	with open('data/' + my.DATA_FOLDER + 'population/' + 'US_tract_2010.prj.csv', 'rb') as fp:
		cr = csv.reader(fp, delimiter=',')
		fields = cr.next()
		fields = dict((i, fields.index(i)) for i in fields)
		print fields

		for row in cr:
			state_id = int(row[fields['STATEA']])
			if state_id == my.STATE_ID:
				out_row = [
							row[fields['GISJOIN']],
							int(row[fields['H7Z003']]),
							int(row[fields['H7Z004']]),
							int(row[fields['H7Z006']]),
							int(row[fields['H7Z010']]),
							int(row[fields['H7Z005']]) 
								+ int(row[fields['H7Z007']]) 
								+  int(row[fields['H7Z008']]) 
								+ int(row[fields['H7Z009']]),
						]
				cw.writerow(out_row)
				population[out_row[0]] = out_row[1:]

				total = int(row[fields['H7V001']])
				total2 = int(row[fields['H7Z001']])
				print sum(out_row[1:]), total, total2
	fpw.close()

	with open('data/' + my.DATA_FOLDER + 'tract_population.json', 'wb') as fp:
		fp.write(jsb.beautify(anyjson.dumps(population)))


def find_tract_race():
	with open('data/' + my.DATA_FOLDER + 'tract_population.json', 'rb') as fp:
		population = anyjson.loads(fp.read())

	race = {}
	lookup = {0 : 'w', 1 : 'b', 2 : 'a', 3 : 'h', 4 : 'o'}

	for gid, pop in population.iteritems():
		ri = pop.index( max(pop) )
		r = lookup[ri]
		race[gid] = r

	with open('data/' + my.DATA_FOLDER + 'tract_race.json', 'wb') as fp:
		fp.write( jsb.beautify( anyjson.dumps(race) ) )


#
# POLYGON
#
def get_tract_polygon():
	''''''
	ds = ogr.Open('data/' + my.DATA_FOLDER + 'shape/' + 'US_tract_2010.shp')
	lyr = ds.GetLayerByIndex(0)
	lyr.ResetReading()
	n_features = len(lyr)
	print n_features
	
	feat_defn = lyr.GetLayerDefn()
	field_defns = [feat_defn.GetFieldDefn(i) \
						for i in range(feat_defn.GetFieldCount())]
	for i, defn in enumerate(field_defns):
		print i, defn.GetName()
		if defn.GetName() == "GISJOIN": idx_gisjoin = i
		if defn.GetName() == "STATEFP10": idx_statefips = i

	spatial_ref = osr.SpatialReference()
	spatial_ref.ImportFromEPSG(4326)
	coord_transform = osr.CoordinateTransformation(	lyr.GetSpatialRef(),
													spatial_ref )
	polygons = {}
	for j, feat in enumerate( lyr ):
		if j % 1000 == 0:
			print "%s/%s (%0.2f%%)" % ( j+1,
										n_features,
										100*((j+1)/float(n_features)) )

		statefips = int(feat.GetField(idx_statefips))
		if statefips == my.STATE_ID:
			gisjoin = feat.GetField(idx_gisjoin)
		
			geom = feat.GetGeometryRef()
			poly = ogr.CreateGeometryFromWkb(geom.ExportToWkb())
			poly.Transform(coord_transform)
			json_poly = anyjson.loads(poly.ExportToJson())
			print json_poly['coordinates'][0]
			polygons[gisjoin] = json_poly
			break
			
			#bbox = poly.GetEnvelope()
			#print bbox

	#with open('data/' + my.DATA_FOLDER + 'tract_polygons.json', 'wb') as fp:
	#	fp.write(anyjson.dumps(polygons))


def check_data():
	with open('data/' + my.DATA_FOLDER + 'tract_population.json', 'rb') as fp:
		population_keys = anyjson.loads(fp.read()).keys()
	with open('data/' + my.DATA_FOLDER + 'tract_polygons.json', 'rb') as fp:
		polygon_keys = anyjson.loads(fp.read()).keys()

	print len(polygon_keys), len(population_keys)

	print len( set(polygon_keys) & set(population_keys) )
	print len( set(polygon_keys) | set(population_keys) )


def get_city_tracts():
	with open('data/' + my.DATA_FOLDER + 'tract_polygons.json', 'rb') as fp:
		polygons = anyjson.loads(fp.read())
	polygons_ = {}

	city = ogr.CreateGeometryFromWkt(my.POLY_WKT)

	for gid, json_poly in polygons.iteritems():
		json_poly_str = anyjson.dumps(json_poly)
		poly = ogr.CreateGeometryFromJson(json_poly_str)
		if city.Intersects(poly):
			pol = json_poly['coordinates'][0]
			if len(pol) <= 1:
				json_poly['coordinates'][0] = json_poly['coordinates'][0][0]
				print 'Fix!'
			polygons_[gid] = json_poly

	print len(polygons_.keys())
	with open('data/' + my.DATA_FOLDER + 'city_tracts.json', 'wb') as fp:
		fp.write( anyjson.dumps(polygons_) )


def find_tract_areas():
	with open('data/' + my.DATA_FOLDER + 'city_tracts.json', 'rb') as fp:
		polygons = anyjson.loads(fp.read())

	tract_areas = {}
	for gid, json_poly in polygons.iteritems():
		json_poly_str = anyjson.dumps(json_poly)
		poly = ogr.CreateGeometryFromJson(json_poly_str)
		tract_areas[gid] = poly.GetArea()

	with open('data/' + my.DATA_FOLDER + 'tract_areas.json', 'wb') as fp:
		fp.write( jsb.beautify( anyjson.dumps(tract_areas) ) )


def find_tract_centers():
	with open('data/' + my.DATA_FOLDER + 'city_tracts.json', 'rb') as fp:
		polygons = anyjson.loads(fp.read())

	tract_centers = {}
	for gid, json_poly in polygons.iteritems():
		pol = json_poly['coordinates'][0]
		lng = sum([ll[0] for ll in pol]) / len(pol)
		lat = sum([ll[1] for ll in pol]) / len(pol)
		tract_centers[gid] = [lng, lat]

	with open('data/' + my.DATA_FOLDER + 'tract_centers.json', 'wb') as fp:
		fp.write( jsb.beautify( anyjson.dumps(tract_centers) ) )


#
# TRACTS WITH USERS
#
def find_tracts_with_users():
	with open('data/' + my.DATA_FOLDER + 'user_homes.json', 'rb') as fp:
		homes = anyjson.loads(fp.read())
	homes = dict( ( int(h[0]), ogr.CreateGeometryFromWkt('POINT(%s %s)' \
						% (h[1][1], h[1][0])) )  for h in homes.items() )

	with open('data/' + my.DATA_FOLDER + 'city_tracts.json', 'rb') as fp:
		polygons = anyjson.loads(fp.read())

	user_counts = dict( (gid, 0) for gid in polygons.keys())
	users_in_tracts = []
	tracts_with_users = []
	tract_users = dict( (gid, []) for gid in polygons.keys())

	for gid, json_poly in polygons.iteritems():
		json_poly_str = anyjson.dumps(json_poly)
		poly = ogr.CreateGeometryFromJson(json_poly_str)
		
		for user_id, h in homes.items():
			if h.Within(poly):
				user_counts[gid] += 1
				users_in_tracts.append(user_id)
				tract_users[gid].append(user_id)
				del homes[user_id]

	tracts_with_users = [gid for gid, v in user_counts.items() if v != 0]

	with open('data/' + my.DATA_FOLDER + 'user_counts.json', 'wb') as fp:
		fp.write( jsb.beautify( anyjson.dumps(user_counts) ) )
	with open('data/' + my.DATA_FOLDER + 'tract_users.json', 'wb') as fp:
		fp.write( jsb.beautify( anyjson.dumps(tract_users) ) )
	with open('data/' + my.DATA_FOLDER + 'users_in_tracts.json', 'wb') as fp:
		fp.write( anyjson.dumps(users_in_tracts) )
	with open('data/' + my.DATA_FOLDER + 'tracts_with_users.json', 'wb') as fp:
		fp.write( anyjson.dumps(tracts_with_users) )


#
# STATISTICS
#
def data_stat():
	with open('data/' + my.DATA_FOLDER + 'tract_population.json', 'rb') as fp:
		population = anyjson.loads(fp.read())
	with open('data/' + my.DATA_FOLDER + 'city_tracts.json', 'rb') as fp:
		polygons = anyjson.loads(fp.read())

	total_pop = []
	total_area = []
	for gid, json_poly in polygons.iteritems():
		json_poly_str = anyjson.dumps(json_poly)
		poly = ogr.CreateGeometryFromJson(json_poly_str)
		total_area.append( poly.GetArea() )

		pop = population[gid]
		total_pop.append( sum(pop) )

	fig = plt.figure(figsize=(10, 10))
	fig.set_tight_layout(True)
	ax = fig.add_subplot(211)
	ax.hist(total_pop, bins=100, range=(0, 10000))
	ax.set_title('Population')

	ax = fig.add_subplot(212)
	ax.hist(total_area, bins=100, range=(0, 0.01))
	ax.set_title('Area')

	plt.savefig('data/' + my.DATA_FOLDER + 'data_stat' + '.pdf')
	



#
# TWEETS
#
def get_tweets():
	with open('data/' + my.DATA_FOLDER + 'users_in_tracts.json') as fp:
		user_ids = anyjson.loads(fp.read())

	pool = Pool(my.PROCESSES)
	tweets = pool.map(_get_tweets, user_ids)
	tweets = dict(tweets)

	path = 'data/' + my.DATA_FOLDER + 'data/'
	if not os.path.exists(path): os.makedirs(path)
	with open(path + 'tweets.json', 'wb') as fp:
		fp.write( anyjson.dumps(tweets) )

def _get_tweets(user_id):
	con = psycopg2.connect(my.DB_CONN_STRING)
	cur = con.cursor()
	SQL = '''SELECT ST_X(geo), ST_Y(geo) \
			FROM  {rel_tweet} \
				WHERE user_id = %s \
			'''.format(rel_tweet=my.REL_TWEET)
	cur.execute(SQL, (user_id, ))
	recs = cur.fetchall()
	con.close()
	points = tuple( ( float(rec[0]), float(rec[1]) ) for rec in recs)
	print user_id, len(points)
	return (user_id, points)


def make_all_tweets():
	path = 'data/' + my.DATA_FOLDER + 'data/'
	with open(path + 'tweets.json', 'rb') as fp:
		tweets = anyjson.loads( fp.read() ).values()
	tweets = list(itertools.chain(*tweets))

	with open(path + 'all_tweets.json', 'wb') as fp:
		fp.write( anyjson.dumps(tweets) )


def split_tweet_file():
	path = 'data/' + my.DATA_FOLDER + 'data/'
	with open(path + 'tweets.json', 'rb') as fp:
		tweets = anyjson.loads( fp.read() )

	path = 'data/' + my.DATA_FOLDER + 'data/' + 'tweets/'
	if not os.path.exists(path): os.makedirs(path)
	for user_id, tw in tweets.iteritems():
		with open(path + str(user_id) + '.json', 'wb') as fp:
			fp.write(anyjson.dumps(tw))


def make_tweet_count():
	path = 'data/' + my.DATA_FOLDER + 'data/'
	with open(path + 'tweets.json', 'rb') as fp:
		tweets = anyjson.loads( fp.read() )
	tweet_count = {}
	for user_id in tweets.keys():
		tweet_count[user_id] = len(tweets[user_id])

	with open('data/' + my.DATA_FOLDER + 'user_tweet_count.json', 'wb') as fp:
		fp.write( anyjson.dumps(tweet_count) )


def check_tweet_counts():
	path = 'data/' + my.DATA_FOLDER + 'data/'
	with open(path + 'all_tweets.json', 'rb') as fp:
		tweets = anyjson.loads(fp.read())
	print len(tweets)
	with open(path + 'artificial_all_tweets.json', 'rb') as fp:
		artificial_tweets = anyjson.loads(fp.read())
	print len(artificial_tweets)



#
# PLOT EACH USER
#
def plot_each_user():
	global user_homes
	with open('data/' + my.DATA_FOLDER + 'user_homes.json', 'rb') as fp:
		user_homes = anyjson.loads(fp.read())
	
	pool = Pool(my.PROCESSES)
	pool.map(_plot_user, user_homes.keys())

def _plot_user(user_id):
		path = 'data/' + my.DATA_FOLDER + 'data/' + 'tweets/'
		with open(path + str(user_id) + '.json', 'rb') as fp:
			tw = anyjson.loads(fp.read())
		path = 'data/' + my.DATA_FOLDER + 'data/' + 'artificial_tweets/'
		with open(path + str(user_id) + '.json', 'rb') as fp:
			tw_arti = anyjson.loads(fp.read())
		tw = np.array(tw)
		tw_arti = np.array(tw_arti)
		home = user_homes[str(user_id)]
		print user_id

		fig = plt.figure(figsize=(10,5))
		fig.set_tight_layout(True)
		
		ax = fig.add_subplot(121)
		ax.set_autoscaley_on(False)
		ax.set_ylim([-0.5,0.5])
		ax.set_xlim([-0.5,0.5])
		ax.set_yticks([0.0])
		ax.set_xticks([0.0])
		ax.set_yticklabels([])
		ax.set_xticklabels([])
		ax.grid(True)
		ax.plot(tw[:, 1] - home[1], tw[:, 0] - home[0], 'k+', alpha=0.75)
		ax.plot([0], [0], 'r^')
		ax.text(-0.45, -0.45, 'Actual', fontsize=10)

		ax = fig.add_subplot(122)
		ax.set_autoscaley_on(False)
		ax.set_ylim([-0.5,0.5])
		ax.set_xlim([-0.5,0.5])
		ax.set_yticks([0.0])
		ax.set_xticks([0.0])
		ax.set_yticklabels([])
		ax.set_xticklabels([])
		ax.grid(True)
		ax.plot(tw_arti[:, 1] - home[1], tw_arti[:, 0] - home[0], 'k+', alpha=0.75)
		ax.plot([0], [0], 'r^')
		ax.text(-0.45, -0.45, 'Artificial', fontsize=10)

		path = 'data/' + my.DATA_FOLDER + 'data/' + 'disp_plot/'
		if not os.path.exists(path): os.makedirs(path)
		plt.savefig(path + str(user_id) + '.png')
		plt.close()

def make_disp_video():
	path = 'data/' + my.DATA_FOLDER + 'data/' + 'disp_plot/'
	files = [f for f in os.listdir(path) if f.endswith('.png')]
	print files


