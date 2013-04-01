# Gambit scripts
#
# Copyright (C) USC Information Sciences Institute
# Author: Nibir Bora <nbora@usc.edu>
# URL: <http://cbg.isi.edu/>
# For license information, see LICENSE


import sys
import os
sys.path.insert(0, os.path.abspath('..'))
import settings as my

import csv


def get_tweets_in(location_id=my.HBK_LOCATION_ID):
# get all tweets in hollenbeck area
	import sys
	sys.path.append("/home/gambit/collector/gambit2/")
	from django.core.management import setup_environ
	from gambit import settings
	setup_environ(settings)

	from scraper.models import Location, Tweet

	print 'Querying database...'
	loc = Location.objects.get(id=location_id)
	tweets = Tweet.filter(geo__within=loc.polygon)
	
	if not os.path.exists('data/' + my.DATA_FOLDER):
		os.makedirs('data/' + my.DATA_FOLDER)
	with open('data/' + my.DATA_FOLDER + my.HBK_TWEET_LOC_FILE, 'wb') as fp:
		csv_writer = csv.writer(fp, delimiter=',')

		for tweet in tweets:
			csv_writer.writerow([tweet.user_id, tweet.geo[0], tweet.geo[1]])

	print 'Done! Fetched ' + str(tweets.count()) + ' entries.'



	########################################################################


def convert_jtc_data():
#Convert JTC data to our data format
	hbk_all_tweet_loc = []
	hbk_user_home_loc = []
	hbk_tweet_dist = []

	with open('data/' + my.DATA_FOLDER + 'jtc.csv', 'Ur') as fp:
		csv_reader = csv.reader(fp, delimiter=',')
		discard = csv_reader.next()
		user_id = 0

		for row in csv_reader:
			user_id += 1
			hbk_all_tweet_loc.append([user_id, row[6], row[7]])
			hbk_user_home_loc.append([user_id, row[3], row[4]])
			hbk_tweet_dist.append([user_id, int(float(row[13])*1000)])
			#print int(float(row[13])*1000)
			#print row[3], row[4], row[6], row[7]

	# write back
	with open('data/' + my.DATA_FOLDER + my.HBK_TWEET_LOC_FILE, 'wb') as fp1:
		csv_writer = csv.writer(fp1, delimiter=',')
		for tweet in hbk_all_tweet_loc:
			csv_writer.writerow(tweet)
	print str(len(hbk_all_tweet_loc)) + ' total instances written.'

	with open('data/' + my.DATA_FOLDER + my.HBK_USER_HOME_LOC_FILE, 'wb') as fp1:
		csv_writer = csv.writer(fp1, delimiter=',')
		for loc in hbk_user_home_loc:
			csv_writer.writerow(loc)
	print str(len(hbk_user_home_loc)) + ' total home locations written.'

	with open('data/' + my.DATA_FOLDER + my.HBK_TWEET_DIST_FILE, 'wb') as fp1:
		csv_writer = csv.writer(fp1, delimiter=',')
		for dist in hbk_tweet_dist:
			csv_writer.writerow(dist)
	print str(len(hbk_tweet_dist)) + ' total distance from home written.'
