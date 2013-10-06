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
import shutil
import anyjson
import psycopg2
import itertools
import cPickle as pickle
import multiprocessing as mp
import matplotlib.pyplot as plt

from pprint import pprint
from pymining import itemmining
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from datetime import datetime, timedelta

import settings as my
sys.path.insert(0, os.path.abspath('..'))


#
# GET DATA
#
def get_data():
	'''
	Matches sets from sets.json
	File names are according to legend.json
	Stopwords = nltk + stopwords.txt - vocab.txt
	'''
	print '\n', my.TS_START, my.TS_WINDOW, '\n'
	SQL = '''SELECT timestamp AT TIME ZONE '{tz}', text, user_id\
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

	global sets
	sets = {} 
	with open('data/' + my.DATA_FOLDER + 'sets.json', 'rb') as fp:
		sets = anyjson.loads(fp.read())
	sets = dict((st[0], tuple(set(s) for s in st[1])) for st in sets.items())
	#pprint(sets)

	global sw
	sw = stopwords.words('english')
	with open('data/' + my.DATA_FOLDER + 'stopwords.txt', 'rb') as fp:
		sw.extend(fp.read().split())
	sw.extend(my.STOPWORDS)
	sw = [w for w in sw if len(w) > 2]
	sw = list(set(sw))
	with open('data/' + my.DATA_FOLDER + 'vocab.txt', 'rb') as fp:
		vocab = fp.read().split()
	sw = tuple(set(sw) - set(vocab))
	print 'Stopword list length', len(sw)

	global ts_start
	ts_start = datetime.strptime(my.TS_START, my.TS_FORMAT)
	td = timedelta(days=my.TS_WINDOW)
	ts_end = ts_start + td
	time = {
		'ts_start' : my.TS_START,
		'ts_end' : str(ts_end)
		}
	with open('data/' + my.DATA_FOLDER + 'time.json', 'wb') as fp:
		fp.write(anyjson.dumps(time))

	# optional
	global influential_user_ids
	with open('data/' + my.DATA_FOLDER + 'influential_user_ids.json', 'rb') as fp:
		influential_user_ids = anyjson.loads(fp.read())

	#for rec in recs:
	#	_match_tweet(rec)
	manager = mp.Manager()
	global q
	q = manager.Queue()
	pool = mp.Pool(processes=my.PROCESSES)
	watcher = pool.apply_async(_tweet_writer, (q,))
	pool.map(_match_tweet, recs)
	q.put([-1, 0, ''])
	pool.close()

def _tweet_writer(q):
	'''Async. writer'''
	files = {}
	writer = {}
	with open('data/' + my.DATA_FOLDER + 'legend.json', 'rb') as fp:
		legend = anyjson.loads(fp.read())
	path = 'data/' + my.DATA_FOLDER + 'data/'
	if not os.path.exists(path): os.makedirs(path)
	for id in legend:
		open(path + str(id) + '.txt', 'wb')
		files[id] = open(path + str(id) + '.txt', 'wb')
		writer[id] = csv.writer(files[id], delimiter=',')

	while 1:
		id, diff, text = q.get()
		if id == -1: break
		writer[id].writerow([diff, text])

def _match_tweet(rec):
	'''Map function'''
	# optional
	user_id = int(rec[2])
	if user_id not in influential_user_ids: return

	text = rec[1].lower().replace('\'', '')
	toks = nltk.word_tokenize(text)
	toks = [\
				t for t in toks \
					if len(t) > 2 \
					and (t.replace('_','a').replace('-','b').isalnum() \
						and not t.isdigit()) \
					and t not in sw \
			]
	
	t = set(toks)
	for id, st in sets.iteritems():
		match = False
		for s in st:
			if len(s & t) >= len(s):
				match = True
				break
		if match:
			text = ' '.join(toks)
			ts = rec[0]
			diff = ts - ts_start
			diff = int(diff.total_seconds())
			q.put([id, diff, text])
			#writer[id].writerow([diff, text])
			#files[id].write(str(diff) + ',' + ' '.join(toks) + '\n')


def get_all_data():
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

	sw = stopwords.words('english')
	with open('data/' + my.DATA_FOLDER + 'stopwords.txt', 'rb') as fp:
		sw.extend(fp.read().split())
	sw.extend(my.STOPWORDS)
	sw = [w for w in sw if len(w) > 2]
	sw = list(set(sw))
	with open('data/' + my.DATA_FOLDER + 'vocab.txt', 'rb') as fp:
		vocab = fp.read().split()
	sw = tuple(set(sw) - set(vocab))
	print 'Stopword list length', len(sw)

	ts_start = datetime.strptime(my.TS_START, my.TS_FORMAT)
	td = timedelta(days=my.TS_WINDOW)
	ts_end = ts_start + td
	time = {
		'ts_start' : my.TS_START,
		'ts_end' : str(ts_end)
		}
	with open('data/' + my.DATA_FOLDER + 'time.json', 'wb') as fp:
		fp.write(anyjson.dumps(time))

	path = 'data/' + my.DATA_FOLDER + 'data/'
	if not os.path.exists(path): os.makedirs(path)
	fp = open(path + 'all.txt', 'wb')
	cr = csv.writer(fp, delimiter=',')

	for rec in recs:
		text = rec[1].lower().replace('\'', '')
		toks = nltk.word_tokenize(text)
		toks = [\
					t for t in toks \
						if len(t) > 2 \
						and (t.replace('_','a').replace('-','b').isalnum() \
							and not t.isdigit()) \
						and t not in sw \
				]
		if len(toks) > 0:
			text = ' '.join(toks)
			ts = rec[0]
			diff = ts - ts_start
			diff = int(diff.total_seconds())
			cr.writerow([diff, text])

	fp.close()


#
# INFLUENTIAL
#
def plot_influential():
	''''''
	follow = []
	friend = []
	users = []
	with open('data/' + my.DATA_FOLDER + 'user_ids_done.csv', 'rb') as fp:
		cr = csv.reader(fp, delimiter=',')
		for row in cr:
			follow.append(int(row[1]))
			friend.append(int(row[2]))
			users.append((int(row[0]), int(row[1])))
	
	influential = tuple(i[0] for i in users if i[1]>5000)
	print len(influential), 'influential users.'
	with open('data/' + my.DATA_FOLDER + 'influential_user_ids.json', 'wb') as fp:
		fp.write(anyjson.dumps(influential))

	fig = plt.figure(figsize=(12,8))
	fig.set_tight_layout(True)
	ax = fig.add_subplot(221)
	ax.hist(follow, bins=100)
	ax.set_ylim(0, 50)
	ax.set_title('Followers')

	fig.set_tight_layout(True)
	ax = fig.add_subplot(222)
	ax.hist(follow, bins=100, range=(100, 100000))
	ax.set_ylim(0, 1000)
	ax.set_title('Followers')

	fig.set_tight_layout(True)
	ax = fig.add_subplot(223)
	ax.hist(friend, bins=100)
	ax.set_title('Friends')

	fig.set_tight_layout(True)
	ax = fig.add_subplot(224)
	ax.hist(friend, bins=100, range=(100, 100000))
	ax.set_ylim(0, 1000)
	ax.set_title('Friends')

	plt.savefig('data/' + my.DATA_FOLDER + 'influential-hist' + '.pdf')


#
#
#
def make_pick_data():
	''''''
	with open('data/' + my.DATA_FOLDER + 'player_legend.json', 'rb') as fp:
		player_legend = anyjson.loads(fp.read()).items()
	with open('data/' + my.DATA_FOLDER + 'picks_legend.json', 'rb') as fp:
		picks_legend = anyjson.loads(fp.read()).items()

	from_path = 'data/' + my.DATA_FOLDER + 'player_data/'
	to_path = 'data/' + my.DATA_FOLDER + 'data/'

	for id, name in picks_legend:
		pid = 0
		screen_name = None
		for id2, n2 in player_legend:
			if _match_names(name, n2):
				player_legend.remove((id2, n2))
				screen_name = n2
				pid = id2
		print name, '\t', screen_name, pid
		shutil.copy(from_path + str(pid) + '.txt', 
					to_path + str(id) + '.txt')

def _match_names(n1, n2):
	n1 = n1.lower().split()
	n2 = n2.lower().split()
	avg_len = min(len(n1), len(n2))
	thres = avg_len / 2.0
	intersect = set(n1) & set(n2)
	if len(intersect) > thres:
		return True
	else: return False
