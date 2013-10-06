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
import cPickle as pickle

from pprint import pprint
from pymining import itemmining
from multiprocessing import Pool
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from datetime import datetime, timedelta

import settings as my
sys.path.insert(0, os.path.abspath('..'))


#
# PREP INPUT
#
def prep_input():
	''''''
	print '\n', my.TS_START, my.TS_WINDOW, '\n'
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
	global tokens
	with open('data/' + my.DATA_FOLDER + 'tokens.json', 'rb') as fp:
		tokens = sorted(anyjson.loads(fp.read()))
	legend = dict((tokens.index(tok), tok) for tok in tokens)

	pool = Pool(processes=my.PROCESSES)
	tweets = pool.map(_trim_tweet, recs)
	tweets = filter(None, tweets)
	print '{count} tokenized tweets prepared.'.format(count=len(tweets))

	path = 'data/' + my.DATA_FOLDER + 'vw/'
	if not os.path.exists(path): os.makedirs(path)
	open(path + 'lda_input' + '.dat', 'wb').close()
	with open(path + 'lda_input' + '.dat', 'ab') as fp:
		for tw in tweets:
			fp.write(tw)
	with open(path + 'lda_legend' + '.json', 'wb') as fp:
		fp.write(anyjson.dumps(legend))

def _trim_tweet(rec):
	'''Map function'''
	text = rec[0].lower()
	toks = nltk.word_tokenize(text)
	toks = [t for t in toks \
				if t not in sw \
				]
				#and t.isalpha()]
	toks = tuple(set(toks) & set(tokens))
	if toks:
		tw = tuple(i for i in toks)
		#tw = tuple(str(tokens.index(i)) for i in toks)
		#tw = tuple(str(tokens.index(i))+':1' for i in toks)
		s = ' '.join(tw) + '\n'
	else:
		s = None
	return s


def prep_input_from_lda():
	path = 'data/' + my.DATA_FOLDER + 'lda/'
	with open(path + 'lda_input' + '.dat', 'rb') as fp:
		docset = fp.readlines()
	with open(path + 'lda_legend' + '.json', 'rb') as fp:
		legend = anyjson.loads(fp.read())

	docset_ = []
	for doc in docset:
		doc = doc.split()
		doc = [w + ':1' for w in doc]
		doc = '| ' + ' '.join(doc) + '\n'
		docset_.append(doc)
	#docset = ['| ' + doc.strip() + '\n' for doc in docset]

	path = 'data/' + my.DATA_FOLDER + 'vw/'
	if not os.path.exists(path): os.makedirs(path)
	open(path + 'lda_input' + '.dat', 'wb').close()
	with open(path + 'lda_input' + '.dat', 'ab') as fp:
		for doc in docset_:
			fp.write(doc)
	with open(path + 'lda_legend' + '.json', 'wb') as fp:
		fp.write(anyjson.dumps(legend))


def run_lda():
	''''''
	path = 'data/' + my.DATA_FOLDER + 'vw/'
	CMD = 'vw {ip_file} --lda {n_topics} ' + \
		'--lda_alpha 0.1 --lda_rho 0.1 ' + \
		'--lda_D {n_docs} ' + \
		'--minibatch 1024 ' + \
		'--power_t 0.5 --initial_t 1 ' + \
		'-b {vocab_size} ' + \
		'-p {pred_file} ' + \
		'--readable_model {topic_file} '
	CMD = CMD.format(
			ip_file=path+'vw_input.dat',
			n_topics=10,
			n_docs=8738,
			vocab_size=13,
			pred_file=path+'predictions.dat',
			topic_file=path+'topics.dat')
	print CMD + '\n'
	os.system(CMD)


def text_vocab():
	''''''
	with open('data/' + my.DATA_FOLDER + 'tokens.json', 'rb') as fp:
		tokens = sorted(anyjson.loads(fp.read()))
	with open('data/' + my.DATA_FOLDER + 'vocab.txt', 'wb') as fp:
		fp.write('\n'.join(tokens))

