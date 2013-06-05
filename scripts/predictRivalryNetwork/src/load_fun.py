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


# LOAD functions
def loadLocNames():
	# Read location names for gang territories
	tty_names = {}
	print 'Reading location data...'
	with open('data/' + my.DATA_FOLDER + my.LOCATION_DATA_FILE, 'rb') as fp1:
		location_data = anyjson.deserialize(fp1.read())
		for loc in location_data:
			if loc['id'] >= 23 and loc['id'] <= 54:
				tty_names[loc['id']] = loc['name'].replace('HBK_', '').replace('.kml', '') #.replace('_', ' ')
	return tty_names
def loadLocPoly():
	# Read location polygons for gang territories
	tty_polys = {}
	hbk_poly = []
	print 'Reading location data...'
	with open('data/' + my.DATA_FOLDER + my.LOCATION_DATA_FILE, 'rb') as fp1:
		location_data = anyjson.deserialize(fp1.read())
		for loc in location_data:
			if loc['id'] >= 23 and loc['id'] <= 54:
				tty_polys[loc['id']] = loc['polygon']
			elif loc['id'] == my.HBK_LOCATION_ID:
				hbk_poly = loc['polygon']
	return tty_polys, hbk_poly
def loadLocCenters():
	# Read location centroids for gang territories
	tty_centers = {}
	print 'Reading location data...'
	with open('data/' + my.DATA_FOLDER + my.LOCATION_DATA_FILE, 'rb') as fp1:
		location_data = anyjson.deserialize(fp1.read())
		for loc in location_data:
			if loc['id'] >= 23 and loc['id'] <= 54:
				tty_centers[loc['id']] = loc['centroid']
	return tty_centers


def loadAllTweets():
	# read all tweets
	hbk_all_tweets = []
	print 'Loading all tweets...'
	with open('data/' + my.DATA_FOLDER + my.HBK_TWEET_LOC_FILE, 'rb') as fp1:
		csv_reader = csv.reader(fp1, delimiter=',')
		for row in csv_reader:
			if len(row) > 0:
				hbk_all_tweets.append([int(row[0]), float(row[1]), float(row[2])])
	print '%s total instances loaded.' % (len(hbk_all_tweets))
	return hbk_all_tweets

def loadAllHomeLoc(hbk_poly):
	# read all home locations
	hbk_user_home_loc = []
	print 'Loading all user homes...'
	with open('data/' + my.DATA_FOLDER + my.HBK_USER_HOME_LOC_FILE, 'rb') as fp1:
		csv_reader = csv.reader(fp1, delimiter=',')
		for row in csv_reader:
			if len(row) > 0 and pip.point_in_poly(float(row[1]), float(row[2]), hbk_poly):
				hbk_user_home_loc.append([int(row[0]), float(row[1]), float(row[2])])
	print str(len(hbk_user_home_loc)) + ' users with homes inside bounds.'
	return hbk_user_home_loc

def loadUsersInGangTty(tty_polys, hbk_user_home_loc):
	# read users with homes in each gang territory
	hbk_users_in_gang_t = {}
	print 'Loading user homes in each gang tty...'
	for user_home in hbk_user_home_loc:
		for gang_id in tty_polys:
			if pip.point_in_poly(float(user_home[1]), float(user_home[2]), tty_polys[gang_id]):
				if gang_id not in hbk_users_in_gang_t:
					hbk_users_in_gang_t[gang_id] = []
				hbk_users_in_gang_t[gang_id].append(int(user_home[0]))
	g_list = dict([(gang_id, len(hbk_users_in_gang_t[gang_id])) for gang_id in hbk_users_in_gang_t])
	print 'Gang IDs with homes inside them: %s' % g_list
	print 'Total home: %s' % (sum(g_list.values()))
	return hbk_users_in_gang_t

