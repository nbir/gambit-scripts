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
import anyjson as json
from datetime import datetime
from pytz import timezone

import lib.PiP_Edge as pip

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
		loc = Location.objects.get(id=my.BOUND_LOC_ID)
		tweets = Tweet.filter(geo__within=loc.polygon)
	elif 'bbox' in my:
		bbox = Location.parse_bbox(my.BBOX)
		tweets = Tweet.filter(geo__within=bbox)
	elif 'polygon' in my:
		polygon = Location.parse_polygon(my.POLYGON)
		tweets = Tweet.filter(geo__within=polygon)

	if 'ts_start' in my:
		ts_start = datetime.strptime(my.TS_START, my.TS_FORMAT)
		ts_start = ts_start.replace(tzinfo=timezone(my.TIMEZONE))
		ts_start = ts_start.astimezone(timezone('UTC'))
		tweets = tweets.filter(timestamp__gte=ts_start)
	if 'ts_end' in my:
		ts_end = datetime.strptime(my.TS_END, my.TS_FORMAT)
		ts_end = ts_end.replace(tzinfo=timezone(my.TIMEZONE))
		ts_end = ts_end.astimezone(timezone('UTC'))
		tweets = tweets.filter(timestamp__lte=ts_end)

	# Count & trim
	hour_list = []
	if 't_start' in my and 't_end' in my:
		t_start = datetime.strptime(my.T_START, my.T_FORMAT)
		t_start = t_start.replace(tzinfo=timezone(my.TIMEZONE))
		t_start = t_start.astimezone(timezone('UTC'))
		h_start = t_start.hour
		t_end = datetime.strptime(my.T_END, my.T_FORMAT)
		t_end = t_end.replace(tzinfo=timezone(my.TIMEZONE))
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
	user_list = [[i, user_tweet_count[i]] for i in user_tweet_count if user_tweet_count[i] > my.MIN_TWEET]
	print '%s users who tweeted min_tweet times.' % len(user_list)

	# Write
	if not os.path.exists('data/' + my.DATA_FOLDER):
		os.makedirs('data/' + my.DATA_FOLDER)
	with open('data/' + my.DATA_FOLDER + my.FILE_MIN_TWEET_USERS, 'wb') as fp:
		csv_writer = csv.writer(fp, delimiter=',')
		for row in user_list:
			csv_writer.writerow(row)


def get_user_latlng(in_file, out_folder, time_bound=None, att_date=None, att_mins=None):
#	Get tweets inside location_id.
#	@param
#		in_file			csv file with first item as user_id
#		out_folder	output dir to store latlng csv files
#		time_bound	consider t_start & t_end bounds?
# 	att_date		include date field in format YYYY-MM-dd
# 	att_mins		include time in minutes of day

	# Django environment
	try:
		import sys
		sys.path.append("/home/gambit/collector/gambit2/")
		from django.core.management import setup_environ
		from gambit import settings
		setup_environ(settings)
	except:
		print 'Could not load django environment!'
		sys.exit(1)

	from scraper.models import Location, Tweet
	loc = Location.objects.get(id=my.LOCATION_ID)
	# Time bounds
	hour_list = []
	if time_bound:
		if 't_start' in my and 't_end' in my:
			t_start = datetime.strptime(my.T_START, my.T_FORMAT)
			t_start = t_start.replace(tzinfo=timezone(my.TIMEZONE))
			t_start = t_start.astimezone(timezone('UTC'))
			h_start = t_start.hour
			t_end = datetime.strptime(my.T_END, my.T_FORMAT)
			t_end = t_end.replace(tzinfo=timezone(my.TIMEZONE))
			t_end = t_end.astimezone(timezone('UTC'))
			h_end = t_end.hour
			if h_start < h_end:
				hour_list = range(h_start, h_end+1)
			else:
				hour_list = range(h_start, 24) + range(0, h_end+1)
			print 'Only tweets in hours %s' % (hour_list)
	else:
		hour_list = range(0,24)
	print 'Hour list ', hour_list

	# Create output folder
	if not os.path.exists('data/' + my.DATA_FOLDER + out_folder):
		os.makedirs('data/' + my.DATA_FOLDER + out_folder)

	# Start reading user_id list
	with open('data/' + my.DATA_FOLDER + in_file, 'rb') as fp1:
		csv_reader = csv.reader(fp1, delimiter=',')
		for row in csv_reader:
			user_id = int(row[0])

			# Filter tweets
			tweets = Tweet.filter(geo__within=loc.polygon)
			tweets = tweets.filter(user_id=user_id)

			if 'ts_start' in my:
				ts_start = datetime.strptime(my.TS_START, my.TS_FORMAT)
				ts_start = ts_start.replace(tzinfo=timezone(my.TIMEZONE))
				ts_start = ts_start.astimezone(timezone('UTC'))
				tweets = tweets.filter(timestamp__gte=ts_start)
			if 'ts_end' in my:
				ts_end = datetime.strptime(my.TS_END, my.TS_FORMAT)
				ts_end = ts_end.replace(tzinfo=timezone(my.TIMEZONE))
				ts_end = ts_end.astimezone(timezone('UTC'))
				tweets = tweets.filter(timestamp__lte=ts_end)

			# Trim and write
			fp_w = open('data/' + my.DATA_FOLDER + out_folder + str(user_id) + '.csv', 'wb')
			csv_writer = csv.writer(fp_w, delimiter=',')
			count=0
			count_store=0

			for tweet in tweets:
				if tweet.timestamp.hour in hour_list:
					out_row = []
					out_row.extend([tweet.geo[0], tweet.geo[1]])

					ts = tweet.timestamp.astimezone(timezone(my.TIMEZONE))
					if att_date:	# include datestring as well
						ds = '%s-%s-%s' % (ts.year, ts.month, ts.day)
						tstr = '%s-%s-%sT%s:%s:%s' % (ts.year, ts.month, ts.day, ts.hour, ts.minute, ts.second)
						out_row.extend([ds, tstr])
					if att_mins:	#	include minutes of day as well
						mins = ts.hour * 60 + ts.minute
						out_row.append(mins)
					csv_writer.writerow(out_row)
					count_store += 1
				count += 1

			# Close o/p file pointer, and delete file if no tweets
			fp_w.close()
			if count_store == 0:
				os.remove('data/' + my.DATA_FOLDER + out_folder + str(user_id) + '.csv')
			print 'user_id: %s\t%s of %s tweets were saved.' % (user_id, count_store, count)



def get_user_latlng_no_dj(in_file, out_folder, time_bound=None, att_date=None, att_mins=None):
#	Get tweets inside location_id. USES PY CONNECTION INSTEAD OF DJANGO
#	@param
#		in_file			csv file with first item as user_id
#		out_folder	output dir to store latlng csv files
#		time_bound	consider t_start & t_end bounds?
# 	att_date		include date field in format YYYY-MM-dd
# 	att_mins		include time in minutes of day

	# Connect
	try:
		import psycopg2
		CONN_STRING = "host='brain.isi.edu' dbname='twitter' user='twitter' password='flat2#tw1tter'"
		conn = psycopg2.connect(CONN_STRING)
		cursor = conn.cursor()
		print 'Connected to Postgres DB.'
	except:
		print 'Could not connect to Postgres DB!'
		sys.exit(1)

	# Create output directory
	if not os.path.exists('data/' + my.DATA_FOLDER + out_folder):
		os.makedirs('data/' + my.DATA_FOLDER + out_folder)

	# Start reading user_id list
	with open('data/' + my.DATA_FOLDER + in_file, 'rb') as fp1:
		csv_reader = csv.reader(fp1, delimiter=',')
		for row in csv_reader:
			user_id = int(row[0])
			# Create output file pointer
			fp_w = open('data/' + my.DATA_FOLDER + out_folder + str(user_id) + '.csv', 'wb')
			csv_writer = csv.writer(fp_w, delimiter=',')
			count=0
			count_store=0

			# TABLE: t2_tweet
			SQL_STM = "select user_id, timestamp, ST_X(geo) as lat, ST_Y(geo) as lng, text \
								from t2_tweet \
								where user_id=" + str(user_id)
			cursor.execute(SQL_STM)
			records = cursor.fetchall()

			for record in records:
				count += 1
				user_id, ts, lat, lng, text  = record
				if in_hbk(lat, lng):
					ts = ts.astimezone(timezone(my.TIMEZONE))
					ds = '%s-%s-%s' % (ts.year, ts.month, ts.day)
					tstr = '%s-%s-%sT%s:%s:%s' % (ts.year, ts.month, ts.day, ts.hour, ts.minute, ts.second)
					mins = ts.hour * 60 + ts.minute
					count_store += 1
					csv_writer.writerow([lat, lng, ds, tstr, mins, text])

			# TABLE: t2_tweet2
			SQL_STM = "select user_id, timestamp, ST_X(geo) as lat, ST_Y(geo) as lng, text \
								from t2_tweet2 \
								where user_id=" + str(user_id)
			cursor.execute(SQL_STM)
			records = cursor.fetchall()

			for record in records:
				count += 1
				user_id, ts, lat, lng, text  = record
				if in_hbk(lat, lng):
					ts = ts.astimezone(timezone(my.TIMEZONE))
					ds = '%s-%s-%s' % (ts.year, ts.month, ts.day)
					tstr = '%s-%s-%sT%s:%s:%s' % (ts.year, ts.month, ts.day, ts.hour, ts.minute, ts.second)
					mins = ts.hour * 60 + ts.minute
					count_store += 1
					csv_writer.writerow([lat, lng, ds, tstr, mins, text])

			# Close o/p file pointer, and delete file if no tweets
			fp_w.close()
			if count_store == 0:
				os.remove('data/' + my.DATA_FOLDER + out_folder + str(user_id) + '.csv')
			print 'user_id: %s\t%s of %s tweets were saved.' % (user_id, count_store, count)

def in_hbk(lat, lng):
# Check if <lat, lng> lies inside HBK bbox
	lat_max, lng_max, lat_min, lng_min = 34.113, -118.155, 34.0129, -118.23
	return True if lat <= lat_max and lat >= lat_min and lng <= lng_max and lng >= lng_min else False
