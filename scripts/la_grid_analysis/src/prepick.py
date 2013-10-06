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
# 
#
def plot_top_players():
	''''''
	picks = {}
	with open('data/' + my.DATA_FOLDER + 'pick_teams.csv', 'rb') as fp:
		cr = csv.reader(fp, delimiter=',')
		cr.next()
		picks = tuple((int(r[0]), int(r[1])) for r in cr)
	global picks_legend
	with open('data/' + my.DATA_FOLDER + 'picks_legend.json', 'rb') as fp:
		picks_legend = dict((int(i[0]), i[1]) 
							for i in anyjson.loads(fp.read()).items())
	global teams_legend
	with open('data/' + my.DATA_FOLDER + 'teams_legend.json', 'rb') as fp:
		teams_legend = dict((int(i[0]), i[1]) 
							for i in anyjson.loads(fp.read()).items())

	for pick_id, team_id in picks[:]:
		_plot_top_players(pick_id, team_id)

def _plot_top_players(pick_id, team_id):
	''''''
	print pick_id, 'picked by', team_id

	with open('data/' + my.DATA_FOLDER + 'volume_mat/' 
				+ str(team_id) + '.json', 'rb') as fp:
		volume_mat = dict((int(i[0]), i[1]) 
							for i in anyjson.loads(fp.read()).items())
		# consider adding a _norm() to the timeline of each player

	with open('data/' + my.DATA_FOLDER + 'volume_mat_all/' 
				+ str(team_id) + '.json', 'rb') as fp:
		volume_mat_all = dict((int(i[0]), i[1]) 
							for i in anyjson.loads(fp.read()).items())

	# make changes here
	#
	window = 30
	mi = max_index(volume_mat_all[pick_id])
	mat = {}
	for pid in volume_mat:
		#volume_mat[pid][mi-2] = 0
		volume_mat[pid][mi-1] = 0
		volume_mat[pid][mi] = 0
		volume_mat[pid][mi+1] = 0
		volume_mat[pid][mi+2] = 0

		#
		#mat[pid] = volume_mat[pid][mi-window:mi]
		mat[pid] = volume_mat[pid][mi-window:mi+window]
		
	vols = [(pid, sum(mat[pid])) for pid in mat]
	vols = sorted(vols, key=lambda x: x[1], reverse=True)
	#print vols[:10]

	y_vol = [mat[pick_id]] \
			+ [mat[v[0]] for v in vols[:5] if v[0] != pick_id]
	y_prob = [[] for i in y_vol]
	for n in range(len(y_vol[0])):
		s = sum([y_vol[m][n] for m in range(len(y_vol))])
		for m in range(len(y_vol)):
			if s == 0: frac = 0
			else: frac = round(y_vol[m][n] / float(s), 2)
			y_prob[m].append(frac)
	y_labels = [picks_legend[pick_id]] \
			+ [picks_legend[v[0]] for v in vols[:5] if v[0] != pick_id]

	#
	#xticks = [0, len(y_vol[0])]
	#xticklabels = ['-1hr', 'Draft']
	xticks = [0, int(len(y_vol[0])/2), len(y_vol[0])]
	xticklabels = ['-1hr', 'Draft', '+1hr']
	
	fig = plt.figure(figsize=(15,3))
	fig.set_tight_layout(True)
	title = 'Pick ' + str(pick_id) + ' : ' + teams_legend[team_id] + ' - ' + picks_legend[pick_id]
	fig.suptitle(title, fontsize=15, weight='semibold')

	# PLOT VOLUME
	#
	ax = fig.add_subplot(121)
	ax.plot(_smooth_triangle(y_vol[0], 1) , '-', lw=3, color='k', alpha=0.75, label=y_labels[0])
	for y, l in zip(y_vol[1:], y_labels[1:]):
		ax.plot(_smooth_triangle(y, 1), '-', alpha=0.9, label=l)
	ax.set_xticks(xticks)
	ax.set_xticklabels(xticklabels)
	ax.xaxis.grid(True)
	ax.set_title('Volume')
	leg = ax.legend(fontsize=12, loc=2)
	for i in leg.legendHandles:
		i.set_linewidth(6)
	
	# PLOT PROB
	#
	ax = fig.add_subplot(122)
	ax.plot(_smooth_triangle(y_prob[0], 1), '-', lw=3, color='k', alpha=0.75)
	for y in y_prob[1:]:
		ax.plot(_smooth_triangle(y, 1), '-', alpha=0.9)
	ax.set_xticks(xticks)
	ax.set_xticklabels(xticklabels)
	ax.xaxis.grid(True)
	ax.set_title('Probability')

	path = 'data/' + my.DATA_FOLDER + 'plots/'
	if not os.path.exists(path): os.makedirs(path)
	plt.savefig(path + str(pick_id) + '.pdf')








def _smooth_triangle(data,degree,dropVals=False):
	"""performs moving triangle smoothing with a variable degree."""
	"""note that if dropVals is False, output length will be identical
	to input length, but with copies of data at the flanking regions"""
	'''http://www.swharden.com/blog/2010-06-20-smoothing-window-data-averaging-in-python-moving-triangle-tecnique/'''
	triangle=np.array(range(degree)+[degree]+range(degree)[::-1])+1
	smoothed=[]
	for i in range(degree,len(data)-degree*2):
		point=data[i:i+len(triangle)]*triangle
		smoothed.append(sum(point)/sum(triangle))
	if dropVals: return smoothed
	smoothed=[smoothed[0]]*(degree+degree/2)+smoothed
	while len(smoothed)<len(data):smoothed.append(smoothed[-1])
	return smoothed




#
#
#
max_index = lambda a: max(enumerate(a), key=lambda x: x[1])[0]

def _norm(x):
	mx = float(max(x))
	mn = float(min(x))
	diff = mx - mn
	if diff == 0:
		return x
	x_ = [(e-mn)/diff for e in x]
	return x_