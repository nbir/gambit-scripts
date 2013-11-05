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
import matplotlib
import numpy as np
import cPickle as pickle
import jsbeautifier as jsb
import matplotlib.pyplot as plt

from datetime import *
from pprint import pprint
from sklearn import cluster

import settings as my
sys.path.insert(0, os.path.abspath('..'))


#
# 
#
def male_average():
	''''''
	with open('data/' + my.DATA_FOLDER + 'dates.json', 'rb') as fp:
		dates = anyjson.loads(fp.read())
	path = 'data/' + my.DATA_FOLDER + 'grid_data/'

	X = []
	index = []

	for date in dates:
		with open(path + date + '.json', 'rb') as fp:
			data = anyjson.loads(fp.read())
			data = list(itertools.chain(*data))
			X.append(data)
			index.append(date)
	
	with open('data/' + my.DATA_FOLDER + 'X.json', 'wb') as fp:
		fp.write(jsb.beautify(anyjson.dumps(X)))
	with open('data/' + my.DATA_FOLDER + 'X_index.json', 'wb') as fp:
		fp.write(jsb.beautify(anyjson.dumps(index)))

def run_cluster():
	ks = [2, 3, 5, 7, 10]
	for k in ks:
		_run_cluster(k)


def _run_cluster(k=7):
	''''''
	with open('data/' + my.DATA_FOLDER + 'X.json', 'rb') as fp:
		X = anyjson.loads(fp.read())
	with open('data/' + my.DATA_FOLDER + 'X_index.json', 'rb') as fp:
		index = np.array(anyjson.loads(fp.read()))

	with open('data/' + my.DATA_FOLDER + 'grid.json', 'rb') as fp:
		grid = anyjson.loads(fp.read())

	cells = grid['cells']
	rows = grid['rows']
	columns = grid['columns']

	cls = cluster.KMeans(n_clusters=k)#, n_jobs=-1)
	cls.fit(X)
	path = 'data/' + my.DATA_FOLDER + 'clusters/' + str(k) + '/'
	if not os.path.exists(path): os.makedirs(path)
	with open(path + 'model' + '.pickle', 'wb') as fp:
		pickle.dump(cls, fp)

	for i in range(k):
		centroid = np.int_(cls.cluster_centers_[i]).reshape(rows, columns)
		labels = cls.labels_
		path = 'data/' + my.DATA_FOLDER + 'clusters/' + str(k) + '/'
		if not os.path.exists(path): os.makedirs(path)
		with open(path + str(i) + '_centroid' + '.json', 'wb') as fp:
			fp.write(jsb.beautify(anyjson.dumps(centroid.tolist())))
		with open(path + 'labels' + '.json', 'wb') as fp:
			fp.write(jsb.beautify(anyjson.dumps(labels.tolist())))

		idx = np.where(labels == i)
		dates = index[idx]
		days, days_ = _day_count(dates)
		info = 'k=' + str(k) + ' | ' + \
				'cluster ' + str(i) + ' | ' + \
				str(len(dates)) + ' days' + ' | ' + \
				days_
		print info

		# figure
		lat1, lng1, lat2, lng2 = my.BBOX
		xticks = np.arange(lng1, lng2, my.LNG_DELTA).tolist()
		xticks.append(lng2)
		yticks = np.arange(lat1, lat2 + my.LAT_DELTA, my.LAT_DELTA).tolist()

		fig=plt.figure(figsize=(10, 7.25))
		fig.set_tight_layout(True)
		ax=fig.add_subplot(111)
		ax.set_title(info, fontsize=17)
		ax.set_xlim(xticks[0], xticks[-1])
		ax.set_ylim(lat1, lat2)
		ax.set_xticks(xticks)
		ax.set_yticks(yticks)
		#ax.grid()
		ax.xaxis.set_ticklabels([])
		ax.yaxis.set_ticklabels([])
		plt.setp(plt.xticks()[1], rotation=90)

		ax.imshow(centroid, 
				cmap=plt.cm.hot, 
				extent=(lng1,lng2,lat1,lat2), 
				interpolation='nearest', 
				alpha=1)
		path = 'data/' + my.DATA_FOLDER + 'plot/' + str(k) + '/'
		if not os.path.exists(path): os.makedirs(path)
		plt.savefig(path + str(i) + '.pdf')

		pass

		bg = matplotlib.image.imread('data/' + my.DATA_FOLDER + 'map_grey.png')
		ax.imshow(bg, 
				aspect='auto', 
				extent=(lng1,lng2,lat1,lat2), 
				alpha=0.15)
		path = 'data/' + my.DATA_FOLDER + 'plot_map/' + str(k) + '/'
		if not os.path.exists(path): os.makedirs(path)
		plt.savefig(path + str(i) + '.png')


def _day_count(dates):
	''''''
	days = [0]*7
	for date in dates:
		date = datetime.strptime(date, my.DATE_FORMAT).date()
		days[date.weekday()] += 1
	day_keys = ['M', 'T', 'W', 'T', 'F', 'S', 'S']
	day_keys = ['m', 't', 'w', 't', 'f', 's', 's']
	days_ = ' '.join(
			map(':'.join, 
				zip(day_keys, map(str, days))))
	return days, days_


def predict():
	dates = ['2012-10-22', '2012-11-06', '2012-11-22', '2012-12-25', '2013-01-02',  '2013-02-03', '2013-02-24']

	events = ['3rd Presidential debate', 'Elections', 'Thanksgiving', 'Christmas', 'New Year', 'Super Bowl', 'Oscar']

	X = []
	index = []

	path = 'data/' + my.DATA_FOLDER + 'grid_data/'
	for date in dates:
		with open(path + date + '.json', 'rb') as fp:
			data = anyjson.loads(fp.read())
			data = list(itertools.chain(*data))
			X.append(data)
			index.append(date)
	
	ks = [2, 3, 5, 7, 10]
	for k in ks:
		print '\n', k
		path = 'data/' + my.DATA_FOLDER + 'clusters/' + str(k) + '/'
		with open(path + 'model' + '.pickle', 'rb') as fp:
			cls = pickle.load(fp)

		y_pred = cls.predict(X)
		pprint( zip(dates, events, y_pred))


