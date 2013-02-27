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

	hbk_trimmed_tweets = []		# home clusters removed

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
