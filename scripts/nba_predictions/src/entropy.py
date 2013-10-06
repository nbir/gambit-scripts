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
import anyjson
import psycopg2
import itertools
import matplotlib
import cPickle as pickle
import jsbeautifier as jsb
import multiprocessing as mp
import matplotlib.pyplot as plt

from math import *
from pylab import *
from pprint import pprint
from matplotlib  import cm
from pymining import itemmining
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from datetime import datetime, timedelta

import settings as my
sys.path.insert(0, os.path.abspath('..'))


#
# VOLUME MATRIX
#
def make_volume_mat():
	''''''
	with open('data/' + my.DATA_FOLDER + 'data_legend.json', 'rb') as fp:
		ids = anyjson.loads(fp.read()).keys()

	global data
	data = {}
	data_path = 'data/' + my.DATA_FOLDER + 'data/'
	for id in ids:
		data[id] = []
		with open(data_path + str(id) + '.txt', 'rb') as fp:
			cr = csv.reader(fp, delimiter=',')
			for row in cr:
				o = int(row[0])
				tweet = row[1].split()
				data[id].append(tuple([o, tweet]))
		data[id] = tuple(data[id])
	
	#for id in ids:
	#	_make_volume_mat(id)
	pool = mp.Pool(4)
	pool.map(_make_volume_mat, ids)

def _make_volume_mat(id):
	''''''
	print '\n', id, '\n'
	volume_mat = {}
	with open('data/' + my.DATA_FOLDER + 'sets.json', 'rb') as fp:
		sets = anyjson.loads(fp.read()).items()

	with open('data/' + my.DATA_FOLDER + 'time.json', 'rb') as fp:
		time = anyjson.loads(fp.read())
	ts_start = datetime.strptime(time['ts_start'], my.TS_FORMAT)
	ts_end = datetime.strptime(time['ts_end'], my.TS_FORMAT)
	diff = ts_end - ts_start
	diff = int(diff.total_seconds())
	combine = 120
	x, x_ticks, x_tickslabels = _make_x(ts_start, diff, combine=combine)
	
	for pid, st in sets:
		offsets = _get_offsets(id, st)
		print pid, st, len(offsets)
		y = dict((i, 0) for i in x)
		for o in offsets:
			idx = int(o/combine)
			if idx in y: y[idx] += 1
		y = y.values()
		volume_mat[pid] = y

	path = 'data/' + my.DATA_FOLDER + 'volume_mat/'
	if not os.path.exists(path): os.makedirs(path)
	with open(path + str(id) + '.json', 'wb') as fp:
		fp.write(jsb.beautify(anyjson.dumps(volume_mat)))

def _make_x(ts_start, diff, combine=120):
	points = diff / combine
	_1 = (1 * 60 * 60) / combine
	_12 = (12 * 60 * 60) / combine
	_24 = (24 * 60 * 60) / combine
	x = range(points+1)
	x_ticks = []
	x_tickslabels = []
	start = (ts_start.hour * 60 * 60) / combine
	for i in x:
		if (start + i) % _1 == 0:
			if (start + i) % _12 == 0:
				if (start + i) % _24 == 0:
					ts = ts_start + timedelta(seconds=i*combine)
					s = ts.strftime('%b %d')
				else:
					s = '12 N'
				x_ticks.append(i)
				x_tickslabels.append(s)
			else:
				hr = int(((start + i) % _24) / _1)
				x_ticks.append(i)
				if hr % 2 == 0:
					x_tickslabels.append(str(hr))
				else: x_tickslabels.append('')
	
	return x, x_ticks, x_tickslabels

def _get_offsets(id, st):
	''''''
	offsets = []
	for o, tweet in data[id]:
		tweet = set(tweet)
		match = False
		for p in st:
			if len(set(p) & tweet) >= len(p):
				offsets.append(o)
				break
	return offsets


#
# PLOT
#
def plot_volume_entropy():
	''''''
	with open('data/' + my.DATA_FOLDER + 'data_legend.json', 'rb') as fp:
		ids = anyjson.loads(fp.read()).keys()
	for id in ids:
		_plot_volume_entropy(id)
		

def _plot_volume_entropy(id):
	''''''
	with open('data/' + my.DATA_FOLDER + 'data_legend.json', 'rb') as fp:
		data_legend = anyjson.loads(fp.read())
	path = 'data/' + my.DATA_FOLDER + 'volume_mat/'
	with open(path + str(id) + '.json', 'rb') as fp:
		volume_mat = anyjson.loads(fp.read())

	mat = []
	ids = sorted([int(i) for i in volume_mat.keys()])
	for i in ids:
		mat.append(volume_mat[str(i)])
	# To limit # of players, change M
	M = len(mat)
	#M = 10
	N = len(mat[0])

	v = []
	e = []
	for n in range(N):
		x = [mat[m][n] for m in range(M)]
		volume = sum(x)
		entropy = _entropy(_norm(x))
		v.append(volume)
		e.append(entropy)

	combine = 2
	z = range(len(v))
	z = [i/float(60/combine) for i in z]
	print id, len(v), len(e)

	v = v[len(v)/2:]
	e = e[len(e)/2:]
	z = z[len(z)/2:]

	print id, len(v), len(e)

	fig = plt.figure(figsize=(12, 6))
	fig.set_tight_layout(True)


	#
	# Fig: Volume timeline
	x = range(721)
	x_ticks = [i for i in x if i % 60 == 0]
	x_tickslabels = [i/30 for i in x_ticks]
	x = x[len(x) - len(v):]

	#ax = fig.add_subplot(222)
	ax = fig.add_subplot(322)
	ax.autoscale_view()
	ax.set_xticks(x_ticks)
	ax.set_xticklabels(x_tickslabels)
	ax.xaxis.grid(True)
	ax.plot(x, v, '-', color='blue', alpha=0.9)
	ax.set_xlim(min(x), max(x))
	ax.set_title('Volume')

	#
	# Fig: 
	#ax = fig.add_subplot(224)
	ax = fig.add_subplot(324)
	ax.autoscale_view()
	ax.set_xticks(x_ticks)
	ax.set_xticklabels(x_tickslabels)
	ax.xaxis.grid(True)
	ax.plot(x, e, '-', color='red', alpha=0.9)
	ax.set_xlim(min(x), max(x))
	ax.set_title('Entropy')


	#
	#
	v, e, z = _trim(v, e, z, 0.90)

	v = np.array(v)
	e = np.array(e)

	#v = np.sqrt(v)
	#e = np.sqrt(e)
	
	print id, len(v), len(e), '\n'


	#
	# Fig: Volume-Entropy scatter
	ax = fig.add_subplot(121)
	ax.autoscale_view()
	ax.set_xlim((0,1))
	ax.set_ylim((0,1))
	ax.set_xlabel('Normalized Volume')
	ax.set_ylabel('Normalized Entropy')
	s = ax.scatter(_norm(v), _norm(e), marker='o', alpha=0.75, 
					c=z, cmap=cm.jet, edgecolors='#333333')
	fig.colorbar(s, ax=ax, orientation='horizontal',
				fraction=0.05, pad=0.1, aspect=30,
				ticks=range(int(min(z)), int(max(z))+1))

	#fig.suptitle(data_legend[id] + ' / ' + str(M) + ' teams', 
	fig.suptitle(data_legend[id] + ' / ' + str(M) + ' players', 
				fontsize=16, weight='semibold')

	

	path = 'data/' + my.DATA_FOLDER + 'plots/volume_entropy/'
	if not os.path.exists(path): os.makedirs(path)
	filename = str(id)
	#filename = data_legend[id].replace(' ', '_')
	plt.savefig(path + filename + '.' + 'pdf')



#
# ENTROPY - RANGE
#
def find_entropy_range():
	''''''
	with open('data/' + my.DATA_FOLDER + 'legend.json', 'rb') as fp:
		legend = anyjson.loads(fp.read())
	with open('data/' + my.DATA_FOLDER + 'picks_legend.json', 'rb') as fp:
		picks_legend = anyjson.loads(fp.read())
	ids = sorted([int(i) for i in legend.keys()])

	pick_ids = []
	for _, pick_name in picks_legend.items():
		for id, name in legend.items():
			if _match_names(pick_name, name):
				pick_ids.append(int(id))
				#print pick_name, '\t', name
	print sorted(pick_ids)
	
	offset = {}
	data_path = 'data/' + my.DATA_FOLDER + 'data/'
	for id in ids:
		offset[id] = []
		with open(data_path + str(id) + '.txt', 'rb') as fp:
			cr = csv.reader(fp, delimiter=',')
			for row in cr:
				o = int(row[0])
				offset[id].append(o)
		#print id, len(offset[id])

	with open('data/' + my.DATA_FOLDER + 'time.json', 'rb') as fp:
		time = anyjson.loads(fp.read())
	ts_start = datetime.strptime(time['ts_start'], my.TS_FORMAT)
	ts_end = datetime.strptime(time['ts_end'], my.TS_FORMAT)
	diff = ts_end - ts_start
	diff = int(diff.total_seconds())
	combine = 120
	x, x_ticks, x_tickslabels = _make_x(ts_start, diff, combine=combine)

	timeline = {}
	for id in ids:
		y = dict((i, 0) for i in x)
		for o in offset[id]:
			idx = int(o/combine)
			if idx in y: y[idx] += 1
		y = y.values()
		timeline[id] = y
	with open('data/' + my.DATA_FOLDER + 'timeline.json', 'wb') as fp:
		fp.write(jsb.beautify(anyjson.dumps(timeline)))

	x = []
	y = []
	x_p = []
	y_p = []
	for id in ids:
		r = max(timeline[id]) - min(timeline[id])
		e = _entropy(_norm(timeline[id]))
		r += 0.00001
		e += 0.00001
		if id in pick_ids:
			x_p.append(sqrt(r))
			y_p.append(sqrt(e))
		else:
			x.append(sqrt(r))
			y.append(sqrt(e))
	print len(x), len(y), len(x_p), len(y_p)

	fig = plt.figure(figsize=(6, 6))
	fig.set_tight_layout(True)
	ax = fig.add_subplot(111)
	ax.autoscale_view()
	ax.set_xlabel(r'$\sqrt{Range}$')
	ax.set_ylabel(r'$\sqrt{Entropy}$')
	ax.scatter(x, y, marker='o', alpha=0.4, 
				color='red', edgecolors='#333333', label='Non-picks')
	ax.scatter(x_p, y_p, marker='o', alpha=0.6, 
				color='blue', edgecolors='#333333', label='Picks')
	ax.legend()
	ax.set_title('')
	
	x1,x2,y1,y2 = plt.axis()
	plt.axis((0,x2,0,y2))
	plt.savefig('data/' + my.DATA_FOLDER + 'range-entropy' + '.' + 'pdf')

#
#
#
def _match_names(n1, n2):
	n1 = n1.lower().split()
	n2 = n2.lower().split()
	avg_len = min(len(n1), len(n2))
	thres = avg_len / 2.0
	intersect = set(n1) & set(n2)
	if len(intersect) > thres:
		return True
	else: return False


#
#
#
def _norm_all(X):
	X_ = []
	for x in X:
		X_.append(_norm(x))
	return X_

def _norm(x):
	if len(x) == 0: return []
	mx = float(max(x))
	mn = float(min(x))
	diff = mx - mn
	if diff == 0:
		return x
	x_ = [(e-mn)/diff for e in x]
	return x_

def _entropy(x):
	ent = -1 * sum([e * log(e) \
					for e in x if e != 0])
	if ent == 0: return 0
	return ent

def _trim(v, e, z, frac):
	data = zip(v, e, z)
	thres = sorted(v)[int(len(data)*frac)]
	data = [i for i in data if i[0] < thres]
	if len(data) == 0: return [0], [0], [0]
	v, e, z = zip(*data)
	return v, e, z
