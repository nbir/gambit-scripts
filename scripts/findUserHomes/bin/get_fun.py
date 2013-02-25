# Gambit scripts
#
# Copyright (C) USC Information Sciences Institute
# Author: Nibir Bora <nbora@usc.edu>
# URL: <http://cbg.isi.edu/>
# For license information, see LICENSE


import sys
import os
sys.path.insert(0, os.path.abspath('..'))
from settings import CURRENT_SETTINGS as my

import csv
import anyjson as json
from datetime import datetime
from pytz import timezone


def get_min_tweet_users():
#	Get list of users with min_tweet tweets

	import sys
	sys.path.append("/home/gambit/collector/gambit2/")
	from django.core.management import setup_environ
	from gambit import settings
	setup_environ(settings)

	from scraper.models import Location, Tweet
	tweets = Tweet.objects.all()

	# Filter tweets
	print 'Finding users with min_tweet tweets...'
	if 'bound_loc_id' in my:
		loc = Location.objects.get(id=my['bound_loc_id'])
		tweets = Tweet.filter(geo__within=loc.polygon)
	elif 'bbox' in my:
		bbox = Location.parse_bbox(my['bbox'])
		tweets = Tweet.filter(geo__within=bbox)
	elif 'polygon' in my:
		polygon = Location.parse_polygon(my['polygon'])
		tweets = Tweet.filter(geo__within=polygon)

	if 'ts_start' in my:
		ts_start = datetime.strptime(my['ts_start'], my['ts_format'])
		ts_start = ts_start.replace(tzinfo=timezone(my['timezone']))
		ts_start = ts_start.astimezone(timezone('UTC'))
		tweets = tweets.filter(timestamp__gte=ts_start)
	if 'ts_end' in my:
		ts_end = datetime.strptime(my['ts_end'], my['ts_format'])
		ts_end = ts_end.replace(tzinfo=timezone(my['timezone']))
		ts_end = ts_end.astimezone(timezone('UTC'))
		tweets = tweets.filter(timestamp__lte=ts_end)

	# Count & trim
	hour_list = []
	if 't_start' in my and 't_end' in my:
		t_start = datetime.strptime(my['t_start'], my['t_format'])
		t_start = t_start.replace(tzinfo=timezone(my['timezone']))
		t_start = t_start.astimezone(timezone('UTC'))
		h_start = t_start.hour
		t_end = datetime.strptime(my['t_end'], my['t_format'])
		t_end = t_end.replace(tzinfo=timezone(my['timezone']))
		t_end = t_end.astimezone(timezone('UTC'))
		h_end = t_end.hour
		if h_start < h_end:
			hour_list = range(h_start, h_end+1)
		else:
			hour_list = range(h_start, 24) + range(0, h_end+1)
		print 'Night time hours in %s' % (hour_list)

	user_tweet_count = {}
	for tweet in tweets:
		if tweet.timestamp.hour in hour_list:
			if tweet.user_id not in user_tweet_count:
				user_tweet_count[tweet.user_id] = 0
			user_tweet_count[tweet.user_id] += 1
	user_list = [[i, user_tweet_count[i]] for i in user_tweet_count if user_tweet_count[i] > my['min_tweet']]
	print '%s users who tweeted min_tweet times.' % len(user_list)

	# Write
	if not os.path.exists('data/' + my['sub_folder']):
		os.makedirs('data/' + my['sub_folder'])
	with open('data/' + my['sub_folder'] + my['files']['users_min_tweet'], 'wb') as fp:
		csv_writer = csv.writer(fp, delimiter=',')
		for row in user_list:
			csv_writer.writerow(row)


def get_user_latlng(in_file, out_folder, time_bound=None, att_date=None):
#	Get tweets inside location_id.
#	@param
#		in_file			csv file with first item as user_id
#		out_folder	output dir to store latlng csv files
#		time_bound	consider t_start & t_end bounds?

	# Django environment
	import sys
	sys.path.append("/home/gambit/collector/gambit2/")
	from django.core.management import setup_environ
	from gambit import settings
	setup_environ(settings)

	from scraper.models import Location, Tweet
	loc = Location.objects.get(id=my['location_id'])
	# Time bounds
	hour_list = []
	if time_bound:
		if 't_start' in my and 't_end' in my:
			t_start = datetime.strptime(my['t_start'], my['t_format'])
			t_start = t_start.replace(tzinfo=timezone(my['timezone']))
			t_start = t_start.astimezone(timezone('UTC'))
			h_start = t_start.hour
			t_end = datetime.strptime(my['t_end'], my['t_format'])
			t_end = t_end.replace(tzinfo=timezone(my['timezone']))
			t_end = t_end.astimezone(timezone('UTC'))
			h_end = t_end.hour
			if h_start < h_end:
				hour_list = range(h_start, h_end+1)
			else:
				hour_list = range(h_start, 24) + range(0, h_end+1)
			print 'Only tweets in hours %s' % (hour_list)
	else:
		hour_list = range(0,24)

	# Prep output file pointers
	if not os.path.exists('data/' + my['sub_folder'] + out_folder):
		os.makedirs('data/' + my['sub_folder'] + out_folder)

	with open('data/' + my['sub_folder'] + in_file, 'rb') as fp1:
		csv_reader = csv.reader(fp1, delimiter=',')
		for row in csv_reader:
			user_id = int(row[0])

			# Filter tweets
			tweets = Tweet.filter(geo__within=loc.polygon)
			tweets = tweets.filter(user_id=user_id)

			if 'ts_start' in my:
				ts_start = datetime.strptime(my['ts_start'], my['ts_format'])
				ts_start = ts_start.replace(tzinfo=timezone(my['timezone']))
				ts_start = ts_start.astimezone(timezone('UTC'))
				tweets = tweets.filter(timestamp__gte=ts_start)
			if 'ts_end' in my:
				ts_end = datetime.strptime(my['ts_end'], my['ts_format'])
				ts_end = ts_end.replace(tzinfo=timezone(my['timezone']))
				ts_end = ts_end.astimezone(timezone('UTC'))
				tweets = tweets.filter(timestamp__lte=ts_end)

			# Trim and write
			fp_w = open('data/' + my['sub_folder'] + out_folder + str(user_id) + '.csv', 'wb')
			csv_writer = csv.writer(fp_w, delimiter=',')
			count=0
			count_store=0
			if att_date:	# include datestring as well
				for tweet in tweets:
					if tweet.timestamp.hour in hour_list:
						ts = tweet.timestamp.astimezone(timezone(my['timezone']))
						ds = '%s-%s-%s' % (ts.year, ts.month, ts.day)
						csv_writer.writerow([tweet.geo[0], tweet.geo[1], ds])
						count_store += 1
					count += 1
			else:
				for tweet in tweets:
					if tweet.timestamp.hour in hour_list:
						csv_writer.writerow([tweet.geo[0], tweet.geo[1]])
						count_store += 1
					count += 1
			fp_w.close()
			if count_store == 0:
				os.remove('data/' + my['sub_folder'] + out_folder + str(user_id) + '.csv')
			print 'user_id: %s\t%s of %s tweets were saved.' % (user_id, count_store, count)