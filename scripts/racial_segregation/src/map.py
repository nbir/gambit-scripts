# Gambit scripts
#
# Copyright (C) USC Information Sciences Institute
# Author: Nibir Bora <nbora@usc.edu>
# URL: <http://cbg.isi.edu/>
# For license information, see LICENSE

import os
import sys
import csv
import numpy
import anyjson
import itertools
import matplotlib.pyplot as plt

from pprint import pprint
from matplotlib.collections import PolyCollection
from matplotlib.font_manager import FontProperties

import settings as my
sys.path.insert(0, os.path.abspath('..'))


#
# BASIC MAP
#
def plot_map():
	lat1, lng1, lat2, lng2 = my.BBOX
	color = my.COLOR

	fig=plt.figure(figsize=(18, 13))
	fig.set_tight_layout(True)
	ax=fig.add_subplot(111)
	ax.set_xlim(lng1, lng2)
	ax.set_ylim(lat1, lat2)
	ax.set_xticks([])
	ax.set_yticks([])
	ax.axis('off')

	#bg = matplotlib.image.imread('data/' + my.DATA_FOLDER + 'map.png')
	#ax.imshow(bg, aspect='auto', extent=(lng1, lng2, lat1, lat2), alpha=0.5)

	with open('data/' + my.DATA_FOLDER + 'tract_population.json', 'rb') as fp:
		population = anyjson.loads(fp.read())
	with open('data/' + my.DATA_FOLDER + 'city_tracts.json', 'rb') as fp:
		polygons = anyjson.loads(fp.read())
	with open('data/' + my.DATA_FOLDER + 'tract_race.json', 'rb') as fp:
		tract_race = anyjson.loads(fp.read())
	with open('data/' + my.DATA_FOLDER + 'tract_areas.json', 'rb') as fp:
		tract_area = anyjson.loads(fp.read())

	gids = list(
		set([g for g,p in population.iteritems() if sum(p)>my.MIN_POPULATION])
		& set([g for g,a in tract_area.iteritems() if a < my.MAX_AREA])
		)
	pols = {'w': [], 'b': [], 'a': [], 'h': [], 'o': []}
	skip_pols = []

	for g, json_poly in polygons.iteritems():
		race = tract_race[g]
		pol = json_poly['coordinates'][0]
		if g in gids:
			pols[race].append(pol)
		else:
			skip_pols.append(pol)
		
	print dict((r, len(p)) for r, p in pols.iteritems())

	for r, p in pols.iteritems():
		coll = PolyCollection(	p,
								edgecolors='#333333', lw=0.5,
								facecolors=color[r], alpha=0.75)
		ax.add_collection(coll)
	coll = PolyCollection(	skip_pols, edgecolors='#333333', lw=0.5, 
							facecolors='none')
	ax.add_collection(coll)

	path = 'data/' + my.DATA_FOLDER + 'map/'
	if not os.path.exists(path): os.makedirs(path)
	plt.savefig(path + 'map_race' + '.png')


#
# MAP & HOMES
#
def plot_map_with_homes():
	lat1, lng1, lat2, lng2 = my.BBOX
	color = my.COLOR

	fig=plt.figure(figsize=(18, 13))
	fig.set_tight_layout(True)
	ax=fig.add_subplot(111)
	ax.set_xlim(lng1, lng2)
	ax.set_ylim(lat1, lat2)
	ax.set_xticks([])
	ax.set_yticks([])
	ax.axis('off')

	#bg = matplotlib.image.imread('data/' + my.DATA_FOLDER + 'map.png')
	#ax.imshow(bg, aspect='auto', extent=(lng1, lng2, lat1, lat2), alpha=0.5)

	with open('data/' + my.DATA_FOLDER + 'tract_population.json', 'rb') as fp:
		population = anyjson.loads(fp.read())
	with open('data/' + my.DATA_FOLDER + 'city_tracts.json', 'rb') as fp:
		polygons = anyjson.loads(fp.read())
	with open('data/' + my.DATA_FOLDER + 'tract_race.json', 'rb') as fp:
		tract_race = anyjson.loads(fp.read())
	with open('data/' + my.DATA_FOLDER + 'tract_areas.json', 'rb') as fp:
		tract_area = anyjson.loads(fp.read())
	with open('data/' + my.DATA_FOLDER + 'tracts_with_users.json', 'rb') as fp:
		tracts_with_users = anyjson.loads(fp.read())
	with open('data/' + my.DATA_FOLDER + 'user_counts.json', 'rb') as fp:
		user_counts = anyjson.loads(fp.read())
	with open('data/' + my.DATA_FOLDER + 'user_homes.json', 'rb') as fp:
		homes = numpy.array(anyjson.loads(fp.read()).values())

	gids = list(
		set([g for g,p in population.iteritems() if sum(p)>my.MIN_POPULATION])
		& set([g for g,a in tract_area.items() if a < my.MAX_AREA])
		& set([g for g,u in user_counts.items() if u >= my.MIN_USERS ])
		)
	pols = {'w': [], 'b': [], 'a': [], 'h': [], 'o': []}
	skip_pols = []

	for g, json_poly in polygons.iteritems():
		race = tract_race[g]
		pol = json_poly['coordinates'][0]
		if g in gids:
			pols[race].append(pol)
		else:
			skip_pols.append(pol)
		
	print dict((r, len(p)) for r, p in pols.iteritems())

	for r, p in pols.iteritems():
		coll = PolyCollection(	p,
								edgecolors='#333333', lw=0.5,
								facecolors=color[r], alpha=0.75)
		ax.add_collection(coll)
	coll = PolyCollection(	skip_pols, edgecolors='#333333', lw=0.5, 
							facecolors='none')
	ax.add_collection(coll)

	ax.plot(homes[:, 1], homes[:, 0], 'k,')

	path = 'data/' + my.DATA_FOLDER + 'map/'
	if not os.path.exists(path): os.makedirs(path)
	plt.savefig(path + 'map_homes' + '.png')


#
# MAP WITH TWEETS
#
def plot_map_with_tweets():
	#_plot_map_with_tweets('all_tweets.json')
	_plot_map_with_tweets('artificial_all_tweets.json')

def _plot_map_with_tweets(filename):
	lat1, lng1, lat2, lng2 = my.BBOX
	color = my.COLOR

	with open('data/' + my.DATA_FOLDER + 'city_tracts.json', 'rb') as fp:
		polygons = anyjson.loads(fp.read())
	with open('data/' + my.DATA_FOLDER + 'tract_race.json', 'rb') as fp:
		tract_race = anyjson.loads(fp.read())

	pols = {'w': [], 'b': [], 'a': [], 'h': [], 'o': []}
	for g, json_poly in polygons.iteritems():
		r = tract_race[g]
		pol = json_poly['coordinates'][0]
		pols[r].append(pol)
	print dict((r, len(p)) for r, p in pols.iteritems())

	fig=plt.figure(figsize=(18, 13))
	fig.set_tight_layout(True)
	ax=fig.add_subplot(111)
	ax.set_xlim(lng1, lng2)
	ax.set_ylim(lat1, lat2)
	ax.set_xticks([])
	ax.set_yticks([])
	ax.axis('off')

	for r, p in pols.iteritems():
		coll = PolyCollection(	p,
								edgecolors='#333333', lw=0.5,
								facecolors=color[r], alpha=0.35)
		ax.add_collection(coll)
	print 'Added collections!'

	with open('data/' + my.DATA_FOLDER + 'data/' + filename, 'rb') as fp:
		tweets = numpy.array( anyjson.loads(fp.read()) )
	ax.plot(tweets[:, 1], tweets[:, 0], 'k,', alpha=0.25)
	print 'Plotted tweets!'

	path = 'data/' + my.DATA_FOLDER + 'map/'
	if not os.path.exists(path): os.makedirs(path)
	plt.savefig(path + 'map_' + filename.replace('.json','') + '.png')


#
# RACE MAP
#
def plot_race_map():
	for race in ['w', 'b', 'a', 'h']:
		_plot_race_map(race)

def _plot_race_map(race):
	lat1, lng1, lat2, lng2 = my.BBOX
	color = my.COLOR

	with open('data/' + my.DATA_FOLDER + 'city_tracts.json', 'rb') as fp:
		polygons = anyjson.loads(fp.read())
	with open('data/' + my.DATA_FOLDER + 'tract_race.json', 'rb') as fp:
		tract_race = anyjson.loads(fp.read())
	with open('data/' + my.DATA_FOLDER + 'tracts_with_users.json', 'rb') as fp:
		tracts_with_users = anyjson.loads(fp.read())
	with open('data/' + my.DATA_FOLDER + 'tract_users.json', 'rb') as fp:
		tract_users = anyjson.loads(fp.read())

	this_race_tracts = [g for g, r in tract_race.iteritems() if r==race]
	user_ids = [tract_users[g] for g in this_race_tracts if g in tract_users]
	user_ids = list(itertools.chain(*user_ids))

	pols = {'w': [], 'b': [], 'a': [], 'h': [], 'o': []}
	for g, json_poly in polygons.iteritems():
		r = tract_race[g]
		pol = json_poly['coordinates'][0]
		pols[r].append(pol)
	print dict((r, len(p)) for r, p in pols.iteritems())

	# Actual
	#
	fig=plt.figure(figsize=(18, 13))
	fig.set_tight_layout(True)
	ax=fig.add_subplot(111)
	ax.set_xlim(lng1, lng2)
	ax.set_ylim(lat1, lat2)
	ax.set_xticks([])
	ax.set_yticks([])
	ax.axis('off')
	for r, p in pols.iteritems():
		coll = PolyCollection(	p,
								edgecolors='#333333', lw=0.5,
								facecolors=color[r], alpha=0.25)
		ax.add_collection(coll)
	ax.add_collection(coll)

	tweets = []
	path = 'data/' + my.DATA_FOLDER + 'data/' + 'tweets/'
	for user_id in user_ids:
		with open(path + str(user_id) + '.json', 'rb') as fp:
			tweets.extend( anyjson.loads(fp.read()) )
	tweets = numpy.array(tweets)
	ax.plot(tweets[:, 1], tweets[:, 0], 'k,', alpha=0.7)
	ax.text(0.05, 0.05, 'Race map - '+race, ha='left', va='bottom', 
			transform = ax.transAxes, family='monospace', fontsize=40)
	plt.savefig('data/' + my.DATA_FOLDER + 'map/' + 'race_map_'+race+'.png')

	# Artificial
	#
	fig=plt.figure(figsize=(18, 13))
	fig.set_tight_layout(True)
	ax=fig.add_subplot(111)
	ax.set_xlim(lng1, lng2)
	ax.set_ylim(lat1, lat2)
	ax.set_xticks([])
	ax.set_yticks([])
	ax.axis('off')
	for r, p in pols.iteritems():
		coll = PolyCollection(	p,
								edgecolors='#333333', lw=0.5,
								facecolors=color[r], alpha=0.25)
		ax.add_collection(coll)
	ax.add_collection(coll)

	tweets = []
	path = 'data/' + my.DATA_FOLDER + 'data/' + 'artificial_tweets/'
	for user_id in user_ids:
		with open(path + str(user_id) + '.json', 'rb') as fp:
			tweets.extend( anyjson.loads(fp.read()) )
	tweets = numpy.array(tweets)
	ax.plot(tweets[:, 1], tweets[:, 0], 'k,', alpha=0.5)
	ax.text(0.05, 0.05, 'Race map - '+race+' (artificial)', ha='left', 
		va='bottom', transform = ax.transAxes, family='monospace', fontsize=40)
	plt.savefig('data/' + my.DATA_FOLDER + 'map/' + 'race_map_artificial_' \
					+ race + '.png')



