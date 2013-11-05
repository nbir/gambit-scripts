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
import itertools
import numpy as np
import lib.geo as geo
import jsbeautifier as jsb
import matplotlib.pyplot as plt

from time import sleep
from matplotlib import cm
from osgeo import ogr, osr
from multiprocessing import Pool
from random import shuffle, randint
from mpl_toolkits.mplot3d import Axes3D

import settings as my
sys.path.insert(0, os.path.abspath('..'))


#
# POPULATION
#
def make_grid():
	path = 'data/' + my.DATA_FOLDER + 'artificial/'
	if not os.path.exists(path): os.makedirs(path)

	lat1 = ( my.LAT_RANGE[0] / my.DELTA_METERS ) * my.LAT_DELTA
	lat2 = ( my.LAT_RANGE[1] / my.DELTA_METERS ) * my.LAT_DELTA
	lng1 = ( my.LNG_RANGE[0] / my.DELTA_METERS ) * my.LNG_DELTA
	lng2 = ( my.LNG_RANGE[1] / my.DELTA_METERS ) * my.LNG_DELTA
	print lng1, lng2, lat1, lat2
	X = np.arange(lng1, lng2, my.LNG_DELTA)
	Y = np.arange(lat1, lat2, my.LAT_DELTA)
	#XY = list( itertools.product(X, Y) )
	#print len(XY)
	#XY = np.array( XY )
	#print len(X), len(Y), len(X) * len(Y), XY.shape, len(XY), len(XY.tolist())
	#print XY.reshape(len(X), len(Y), 2).reshape(len(X), len(Y), 2)
	#XY = XY.reshape(len(X), len(Y), 2).tolist()

	#with open(path + 'grid_coordinates.json', 'wb') as fp:
	#	fp.write( anyjson.dumps( XY ) )

	with open('data/' + my.DATA_FOLDER + 'user_disp_param.json', 'rb') as fp:
		disp_param = anyjson.loads(fp.read())
	amp = disp_param['amp']
	index = disp_param['index']
	powerlaw = lambda x: amp * (x**index) if x != 0 else 0

	delta = []
	theta = []
	prob = []
	points = []		# stored as (y, x) or (lat, lng)
	for y in Y:
		this_delta = []
		this_theta = []
		this_prob = []
		for x in X:
			dist = int(round( geo.distance(	geo.xyz(0, 0), geo.xyz(y, x) )))
			this_delta.append( powerlaw(dist) ) 
			this_theta.append( 1.0/360 )
			this_prob.append( powerlaw(dist) * 1.0/360 )
			points.append( (y, x, powerlaw(dist) * 1.0/360) )
		delta.append(this_delta)
		theta.append(this_theta)
		prob.append(this_prob)
	
	all_prob = list(itertools.chain(*prob))
	print min(all_prob), max(all_prob)
	mn = min(tuple(i for i in all_prob if i!=0))
	print sum(int(round(i/mn)) for i in all_prob)
	
	points_ = []
	for p in points:
		for i in range(int(round( p[2]/mn ))):
			points_.append( ( round(p[0], 4), round(p[1], 4) ) )
	print len(points), len(points_)
	with open(path + 'artificial_points.json', 'wb') as fp:
		fp.write( anyjson.dumps( points_ ) )
	
	with open(path + 'grid_delta.json', 'wb') as fp:
		fp.write( anyjson.dumps( delta ) )
		#fp.write( jsb.beautify( anyjson.dumps( delta ) ) )
	with open(path + 'grid_theta.json', 'wb') as fp:
		fp.write( anyjson.dumps( theta ) )
		#fp.write( jsb.beautify( anyjson.dumps( theta ) ) )
	with open(path + 'grid_prob.json', 'wb') as fp:
		fp.write( anyjson.dumps( prob ) )
		#fp.write( jsb.beautify( anyjson.dumps( prob ) ) )

	fig=plt.figure(figsize=(10, 10))
	fig.set_tight_layout(True)
	ax=fig.add_subplot(111)
	ax.set_xlim(lng1, lng2)
	ax.set_ylim(lat1, lat2)
	ax.grid()
	ax.set_title('Single User Sample Space')
	plt.savefig(path + 'artificial_grid' + '.png')


def plot_sample_space():
	path = 'data/' + my.DATA_FOLDER + 'artificial/'
	with open(path + 'grid_prob.json', 'rb') as fp:
		prob = anyjson.loads(fp.read())
	for i in range(len(prob)):
		for j in range(len(prob[0])):
			if prob[i][j] == 0:
				prob[i][j] = 0.3
	prob = np.array(prob)
	print prob.shape

	lat1 = ( my.LAT_RANGE[0] / my.DELTA_METERS ) * my.LAT_DELTA
	lat2 = ( my.LAT_RANGE[1] / my.DELTA_METERS ) * my.LAT_DELTA
	lng1 = ( my.LNG_RANGE[0] / my.DELTA_METERS ) * my.LNG_DELTA
	lng2 = ( my.LNG_RANGE[1] / my.DELTA_METERS ) * my.LNG_DELTA
	print lng1, lng2, lat1, lat2
	X, Y = np.mgrid[lng1:lng2:my.LNG_DELTA, lat1:lat2:my.LAT_DELTA]
	print X.shape
	print Y.shape

	fig = plt.figure()
	ax = fig.gca(projection='3d')
	#surf = ax.plot_wireframe(X, Y, prob, cmap='autumn')
	surf = ax.plot_surface(X, Y, prob, cmap=cm.coolwarm, linewidth=0)
	ax.set_xlabel("Lng")
	ax.set_ylabel("Lat")
	ax.set_zlabel("Probability")
	ax.set_xlim(-0.01, 0.01)
	ax.set_ylim(-0.01, 0.01)
	#ax.set_zlim(0, 2)
	plt.savefig(path + 'artificial_grid' + '.pdf')

def plot_sample_points():
	path = 'data/' + my.DATA_FOLDER + 'artificial/'
	with open(path + 'artificial_points.json', 'rb') as fp:
		points = anyjson.loads(fp.read())
	points = np.array(points)
	print points.shape

	fig = plt.figure(figsize=(100,100))
	ax = fig.add_subplot(111)
	ax.plot(points[:, 1], points[:, 0], 'k,', alpha=0.25)
	plt.savefig(path + 'artificial_grid_points' + '.png')


#
# TWEETS
#
def make_artificial_index():
	with open('data/' + my.DATA_FOLDER + 'users_in_tracts.json', 'rb') as fp:
		user_ids = anyjson.loads(fp.read())
	with open('data/' + my.DATA_FOLDER + 'user_tweet_count.json', 'rb') as fp:
		tweet_count = anyjson.loads(fp.read())

	ip = []
	for user_id in user_ids:
		ip.append( (user_id, tweet_count[str(user_id)], 12088806) )
	pool = Pool(my.PROCESSES)
	indexes = pool.map(_random_index, ip)
	indexes = dict(indexes)

	with open('data/' + my.DATA_FOLDER + 'data/' + \
				'artificial_indexes.json', 'wb') as fp:
		fp.write( anyjson.dumps( indexes ) )

def _random_index(ip):
	user_id, count, mx = ip
	index = []
	for i in range(count):
		index.append( randint(0, mx) )
	return (user_id, index)


def make_artificial_tweets():
	with open('data/' + my.DATA_FOLDER + 'user_homes.json', 'rb') as fp:
		user_homes = anyjson.loads(fp.read())
	path = 'data/' + my.DATA_FOLDER + 'data/'
	with open(path + 'artificial_indexes.json', 'rb') as fp:
		indexes = anyjson.loads(fp.read())

	with open('data/' + my.DATA_FOLDER + 'artificial/' + \
				'artificial_points.json', 'rb') as fp:
		artificial_points = anyjson.loads(fp.read())
	shuffle(artificial_points)

	tweets = {}
	for user_id, index in indexes.iteritems():
		tweets[user_id] = []
		home = user_homes[str(user_id)]
		home = ( round(home[0], 4), round(home[1], 4))
		for i in index:
			tweets[user_id].append((home[0] + artificial_points[i][0],
									home[1] + artificial_points[i][1]))
		print user_id, len(tweets[user_id])

	with open(path + 'artificial_tweets.json', 'wb') as fp:
		fp.write( anyjson.dumps(tweets) )

	tweets = list(itertools.chain(*tweets.values()))

	with open(path + 'artificial_all_tweets.json', 'wb') as fp:
		fp.write( anyjson.dumps(tweets) )

def split_tweet_file():
	path = 'data/' + my.DATA_FOLDER + 'data/'
	with open(path + 'artificial_tweets.json', 'rb') as fp:
		tweets = anyjson.loads( fp.read() )

	path = 'data/' + my.DATA_FOLDER + 'data/' + 'artificial_tweets/'
	if not os.path.exists(path): os.makedirs(path)
	for user_id, tw in tweets.iteritems():
		with open(path + str(user_id) + '.json', 'wb') as fp:
			fp.write(anyjson.dumps(tw))


