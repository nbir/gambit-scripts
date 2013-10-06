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
import numpy as np
import cPickle as pickle
import matplotlib.pyplot as plt

from pylab import *
from pprint import pprint
from pymining import itemmining
from multiprocessing import Pool
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from datetime import datetime, timedelta

import settings as my
sys.path.insert(0, os.path.abspath('..'))


#
# TEXT - VOCABULARY
#
def get_vocab():
	''' '''
	print my.TS_START, my.TS_WINDOW, '\n'
	SQL = '''SELECT text\
			FROM {rel_tweet} \
			WHERE timestamp BETWEEN '{ts_start}'
				AND timestamp '{ts_start}' + INTERVAL '{window} days'
			'''.format(rel_tweet=my.REL_TWEET, 
				ts_start=my.TS_START, window=my.TS_WINDOW)

	print 'Querying DB...'
	con = psycopg2.connect(my.DB_CONN_STRING)
	cur = con.cursor()
	cur.execute(SQL)
	recs = cur.fetchall()
	con.close()
	print '{count} records retrieved.'.format(count=len(recs))

	global sw
	sw = stopwords.words('english')
	sw.extend(my.STOPWORDS)
	sw = list(set(sw))

	pool = Pool(processes=my.PROCESSES)
	tweets = pool.map(_prep_tweet, recs)
	tweets = list(itertools.chain(*tweets))
	fd = FreqDist(tweets)
	print '\n'
	print fd.B(), fd.N(), fd.Nr(1)
	
	keys = fd.keys()
	with open('data/' + my.DATA_FOLDER + 'vocab_1m.txt', 'wb') as fp:
		#fp.write(anyjson.dumps(keys[:1000000]))
		fp.write('\n'.join(keys[:1000000]))
	keys = keys[:my.VOCAB_SIZE]
	with open('data/' + my.DATA_FOLDER + 'tokens.json', 'wb') as fp:
		fp.write(anyjson.dumps(keys))

def _prep_tweet(rec):
	'''Map function'''
	text = rec[0].lower()
	toks = nltk.word_tokenize(text)
	toks = [t for t in toks \
				if t not in sw \
				and t.isalpha()]
	return toks

def add_nba_vocab():
	"""nba_vocab = []
	with open('data/' + my.DATA_FOLDER + 'default_streams.csv', 'rb') as fp:
		cr = csv.reader(fp, delimiter=',')
		for row in cr:
			print row
			row.pop(0)
			for element in row:
				nba_vocab.extend(element.lower().split())
	with open('data/' + my.DATA_FOLDER + 'nba_vocab.txt', 'wb') as fp:
		fp.write('\n'.join(list(set(nba_vocab))))
	"""
	with open('data/' + my.DATA_FOLDER + 'tokens.json', 'rb') as fp:
		vocab = anyjson.loads(fp.read())
	with open('data/' + my.DATA_FOLDER + 'nba_vocab.txt', 'rb') as fp:
		nba_vocab = fp.read().split()
	with open('data/' + my.DATA_FOLDER + 'nba_players.txt', 'rb') as fp:
		nba_players = fp.read().split()
	nba_players = [n.lower() for n in nba_players]
	
	print len(vocab), len(nba_vocab), len(nba_players)
	vocab = tuple(set(vocab) | set(nba_vocab) | set(nba_players))
	print len(vocab)
	
	with open('data/' + my.DATA_FOLDER + 'tokens.json', 'wb') as fp:
		fp.write(anyjson.dumps(vocab))


#
# TEXT - FREQUENT SETS
#
def find_freq_sets():
	'''Match'''
	print '\n', my.TS_START, my.TS_WINDOW, '\n'
	SQL = '''SELECT timestamp, text\
			FROM {rel_tweet} \
			WHERE timestamp BETWEEN '{ts_start}'
				AND timestamp '{ts_start}' + INTERVAL '{window} days'
			'''.format(rel_tweet=my.REL_TWEET, 
				ts_start=my.TS_START, window=my.TS_WINDOW)

	print 'Querying DB...'
	con = psycopg2.connect(my.DB_CONN_STRING)
	cur = con.cursor()
	cur.execute(SQL)
	recs = cur.fetchall()
	con.close()
	print '{count} records retrieved.'.format(count=len(recs))

	global sw
	sw = stopwords.words('english')
	sw.extend(my.STOPWORDS)
	sw = list(set(sw))

	global tokens
	with open('data/' + my.DATA_FOLDER + 'tokens.json', 'rb') as fp:
		tokens = sorted(anyjson.loads(fp.read()))
	print len(tokens)
	pool = Pool(processes=my.PROCESSES)
	tweets = pool.map(_trim_tweet, recs)
	tweets = filter(None, tweets)
	tweets_len = len(tweets)
	recs = None
	print '{count} tokenized tweets to be processed.'.format(count=len(tweets))

	# Frequent itemset mining
	relim_input = itemmining.get_relim_input(tweets)
	tweets = None
	print 'Generated Relim input.'
	sets = itemmining.relim(relim_input, 
							min_support=int(math.sqrt(tweets_len)))
	relim_input = None
	print len(sets), min(sets.values()), max(sets.values())
	sets = sorted(sets.items(), key=lambda x:x[1], reverse=True)
	texts = []
	for s, f in sets[:my.K]:
		txt = ' '.join(tokens[i] for i in list(s))
		texts.append(txt)

	filename = 'data/' + my.DATA_FOLDER  + 'frequent_sets'
	with open(filename + '_all' + '.pickle', 'wb') as fp:
		pickle.dump(sets, fp)
	with open(filename + '.pickle', 'wb') as fp:
		pickle.dump(sets[:my.K], fp)
	with open(filename + '.txt', 'wb') as fp:
		fp.write('\n'.join(texts))

def _trim_tweet(rec):
	'''Map function'''
	text = rec[1].lower()
	toks = nltk.word_tokenize(text)
	toks = [t for t in toks \
				if t not in sw \
				]
				#and t.isalpha()]
	toks = tuple(set(toks) & set(tokens))
	tw = tuple(tokens.index(i) for i in toks)
	return tw
		

def trim_freq_sets():
	'''Trim freq. sets of phrases containing tokens from vocab_remove.txt'''
	with open('data/' + my.DATA_FOLDER + 'tokens.json', 'rb') as fp:
		tokens = sorted(anyjson.loads(fp.read()))
	remove = []
	filename = 'data/' + my.DATA_FOLDER + 'vocab_remove.txt'
	if os.path.exists(filename):
		with open(filename, 'rb') as fp:
			remove = fp.read().split()
	remove = set(tokens.index(i) for i in remove if i in tokens)
	filename = 'data/' + my.DATA_FOLDER  + 'frequent_sets'
	with open(filename + '_all' + '.pickle', 'rb') as fp:
		sets = pickle.load(fp)

	texts = []
	new_sets = []
	extent = 0
	for s, f in sets:
		extent += 1
		if len(s & remove) == 0:
			txt = ' '.join(tokens[i] for i in list(s))
			texts.append(txt)
			new_sets.append((s, f))
			if len(texts) >= my.K: break
	print 'Trimmed to {k} of {e}'.format(k=len(texts), e=extent)

	with open(filename + '.pickle', 'wb') as fp:
		pickle.dump(new_sets, fp)
	with open(filename + '.txt', 'wb') as fp:
		fp.write('\n'.join(texts))
	

def group_by_len():
	'''Group freq. sets by length and write to groups.json'''
	with open('data/' + my.DATA_FOLDER + 'tokens.json', 'rb') as fp:
		tokens = sorted(anyjson.loads(fp.read()))
	with open('data/' + my.DATA_FOLDER + \
						'frequent_sets' + '.pickle', 'rb') as fp:
		sets = pickle.load(fp)
	
	groups = {}
	for s, f in sets[:my.K]:
		l = len(list(s))
		txt = ' '.join(tokens[i] for i in list(s))
		if l not in groups:
			groups[l] = []
		groups[l].append((txt, f))
	with open('data/' + my.DATA_FOLDER  + \
						'groups' + '.json', 'wb') as fp:
		fp.write(anyjson.dumps(groups))

def group_to_tex():
	''''''
	with open('data/' + my.DATA_FOLDER + 'groups.json', 'rb') as fp:
		groups = anyjson.loads(fp.read())
	path = 'data/' + my.DATA_FOLDER + 'group_tex/'
	if not os.path.exists(path): os.makedirs(path)

	for i, items in groups.iteritems():
		temp = []
		for ph, f in items:
			temp.append('\\ \\ '.join([str(f), ph]))
		tex = ' \\\\'.join(temp)
		with open(path + i + '.tex', 'wb') as fp:
			fp.write(tex)


#
# TEXT - TIME OFFSETS
#
def find_timestamps():
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

	global sw
	sw = stopwords.words('english')
	sw.extend(my.STOPWORDS)
	sw = list(set(sw))

	global ts_start
	ts_start = datetime.strptime(my.TS_START, my.TS_FORMAT)
	td = timedelta(days=my.TS_WINDOW)
	ts_end = ts_start + td

	legend = {
		'legend' : {},
		'ts_start' : my.TS_START,
		'ts_end' : str(ts_end)
		}

	global tokens
	with open('data/' + my.DATA_FOLDER + 'tokens.json', 'rb') as fp:
		tokens = sorted(anyjson.loads(fp.read()))
	with open('data/' + my.DATA_FOLDER + \
						'frequent_sets' + '.pickle', 'rb') as fp:
		sets = pickle.load(fp)

	global phrases
	phrases = []
	offsets = {}
	i = 0
	for s, f in sets[:my.K]:
		i += 1
		txt = ' '.join(tokens[i] for i in list(s))
		phrases.append((i, set(s)))
		offsets[i] = []
		legend['legend'][i] = txt

	pool = Pool(processes=my.PROCESSES)
	matches = pool.map(_match_tweet, recs)
	recs = None

	c = 0
	for offset, match in matches:
		for i in match:
			offsets[i].append(offset)
			c += 1
	print '{c} total matches.'.format(c=c)

	with open('data/' + my.DATA_FOLDER + 'match_legend.json', 'wb') as fp:
		fp.write(anyjson.dumps(legend))
	with open('data/' + my.DATA_FOLDER + 'match_offsets.json', 'wb') as fp:
		fp.write(anyjson.dumps(offsets))

def _match_tweet(rec):
	'''Map function'''
	text = rec[1].lower()
	toks = nltk.word_tokenize(text)
	toks = [t for t in toks \
				if t not in sw \
				]
				#and t.isalpha()]
	toks = tuple(set(toks) & set(tokens))
	tw = set(tokens.index(i) for i in toks)

	match = []
	for i, ph in phrases:
		if len(tw & ph) == len(ph):
			match.append(i)

	ts = rec[0]
	diff = ts - ts_start
	diff = int(diff.total_seconds())
	
	return (diff, tuple(match))



#
# PLOT - PHRASE TIMELINE
#
def plot_phrases():
	''''''
	with open('data/' + my.DATA_FOLDER + 'match_legend.json', 'rb') as fp:
		legend = anyjson.loads(fp.read())
	with open('data/' + my.DATA_FOLDER + 'match_offsets.json', 'rb') as fp:
		offsets = anyjson.loads(fp.read())

	ts_start = datetime.strptime(legend['ts_start'], my.TS_FORMAT)
	ts_end = datetime.strptime(legend['ts_end'], my.TS_FORMAT)
	diff = ts_end - ts_start
	diff = int(diff.total_seconds())
	combine = 120
	
	x, x_ticks, x_tickslabels = _make_x(ts_start, diff, combine=combine)

	Y = []
	for pid, offset in offsets.iteritems():
		y = dict((i, 0) for i in x)
		for o in offset:
			idx = int(o/combine)
			if idx in y: y[idx] += 1
		y = y.values()
		Y.append(y)

	path = 'data/' + my.DATA_FOLDER  + 'plots/'
	filename = 'all_phrases'

	_plot(x, Y, x_ticks=x_ticks, x_tickslabels=x_tickslabels, 
		figsize=(15,5), alpha=0.5, 
		in_text='All Phrases', path=path, filename=filename, ext='png')

def _make_x(ts_start, diff, combine=120):
	points = diff / combine
	_12 = (12 * 60 * 60) / combine
	_24 = (24 * 60 * 60) / combine
	x = range(points+1)
	x_ticks = []
	x_tickslabels = []
	start = (ts_start.hour * 60 * 60) / combine
	for i in x:
		if (start + i) % _12 == 0:
			if (start + i) % _24 == 0:
				ts = ts_start + timedelta(seconds=i*combine)
				s = ts.strftime('%b %d')
			else:
				s = '12 N'
			x_ticks.append(i)
			x_tickslabels.append(s)
	
	return x, x_ticks, x_tickslabels

def _plot(x, Y, x_ticks=None, x_tickslabels=None, 
		figsize=(15,5), alpha=0.5, lw=1, y_labels=None,
		in_text=None, path=None, filename=None, ext='pdf'):
	fig = plt.figure(figsize=figsize)
	plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
	ax = fig.add_subplot(111) 
	ax.autoscale_view()
	ax.set_xlim(min(x), max(x))
	ax.set_xticks(x_ticks)
	ax.set_xticklabels(x_tickslabels)
	ax.text(0.95, 0.95, in_text, ha='right', va='top', 
			transform = ax.transAxes, family='monospace', fontsize=30)
	
	handles = []
	for y in Y:
		h, = ax.plot(x, y, '-', lw=lw, alpha=alpha, label='')
		handles.append(h)
	if y_labels:
		ax.legend(handles, y_labels)

	if not os.path.exists(path): os.makedirs(path)
	plt.savefig(path + filename + '.' + ext)


def plot_phrase_lengths():
	''''''
	with open('data/' + my.DATA_FOLDER + 'match_legend.json', 'rb') as fp:
		legend = anyjson.loads(fp.read())
	with open('data/' + my.DATA_FOLDER + 'match_offsets.json', 'rb') as fp:
		offsets = anyjson.loads(fp.read())

	groups = {}
	for pid, s in legend['legend'].iteritems():
		l = len(s.split())
		if l not in groups:
			groups[l] = []
		groups[l].append(pid)

	ts_start = datetime.strptime(legend['ts_start'], my.TS_FORMAT)
	ts_end = datetime.strptime(legend['ts_end'], my.TS_FORMAT)
	diff = ts_end - ts_start
	diff = int(diff.total_seconds())
	combine = 120

	x, x_ticks, x_tickslabels = _make_x(ts_start, diff, combine=combine)

	Y_all = []
	y_labels = []
	for i, pids in groups.iteritems():
		Y = []
		y_all = dict((i, 0) for i in x)
		for pid in pids:
			offset = offsets[pid]
			y = dict((i, 0) for i in x)
			for o in offset:
				idx = int(o/combine)
				if idx in y: y[idx] += 1
				if idx in y_all: y_all[idx] += 1
			y = y.values()
			Y.append(y)

		path = 'data/' + my.DATA_FOLDER  + 'plots/'
		filename = 'length_' + str(i)
		text = 'Phrase length ' + str(i)

		y_all = y_all.values()
		Y_all.append(y_all)
		y_labels.append(text)

		_plot(x, Y, x_ticks=x_ticks, x_tickslabels=x_tickslabels, 
			figsize=(15,5), alpha=0.5, 
			in_text=text, path=path, filename=filename, ext='png')

	_plot(x, Y_all, x_ticks=x_ticks, x_tickslabels=x_tickslabels, 
		figsize=(15,5), alpha=0.5, lw=2, y_labels=y_labels,
		path=path, filename='length_all', ext='png')






