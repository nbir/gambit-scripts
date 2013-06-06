# Gambit scripts
#
# Copyright (C) USC Information Sciences Institute
# Author: Nibir Bora <nbora@usc.edu>
# URL: <http://cbg.isi.edu/>
# For license information, see LICENSE

import os
import sys
import csv
import time
import anyjson
import psycopg2
import matplotlib
import numpy as np
import lib.geo as geo
import matplotlib.pyplot as plt

from pylab import *
from datetime import *
from pytz import timezone, utc
from multiprocessing import Pool
from scipy.spatial import distance
from sklearn.cluster import DBSCAN
from pprint import pprint as pprint

import settings as my
sys.path.insert(0, os.path.abspath('..'))


'''Load list of all nhoods in region'''
_load_nhoodIDs = lambda: [int(nid) for nid in anyjson.loads(open('data/' + my.DATA_FOLDER + 'hood_ids.txt', 'rb').read())]

#
# DAISPLACEMENT FROM HOME
#
def find_daily_disp():
	'''Find daily max displacement for users
	Also generated displacement plots for each user'''	
	SQL = 'SELECT user_id \
		FROM {rel_home} \
		WHERE ST_Within (geo, ST_UNION( \
			ARRAY(SELECT pol FROM {rel_nhood} \
					WHERE id in %s)))'.format(rel_home=my.REL_HOME, rel_nhood=my.REL_NHOOD)
	
	con = psycopg2.connect(my.DB_CONN_STRING)
	cur = con.cursor()
	cur.execute(SQL, (tuple(_load_nhoodIDs()), ))
	records = cur.fetchall()
	con.close()
	user_ids = [int(rec[0]) for rec in records]
	print 'Read {0} user_ids'.format(len(user_ids))
	with open('data/' + my.DATA_FOLDER + 'user_list.json', 'wb') as fpw:
		fpw.write(anyjson.dumps(user_ids))

	#for user_id in user_ids:
	#	_find_daily_disp(user_id)

	pool = Pool(processes=my.PROCESSES)
	pool.map(_find_daily_disp, user_ids)

def _find_daily_disp(user_id):
	'''Find daily max displacements for user_id and generate scatter plot'''
	# Displacement csv
	SQL = 'SELECT ST_X(geo), ST_Y(geo) \
		FROM {rel_home} \
		WHERE user_id = %s '.format(rel_home=my.REL_HOME)

	con = psycopg2.connect(my.DB_CONN_STRING)
	cur = con.cursor()
	cur.execute(SQL, (user_id,))
	records = cur.fetchall()

	if len(records) > 0:
		home = records[0]
		user_disp = {}
		x, y = [], []
		with open('data/' + my.DATA_FOLDER + 'city_bound_pol.txt', 'rb') as fpr:
			bound_pol = fpr.read().strip()
		SQL = 'SELECT ST_X(geo), ST_Y(geo), (timestamp AT TIME ZONE \'{timezone}\')::date \
			FROM {rel_tweet} \
			WHERE user_id = %s \
			AND geo && ST_GeomFromGeoJSON(%s) '.format(rel_tweet=my.REL_TWEET, timezone=my.TIMEZONE) \
			+ my.QUERY_CONSTRAINT \
			+ 'ORDER BY timestamp'
		cur.execute(SQL, (user_id, bound_pol))
		records = cur.fetchall()
		con.close()

		for rec in records:
			lat, lng, ds = rec
			x.append(lng-home[1])
			y.append(lat-home[0])
			if ds not in user_disp:
				user_disp[ds] = 0
			try:
				dist = int(round(geo.distance(geo.xyz(home[0], home[1]), geo.xyz(lat, lng))))
			except:
				dist = 0
			if dist > user_disp[ds]:
				user_disp[ds] = dist

		if not os.path.exists('data/' + my.DATA_FOLDER + 'displacement/' + 'user_disp/'):
			os.makedirs('data/' + my.DATA_FOLDER + 'displacement/' + 'user_disp/')
		with open('data/' + my.DATA_FOLDER + 'displacement/' + 'user_disp/' + str(user_id) + '.csv', 'wb') as fpw:
			cw = csv.writer(fpw, delimiter=',')
			for ds in user_disp:
				cw.writerow([user_id, user_disp[ds], ds])

		# Displacement plot
		fig = plt.figure(figsize=(5,5))
		ax = fig.add_subplot(111)
		plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
		ax.set_autoscaley_on(False)
		ax.set_ylim([-0.5,0.5])
		ax.set_xlim([-0.5,0.5])
		ax.set_yticks([0.0])
		ax.set_xticks([0.0])
		ax.set_yticklabels([])
		ax.set_xticklabels([])
		ax.grid(True)
		ax.plot(x, y, 'b+')
		ax.plot([0], [0], 'r^')
		ax.text(-0.45, -0.45, str(user_id), fontsize=10)
		if not os.path.exists('data/' + my.DATA_FOLDER + 'displacement/' + 'plot_disp/'):
			os.makedirs('data/' + my.DATA_FOLDER + 'displacement/' + 'plot_disp/')
		plt.savefig('data/' + my.DATA_FOLDER + 'displacement/' + 'plot_disp/' + str(user_id) + '.png')

	else:
		con.close()
		print 'Missed 1 user_id!'

def join_daily_disp():
	'''Join max displacement for all users into one file'''
	doc_path = 'data/' + my.DATA_FOLDER + 'displacement/' + 'user_disp/'
	doc_names = os.listdir(doc_path)
	if '.DS_Store' in doc_names:
		doc_names.remove('.DS_Store')
	
	fpw = open('data/' + my.DATA_FOLDER + 'displacement/' + 'user_disp.csv', 'wb')
	cw = csv.writer(fpw, delimiter=',')
	for doc in doc_names:
		with open(doc_path + doc, 'rb') as fp1:
			cr = csv.reader(fp1, delimiter=',')
			for row in cr:
				user_id, dist, date = int(row[0]), int(row[1]), row[2]
				cw.writerow([user_id, dist, date])
	fpw.close()


def plot_super_disp_plot():
	'''Plot displacement from home for all users in region'''
	SQL = 'SELECT user_id \
		FROM {rel_home} \
		WHERE ST_Within (geo, ST_UNION( \
			ARRAY(SELECT pol FROM {rel_nhood} \
				WHERE id in %s)))'.format(rel_home=my.REL_HOME, rel_nhood=my.REL_NHOOD)

	con = psycopg2.connect(my.DB_CONN_STRING)
	cur = con.cursor()
	cur.execute(SQL, (tuple(_load_nhoodIDs()), ))
	records = cur.fetchall()
	con.close()
	user_ids = [int(rec[0]) for rec in records]
	print 'Read {0} user_ids'.format(len(user_ids))

	# Plot super displacement plot
	x, y = [], []
	con = psycopg2.connect(my.DB_CONN_STRING)
	cur = con.cursor()
	with open('data/' + my.DATA_FOLDER + 'city_bound_pol.txt', 'rb') as fpr:
		bound_pol = fpr.read().strip()

	for user_id in user_ids:
		SQL = 'SELECT ST_X(geo), ST_Y(geo) \
				FROM {rel_home} \
				WHERE user_id = %s '.format(rel_home=my.REL_HOME)
		cur.execute(SQL, (user_id,))
		records = cur.fetchall()

		if len(records) > 0:
			home = records[0]
			SQL = 'SELECT ST_X(geo), ST_Y(geo) \
				FROM {rel_tweet} \
				WHERE user_id = %s \
				AND geo && ST_GeomFromGeoJSON(%s) '.format(rel_tweet=my.REL_TWEET) \
				+ my.QUERY_CONSTRAINT

			cur.execute(SQL, (user_id, bound_pol))
			records = cur.fetchall()
			for rec in records:
				lat, lng = rec
				x.append(lng-home[1])
				y.append(lat-home[0])

		else:
			print 'Missed 1 user_id!'
	con.close()
	
	# Displacement plot
	fig = plt.figure(figsize=(5,5))
	ax = fig.add_subplot(111)
	plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
	ax.set_autoscaley_on(False)
	ax.set_ylim([-0.5,0.5])
	ax.set_xlim([-0.5,0.5])
	ax.set_yticks([0.0])
	ax.set_xticks([0.0])
	ax.set_yticklabels([])
	ax.set_xticklabels([])
	ax.grid(True)
	ax.plot(x, y, 'b,', alpha=0.75)
	ax.plot([0], [0], 'r^')
	ax.text(-0.45, -0.45, my.DATA_FOLDER.replace('/', '').upper(), fontsize=10)
	
	plt.savefig('data/' + my.DATA_FOLDER + 'displacement/' + 'plot_disp__super' + '.png')

