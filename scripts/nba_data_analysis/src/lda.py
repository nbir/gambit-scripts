# Gambit scripts
#
# Copyright (C) USC Information Sciences Institute
# Author: Nibir Bora <nbora@usc.edu>
# URL: <http://cbg.isi.edu/>
# For license information, see LICENSE

import os
import re
import sys
import csv
import math
import nltk
#import time
import numpy
import getopt
import random
import string
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
from pytagcloud.colors import COLOR_SCHEMES
from pytagcloud import create_tag_image, make_tags
from pytagcloud.lang.counter import get_tag_counts

import settings as my
from lib import onlineldavb
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

	path = 'data/' + my.DATA_FOLDER + 'lda/'
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


def run_lda():
	''''''
	K_ = range(my.TOPICS_START, my.TOPICS_END+1, my.TOPICS_STEP)
	#for K in K_:
	#	_run_lda(K)
	pool = Pool(processes=my.PROCESSES)
	#pool = Pool(processes=2)
	pool.map(_run_lda, K_)

def _run_lda(K=10):
	'''Map function'''
	path = 'data/' + my.DATA_FOLDER + 'lda/'
	with open(path + 'lda_legend.json', 'rb') as fp:
		legend = anyjson.loads(fp.read())
	#vocab = legend.keys()
	vocab = legend.values()
	W = len(vocab)

	with open(path + 'lda_input.dat', 'rb') as fp:
		docset = fp.readlines()
	D = len(docset)
	
	print '\nRunning OLDA. Vocab size: {v}, Docs: {c}, K: {k}, D: {d}.'\
		.format(v=W, c=len(docset), k=K, d=D)
	olda = onlineldavb.OnlineLDA(vocab, K, D, 1./K, 1./K, 1024., 0.7)

	i = 0
	while i <= len(docset):
		print 'K:', K, ', Batch:', i, i+my.BATCH_SIZE
		(gamma, bound) = olda.update_lambda(docset[i:i+my.BATCH_SIZE])
		i += my.BATCH_SIZE

	(wordids, wordcts) = onlineldavb.parse_doc_list(docset, olda._vocab)
	perwordbound = bound * len(docset) / (D * sum(map(sum, wordcts)))
	print 'K = %f, rho_t = %f,  held-out perplexity estimate = %f' % \
		(K, olda._rhot, numpy.exp(-perwordbound))

	path = path + 'models/' + str(K) + '/'
	if not os.path.exists(path): os.makedirs(path)
	numpy.savetxt(path + 'output_lambda.dat', olda._lambda)
	numpy.savetxt(path + 'output_gamma.dat', gamma)


def print_topics():
	''''''
	path = 'data/' + my.DATA_FOLDER + 'lda/'
	with open(path + 'lda_legend.json', 'rb') as fp:
		legend = anyjson.loads(fp.read())
	#vocab = legend.keys()
	vocab = legend.values()

	K_ = range(my.TOPICS_START, my.TOPICS_END+1, my.TOPICS_STEP)
	for K in K_:
		print '\n\nK =', K, '\n'
		path = 'data/' + my.DATA_FOLDER + 'lda/' + 'models/' + str(K) + '/'
		testlambda = numpy.loadtxt(path + 'output_lambda.dat')
		for k in range(0, len(testlambda)):
			lambdak = list(testlambda[k, :])
			lambdak = lambdak / sum(lambdak)
			temp = zip(lambdak, range(0, len(lambdak)))
			temp = sorted(temp, key = lambda x: x[0], reverse=True)
			#print 'topic %d:' % (k)
			#for i in range(0, 53):
			#	print '%20s  \t---\t  %.4f' % (vocab[temp[i][1]], temp[i][0])
			print 'topic %d:' % (k), '\t', [vocab[temp[i][1]] for i in range(10)]


def make_topics():
	K_ = range(my.TOPICS_START, my.TOPICS_END+1, my.TOPICS_STEP)
	for K in K_:
		_make_topic(K)
		

def _make_topic(K=10):
	''''''
	print '\n', K, '\n'
	path = 'data/' + my.DATA_FOLDER + 'lda/'
	with open(path + 'lda_legend.json', 'rb') as fp:
		legend = anyjson.loads(fp.read())
	#vocab = legend.keys()
	vocab = legend.values()
	testlambda = numpy.loadtxt(path + 'models/' + str(K) + '/' \
										+ 'output_lambda.dat')

	tex_path = path + 'tex/'
	if not os.path.exists(tex_path): os.makedirs(tex_path)
	pdfs_path = path + 'pdfs/'
	if not os.path.exists(pdfs_path): os.makedirs(pdfs_path)

	tex_gfx_path = path + 'tex/gfx/word_clouds/' + str(K) + '/'
	if not os.path.exists(tex_gfx_path): os.makedirs(tex_gfx_path)

	word_path = path + 'word_clouds/' + str(K) + '/'
	if not os.path.exists(word_path): os.makedirs(word_path)
	for k in range(0, len(testlambda)):
		lambdak = list(testlambda[k, :])
		lambdak = lambdak / sum(lambdak)
		temp = zip(lambdak, range(0, len(lambdak)))
		temp = sorted(temp, key = lambda x: x[0], reverse=True)
		words = [vocab[temp[i][1]] for i in range(10)]
		weights = [temp[i][0] for i in range(10)]
		fracs = [int(round(100 * w / sum(weights))) for w in weights]
		print 'topic %d:' % (k), '\t', words			
		text = [(words[i], fracs[i]) for i in range(len(words))]
		
		tags = make_tags(text, minsize=20, maxsize=50,
						colors=COLOR_SCHEMES['oldschool'])
		create_tag_image(tags, word_path + str(k) + '.png', 
							size=(500, 500),
							layout=3)
		create_tag_image(tags, tex_gfx_path + str(k) + '.png', 
							size=(500, 500),
							layout=3)

	_make_tex(filename=str(K) + '-topics',
			title='June 30, 6:00am +24 hrs', n_topics=K)


def _make_tex(filename, title, n_topics):
	head = """\documentclass[11pt,letterpaper]{report}

		\usepackage[landscape,margin=0.5in]{geometry}
		\usepackage{multicol}
		\usepackage{nopageno}
		\usepackage{graphicx}
		\usepackage{pifont}
		\usepackage{amsmath}

		\setlength{\parindent}{0cm}
		\setlength{\pdfpageheight}{60in}

		\\newcommand{\subfolder}{word_clouds/%s}

		\\begin{document}

		\\textbf{NBA Drafts 2013 \\texttt{%s}. %s topics}

		\\begin{centering}
		""" % (n_topics, title, n_topics)

	foot = """\end{centering}
		\end{document}
		"""

	body = []
	for i in range(n_topics):
		body.append("""\\frame{\includegraphics[width=3.33in]{gfx/\subfolder/%s}}""" % i)
	body = '\n'.join(body)

	tex = '\n'.join([head, body, foot])
	
	path = 'data/' + my.DATA_FOLDER + 'lda/tex/'
	with open(path + filename + '.tex', 'wb') as fp:
		fp.write(tex)
	os.system('cd ' + path + '; pdflatex ' + filename)
	pdf_path = 'data/' + my.DATA_FOLDER + 'lda/' + 'pdfs/'
	os.system('cp ' + path + filename + '.pdf' + ' ' + pdf_path)

					
	




