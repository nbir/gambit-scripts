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
import numpy
import anyjson
import datetime
import psycopg2
import itertools
import matplotlib
import numpy as np
import cPickle as pickle
import matplotlib.pyplot as plt

from math import *
from pylab import *
from pprint import pprint
from random import shuffle
from multiprocessing import Pool
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from datetime import datetime, timedelta

import settings as my
sys.path.insert(0, os.path.abspath('..'))


#
# TOP PLAYERS
#
def get_top_players():
	''''''
	print '\n', my.TS_START, my.TS_WINDOW, '\n'
	SQL = '''SELECT timestamp AT TIME ZONE '{tz}', text\
			FROM {rel_tweet} \
			WHERE timestamp BETWEEN '{ts_start}'
				AND timestamp '{ts_start}' + INTERVAL '{window} days'
			'''.format(rel_tweet=my.REL_TWEET, 
				ts_start=my.TS_START, window=my.TS_WINDOW, tz=my.TIMEZONE)

	print 'Querying DB...'
	con = psycopg2.connect(my.DB_CONN_STRING)
	cur = con.cursor()
	cur.execute(SQL)
	recs = cur.fetchall()
	con.close()
	print '{count} records retrieved.'.format(count=len(recs))

	global ts_start
	ts_start = datetime.strptime(my.TS_START, my.TS_FORMAT)
	td = timedelta(days=my.TS_WINDOW)
	ts_end = ts_start + td

	legend = {
		'legend' : {},
		'ts_start' : my.TS_START,
		'ts_end' : str(ts_end)
		}

	global vocab
	global names
	with open('data/' + my.DATA_FOLDER + 'nba_players.txt', 'rb') as fp:
		raw_names = fp.readlines()
	raw_names = [n.strip() for n in raw_names if n.strip()]
	names = {}
	for name in raw_names:
		id = raw_names.index(name)
		names[id] = tuple(tok.lower() for tok in name.split())
		legend['legend'][id] = name
	vocab = tuple(itertools.chain(*names.values()))

	more_stopwords = ['love']
	repeats = [n for n in vocab if vocab.count(n) > 1]
	for name in raw_names:
		id = raw_names.index(name)
		names[id] = tuple(tok.lower() for tok in name.split())
		names[id] = [n for n in names[id] if n not in repeats \
											and n not in my.STOPWORDS \
											and n not in more_stopwords]
	pprint(names)
	print repeats

	pool = Pool(processes=my.PROCESSES)
	matches = pool.map(_match_tweet, recs)
	matches = filter(None, matches)

	counts = dict((i, 0) for i in names.keys())
	c = 0
	for offset, match in matches:
		for i in match:
			if i in counts: counts[i] += 1
			c += 1
	print '{c} total matches.'.format(c=c)

	with open('data/' + my.DATA_FOLDER + 'player_legend.json', 'wb') as fp:
		fp.write(anyjson.dumps(legend))
	with open('data/' + my.DATA_FOLDER + 'player_counts.json', 'wb') as fp:
		fp.write(anyjson.dumps(counts))


def plot_top_players():
	''''''
	with open('data/' + my.DATA_FOLDER + 'player_legend.json', 'rb') as fp:
		legend = anyjson.loads(fp.read())
	with open('data/' + my.DATA_FOLDER + 'player_counts.json', 'rb') as fp:
		counts = anyjson.loads(fp.read())
	counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)

	x = [x[1] for x in counts[:my.TOP_N]]
	labels = list(legend['legend'][x[0]] for x in counts[:my.TOP_N])
	#labels = list(x[0] for x in counts[:my.TOP_N])
	others = sum(x[1] for x in counts[my.TOP_N:])
	x.append(others)
	labels.append('Others')
	my_norm = matplotlib.colors.Normalize(min(x), max(x[:-1])+x[1])
	my_cmap = matplotlib.cm.get_cmap('Set2')
	
	fig = plt.figure(figsize=(15,15))
	#fig.set_tight_layout(True)
	ax = fig.add_subplot(111) 
	ax.autoscale_view()
	ax.pie(x, labels=labels, colors=my_cmap(my_norm(x)), 
			startangle=-50)

	filename = 'top_' + str(my.TOP_N) + '_players'
	plt.savefig('data/' + my.DATA_FOLDER + filename + '.' + 'pdf')

	tex = []
	for i in range(len(x)):
		tex.append(' & ' + str(i + 1) + '\t & ' \
			+ labels[i] + '\t & ' \
			+ '{:,d}'.format(x[i]) + '\t \\\ ')
	with open('data/' + my.DATA_FOLDER + 'tex_' + filename + '.tex', 'wb') as fp:
		fp.write('\n'.join(tex))


#
# PLAYER - TIME OFFSETS
#
def get_player_times():
	_get_timeline('nba_players.txt')

def get_pick_times():
	_get_timeline('nba_picks.txt')


def _get_timeline(filename):
	''''''
	print '\n', my.TS_START, my.TS_WINDOW, '\n'
	SQL = '''SELECT timestamp AT TIME ZONE '{tz}', text\
			FROM {rel_tweet} \
			WHERE timestamp BETWEEN '{ts_start}'
				AND timestamp '{ts_start}' + INTERVAL '{window} days'
			'''.format(rel_tweet=my.REL_TWEET, 
				ts_start=my.TS_START, window=my.TS_WINDOW, tz=my.TIMEZONE)

	print 'Querying DB...'
	con = psycopg2.connect(my.DB_CONN_STRING)
	cur = con.cursor()
	cur.execute(SQL)
	recs = cur.fetchall()
	con.close()
	print '{count} records retrieved.'.format(count=len(recs))

	global ts_start
	ts_start = datetime.strptime(my.TS_START, my.TS_FORMAT)
	td = timedelta(days=my.TS_WINDOW)
	ts_end = ts_start + td

	legend = {
		'legend' : {},
		'ts_start' : my.TS_START,
		'ts_end' : str(ts_end)
		}
	offsets = {}

	global vocab
	global names
	with open('data/' + my.DATA_FOLDER + filename, 'rb') as fp:
		raw_names = fp.readlines()
	raw_names = [n.strip() for n in raw_names]
	names = {}
	for name in raw_names:
		id = raw_names.index(name)
		names[id] = tuple(tok.lower() for tok in name.split())
		legend['legend'][id] = name
		offsets[id] = []
	vocab = tuple(itertools.chain(*names.values()))

	more_stopwords = ['love', 'west', 'wall', 'iii', 'len', 'ty', 'jj', 'jr', 'gay', 'ed', 'ish', 'j.r.', 'p.j.', 'mo']
	repeats = [n for n in vocab if vocab.count(n) > 1]
	for name in raw_names:
		id = raw_names.index(name)
		names[id] = tuple(tok.lower() for tok in name.split())
		names[id] = [n for n in names[id] if n not in repeats \
											and n not in my.STOPWORDS \
											and n not in more_stopwords]

	pprint(names)
	pool = Pool(processes=my.PROCESSES)
	matches = pool.map(_match_tweet, recs)
	matches = filter(None, matches)

	c = 0
	for offset, match in matches:
		for i in match:
			offsets[i].append(offset)
			c += 1
	print '{c} total matches.'.format(c=c)

	with open('data/' + my.DATA_FOLDER + 'player_legend.json', 'wb') as fp:
		fp.write(anyjson.dumps(legend))
	with open('data/' + my.DATA_FOLDER + 'player_offsets.json', 'wb') as fp:
		fp.write(anyjson.dumps(offsets))

def _match_tweet(rec):
	'''Map function'''
	text = rec[1].lower()
	toks = nltk.word_tokenize(text)
	toks = [t for t in toks \
				]
				#and t.isalpha()]
	if len(set(toks) & set(vocab)) > 0:
		match = []
		for id, name in names.iteritems():
			if len(set(toks) & set(name)) > 0:
				match.append(id)

		ts = rec[0]
		diff = ts - ts_start
		diff = int(diff.total_seconds())
		
		return (diff, tuple(match))
	else:
		return None

#
# PLOT - PLAYER TIMELINE
#
def plot_players():
	''''''
	with open('data/' + my.DATA_FOLDER + 'player_legend.json', 'rb') as fp:
		legend = anyjson.loads(fp.read())
	with open('data/' + my.DATA_FOLDER + 'player_offsets.json', 'rb') as fp:
		offsets = anyjson.loads(fp.read())

	ts_start = datetime.strptime(legend['ts_start'], my.TS_FORMAT)
	ts_end = datetime.strptime(legend['ts_end'], my.TS_FORMAT)
	diff = ts_end - ts_start
	diff = int(diff.total_seconds())
	combine = 120
	x, x_ticks, x_tickslabels = _make_x(ts_start, diff, combine=combine)
	
	path = 'data/' + my.DATA_FOLDER  + 'plots/'
	Y = []
	for pid, offset in offsets.iteritems():
		y = dict((i, 0) for i in x)
		for o in offset:
			idx = int(o/combine)
			if idx in y: y[idx] += 1
		y = y.values()
		Y.append(y)

		player_name = legend['legend'][pid]
		txt = '#' + str(int(pid)+1) + ' ' + player_name
		filename = player_name.replace(' ', '_').replace('.','_')
		if my.PLOT_SEPERATE:
			_plot(x, [y], x_ticks=x_ticks, x_tickslabels=x_tickslabels, 
				figsize=(15,3), color='#46A492', alpha=0.75, fill=True,
				in_text=txt, path=path, filename=filename, ext='pdf')
	
	E = [round(_entropy(_norm(y)), 4) for y in Y]
	file('data/' + my.DATA_FOLDER + 'entropies.json', 'wb').write(anyjson.dumps(E))
	R = [max(y) - min(y) for y in Y]
	file('data/' + my.DATA_FOLDER + 'ranges.json', 'wb').write(anyjson.dumps(R))

	text = 'All Picks (' + str(len(Y)) + ' p.) norm.'
	
	#for e in range(0, 180, 5):
	#e = 30
	#lt = 75
	#Y_ = _trim_by_entropy(Y, gt=e, lt=lt)
	#text = 'Entropy ' + str(e) + '-' + str(lt) + ' (' + str(len(Y_)) + ' p.) norm.'

	_plot(x, Y, x_ticks=x_ticks, x_tickslabels=x_tickslabels, norm=True,
		figsize=(15,3), alpha=0.65, 
		in_text=text, path=path, filename=text.replace(' ', '_').replace('.', ''), ext='pdf')
	 

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
		ax.legend(handles, y_labels)

	x1,x2,y1,y2 = plt.axis()
	plt.axis((x1,x2,0,y2))

	if hasattr(my, 'PICK_X_LIM'):
		ax.set_xlim(my.PICK_X_LIM)

	if not os.path.exists(path): os.makedirs(path)
	plt.savefig(path + filename + '.' + ext)


#
# PLOT AUX
#
def _trim_by_entropy(X, gt=-1, lt=-1):
	X_ = []
	for x in X:
		e = round(_entropy(_norm(x)), 4)
		flag = False
		if gt != -1 and e > gt:
			if lt == -1 or (lt != -1 and e <= lt):
				flag = True
		elif lt != -1 and e <= lt:
			if gt == -1 or (gt != -1 and e > gt):
				flag = True
		else: flag = False

		if flag: X_.append(x)
	return X_

def plot_entropies():
	E = anyjson.loads(file('data/' + my.DATA_FOLDER + 'entropies.json', 'rb').read())
	num_bins = 100
	fig = plt.figure(figsize=(6,4))
	fig.set_tight_layout(True)
	ax = fig.add_subplot(111)
	ax.hist(E, num_bins, facecolor='green', alpha=0.5)
	ax.set_xlabel('Entropy')
	plt.savefig('data/' + my.DATA_FOLDER + 'entropies.pdf')

def plot_ranges():
	R = anyjson.loads(file('data/' + my.DATA_FOLDER + 'ranges.json', 'rb').read())
	num_bins = 100
	fig = plt.figure(figsize=(6,4))
	fig.set_tight_layout(True)
	ax = fig.add_subplot(111)
	ax.hist(R, num_bins, facecolor='blue', alpha=0.5)
	ax.set_xlabel('Range')
	plt.savefig('data/' + my.DATA_FOLDER + 'ranges.pdf')



#
# PLOT - NON PICKS
#
def plot_non_picks():
	with open('data/' + my.DATA_FOLDER + 'player_legend.json', 'rb') as fp:
		legend = anyjson.loads(fp.read())
	with open('data/' + my.DATA_FOLDER + 'player_offsets.json', 'rb') as fp:
		offsets = anyjson.loads(fp.read())
	with open('data/' + my.DATA_FOLDER + 'nba_picks.txt', 'rb') as fp:
		pick_names = fp.readlines()

	pick_ids = []
	for id, n1 in legend['legend'].iteritems():
		for n2 in pick_names:
			if _match_names(n1, n2):
				pick_ids.append(id)
				pick_names.remove(n2)
				#print n1, '\t', n2.strip()
				break
	print len(pick_ids), ' matched.', 'Not matched: ', pick_names
	
	ts_start = datetime.strptime(legend['ts_start'], my.TS_FORMAT)
	ts_end = datetime.strptime(legend['ts_end'], my.TS_FORMAT)
	diff = ts_end - ts_start
	diff = int(diff.total_seconds())
	combine = 120
	x, x_ticks, x_tickslabels = _make_x(ts_start, diff, combine=combine)
	
	path = 'data/' + my.DATA_FOLDER  + 'plots/'
	Y = []
	Y_ = {}
	R_ = {}
	for pid, offset in offsets.iteritems():
		if pid not in pick_ids:
			y = dict((i, 0) for i in x)
			for o in offset:
				idx = int(o/combine)
				if idx in y: y[idx] += 1
			y = y.values()
			if max(y) - min(y):
				Y.append(y)

				Y_[pid] = y
				R_[pid] = max(y) - min(y)

				player_name = legend['legend'][pid]
				txt = '#' + str(int(pid)+1) + ' ' + player_name
				filename = player_name.replace(' ', '_').replace('.','_')
				if my.PLOT_SEPERATE:
					_plot(x, [y], 
						x_ticks=x_ticks, x_tickslabels=x_tickslabels, 
						figsize=(15,3), color='#46A492', alpha=0.75, fill=True,
						in_text=txt, path=path, filename=filename, ext='pdf')
		
	E = [round(_entropy(_norm(y)), 4) for y in Y]
	file('data/' + my.DATA_FOLDER + 'entropies.json', 'wb').write(anyjson.dumps(E))
	R = [max(y) - min(y) for y in Y]
	file('data/' + my.DATA_FOLDER + 'ranges.json', 'wb').write(anyjson.dumps(R))

	R_ = sorted(R_.items(), key=lambda x: x[1])
	print len(R_)

	c = 0
	i = 0
	while i <= len(R_):
		r = (i, i+50)
		c += 1
		print c, r
		i += 50
		y = [Y_[item[0]] for item in R_[r[0] : r[1]]]

		text = 'Non Picks (' + str(len(y)) + ' p.)' + ' set ' + str(c)
		_plot(x, y, x_ticks=x_ticks, x_tickslabels=x_tickslabels, #norm=True,
		figsize=(15,3), alpha=0.65, 
		in_text=text, path=path, filename=text.replace(' ', '_').replace('.', ''), ext='pdf') 

	text = 'All Non Picks (' + str(len(Y)) + ' p.)'
	_plot(x, Y, x_ticks=x_ticks, x_tickslabels=x_tickslabels, #norm=True,
		figsize=(15,3), alpha=0.65, 
		in_text=text, path=path, filename=text.replace(' ', '_').replace('.', ''), ext='pdf') 

def _match_names(n1, n2):
	n1 = n1.lower().split()
	n2 = n2.lower().split()
	avg_len = min(len(n1), len(n2))
	thres = avg_len / 2.0
	intersect = set(n1) & set(n2)
	if len(intersect) > thres:
		return True
	else: return False

def make_img_tex():
	''''''
	with open('data/' + my.DATA_FOLDER + 'player_legend.json', 'rb') as fp:
		legend = anyjson.loads(fp.read())
	players = sorted(legend['legend'].items(), key=lambda x: int(x[0]))

	img = '''
		\\begin{figure}[H]
			\centering
			\includegraphics[width=7.5in]{gfx/\subfolder/%s}
		\end{figure}
		'''
	img = '''
		\\begin{centering}
			\includegraphics[width=7.5in]{gfx/\subfolder/%s}
		\end{centering}
		'''
	tex = []
	for pid, name in players:
		filename = name.replace(' ', '_').replace('.','_')
		tex.append(img % (filename))
		print img % (filename)

	with open('data/' + my.DATA_FOLDER + 'tex_img.tex', 'wb') as fp:
		fp.write('\n'.join(tex))


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


