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