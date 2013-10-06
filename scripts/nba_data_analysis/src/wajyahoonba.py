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
import matplotlib
import numpy as np
import matplotlib.pyplot as plt

from pylab import *
from twitter import *
from dateutil import tz
from pprint import pprint
from datetime import datetime, timedelta

import settings as my
sys.path.insert(0, os.path.abspath('..'))



#
#
#
def get_tweets():
	#
	# screen_name = WojYahooNBA
	#
	auth = OAuth(my.ACCESS_TOKEN, my.ACCESS_SECRET,
				my.CONSUMER_TOKEN, my.CONSUMER_SECRET,)
	twitter = Twitter(auth=auth)
	results = twitter.statuses.user_timeline(
							screen_name='WojYahooNBA',
							#user_id=423984095,
							since_id=my.SINCE_ID,
							max_id=my.MAX_ID,
							count=200,
							trim_user=1)

	print '{l} tweets received.'.format(l=len(results))
	with open('data/' + my.DATA_FOLDER + 'tweets.json', 'wb') as fp:
		fp.write(anyjson.dumps(results))

def show_ts():
	with open('data/' + my.DATA_FOLDER + 'tweets.json', 'rb') as fp:
		tweets = anyjson.loads(fp.read())

	for tw in tweets:
		ts = datetime.strptime(tw["created_at"], 
								"%a %b %d %H:%M:%S +0000 %Y")
		ts = ts.replace(tzinfo=tz.gettz("UTC"))
		ts_utc = ts
		ts = ts.astimezone(tz.gettz(my.TIMEZONE))
		#ts = ts.replace(tzinfo=None)
		print ts_utc, '\t', ts


def plot_time():
	with open('data/' + my.DATA_FOLDER + 'tweets.json', 'rb') as fp:
		tweets = anyjson.loads(fp.read())

	n_days = my.WOJ__N_DAYS
	fig = plt.figure(figsize=(15,4*n_days))
	fig.set_tight_layout(True)
	ts_start = datetime.strptime(my.WOJ__TS_START, my.TS_FORMAT)
	
	c = 0
	while n_days > 0:
		ts_str = ts_start.strftime('%b %d, %Y')
		print ts_str
		diff = int(timedelta(days=1).total_seconds())
		combine = 120
		x, x_ticks, x_tickslabels = _make_x(ts_start, diff, combine=combine)
		ret = [0] * (24 * 60 * 60 / combine + 1) 
		fav = [0] * (24 * 60 * 60 / combine + 1)
		
		for tw in tweets:
			ts = datetime.strptime(tw["created_at"], 
									"%a %b %d %H:%M:%S +0000 %Y")
			ts = ts.replace(tzinfo=tz.gettz("UTC"))
			ts = ts.astimezone(tz.gettz(my.TIMEZONE))
			ts = ts.replace(tzinfo=None)
			td = ts - ts_start
			sec = int(td.total_seconds()) / combine
			if sec in x:
				if 'retweet_count' in tw: ret[sec] = tw['retweet_count']
				if 'favorite_count' in tw: fav[sec] = tw['favorite_count']

		c += 1
		ax = fig.add_subplot(my.WOJ__N_DAYS, 1, c)
		ax.set_ylim(0, 8000)
		ax.set_xlim(min(x), max(x))
		ax.set_xticks(x_ticks)
		ax.set_xticklabels(x_tickslabels)
		ax.text(0.05, 0.95, ts_str, ha='left', va='top', 
				transform = ax.transAxes, family='monospace', fontsize=25)
		width = 1
		r = ax.bar(x, ret, width, color='#377EB8', ec='#377EB8')
		f = ax.bar(x, fav, width, bottom=ret, color='#FF7F00', ec='#FF7F00')

		ts_start = ts_start + timedelta(days=1)
		n_days -= 1

	fig.legend((r[0], f[0]), ('Retweets', 'Favorites') )
	ts_start = datetime.strptime(my.WOJ__TS_START, my.TS_FORMAT)
	file_name = ts_start.strftime('%b %d') + ' + ' + \
										str(my.WOJ__N_DAYS) + ' days'
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


