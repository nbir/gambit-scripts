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


def calc_matrics():
	tty_polys, hbk_poly = loadLocPoly()
	hbk_all_tweets = loadAllTweets()
	hbk_user_home_loc = loadAllHomeLoc(hbk_poly)
	hbk_users_in_gang_t = loadUsersInGangTty(tty_polys, hbk_user_home_loc)
	visit_mat = calcVisitationMat(hbk_all_tweets, tty_polys, hbk_users_in_gang_t)
	for gang_id in visit_mat:
		for to_id in visit_mat[gang_id]:
			if visit_mat[gang_id][to_id] != 0:
				print str(gang_id) + ' => ' + str(to_id) + ' : ' + str(visit_mat[gang_id][to_id])
	norm = calcNorm(visit_mat)
	for gang_id in norm:
		print str(gang_id) + ' : ' + str(norm[gang_id])

	measure1 = {}
	measure2 = {}
	for gang_id in my.HBK_GANG_AND_RIVAL_IDS:
		measure1[gang_id] = {
			'rival' : [],
			'nonrival' : []
			}
		measure2[gang_id] = {
			'rival' : [],
			'nonrival' : []
			}

		for rival_id in my.HBK_GANG_AND_RIVAL_IDS[gang_id]:
			if gang_id != rival_id and visit_mat[gang_id][rival_id] != 0:
				measure1[gang_id]['rival'].append(visit_mat[gang_id][rival_id])
				measure2[gang_id]['rival'].append(round(visit_mat[gang_id][rival_id]/norm[rival_id], 2))

		for non_rival_id in my.HBK_GANG_ID_LIST:
			if gang_id != non_rival_id and non_rival_id not in my.HBK_GANG_AND_RIVAL_IDS[gang_id]:
				if visit_mat[gang_id][non_rival_id] != 0 and norm[non_rival_id] != 0:
					measure1[gang_id]['nonrival'].append(visit_mat[gang_id][non_rival_id])
					measure2[gang_id]['nonrival'].append(round(visit_mat[gang_id][non_rival_id]/norm[non_rival_id], 2))

	with open(my.DATA_FOLDER + '/' + my.OUT_MEASURE1_FILE, 'wb') as fp2:
		fp2.write(anyjson.serialize(measure1))
	with open(my.DATA_FOLDER + '/' + my.OUT_MEASURE2_FILE, 'wb') as fp2:
		fp2.write(anyjson.serialize(measure2))
		

def generate_output():
	measure1 = {}
	measure2 = {}
	tty_names = loadLocNames()

	visitation_sum = ''
	visitation_sum_norm = ''
	visitation_avg = ''
	visitation_avg_norm = ''

	each_gang = ''
	each_gang_norm = ''

	series_rival = []
	series_nonrival = []
	series_rival_norm = []
	series_nonrival_norm = []

	with open(my.DATA_FOLDER + '/' + my.OUT_MEASURE1_FILE, 'rb') as fp1:
		measure1 = anyjson.deserialize(fp1.read())
	with open(my.DATA_FOLDER + '/' + my.OUT_MEASURE2_FILE, 'rb') as fp1:
		measure2 = anyjson.deserialize(fp1.read())

	for gang_id in measure1:
		if not (len(measure1[gang_id]['rival']) == 0 and len(measure1[gang_id]['nonrival']) == 0):
			visitation_sum += tty_names[int(gang_id)] + ',' + str(sum(measure1[gang_id]['rival'])) + ', ' + str(sum(measure1[gang_id]['nonrival'])) + '\n'
			visitation_avg += tty_names[int(gang_id)] + ',' + str(0 if len(measure1[gang_id]['rival']) == 0 else round(sum(measure1[gang_id]['rival'])/float(len(measure1[gang_id]['rival'])), 2)) + ', ' + str(0 if len(measure1[gang_id]['nonrival']) == 0 else round(sum(measure1[gang_id]['nonrival'])/float(len(measure1[gang_id]['nonrival'])), 2) ) + '\n'

			each_gang += "name = '" + tty_names[int(gang_id)] + "'\n"
			each_gang += 'rival = ' + arr_to_str(measure1[gang_id]['rival']) + '\n'
			each_gang += 'nonrival = ' + arr_to_str(measure1[gang_id]['nonrival']) + '\n\n'

			series_rival += measure1[gang_id]['rival']
			series_nonrival += measure1[gang_id]['nonrival']
	visit_series = 'rival = ' + arr_to_str(series_rival) + '\n' + 'nonrival = ' + arr_to_str(series_nonrival)
	
	with open(my.DATA_FOLDER + '/out/' + 'visitation_sum' + '.csv', 'wb') as fp:
		fp.write(visitation_sum)
	with open(my.DATA_FOLDER + '/out/' + 'visitation_avg' + '.csv', 'wb') as fp:
		fp.write(visitation_avg)
	with open(my.DATA_FOLDER + '/out/' + 'each_gang' + '.txt', 'wb') as fp:
		fp.write(each_gang)
	with open(my.DATA_FOLDER + '/out/' + 'visit_series' + '.txt', 'wb') as fp:
		fp.write(visit_series)

	for gang_id in measure2:
		if not (len(measure2[gang_id]['rival']) == 0 and len(measure2[gang_id]['nonrival']) == 0):
			visitation_sum_norm += tty_names[int(gang_id)] + ',' + str(sum(measure2[gang_id]['rival'])) + ', ' + str(sum(measure2[gang_id]['nonrival'])) + '\n'
			visitation_avg_norm += tty_names[int(gang_id)] + ',' + str(0 if len(measure2[gang_id]['rival']) == 0 else round(sum(measure2[gang_id]['rival'])/float(len(measure2[gang_id]['rival'])), 2)) + ', ' + str(0 if len(measure2[gang_id]['nonrival']) == 0 else round(sum(measure2[gang_id]['nonrival'])/float(len(measure2[gang_id]['nonrival'])), 2) ) + '\n'

			each_gang_norm += "name = '" + tty_names[int(gang_id)] + "'\n"
			each_gang_norm += 'rival = ' + arr_to_str(measure2[gang_id]['rival']) + '\n'
			each_gang_norm += 'nonrival = ' + arr_to_str(measure2[gang_id]['nonrival']) + '\n\n'

			series_rival_norm += measure2[gang_id]['rival']
			series_nonrival_norm += measure2[gang_id]['nonrival']
	visit_series_norm = 'rival = ' + arr_to_str(series_rival_norm) + '\n' + 'nonrival = ' + arr_to_str(series_nonrival_norm)

	with open(my.DATA_FOLDER + '/out/' + 'visitation_sum_norm' + '.csv', 'wb') as fp:
		fp.write(visitation_sum_norm)
	with open(my.DATA_FOLDER + '/out/' + 'visitation_avg_norm' + '.csv', 'wb') as fp:
		fp.write(visitation_avg_norm)
	with open(my.DATA_FOLDER + '/out/' + 'each_gang_norm' + '.txt', 'wb') as fp:
		fp.write(each_gang_norm)
	with open(my.DATA_FOLDER + '/out/' + 'visit_series_norm' + '.txt', 'wb') as fp:
		fp.write(visit_series_norm)


def arr_to_str(arr):
	arr_str = ''
	for val in arr:
		arr_str += str(val) + ','
	return '[' + arr_str[:-1] + ']'


# CALC functions
def calcVisitationMat(hbk_all_tweets, tty_polys, hbk_users_in_gang_t):
# visit_mat[i][j] = #tw(i) in j
	print 'Calculating visitation matrix...'
	visit_mat = {}
	for gang_id in my.HBK_GANG_ID_LIST:
		visit_mat[gang_id] = {}

	for gang_id in my.HBK_GANG_ID_LIST:
		if gang_id not in hbk_users_in_gang_t:
			for to_id in my.HBK_GANG_ID_LIST:
				visit_mat[gang_id][to_id] = 0
				#visit_mat[to_id][gang_id] = 0
		else:
			this_gang_tweets = keepUserIds(hbk_all_tweets, hbk_users_in_gang_t[gang_id])
			for to_id in my.HBK_GANG_ID_LIST:
				this_tty_tweets = keepPolygon(this_gang_tweets, tty_polys[to_id])
				visit_mat[gang_id][to_id] = len(this_tty_tweets)
				#visit_mat[to_id][gang_id] = len(this_tty_tweets)
	print 'Done calculating visitation matrix...'
	return visit_mat

def calcNorm(visit_mat):
	print 'Calculating norm vector...'
	norm = {}
	for gang_id in my.HBK_GANG_ID_LIST:
		norm[gang_id] = 0
	for gang_id in my.HBK_GANG_ID_LIST:
		for to_id in my.HBK_GANG_ID_LIST:
			if gang_id != to_id:
				norm[to_id] += visit_mat[gang_id][to_id]
	total = sum([norm[id] for id in norm])
	for gang_id in my.HBK_GANG_ID_LIST:
		norm[gang_id] = float(norm[gang_id]) / float(total)
	return norm
#- CALC functions



# LOAD functions
def loadLocNames():
	# Read location names for gang territories
	tty_names = {}
	print 'Reading location data...'
	with open(my.DATA_FOLDER + '/' + my.LOCATION_DATA_FILE, 'rb') as fp1:
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
	g_list = ''
	for gang_id in hbk_users_in_gang_t:
		g_list += str(gang_id) + ':' + str(len(hbk_users_in_gang_t[gang_id])) + ', '
	print 'Gang IDs with homes inside them: ' + g_list
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
