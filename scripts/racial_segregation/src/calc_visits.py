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
import numpy
import pickle
import anyjson
import psycopg2
import itertools
import matplotlib
import numpy as np
import lib.geo as geo
import jsbeautifier as jsb
import matplotlib.pyplot as plt

#from mpl_toolkits.basemap import Basemap
from matplotlib.collections import PolyCollection
from scipy.optimize import leastsq

from pylab import *
from datetime import *
from pprint import pprint
from pytz import timezone, utc
from multiprocessing import Pool

import settings as my
import lib.PiP_Edge as pip
import lib.geo as geo
sys.path.insert(0, os.path.abspath('..'))


#
# ASSIGN RACE
#
def find_user_race():
	with open('data/' + my.DATA_FOLDER + 'user_homes.json', 'rb') as fp:
		homes = anyjson.loads(fp.read())

	global loc_data
	with open('data/' + my.DATA_FOLDER + 'loc_data.json', 'rb') as fp:
		loc_data = anyjson.loads(fp.read())

	#for user in homes.items()[:100]:
	#	_find_race(user)
	pool = Pool(my.PROCESSES)
	user_race = pool.map(_find_race, homes.items())
	user_race = filter(None, user_race)

	races = {
		'w' : [],
		'b' : [],
		'a' : [],
		'h' : [],
		'o' : []
	}
	for user_id, race in user_race:
		races[race].append(user_id)

	with open('data/' + my.DATA_FOLDER + 'user_race.json', 'wb') as fp:
		fp.write(jsb.beautify(anyjson.dumps(races)))

def _find_race(user):
	user_id, ll = user
	lat = ll[0]
	lng = ll[1]

	for race, pols in loc_data.items():
		for pol in pols:
			if pip.point_in_poly(lat, lng, pol):
				return [int(user_id), race[0]]


#
# VISITS
#
def calc_user_visits():
	global homes
	with open('data/' + my.DATA_FOLDER + 'user_homes.json', 'rb') as fp:
		homes = anyjson.loads(fp.read())

	global loc_data
	with open('data/' + my.DATA_FOLDER + 'loc_data.json', 'rb') as fp:
		loc_data = anyjson.loads(fp.read())

	with open('data/' + my.DATA_FOLDER + 'user_race.json', 'rb') as fp:
		user_race = anyjson.loads(fp.read())
	user_ids = list(itertools.chain(*user_race.values()))

	#print len(user_ids)
	#for user_id in user_ids:
	#	_calc_visits(user_id)
	pool = Pool(my.PROCESSES)
	user_visits = pool.map(_calc_visits, user_ids)
	user_visits = dict(user_visits)

	with open('data/' + my.DATA_FOLDER + 'visits.json', 'wb') as fp:
		fp.write(jsb.beautify(anyjson.dumps(user_visits)))

def _calc_visits(user_id):
	con = psycopg2.connect(my.DB_CONN_STRING)
	cur = con.cursor()
	SQL = '''SELECT ST_X(geo), ST_Y(geo) \
			FROM  {rel_tweet} \
				WHERE user_id = %s \
			'''.format(rel_tweet=my.REL_TWEET)
	cur.execute(SQL, (user_id, ))
	recs = cur.fetchall()
	con.close()

	home = homes[str(user_id)]

	visits = [0]*6
	legend = {'w': 0, 'b': 1, 'a': 2, 'h': 3, 'o': 4}

	for rec in recs:
		lat, lng = rec
		dist = int(round(geo.distance(geo.xyz(home[0], home[1]), 
									geo.xyz(lat, lng))))
		if dist > my.MIN_DIST:
			race = _find_race([user_id, [lat, lng]])
			if race:
				visits[legend[race[1]]] += 1
			else:
				visits[5] += 1

	print [user_id, visits]
	return [user_id, visits]

#
#
#
def get_race_points():
	global homes
	with open('data/' + my.DATA_FOLDER + 'user_homes.json', 'rb') as fp:
		homes = anyjson.loads(fp.read())

	with open('data/' + my.DATA_FOLDER + 'user_race.json', 'rb') as fp:
		user_race = anyjson.loads(fp.read())
	user_ids = list(itertools.chain(*user_race.values()))

	global race_lookup
	race_lookup = {}
	for race, uids in user_race.items():
		for uid in uids:
			race_lookup[uid] = race

	pool = Pool(my.PROCESSES)
	points = pool.map(_get_points, user_ids)
	
	race_points = {
		'w': [], 
		'b': [], 
		'a': [], 
		'h': [], 
		'o': []}

	for race, pts in points:
		race_points[race].extend(pts)
	for race in race_points: print race, ':', len(race_points[race])

	with open('data/' + my.DATA_FOLDER + 'race_points.json', 'wb') as fp:
		fp.write(anyjson.dumps(race_points))

def _get_points(user_id):
	con = psycopg2.connect(my.DB_CONN_STRING)
	cur = con.cursor()
	SQL = '''SELECT ST_X(geo), ST_Y(geo) \
			FROM  {rel_tweet} \
				WHERE user_id = %s \
			'''.format(rel_tweet=my.REL_TWEET)
	cur.execute(SQL, (user_id, ))
	recs = cur.fetchall()
	con.close()

	home = homes[str(user_id)]

	points = []

	for rec in recs:
		lat, lng = rec
		dist = int(round(geo.distance(geo.xyz(home[0], home[1]), 
									geo.xyz(lat, lng))))
		if dist > my.MIN_DIST:
			points.append([round(lat,5), round(lng,5)])

	return [race_lookup[user_id], points]


#
# PLOT VISITS
#
def plot_visits_map():
	for race in ['w', 'b', 'a', 'h']:
		_plot_map(race)

def _plot_map(race):
	lat1, lng1, lat2, lng2 = my.BBOX
	color = {
		'w': 'blue', 
		'b': 'green', 
		'a': 'red', 
		'h': '#FF7F00', 
		'o': 'brown'}


	fig=plt.figure(figsize=(8, 5.77))
	fig.set_tight_layout(True)
	ax=fig.add_subplot(111)
	ax.set_xlim(lng1, lng2)
	ax.set_ylim(lat1, lat2)
	ax.set_xticks([])
	ax.set_yticks([])
	ax.axis('off')

	bg = matplotlib.image.imread('data/' + my.DATA_FOLDER + 'map.png')
	ax.imshow(bg, aspect='auto', extent=(lng1, lng2, lat1, lat2), alpha=1)

	bg2 = matplotlib.image.imread('data/' + my.DATA_FOLDER + 'seg.png')
	ax.imshow(bg2, aspect='auto', extent=(lng1, lng2, lat1, lat2), alpha=.75)


	with open('data/' + my.DATA_FOLDER + 'loc_data.json', 'rb') as fp:
		loc_data = anyjson.loads(fp.read())	
	for r, pols in loc_data.items():
		r = r[0]
		pol_plot = []
		for pol in pols:
			pol = [[ll[1], ll[0]] for ll in pol]
			pol_plot.append(pol)
		
		coll = PolyCollection(	pol_plot,
								edgecolors=color[r], linewidths=2,
								facecolors='none', alpha=0.75)
		ax.add_collection(coll)


	with open('data/' + my.DATA_FOLDER + 'race_points.json', 'rb') as fp:
		points = anyjson.loads(fp.read())[race]

	x = [pt[1] for pt in points]
	y = [pt[0] for pt in points]
	
	ax.plot(x, y, ',', color=color[race], alpha=0.9)

	plt.savefig('data/' + my.DATA_FOLDER + 'race_map_' + race + '.png')
	
#
#
#
def plot_general_map():
	lat1, lng1, lat2, lng2 = my.BBOX
	color = {
		'w': 'blue', 
		'b': 'green', 
		'a': 'red', 
		'h': '#FF7F00', 
		'o': 'brown'}

	fig=plt.figure(figsize=(8, 5.77))
	fig.set_tight_layout(True)
	ax=fig.add_subplot(111)
	ax.set_xlim(lng1, lng2)
	ax.set_ylim(lat1, lat2)
	ax.set_xticks([])
	ax.set_yticks([])
	ax.axis('off')

	bg = matplotlib.image.imread('data/' + my.DATA_FOLDER + 'map.png')
	ax.imshow(bg, aspect='auto', extent=(lng1, lng2, lat1, lat2), alpha=1)

	bg2 = matplotlib.image.imread('data/' + my.DATA_FOLDER + 'seg.png')
	ax.imshow(bg2, aspect='auto', extent=(lng1, lng2, lat1, lat2), alpha=.75)


	with open('data/' + my.DATA_FOLDER + 'loc_data.json', 'rb') as fp:
		loc_data = anyjson.loads(fp.read())	
	for r, pols in loc_data.items():
		r = r[0]
		pol_plot = []
		for pol in pols:
			pol = [[ll[1], ll[0]] for ll in pol]
			pol_plot.append(pol)
		
		coll = PolyCollection(	pol_plot,
								edgecolors='k', linewidths=2,
								facecolors=color[r], alpha=0.35)
		ax.add_collection(coll)

	plt.savefig('data/' + my.DATA_FOLDER + 'race_map' + '.png')


#
# PIE
#
def plot_race_pies():
	for race in ['w', 'b', 'a', 'h']:
		_plot_pies(race)

def _plot_pies(race):
	with open('data/' + my.DATA_FOLDER + 'user_race.json', 'rb') as fp:
		user_ids = anyjson.loads(fp.read())[race]

	with open('data/' + my.DATA_FOLDER + 'visits.json', 'rb') as fp:
		visits = anyjson.loads(fp.read())

	sizes = [0]*6
	for user_id in user_ids:
		v = visits[str(user_id)]
		for i in range(6):
			sizes[i] += v[i]


	labels = ['White', 'Black', 'Asian', 'Hispanic', '', 'None']
	colors = ['lightskyblue', 'yellowgreen', '#C94949', 'orange', '#A65628', '#AAAAAA']

	fig=plt.figure(figsize=(6, 10))
	#fig.set_tight_layout(True)
	plt.subplots_adjust(left=0.125, right=0.875, top=1., bottom=0.)
	ax=fig.add_subplot(211)
	ax.pie(	sizes[:-1], labels=labels[:-1], colors=colors[:-1],
			autopct='%1.1f%%', shadow=True, startangle=90)
	ax.axis('equal')
	ax.axis('off')

	ax=fig.add_subplot(212)
	ax.pie(	sizes, labels=labels, colors=colors,
			autopct='%1.1f%%', shadow=True, startangle=90)
	ax.axis('equal')
	ax.axis('off')

	plt.savefig('data/' + my.DATA_FOLDER + 'visit_pie_' + race + '.png')


#
# DISPLACEMENT
#
def get_distance():
	global homes
	with open('data/' + my.DATA_FOLDER + 'user_homes.json', 'rb') as fp:
		homes = anyjson.loads(fp.read())

	with open('data/' + my.DATA_FOLDER + 'user_race.json', 'rb') as fp:
		user_race = anyjson.loads(fp.read())
	user_ids = list(itertools.chain(*user_race.values()))

	pool = Pool(my.PROCESSES)
	user_disp = pool.map(_get_dist, user_ids)

	user_disp = filter(None, user_disp)
	user_disp = list(itertools.chain(*user_disp))

	with open('data/' + my.DATA_FOLDER + 'user_disp.json', 'wb') as fp:
		fp.write(anyjson.dumps(user_disp))

def _get_dist(user_id):
	con = psycopg2.connect(my.DB_CONN_STRING)
	cur = con.cursor()
	SQL = '''SELECT ST_X(geo), ST_Y(geo) \
			FROM  {rel_tweet} \
				WHERE user_id = %s \
			'''.format(rel_tweet=my.REL_TWEET)
	cur.execute(SQL, (user_id, ))
	recs = cur.fetchall()
	con.close()

	home = homes[str(user_id)]

	disp = []

	for rec in recs:
		lat, lng = rec
		dist = int(round(geo.distance(geo.xyz(home[0], home[1]), 
									geo.xyz(lat, lng))))
		if dist > 100:
			disp.append(dist)

	if len(disp) > 0:
		return disp


def plot_disp():
	with open('data/' + my.DATA_FOLDER + 'user_disp.json', 'rb') as fp:
		user_disp = anyjson.loads(fp.read())
	print len(user_disp), max(user_disp), min(user_disp), max(user_disp) - min(user_disp)
	user_disp = [d for d in user_disp if d <= my.MAX_DIST]
	print len(user_disp), max(user_disp), min(user_disp), max(user_disp) - min(user_disp)

	fig=plt.figure(figsize=(12, 2.5))
	fig.set_tight_layout(True)
	ax=fig.add_subplot(121)
	ax.set_xlabel('Distance')
	ax.set_ylabel('Count')
	n, b, _ = ax.hist(user_disp, bins=800, range=(0, my.MAX_DIST))

	#print len(n), n
	#print len(b), [int(round(i)) for i in b.tolist()]
	n = [i if i != 0.0 else 0.0001 for i in n]
	b = [int(round(i)) for i in b.tolist()]

	x = numpy.array(b[1:])
	y = numpy.array(n)
	logx = log10(x)
	logy = log10(y)

	fitfunc = lambda p, x: p[0] + p[1] * x
	errfunc = lambda p, x, y: (y - fitfunc(p, x))
	powerlaw = lambda x, amp, index: amp * (x**index)

	pinit = [1.0, -1.0]
	out = leastsq(errfunc, pinit, args=(logx, logy), full_output=1)
	pfinal = out[0]
	covar = out[1]
	index = pfinal[1]
	amp = 10.0**pfinal[0]

	ax.plot(x, powerlaw(x, amp, index), color='b', lw=2, alpha=0.75)
	ax.set_ylim(0, max(y))
	

	x = numpy.array(b[1:])
	#y = numpy.array(max_norm(n))	# MAX norm
	y = numpy.array(sum_norm(n))	# SUM norm
	logx = log10(x)
	logy = log10(y)

	pinit = [1.0, -1.0]
	out = leastsq(errfunc, pinit, args=(logx, logy), full_output=1)
	pfinal = out[0]
	covar = out[1]
	index = pfinal[1]
	amp = 10.0**pfinal[0]

	ax=fig.add_subplot(122)
	ax.plot(x, powerlaw(x, amp, index), color='r', lw=2, alpha=0.75)
	ax.plot(x, 1-powerlaw(x, amp, index), color='g', alpha=0.75)
	ax.set_ylim(0, max(y))

	#fig.suptitle('Distance Normalization')

	plt.savefig('data/' + my.DATA_FOLDER + 'user_disp' + '.pdf')

	with open('data/' + my.DATA_FOLDER + 'user_disp_param.json', 'wb') as fp:
		fp.write(anyjson.dumps({'amp': amp, 'index': index}))


def max_norm(x):
	if len(x) == 0: return []
	mx = float(max(x))
	x_ = [e/mx for e in x]
	return x_

def sum_norm(x):
	if len(x) == 0: return []
	sm = float(sum(x))
	x_ = [e/sm for e in x]
	return x_


#
# DIST NORM
#

def calc_user_visits_dist_norm():
	global homes
	with open('data/' + my.DATA_FOLDER + 'user_homes.json', 'rb') as fp:
		homes = anyjson.loads(fp.read())

	global loc_data
	with open('data/' + my.DATA_FOLDER + 'loc_data.json', 'rb') as fp:
		loc_data = anyjson.loads(fp.read())

	with open('data/' + my.DATA_FOLDER + 'user_race.json', 'rb') as fp:
		user_race = anyjson.loads(fp.read())
	user_ids = list(itertools.chain(*user_race.values()))

	#print len(user_ids)
	#for user_id in user_ids:
	#	_calc_visits(user_id)
	pool = Pool(my.PROCESSES)
	user_visits = pool.map(_calc_visits_dist_norm, user_ids)
	user_visits = dict(user_visits)

	with open('data/' + my.DATA_FOLDER + 'visits_dist_norm.json', 'wb') as fp:
		fp.write(jsb.beautify(anyjson.dumps(user_visits)))

def _calc_visits_dist_norm(user_id):
	con = psycopg2.connect(my.DB_CONN_STRING)
	cur = con.cursor()
	SQL = '''SELECT ST_X(geo), ST_Y(geo) \
			FROM  {rel_tweet} \
				WHERE user_id = %s \
			'''.format(rel_tweet=my.REL_TWEET)
	cur.execute(SQL, (user_id, ))
	recs = cur.fetchall()
	con.close()

	home = homes[str(user_id)]

	visits = [0.0]*6
	legend = {'w': 0, 'b': 1, 'a': 2, 'h': 3, 'o': 4}

	with open('data/' + my.DATA_FOLDER + 'user_disp_param.json', 'rb') as fp:
		param = anyjson.loads(fp.read())
	amp = param['amp']
	index = param['index']
	powerlaw = lambda x: amp * (x**index)

	for rec in recs:
		lat, lng = rec
		dist = int(round(geo.distance(geo.xyz(home[0], home[1]), 
									geo.xyz(lat, lng))))
		if dist > my.MIN_DIST:
			weight = 1 - powerlaw(dist)
			race = _find_race([user_id, [lat, lng]])
			if race:
				visits[legend[race[1]]] += weight
			else:
				visits[5] += weight
	visits = [round(i, 4) for i in visits]
	print [user_id, visits]
	return [user_id, visits]


#
# 
#
def plot_race_pies_dn():
	for race in ['w', 'b', 'a', 'h']:
		_plot_pies_dn(race)

def _plot_pies_dn(race):
	with open('data/' + my.DATA_FOLDER + 'user_race.json', 'rb') as fp:
		user_ids = anyjson.loads(fp.read())[race]

	with open('data/' + my.DATA_FOLDER + 'visits.json', 'rb') as fp:
		visits = anyjson.loads(fp.read())
	with open('data/' + my.DATA_FOLDER + 'visits_dist_norm.json', 'rb') as fp:
		visits_dn = anyjson.loads(fp.read())

	labels = ['White', 'Black', 'Asian', 'Hispanic', '', 'None']
	colors = ['lightskyblue', 'yellowgreen', '#C94949', 'orange', '#A65628', '#AAAAAA']

	sizes = [0]*6
	for user_id in user_ids:
		v = visits[str(user_id)]
		for i in range(6):
			sizes[i] += v[i]


	fig=plt.figure(figsize=(10, 10))
	#fig.set_tight_layout(True)
	plt.subplots_adjust(left=0.1, right=0.9, top=0.95, bottom=0.)
	
	ax=fig.add_subplot(221)
	ax.pie(	sizes[:-1], labels=labels[:-1], colors=colors[:-1],
			autopct='%1.1f%%', shadow=True, startangle=90)
	ax.axis('equal')
	ax.axis('off')
	ax.set_title('Absolute counts')

	ax=fig.add_subplot(222)
	ax.pie(	sizes, labels=labels, colors=colors,
			autopct='%1.1f%%', shadow=True, startangle=90)
	ax.axis('equal')
	ax.axis('off')
	ax.set_title('Absolute counts')


	sizes = [0]*6
	for user_id in user_ids:
		v = visits_dn[str(user_id)]
		for i in range(6):
			sizes[i] += v[i]

	ax=fig.add_subplot(223)
	ax.pie(	sizes[:-1], labels=labels[:-1], colors=colors[:-1],
			autopct='%1.1f%%', shadow=True, startangle=90)
	ax.axis('equal')
	ax.axis('off')
	ax.set_title('Distance norm.')

	ax=fig.add_subplot(224)
	ax.pie(	sizes, labels=labels, colors=colors,
			autopct='%1.1f%%', shadow=True, startangle=90)
	ax.axis('equal')
	ax.axis('off')
	ax.set_title('Distance norm.')

	plt.savefig('data/' + my.DATA_FOLDER + 'visit_dn_pie_' + race + '.png')




