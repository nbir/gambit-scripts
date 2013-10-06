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
import anyjson
import psycopg2
import matplotlib
import matplotlib.pyplot as plt

from pylab import *
from PIL import Image
from pprint import pprint
from matplotlib import cm
from datetime import datetime, timedelta
from mpl_toolkits.basemap import Basemap
from matplotlib.collections import LineCollection
from matplotlib.collections import PolyCollection

import settings as my
sys.path.insert(0, os.path.abspath('..'))


#
# TIMELINE
#
def get_timeline():
	''''''
	print '\n', my.TL__TS_START, my.TL__N_DAYS, '\n'
	ts_start = datetime.strptime(my.TL__TS_START, my.TS_FORMAT)
	n_days = my.TL__N_DAYS

	SQL = '''SELECT timestamp AT TIME ZONE '{tz}' 
			FROM {rel_tweet} 
			WHERE timestamp BETWEEN %s 
				AND timestamp %s + INTERVAL '1 days' 
			'''.format(rel_tweet=my.REL_TWEET, tz=my.TIMEZONE)

	data = []

	con = psycopg2.connect(my.DB_CONN_STRING)
	cur = con.cursor()
	while n_days > 0:
		ts_iso = ts_start.isoformat()
		data_this = {
			'ts_start' : ts_iso,
			'offsets' : []
			}

		cur.execute(SQL, (ts_iso, ts_iso))
		recs = cur.fetchall()
		print len(recs)
		for rec in recs:
			ts = rec[0]
			td = ts - ts_start
			data_this['offsets'].append(int(td.total_seconds()))
		data.append(data_this)

		ts_start = ts_start + timedelta(days=1)
		n_days -= 1
	con.close()

	with open('data/' + my.DATA_FOLDER + 'offsets.json', 'wb') as fp:
		fp.write(anyjson.dumps(data))

def plot_timeline():
	''''''
	with open('data/' + my.DATA_FOLDER + 'offsets.json', 'rb') as fp:
		data = anyjson.loads(fp.read())

	fig = plt.figure(figsize=(15,2.5*len(data)))
	fig.set_tight_layout(True)
	c = 0
	for item in data:
		ts_start = datetime.strptime(item['ts_start'], my.TS_ISO_FORMAT)
		ts_str = ts_start.strftime('%b %d, %Y')
		diff = int(timedelta(days=1).total_seconds())
		combine = 120
		x, x_ticks, x_tickslabels = _make_x(ts_start, diff, combine=combine)
		y = dict((i, 0) for i in x)
		for o in item['offsets']:
			idx = int(o/combine)
			if idx in y: y[idx] += 1
		y = y.values()

		c += 1
		ax = fig.add_subplot(my.TL__N_DAYS, 1, c)
		ax.set_ylim(0, 80000)
		ax.set_xlim(min(x), max(x))
		ax.set_xticks(x_ticks)
		ax.set_xticklabels(x_tickslabels)
		ax.text(0.05, 0.95, ts_str, ha='left', va='top', 
				transform = ax.transAxes, family='monospace', fontsize=25)
		ax.plot(x, y, c='red', ls='-', alpha=0.9)
		ax.fill_between(x, y, color='red', alpha=0.5)

	x1, x2, y1, y2 = plt.axis()
	plt.axis((x1, x2, 0, y2))

	ts_start = datetime.strptime(my.TL__TS_START, my.TS_FORMAT)
	file_name = ts_start.strftime('%b %d') + ' + ' + \
										str(my.TL__N_DAYS) + ' days'
	plt.savefig('data/' + my.DATA_FOLDER + file_name + '.' + 'png')

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


#
# FILLER
#
def get_filler_ids():
	SQL = '''SELECT DISTINCT user_id
		FROM {rel_tweet}
		WHERE timestamp BETWEEN '{ts_start}' AND '{ts_end}'

		UNION

		SELECT user_id
		FROM {rel_tweet}
		GROUP BY user_id
		HAVING COUNT(*) > {min_count};
	'''.format(rel_tweet=my.REL_TWEET, 
			ts_start=my.FILL_TS_START, ts_end=my.FILL_TS_END,
			min_count=my.FILL_MIN_COUNT)

	con = psycopg2.connect(my.DB_CONN_STRING)
	cur = con.cursor()
	cur.execute(SQL)
	recs = cur.fetchall()
	con.close()
	print '{n} user_ids retrieved.'.format(n=len(recs))
	user_ids = [rec[0] for rec in recs]

	with open('data/' + my.DATA_FOLDER + 'filler_ids.json', 'wb') as fp:
		fp.write(anyjson.dumps(user_ids))