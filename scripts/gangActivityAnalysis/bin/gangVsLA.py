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
import anyjson
import lib.geo as geo
import lib.PiP_Edge as pip

def get_tweets_in(location_id=my.HBK_LOCATION_ID):
	# get all tweets in hollenbeck area
	import sys
	sys.path.append("/home/gambit/collector/gambit2/")
	from django.core.management import setup_environ
	from gambit import settings
	setup_environ(settings)

	from scraper.models import Location, Tweet

	print 'Querying database...'
	tweets = Tweet.objects.all()
	loc = Location.objects.get(id=location_id)
	tweets = tweets.filter(geo__within=loc.polygon)
	print 'Querying complete. Writing to file...'
	
	with open(my.DATA_FOLDER + '/' + my.HBK_TWEET_LOC_FILE, 'wb') as fp:
		csv_writer = csv.writer(fp, delimiter=',')

		for tweet in tweets:
			csv_writer.writerow([tweet.user_id, tweet.geo[0], tweet.geo[1]])

	print 'Done! Fetched ' + str(tweets.count()) + ' entries.'


def trim_home_clusters():
# trim all home clusters
	_, hbk_poly = loadLocPoly()
	hbk_all_tweets = loadAllTweets()
	hbk_user_home_loc = loadAllHomeLoc(hbk_poly)

	hbk_trimmed_tweets = []		# home clusters removed

	# tweet list with home clusters removed
	print 'Removing home clusters...'
	hbk_home_list = {}
	for user_home in hbk_user_home_loc:
		hbk_home_list[user_home[0]] = [user_home[1], user_home[2]]
	#hbk_home_list = [[user_home[1], user_home[2]] for user_home in hbk_user_home_loc]
	hbk_trimmed_tweets = removeNearPoints(hbk_all_tweets, hbk_home_list, 50)
	print str(len(hbk_trimmed_tweets)) + ' instances after home clusters removed.'

	# replace old tweet list with trimmed list
	print 'Replacing old set of tweets...'
	with open(my.DATA_FOLDER + '/' + my.HBK_TWEET_LOC_FILE, 'wb') as fp1:
		csv_writer = csv.writer(fp1, delimiter=',')
		for tweet in hbk_trimmed_tweets:
			csv_writer.writerow(tweet)
	print str(len(hbk_trimmed_tweets)) + ' total instances written.'


def calc_gang_vs_la_tweeting_pattern():
	counts = {}
	tty_counts = {}
	
	tty_polys, hbk_poly = loadLocPoly()
	hbk_all_tweets = loadAllTweets()
	hbk_user_home_loc = loadAllHomeLoc(hbk_poly)
	hbk_users_in_gang_t = loadUsersInGangTty()

	print 'Start counting...'
	# Count tweets
	for gang_id in my.HBK_GANG_AND_RIVAL_IDS:
		counts[gang_id] = {
			'gang' : {
				'total' : 0,
				'home' : 0,
				'rival' : {}
			},
			'la' : {
				'total' : 0,
				'home' : 0,
				'rival' : {}
			}
		}

		# Count tweets for all gang members
		this_gang_all_tweets = keepUserIds(hbk_all_tweets, hbk_users_in_gang_t[gang_id])
		counts[gang_id]['gang']['total'] = len(this_gang_all_tweets)

		this_gang_home_tweets = keepPolygon(this_gang_all_tweets, tty_polys[gang_id])
		counts[gang_id]['gang']['home'] = len(this_gang_home_tweets)

		for rival_id in my.HBK_GANG_AND_RIVAL_IDS[gang_id]:
			this_gang_rival_tweets = keepPolygon(this_gang_all_tweets, tty_polys[rival_id])
			counts[gang_id]['gang']['rival'][rival_id] = len(this_gang_rival_tweets)

		# Count tweets for all LA users
		counts[gang_id]['la']['total'] = len(hbk_all_tweets)

		if not gang_id in tty_counts:
			all_user_tweets_in_tty = keepPolygon(hbk_all_tweets, tty_polys[gang_id])
			tty_counts[gang_id] = len(all_user_tweets_in_tty)
		counts[gang_id]['la']['home'] = tty_counts[gang_id]

		for rival_id in my.HBK_GANG_AND_RIVAL_IDS[gang_id]:
			if not rival_id in tty_counts:
				all_user_tweets_in_tty = keepPolygon(hbk_all_tweets, tty_polys[rival_id])
				tty_counts[rival_id] = len(all_user_tweets_in_tty)
			counts[gang_id]['la']['rival'][rival_id] = tty_counts[rival_id]

	with open(my.DATA_FOLDER + '/' + my.OUTPUT_COUNT_FILE, 'wb') as fp2:
		fp2.write(anyjson.serialize(counts))
	print counts


# LOAD functions
def loadLocPoly():
	# Read location polygons for gang territories
	tty_polys = {}
	hbk_poly = []
	print 'Reading location data...'
	with open(my.DATA_FOLDER + '/' + my.LOCATION_DATA_FILE, 'rb') as fp1:
		location_data = anyjson.deserialize(fp1.read())
		for loc in location_data:
			if loc['id'] >= 23 and loc['id'] <= 54:
				tty_polys[loc['id']] = loc['polygon']
			elif loc['id'] == my.HBK_LOCATION_ID:
				hbk_poly = loc['polygon']
	return tty_polys, hbk_poly

def loadAllTweets():
	# read all tweets
	hbk_all_tweets = []
	print 'Loading all tweets...'
	with open(my.DATA_FOLDER + '/' + my.HBK_TWEET_LOC_FILE, 'rb') as fp1:
		csv_reader = csv.reader(fp1, delimiter=',')
		for row in csv_reader:
			if len(row) > 0:
				hbk_all_tweets.append([int(row[0]), float(row[1]), float(row[2])])
	print str(len(hbk_all_tweets)) + ' total instances loaded.'
	return hbk_all_tweets

def loadAllHomeLoc(hbk_poly):
	# read all home locations
	hbk_user_home_loc = []
	print 'Loading all user homes...'
	with open(my.DATA_FOLDER + '/' + my.HBK_USER_HOME_LOC_FILE, 'rb') as fp1:
		csv_reader = csv.reader(fp1, delimiter=',')
		for row in csv_reader:
			if len(row) > 0 and pip.point_in_poly(float(row[1]), float(row[2]), hbk_poly):
				hbk_user_home_loc.append([int(row[0]), float(row[1]), float(row[2])])
	print str(len(hbk_user_home_loc)) + ' users with homes inside bounds.'
	return hbk_user_home_loc

def loadUsersInGangTty():
	# read users with homes in each gang territory
	hbk_users_in_gang_t = {}
	print 'Loading user homes in each gang tty...'
	for gang_id in my.HBK_GANG_AND_RIVAL_IDS:
		hbk_users_in_gang_t[gang_id] = []
		with open(my.DATA_FOLDER + '/' + my.HBK_HOMES_IN_GANG_TTY_FOLDER + '/' + str(gang_id) + '.csv', 'rb') as fp1:
			csv_reader = csv.reader(fp1, delimiter=',')
			for row in csv_reader:
				if len(row) > 0:
					hbk_users_in_gang_t[gang_id].append(int(row[0]))
	return hbk_users_in_gang_t
#- LOAD functions


# TRIM fucnctions
def removeUserIds(tweets, user_ids):
	new_tweets = []
	for tweet in tweets:
		if not tweet[0] in user_ids:
			new_tweets.append(tweet)
	return new_tweets
def keepUserIds(tweets, user_ids):
	new_tweets = []
	for tweet in tweets:
		if tweet[0] in user_ids:
			new_tweets.append(tweet)
	return new_tweets

def removeNearPoints(tweets, points, radius):
	print points
	new_tweets = []
	for tweet in tweets:
		if (tweet[0] not in points) or geo.distance(geo.xyz(tweet[1], tweet[2]), geo.xyz(points[tweet[0]][0], points[tweet[0]][1])) > radius:
			new_tweets.append(tweet)
		#inside = False
		#for point in points:
			#if geo.distance(geo.xyz(tweet[1], tweet[2]), geo.xyz(point[0], point[1])) < radius:
				#inside = True
				#break
		#if not inside:
			#new_tweets.append(tweet)
	return new_tweets

def removePolygon(tweets, polygon):
	new_tweets = []
	for tweet in tweets:
		if not pip.point_in_poly(tweet[1], tweet[2], polygon):
			new_tweets.append(tweet)
	return new_tweets
def keepPolygon(tweets, polygon):
	new_tweets = []
	for tweet in tweets:
		if pip.point_in_poly(tweet[1], tweet[2], polygon):
			new_tweets.append(tweet)
	return new_tweets
#- TRIM functions



# OBSOLETE
def calc_tweet_freq_in_rival_home():
# 
# 
# 
	import sys
	sys.path.append("/home/gambit/collector/gambit2/")
	from django.core.management import setup_environ
	from gambit import settings
	setup_environ(settings)

	from scraper.models import Location, Tweet


	counts = {}

	tty_counts = {}
	tty_polys = {}

	# Read location polygons for gang territories
	with open(my.DATA_FOLDER + '/' + my.LOCATION_DATA_FILE, 'rb') as fp1:
		location_data = anyjson.deserialize(fp1.read())
		for loc in location_data:
			if loc['id'] >= 23 and loc['id'] <= 54:
				tty_polys[loc['id']] = loc['polygon']

	# Count tweets
	for gang_id in my.HBK_GANG_AND_RIVAL_IDS:
		gang_data = {}
		with open(my.DATA_FOLDER + '/' + my.GANG_DATA_FOLDER + '/' + str(gang_id) + '.json', 'rb') as fp1:
			gang_data = anyjson.deserialize(fp1.read())
		gang_center = calc_center(gang_data['location_polygon'])
		bounds = get_bounding_box(gang_center, my.BOUND_RADIUS_MILES)
		bbox = arr_to_str(bounds)

		counts[gang_id] = {
			'gang' : {
				'total' : 0,
				'home' : 0,
				'rival' : {}
			},
			'la' : {
				'total' : 0,
				'home' : 0,
				'rival' : {}
			}
		}

		# Count tweets for all gang members
		counts[gang_id]['gang']['total'] = 0
		counts[gang_id]['gang']['home'] = 0
		for rival_id in my.HBK_GANG_AND_RIVAL_IDS[gang_id]:
			counts[gang_id]['gang']['rival'][rival_id] = 0

		for user_id in gang_data['users']:
			counts[gang_id]['gang']['total'] += len(gang_data['users'][user_id]['points_inside']) + len(gang_data['users'][user_id]['points_outside'])	# Universe

			counts[gang_id]['gang']['home'] += len(gang_data['users'][user_id]['points_inside'])		# Home tty

			for latlng in gang_data['users'][user_id]['points_outside']:
				for rival_id in my.HBK_GANG_AND_RIVAL_IDS[gang_id]:
					if pip.point_in_poly(latlng[0], latlng[1], tty_polys[rival_id]):
						counts[gang_id]['gang']['rival'][rival_id] += 1									# Rival tty

		# Count tweets for all LA users
		print 'Django query... gang-id ' + str(gang_id) + '... universe.'
		tweets = Tweet.objects.all()
		loc = Location.parse_bbox(my.HBK_BIG_BOUNDS_string)
		tweets = tweets.filter(geo__within=loc)
		bbox = Location.parse_bbox(bbox)
		tweets = tweets.filter(geo__within=bbox)
		counts[gang_id]['la']['total'] = tweets.count()				# Universe

		if gang_id in tty_counts:
			counts[gang_id]['la']['home'] = tty_counts[gang_id]
		else:
			print 'Django query... gang-id ' + str(gang_id) + '... home tty.'
			tweets = Tweet.objects.all()
			loc = Location.parse_bbox(my.HBK_BIG_BOUNDS_string)
			tweets = tweets.filter(geo__within=loc)
			polygon = Location.parse_polygon(arr_to_str(tty_polys[gang_id]))
			tweets = tweets.filter(geo__within=polygon)
			tty_counts[gang_id] = tweets.count()								# Home tty
			counts[gang_id]['la']['home'] = tty_counts[gang_id]

		for rival_id in my.HBK_GANG_AND_RIVAL_IDS[gang_id]:
			if rival_id in tty_counts:
				counts[gang_id]['la']['rival'][rival_id] = tty_counts[rival_id]
			else:
				print 'Django query... rival-id ' + str(rival_id) + '... rival tty.'
				tweets = Tweet.objects.all()
				loc = Location.parse_bbox(my.HBK_BIG_BOUNDS_string)
				tweets = tweets.filter(geo__within=loc)
				polygon = Location.parse_polygon(arr_to_str(tty_polys[rival_id]))
				tweets = tweets.filter(geo__within=polygon)
				tty_counts[rival_id] = tweets.count()							# Rival tty
				counts[gang_id]['la']['rival'][rival_id] = tty_counts[rival_id]

	with open(my.DATA_FOLDER + '/' + my.OUTPUT_COUNT_FILE, 'wb') as fp2:
		fp2.write(anyjson.serialize(counts))
	print counts
# OBSOLETE -*-

def calc_center(loc_arr):
	center = [0.0,0.0]
	points = 0
	for latlng in loc_arr:
		center[0] += latlng[0]
		center[1] += latlng[1]
		points += 1

	center[0] /= points
	center[1] /= points
	return center

def get_bounding_box(center, miles):
	this_point = [center[0], center[1]]
	while geo.distance(geo.xyz(center[0], center[1]), geo.xyz(this_point[0], this_point[1])) <= (miles*my.CONST_MILE_TO_METER):
		this_point[0] += 0.0001	# lat
	lat_hi = this_point[0]
	this_point = [center[0], center[1]]
	while geo.distance(geo.xyz(center[0], center[1]), geo.xyz(this_point[0], this_point[1])) <= (miles*my.CONST_MILE_TO_METER):
		this_point[0] -= 0.0001	# lat
	lat_lo = this_point[0]
	if lat_lo > lat_hi:
		lat_hi, lat_lo = lat_lo, lat_hi

	this_point = [center[0], center[1]]		
	while geo.distance(geo.xyz(center[0], center[1]), geo.xyz(this_point[0], this_point[1])) <= (miles*my.CONST_MILE_TO_METER):
		this_point[1] += 0.0001	# lng
	lng_hi = this_point[1]
	this_point = [center[0], center[1]]		
	while geo.distance(geo.xyz(center[0], center[1]), geo.xyz(this_point[0], this_point[1])) <= (miles*my.CONST_MILE_TO_METER):
		this_point[1] -= 0.0001	# lng
	lng_lo = this_point[1]
	if lng_lo > lng_hi:
		lng_hi, lng_lo = lng_lo, lng_hi

	#return [[lat_lo, lng_lo], [lat_hi, lng_lo], [lat_hi, lng_hi], [lat_lo, lng_hi]]	#polygon
	return [[lat_lo, lng_lo], [lat_hi, lng_hi]]		#bbox

def arr_to_str(arr):
	arr_str = ''
	for sub in arr:
		for val in sub:
			arr_str += str(round(val, 5)) + ','
	return arr_str[:-1]


def generate_frac_csv():
	counts = {}
	fractions = {}

	with open(my.DATA_FOLDER + '/' + my.OUTPUT_COUNT_FILE, 'rb') as fp1:
		counts = anyjson.deserialize(fp1.read())
	
	for gang_id in counts:
		fractions[gang_id] = {
			'gang' : {
				'home' : 0,
				'rival' : {}
			},
			'la' : {
				'home' : 0,
				'rival' : {}
			}
		}

		fractions[gang_id]['gang']['home'] = round(float(counts[gang_id]['gang']['home']) / float(counts[gang_id]['gang']['total']), 4) if counts[gang_id]['gang']['total'] != 0 else 0
		for rival_id in counts[gang_id]['gang']['rival']:
			fractions[gang_id]['gang']['rival'][rival_id] = round(float(counts[gang_id]['gang']['rival'][rival_id]) / float(counts[gang_id]['gang']['total']), 4) if counts[gang_id]['gang']['total'] != 0 else 0

		fractions[gang_id]['la']['home'] = round(float(counts[gang_id]['la']['home']) / float(counts[gang_id]['la']['total']), 4)
		for rival_id in counts[gang_id]['la']['rival']:
			fractions[gang_id]['la']['rival'][rival_id] = round(float(counts[gang_id]['la']['rival'][rival_id]) / float(counts[gang_id]['la']['total']), 4)

	with open(my.DATA_FOLDER + '/' + my.OUTPUT_FRACTION_FILE, 'wb') as fp2:
		csv_writer = csv.writer(fp2, delimiter=',')
		csv_writer.writerow(['gang/rival_id', 'frac_gang', 'frac_LA', 'count_gang,count_LA', 'count_gang', 'count_LA'])
		for gang_id in fractions:
			csv_writer.writerow([gang_id, fractions[gang_id]['gang']['home'], \
				fractions[gang_id]['la']['home'], \
				str(counts[gang_id]['gang']['home']) + '/' + str(counts[gang_id]['gang']['total']) + '; ' + str(counts[gang_id]['la']['home']), \
				counts[gang_id]['gang']['home'], \
				counts[gang_id]['la']['home']])
			for rival_id in fractions[gang_id]['gang']['rival']:
				csv_writer.writerow([rival_id, fractions[gang_id]['gang']['rival'][rival_id], \
					fractions[gang_id]['la']['rival'][rival_id], \
					str(counts[gang_id]['gang']['rival'][rival_id]) + '/' + str(counts[gang_id]['gang']['total']) + '; ' + str(counts[gang_id]['la']['rival'][rival_id]), \
					counts[gang_id]['gang']['rival'][rival_id], \
					counts[gang_id]['la']['rival'][rival_id]])
			csv_writer.writerow(['-', '-', '-' ,'-', '-'])
