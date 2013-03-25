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

import bin.load_fun as load



def trim_home_clusters():
# trim all home clusters
	_, hbk_poly = load.loadLocPoly()
	hbk_all_tweets = load.loadAllTweets()
	hbk_user_home_loc = load.loadAllHomeLoc(hbk_poly)

	hbk_trimmed_tweets = []		# home clusters removed

	# tweet list with home clusters removed
	print 'Removing home clusters...'
	hbk_home_list = dict([(user_home[0], [user_home[1], user_home[2]]) for user_home in hbk_user_home_loc])
	hbk_trimmed_tweets = removeNearPoints(hbk_all_tweets, hbk_home_list, my.HOME_RADIUS)
	print str(len(hbk_trimmed_tweets)) + ' instances after home clusters removed.'

	# replace old tweet list with trimmed list
	print 'Replacing old set of tweets...'
	with open('data/' + my.DATA_FOLDER + my.HBK_TWEET_LOC_FILE, 'wb') as fp1:
		csv_writer = csv.writer(fp1, delimiter=',')
		for tweet in hbk_trimmed_tweets:
			csv_writer.writerow(tweet)
	print str(len(hbk_trimmed_tweets)) + ' total instances written.'


def trim_non_gang_users():
# trim all non gang users in data
	tty_polys, hbk_poly = load.loadLocPoly()
	hbk_all_tweets = load.loadAllTweets()
	hbk_user_home_loc = load.loadAllHomeLoc(hbk_poly)
	hbk_users_in_gang_t = load.loadUsersInGangTty(tty_polys, hbk_user_home_loc)

	hbk_trimmed_tweets = []

	# tweet list with home clusters removed
	print 'Removing non gang user tweets...'

	gang_user_list = []
	for gang_id in hbk_users_in_gang_t:
		gang_user_list += hbk_users_in_gang_t[gang_id]
		
	hbk_trimmed_tweets = keepUserIds(hbk_all_tweets, gang_user_list)
	print str(len(hbk_trimmed_tweets)) + ' instances after non gang users removed.'

	# replace old tweet list with trimmed list
	print 'Replacing old set of tweets...'
	with open('data/' + my.DATA_FOLDER + my.HBK_TWEET_LOC_FILE, 'wb') as fp1:
		csv_writer = csv.writer(fp1, delimiter=',')
		for tweet in hbk_trimmed_tweets:
			csv_writer.writerow(tweet)
	print str(len(hbk_trimmed_tweets)) + ' total instances written.'


def trim_low_tweet_gangs():
# Trim gang tweets with low non-home tweet counts
	tty_polys, hbk_poly = load.loadLocPoly()
	hbk_all_tweets = load.loadAllTweets()
	hbk_user_home_loc = load.loadAllHomeLoc(hbk_poly)
	hbk_users_in_gang_t = load.loadUsersInGangTty(tty_polys, hbk_user_home_loc)

	print 'Trimming tweets by low tweeting gangs...'
	# read each gang's tweet count
	hbk_tweets_by_gang = {}
	for gang_id in hbk_users_in_gang_t:
		this_gang_tweets = keepUserIds(hbk_all_tweets, hbk_users_in_gang_t[gang_id])
		hbk_tweets_by_gang[gang_id] = 0
		for foreign_id in my.HBK_GANG_ID_LIST:
			if gang_id != foreign_id:
				hbk_tweets_by_gang[gang_id] += len(keepPolygon(this_gang_tweets, tty_polys[foreign_id]))
	print 'Each gang\'s tweet count: %s' % hbk_tweets_by_gang

	print 'Removing users from gangs: %s' % [gang_id for gang_id in hbk_tweets_by_gang if hbk_tweets_by_gang[gang_id] < my.MIN_NON_HOME_TWEETS]
	remove_user_list = []
	for gang_id in hbk_tweets_by_gang:
		if hbk_tweets_by_gang[gang_id] < my.MIN_NON_HOME_TWEETS:
			remove_user_list += hbk_users_in_gang_t[gang_id]
	hbk_trimmed_tweets = removeUserIds(hbk_all_tweets, remove_user_list)

	# replace old tweet list with trimmed list
	print 'Replacing old set of tweets...'
	with open('data/' + my.DATA_FOLDER + my.HBK_TWEET_LOC_FILE, 'wb') as fp1:
		csv_writer = csv.writer(fp1, delimiter=',')
		for tweet in hbk_trimmed_tweets:
			csv_writer.writerow(tweet)
	print str(len(hbk_trimmed_tweets)) + ' total instances written.'


def trim_low_user_gangs():
# Trim gang tweets for gangs with low members
	tty_polys, hbk_poly = load.loadLocPoly()
	hbk_all_tweets = load.loadAllTweets()
	hbk_user_home_loc = load.loadAllHomeLoc(hbk_poly)
	hbk_users_in_gang_t = load.loadUsersInGangTty(tty_polys, hbk_user_home_loc)
	g_list = dict([(gang_id, len(hbk_users_in_gang_t[gang_id])) for gang_id in hbk_users_in_gang_t])

	print 'Trimming tweets by low user gangs...'
	
	print 'Removing users from gangs: %s' % [gang_id for gang_id in g_list if g_list[gang_id] < my.MIN_GANG_USERS]
	remove_user_list = []
	for gang_id in g_list:
		if g_list[gang_id] < my.MIN_GANG_USERS:
			remove_user_list += hbk_users_in_gang_t[gang_id]
	hbk_trimmed_tweets = removeUserIds(hbk_all_tweets, remove_user_list)

	# replace old tweet list with trimmed list
	print 'Replacing old set of tweets...'
	with open('data/' + my.DATA_FOLDER + my.HBK_TWEET_LOC_FILE, 'wb') as fp1:
		csv_writer = csv.writer(fp1, delimiter=',')
		for tweet in hbk_trimmed_tweets:
			csv_writer.writerow(tweet)
	print str(len(hbk_trimmed_tweets)) + ' total instances written.'


def trim_near_lines():
# Trim tweets near border lines
	with open('data/' + my.DATA_FOLDER  + 'json/' + 'border_lines.json', 'rb') as fp1:
		border_lines = anyjson.loads(fp1.read())
	hbk_all_tweets = load.loadAllTweets()
	hbk_trimmed_tweets = []
	border_points = []

	for tweet in hbk_all_tweets:
		is_near = False
		for line in border_lines:
			if isNear([tweet[1], tweet[2]], line):
				is_near = True
				break

		if is_near:
			border_points.append([tweet[1], tweet[2]])
		else:
			hbk_trimmed_tweets.append(tweet)

	print 'After trimming: %s. %s removed.' % (len(hbk_trimmed_tweets), len(border_points))
	
	# replace old tweet list with trimmed list
	print 'Replacing old set of tweets...'
	with open('data/' + my.DATA_FOLDER + my.HBK_TWEET_LOC_FILE, 'wb') as fp1:
		csv_writer = csv.writer(fp1, delimiter=',')
		for tweet in hbk_trimmed_tweets:
			csv_writer.writerow(tweet)
	print str(len(hbk_trimmed_tweets)) + ' total instances written.'

	# write border tweets
	with open('data/' + my.DATA_FOLDER  + 'json/' + 'border_points.json', 'wb') as fp1:
		fp1.write(anyjson.dumps(border_points))
		
def isNear(point, line):
	[[x1,y1], [x2,y2]] = line
	[px, py] = point

	if ((py<=y1 and py>=y2) or (py>=y1 and py<=y2))	and \
		(px<=x1 and px>=x2) or (px>=x1 and px<=x2):
		# If inside the box - calc perpendicular distance
		if x1 == x2:	# vertical line
			#return False
			x = x1
			if (py<=y1 and py>=y2) or (py>=y1 and py<=y2):
				y = py
			else:
				y = y1 if abs(py-y1) < abs(py-y2) else y2

		elif y1 == y2:	# horizontal line
			#return False
			y = y1
			if (px<=x1 and px>=x2) or (px>=x1 and px<=x2):
				x = px
			else:
				x = x1 if abs(px-x1) < abs(px-x2) else x2

		else:		# usual line
			m = (y2-y1)/(x2-x1)
			c = (y1 - m*x1)
			x = (m*py + px -m*c) / (m*m + 1)
			y = (m*m*py + m*px + c) / (m*m + 1)
			# Initial
			#m = (y2-y1)/(x2-x1)
			#x = (px + m * (m*x1 - y1 + py)) / (1 + m*m)
			#y = py - (x - px)/m

		try:
			if geo.distance(geo.xyz(px, py), geo.xyz(x, y)) < my.BORDER_LINE_SPAN:
				return True
			else:
				return False
		except Exception:
			print 'Couldn\'t calculate geo.distance'
		return False

	else:
		# If outside box - calc dist from end points of line
		if geo.distance(geo.xyz(px, py), geo.xyz(x1, y1)) < my.BORDER_LINE_SPAN or geo.distance(geo.xyz(px, py), geo.xyz(x2, y2)) < my.BORDER_LINE_SPAN :
			return True
		else:
			return False


def trim_inside_pols():
# Trim public/social location	polygons
	with open('data/' + my.DATA_FOLDER  + 'json/' + 'public_pols.json', 'rb') as fp1:
		public_pols = anyjson.loads(fp1.read())
	hbk_all_tweets = load.loadAllTweets()

	for pol in public_pols:
		hbk_all_tweets = removePolygon(hbk_all_tweets, pol)
	
	# replace old tweet list with trimmed list
	print 'Replacing old set of tweets...'
	with open('data/' + my.DATA_FOLDER + my.HBK_TWEET_LOC_FILE, 'wb') as fp1:
		csv_writer = csv.writer(fp1, delimiter=',')
		for tweet in hbk_all_tweets:
			csv_writer.writerow(tweet)
	print str(len(hbk_all_tweets)) + ' total instances written.'




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
	#print points
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
