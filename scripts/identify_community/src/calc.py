# Gambit scripts
#
# Copyright (C) USC Information Sciences Institute
# Author: Nibir Bora <nbora@usc.edu>
# URL: <http://cbg.isi.edu/>
# For license information, see LICENSE

import os
import sys
sys.path.insert(0, os.path.abspath('..'))
import settings as my
import lib.geo as geo

import csv
import pickle
from pprint import pprint

from dateutil import parser
from datetime import *
from pytz import timezone


def calc_interactions():
	with open('data/' + my.DATA_FOLDER  + 'all_tweets.pickle', 'rb') as fp1:
		tweets = pickle.load(fp1)
	interactions = {}
	user_list = [user_id for user_id in tweets]

	while len(user_list) != 0:
		user_id = user_list.pop()
		interactions[user_id] = []

		for tweet in tweets[user_id]:
			for other_uid in user_list:
				for other_tw in tweets[other_uid]:
					if _is_interaction(tweet, other_tw):
						interactions[user_id].append([tweet, other_tw])
		print '%5s interactions for user_id %10s' % (len(interactions[user_id]), user_id)

	with open('data/' + my.DATA_FOLDER  + 'interactions.pickle', 'wb') as fp1:
		pickle.dump(interactions, fp1)

def _is_interaction(tw1, tw2):
	lat1, lng1, _, ts1, _ = tw1
	lat2, lng2, _, ts2, _ = tw2

	dist = geo.distance(geo.xyz(lat1, lng1), geo.xyz(lat2, lng2))
	tds = ts1 - ts2
	tds = abs(tds.total_seconds())

	if dist <= my.MAX_INTERACTION_DIST and tds <= my.MAX_INTERACTION_TIME:
		#print dist, tds
		return True
	else:
		return False

