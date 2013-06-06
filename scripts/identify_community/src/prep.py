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

import csv
import pickle
import anyjson as json
from pprint import pprint

from dateutil import parser
from datetime import *
from pytz import timezone


def read_tweets_pickle():
	tweets = {}

	with open('data/' + my.DATA_FOLDER + 'in/' + 'user_list.csv', 'rb') as fp_in:
		cr_in = csv.reader(fp_in)
		for row in cr_in:
			user_id = int(row[0]);
			tweets[user_id] = []
			
			with open('data/' + my.DATA_FOLDER + 'in/' + 'user_all_data/' + str(user_id) + '.csv', 'rb') as fp_tw:
				cr_tw = csv.reader(fp_tw)
				for tw in cr_tw:
					lat, lng, _, ts, _, text = tw;
					lat, lng = float(lat), float(lng)
					ts = parser.parse(ts)
					ts.replace(tzinfo=timezone(my.TIMEZONE))
					tweets[user_id].append([lat, lng, user_id, ts, text])
	
	with open('data/' + my.DATA_FOLDER  + 'all_tweets.pickle', 'wb') as fp1:
		pickle.dump(tweets, fp1)
	#pprint(tweets)


def show_tweet_count():
	with open('data/' + my.DATA_FOLDER  + 'all_tweets.pickle', 'rb') as fp1:
		tweets = pickle.load(fp1)

	pprint(dict([(user_id, len(tweets[user_id])) for user_id in tweets]))




