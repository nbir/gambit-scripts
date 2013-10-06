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
import multiprocessing as mp
import matplotlib.pyplot as plt

from math import *
from pylab import *
from pprint import pprint
from pymining import itemmining
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from datetime import datetime, timedelta

import settings as my
sys.path.insert(0, os.path.abspath('..'))


#
# TEXT - FREQUENT PHRASES
#
def find_freq_phrases():
	''''''
	with open('data/' + my.DATA_FOLDER + 'sets.json', 'rb') as fp:
		ids = anyjson.loads(fp.read()).keys()
	
	for id in ids:
		try:
			_freq_phrases(id)
		except: pass
	#pool = mp.Pool(processes=my.PROCESSES)
	#pool.map(_freq_phrases, ids)

def _freq_phrases(id):
	'''Map function'''
	with open('data/' + my.DATA_FOLDER + 'sets.json', 'rb') as fp:
		sets = anyjson.loads(fp.read())
	keywords = tuple(itertools.chain(*sets[str(id)]))

	data_path = 'data/' + my.DATA_FOLDER + 'data/'
	with open(data_path + str(id) + '.txt', 'rb') as fp:
		cr = csv.reader(fp, delimiter=',')
		tweets = [row[1].split() for row in cr]
	tweets_len = len(tweets)
	print 'Tweets:', tweets_len
	if tweets_len < 5000: return

	fd = FreqDist(tuple(itertools.chain(*tweets)))
	vocab = fd.keys()[:-fd.Nr(1)]
	for w in keywords:
		if w in vocab: vocab.remove(w)
	print 'Tokens:', fd.N(), ',', fd.B(), '-', fd.Nr(1), '=', len(vocab)

	path = 'data/' + my.DATA_FOLDER + 'frequent_tokens/'
	if not os.path.exists(path): os.makedirs(path)
	with open(path + str(id) + '.txt', 'wb') as fp:
		fp.write('\n'.join(vocab))
	
	words = dict((w, vocab.index(w)) for w in vocab)
	tweets = tuple(tuple(words[w] for w in tw if w in words) \
									for tw in tweets)
	
	relim_input = itemmining.get_relim_input(tweets)
	print 'Generated Relim input... Min support:', math.sqrt(tweets_len)
	sets = itemmining.relim(relim_input, 
							min_support=int(math.sqrt(tweets_len)))
	print len(sets), min(sets.values()), max(sets.values())
	sets = sorted(sets.items(), key=lambda x:x[1], reverse=True)
	
	texts = []
	for s, f in sets[:1000]:
		txt = ' '.join(vocab[i] for i in tuple(s))
		texts.append(txt)

	path = 'data/' + my.DATA_FOLDER + 'frequent_phrases/'
	if not os.path.exists(path): os.makedirs(path)
	with open(path + str(id) + '_all' + '.pickle', 'wb') as fp:
		pickle.dump(sets, fp)
	with open(path + str(id) + '.pickle', 'wb') as fp:
		pickle.dump(sets[:my.K], fp)
	with open(path + str(id) + '.txt', 'wb') as fp:
		fp.write('\n'.join(texts))



#
# CHECK TIMELINES
#
def plot_timelines():
	''''''
	with open('data/' + my.DATA_FOLDER + 'sets.json', 'rb') as fp:
		ids = anyjson.loads(fp.read()).keys()

	for id in ids:
		print '\n', id
		_plot_timelines(id, 'frequent_tokens/')
		_plot_timelines(id, 'frequent_phrases/')
		#break

def _plot_timelines(id, folder):
	''''''
	with open('data/' + my.DATA_FOLDER + 'legend.json', 'rb') as fp:
		legend = anyjson.loads(fp.read())

	with open('data/' + my.DATA_FOLDER + 'time.json', 'rb') as fp:
		time = anyjson.loads(fp.read())
	ts_start = datetime.strptime(time['ts_start'], my.TS_FORMAT)
	ts_end = datetime.strptime(time['ts_end'], my.TS_FORMAT)
	diff = ts_end - ts_start
	diff = int(diff.total_seconds())
	combine = 120
	x, x_ticks, x_tickslabels = _make_x(ts_start, diff, combine=combine)

	path = 'data/' + my.DATA_FOLDER + folder
	if not os.path.exists(path + str(id) + '.txt'): return
	with open(path + str(id) + '.txt', 'rb') as fp:
		phrases = fp.read().split('\n')[:10]
	
	Y = []
	labels = []
	for phrase in phrases:
		offsets = _get_offsets(id, phrase.split())
		print phrase, len(offsets)
		labels.append(phrase)

		y = dict((i, 0) for i in x)
		for o in offsets:
			idx = int(o/combine)
			if idx in y: y[idx] += 1
		y = y.values()
		Y.append(y)

	path = 'data/' + my.DATA_FOLDER + 'plots/' + folder
	if not os.path.exists(path): os.makedirs(path)
	text = legend[id]
	_plot(x, Y, x_ticks=x_ticks, x_tickslabels=x_tickslabels, #norm=True,
		figsize=(15,3), alpha=0.65, in_text=text, y_labels=labels,
		path=path, filename=str(id), ext='pdf')
	_plot(x, Y, x_ticks=x_ticks, x_tickslabels=x_tickslabels, norm=True,
		figsize=(15,3), alpha=0.65, in_text=text + ', norm.', y_labels=labels,
		path=path, filename=str(id) + '_norm', ext='pdf')


def _get_offsets(id, phrase):
	''''''
	offsets = []
	p = set(phrase)
	p_len = len(phrase)
	data_path = 'data/' + my.DATA_FOLDER + 'data/'
	with open(data_path + str(id) + '.txt', 'rb') as fp:
		cr = csv.reader(fp, delimiter=',')
		for row in cr:
			o = int(row[0])
			tweet = row[1].split()
			if len(p & set(tweet)) >= p_len:
				offsets.append(o)
	return offsets

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

def _plot(x, Y, x_ticks=None, x_tickslabels=None, norm=False,
		figsize=(15,5), color=None, alpha=0.75, lw=1, fill=False, 
		y_labels=None, in_text=None, path=None, filename=None, ext='pdf'):
	if norm:
		Y = _norm_all(Y)

	fig = plt.figure(figsize=figsize)
	fig.set_tight_layout(True)
	ax = fig.add_subplot(111) 
	ax.autoscale_view()
	ax.set_xlim(min(x), max(x))
	ax.set_xticks(x_ticks)
	ax.set_xticklabels(x_tickslabels)
	ax.xaxis.grid(True)
	ax.text(0.05, 0.95, in_text, ha='left', va='top', 
				transform = ax.transAxes, family='monospace', fontsize=20)
	
	handles = []
	for y in Y:
		if color:
			h, = ax.plot(x, y, '-', lw=lw, color=color, alpha=alpha, label='')
		else:
			h, = ax.plot(x, y, '-', lw=lw, alpha=alpha, label='')
		handles.append(h)
		if fill:
			if color: fill_between(x, y, color=color, alpha=alpha)
			else: fill_between(x, y, alpha=alpha)

	if y_labels:
		l = ax.legend(handles, y_labels, ncol=2, fontsize=10)
		#l.get_frame().set_alpha(0.5)
		for lh in l.legendHandles:
			lh.set_linewidth(10)

	x1,x2,y1,y2 = plt.axis()
	plt.axis((x1,x2,0,y2))

	if hasattr(my, 'PICK_X_LIM'):
		ax.set_xlim(my.PICK_X_LIM)

	if not os.path.exists(path): os.makedirs(path)
	plt.savefig(path + filename + '.' + ext)


#
# PLOT TOP PHRASES BAR GRAPH
#
def plot_freq_bar():
	with open('data/' + my.DATA_FOLDER + 'sets.json', 'rb') as fp:
		ids = anyjson.loads(fp.read()).keys()

	for id in ids:
		print '\n', id
		#_plot_freq_bar(id, 'frequent_tokens/')
		_plot_freq_bar(id, 'frequent_phrases/')
		#break
	#pool = mp.Pool(processes=my.PROCESSES)
	#pool.map(_plot_freq_bar, zip(ids, ['frequent_phrases/'] * len(ids)))

def _plot_freq_bar(id, folder):
	#id, folder = data
	with open('data/' + my.DATA_FOLDER + 'legend.json', 'rb') as fp:
		legend = anyjson.loads(fp.read())

	path = 'data/' + my.DATA_FOLDER + folder
	with open(path + str(id) + '.txt', 'rb') as fp:
		phrases = fp.read().split('\n')[:50]
	
	y = []
	labels = []
	for phrase in phrases:
		freq = len(_get_offsets(id, phrase.split()))
		print phrase, freq
		y.append(freq)
		labels.append(phrase)
	
	fig = plt.figure(figsize=(15,5))
	fig.set_tight_layout(True)
	ax = fig.add_subplot(111) 
	ax.autoscale_view()

	width  = 2.4
	ind = np.arange(0, len(y)*3, 3)
	#FF3333, #339966
	ax.bar(ind, y, width, color='#339966', edgecolor='#339966', alpha=0.75)
	ax.set_xticks(ind + width/2)
	ax.set_xticklabels(labels, rotation=85, fontsize=12)
	ax.text(0.95, 0.95, legend[id], ha='right', va='top', 
				transform = ax.transAxes, family='monospace', fontsize=30)

	path = 'data/' + my.DATA_FOLDER + 'plots/most_' + folder
	if not os.path.exists(path): os.makedirs(path)
	filename = str(id)
	plt.savefig(path + filename + '.' + 'pdf')



#
#
#
def _norm_all(X):
	X_ = []
	for x in X:
		X_.append(_norm(x))
	return X_

def _norm(x):
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