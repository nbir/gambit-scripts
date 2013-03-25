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
import bin.prep_fun as prep
import bin.calc_fun as calc



def generate_output(metrics_folder='metrics/'):
	measure1 = {}
	measure2 = {}
	tty_names = load.loadLocNames()

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

	with open('data/' + my.DATA_FOLDER + metrics_folder + 'measure1.json', 'rb') as fp1:
		measure1 = anyjson.deserialize(fp1.read())
	with open('data/' + my.DATA_FOLDER + metrics_folder + 'measure2.json', 'rb') as fp1:
		measure2 = anyjson.deserialize(fp1.read())

	# Measure 1
	for gang_id in measure1:
		if not (len(measure1[gang_id]['rival']) == 0 and len(measure1[gang_id]['nonrival']) == 0):
			visitation_sum += tty_names[int(gang_id)] + ',' + str(sum(measure1[gang_id]['rival'])) + ', ' + str(sum(measure1[gang_id]['nonrival'])) + '\n'
			visitation_avg += tty_names[int(gang_id)] + ',' + str(0 if len(measure1[gang_id]['rival']) == 0 else round(sum(measure1[gang_id]['rival'])/float(len(measure1[gang_id]['rival'])), 5)) + ', ' + str(0 if len(measure1[gang_id]['nonrival']) == 0 else round(sum(measure1[gang_id]['nonrival'])/float(len(measure1[gang_id]['nonrival'])), 5) ) + '\n'

			each_gang += "name = '" + tty_names[int(gang_id)] + "'\n"
			each_gang += 'rival = ' + arr_to_str(measure1[gang_id]['rival']) + '\n'
			each_gang += 'nonrival = ' + arr_to_str(measure1[gang_id]['nonrival']) + '\n\n'

			series_rival += measure1[gang_id]['rival']
			series_nonrival += measure1[gang_id]['nonrival']
	visit_series = 'rival = ' + arr_to_str(series_rival) + '\n' + 'nonrival = ' + arr_to_str(series_nonrival)
	
	if not os.path.exists('data/' + my.DATA_FOLDER + metrics_folder + 'out/'):
		os.makedirs('data/' + my.DATA_FOLDER + metrics_folder + 'out/')
	with open('data/' + my.DATA_FOLDER + metrics_folder + 'out/' + 'visitation_sum' + '.csv', 'wb') as fp:
		fp.write(visitation_sum)
	with open('data/' + my.DATA_FOLDER + metrics_folder + 'out/' + 'visitation_avg' + '.csv', 'wb') as fp:
		fp.write(visitation_avg)
	with open('data/' + my.DATA_FOLDER + metrics_folder + 'out/' + 'each_gang' + '.txt', 'wb') as fp:
		fp.write(each_gang)
	with open('data/' + my.DATA_FOLDER + metrics_folder + 'out/' + 'visit_series' + '.txt', 'wb') as fp:
		fp.write(visit_series)

	# Measure 2
	for gang_id in measure2:
		if not (len(measure2[gang_id]['rival']) == 0 and len(measure2[gang_id]['nonrival']) == 0):
			visitation_sum_norm += tty_names[int(gang_id)] + ',' + str(sum(measure2[gang_id]['rival'])) + ', ' + str(sum(measure2[gang_id]['nonrival'])) + '\n'
			visitation_avg_norm += tty_names[int(gang_id)] + ',' + str(0 if len(measure2[gang_id]['rival']) == 0 else round(sum(measure2[gang_id]['rival'])/float(len(measure2[gang_id]['rival'])), 5)) + ', ' + str(0 if len(measure2[gang_id]['nonrival']) == 0 else round(sum(measure2[gang_id]['nonrival'])/float(len(measure2[gang_id]['nonrival'])), 5) ) + '\n'

			each_gang_norm += "name = '" + tty_names[int(gang_id)] + "'\n"
			each_gang_norm += 'rival = ' + arr_to_str(measure2[gang_id]['rival']) + '\n'
			each_gang_norm += 'nonrival = ' + arr_to_str(measure2[gang_id]['nonrival']) + '\n\n'

			series_rival_norm += measure2[gang_id]['rival']
			series_nonrival_norm += measure2[gang_id]['nonrival']
	visit_series_norm = 'rival = ' + arr_to_str(series_rival_norm) + '\n' + 'nonrival = ' + arr_to_str(series_nonrival_norm)

	with open('data/' + my.DATA_FOLDER + metrics_folder + 'out/' + 'visitation_sum_norm' + '.csv', 'wb') as fp:
		fp.write(visitation_sum_norm)
	with open('data/' + my.DATA_FOLDER + metrics_folder + 'out/' + 'visitation_avg_norm' + '.csv', 'wb') as fp:
		fp.write(visitation_avg_norm)
	with open('data/' + my.DATA_FOLDER + metrics_folder + 'out/' + 'each_gang_norm' + '.txt', 'wb') as fp:
		fp.write(each_gang_norm)
	with open('data/' + my.DATA_FOLDER + metrics_folder + 'out/' + 'visit_series_norm' + '.txt', 'wb') as fp:
		fp.write(visit_series_norm)

	#-CH
	# Measure 3
	try:
		measure3 = {}
		with open('data/' + my.DATA_FOLDER + metrics_folder + 'measure3.json', 'rb') as fp1:
			measure3 = anyjson.deserialize(fp1.read())
		m3_visitation_sum = ''
		m3_visitation_avg = ''
		for gang_id in measure3:
			if not (len(measure3[gang_id]['rival']) == 0 and len(measure3[gang_id]['nonrival']) == 0):
				m3_visitation_sum += tty_names[int(gang_id)] + ',' \
					+ str(sum([(x[0]*(x[0]/x[1])) for x in measure3[gang_id]['rival']])) + ', ' \
					+ str(sum([(x[0]*(x[0]/x[1])) for x in measure3[gang_id]['nonrival']])) + '\n'
				m3_visitation_avg += tty_names[int(gang_id)] + ',' \
					+ str(0 if len(measure3[gang_id]['rival']) == 0 else round(sum([(x[0]*(x[0]/x[1])) for x in measure3[gang_id]['rival']])/float(len(measure3[gang_id]['rival'])), 5)) + ', ' \
					+ str(0 if len(measure3[gang_id]['nonrival']) == 0 else round(sum([(x[0]*(x[0]/x[1])) for x in measure3[gang_id]['nonrival']])/float(len(measure3[gang_id]['nonrival'])), 5) ) + '\n'
		
		with open('data/' + my.DATA_FOLDER + metrics_folder + 'out/' + 'm3_visitation_sum' + '.csv', 'wb') as fp:
			fp.write(m3_visitation_sum)
		with open('data/' + my.DATA_FOLDER + metrics_folder + 'out/' + 'm3_visitation_avg' + '.csv', 'wb') as fp:
			fp.write(m3_visitation_avg)
	except Exception:
		print 'Error in generating output for measure3.'


def arr_to_str(arr):
	arr_str = ''
	for val in arr:
		arr_str += str(val) + ','
	return '[' + arr_str[:-1] + ']'




####################################################################################

def generate_gang_tweet_counts():
# Generate each gang's tweet count
	tty_polys, hbk_poly = load.loadLocPoly()
	hbk_all_tweets = load.loadAllTweets()
	hbk_user_home_loc = load.loadAllHomeLoc(hbk_poly)
	hbk_users_in_gang_t = load.loadUsersInGangTty(tty_polys, hbk_user_home_loc)

	# read each gang's tweet count
	hbk_tweets_by_gang = {}
	print 'Finding tweet count by each gang...'
	for gang_id in hbk_users_in_gang_t:
		#hbk_tweets_by_gang[gang_id] = len(prep.keepUserIds(hbk_all_tweets, hbk_users_in_gang_t[gang_id]))
		#hbk_tweets_by_gang[gang_id] = len(prep.removePolygon(prep.keepUserIds(hbk_all_tweets, hbk_users_in_gang_t[gang_id]), tty_polys[gang_id]))

		this_gang_tweets = prep.keepUserIds(hbk_all_tweets, hbk_users_in_gang_t[gang_id])
		hbk_tweets_by_gang[gang_id] = 0
		for foreign_id in my.HBK_GANG_ID_LIST:
			if gang_id != foreign_id:
				hbk_tweets_by_gang[gang_id] += len(prep.keepPolygon(this_gang_tweets, tty_polys[foreign_id]))
	print 'Each gang\'s tweet count: %s' % hbk_tweets_by_gang

	if not os.path.exists('data/' + my.DATA_FOLDER + 'json/'):
		os.makedirs('data/' + my.DATA_FOLDER + 'json/')
	with open('data/' + my.DATA_FOLDER  + 'json/' + 'gang_tweet_counts.json', 'wb') as fp1:
		fp1.write(anyjson.dumps(hbk_tweets_by_gang))

def generate_visit_mat():
# Generate visit matrix json
	tty_polys, hbk_poly = load.loadLocPoly()
	hbk_all_tweets = load.loadAllTweets()
	hbk_user_home_loc = load.loadAllHomeLoc(hbk_poly)
	hbk_users_in_gang_t = load.loadUsersInGangTty(tty_polys, hbk_user_home_loc)
	visit_mat = calc.calcVisitationMat(hbk_all_tweets, tty_polys, hbk_users_in_gang_t)

	if not os.path.exists('data/' + my.DATA_FOLDER + 'json/'):
		os.makedirs('data/' + my.DATA_FOLDER + 'json/')
	with open('data/' + my.DATA_FOLDER  + 'json/' + 'visit_matrix.json', 'wb') as fp1:
		fp1.write(anyjson.dumps(visit_mat))

def generate_rivalry_mat():
# Generate rivalry martix
	
	rivalry_matrix = {}
	for gang_id in my.HBK_GANG_AND_RIVAL_IDS:
		rivalry_matrix[gang_id] = {
			'rival' : [],
			'nonrival' : []
			}
		for rival_id in my.HBK_GANG_AND_RIVAL_IDS[gang_id]:
			rivalry_matrix[gang_id]['rival'].append(rival_id)
		for non_rival_id in my.HBK_GANG_ID_LIST:
			if gang_id != non_rival_id and non_rival_id not in my.HBK_GANG_AND_RIVAL_IDS[gang_id]:
				rivalry_matrix[gang_id]['nonrival'].append(non_rival_id)

	if not os.path.exists('data/' + my.DATA_FOLDER + 'json/'):
		os.makedirs('data/' + my.DATA_FOLDER + 'json/')
	with open('data/' + my.DATA_FOLDER  + 'json/' + 'rivalry_matrix.json', 'wb') as fp1:
		fp1.write(anyjson.dumps(rivalry_matrix))


def generate_gang_locs_json():
# Generate each gang's locations json

	tty_polys, hbk_poly = load.loadLocPoly()
	hbk_all_tweets = load.loadAllTweets()
	hbk_user_home_loc = load.loadAllHomeLoc(hbk_poly)
	hbk_users_in_gang_t = load.loadUsersInGangTty(tty_polys, hbk_user_home_loc)

	# trim each gang's tweets
	hbk_tweets_by_gang = {}
	print 'Finding tweets by each gang...'
	for gang_id in my.HBK_GANG_ID_LIST:
		this_gang_tweets = prep.keepUserIds(hbk_all_tweets, hbk_users_in_gang_t[gang_id]) if gang_id in hbk_users_in_gang_t else []
		hbk_tweets_by_gang[gang_id] = [[tweet[1], tweet[2]] for tweet in this_gang_tweets]
	print 'Each gang\'s tweet count: %s' % dict([(gang_id, len(hbk_tweets_by_gang[gang_id])) for gang_id in hbk_tweets_by_gang])
	print 'Total tweets = %s' % (sum([len(hbk_tweets_by_gang[gang_id]) for gang_id in hbk_tweets_by_gang]))

	if not os.path.exists('data/' + my.DATA_FOLDER + 'json/'):
		os.makedirs('data/' + my.DATA_FOLDER + 'json/')
	with open('data/' + my.DATA_FOLDER  + 'json/' + 'gang_tweet_locs.json', 'wb') as fp1:
		fp1.write(anyjson.dumps(hbk_tweets_by_gang))


def generate_border_lines():
# Generate all lines from polygon borders

	tty_polys, hbk_poly = load.loadLocPoly()
	border_lines = []
	EXTRA_LINES = [[[34.03132292028969, -118.1923770904541], [34.029117842533914, -118.20130348205566]], [[34.029117842533914, -118.20130348205566], [34.02840651490425, -118.2062816619873]], [[34.02840651490425, -118.2062816619873], [34.02847764793555, -118.20877075195312]], [[34.03843568373245, -118.22138786315918], [34.04298753935195, -118.22121620178223]], [[34.04483666091566, -118.21606636047363], [34.04184959834946, -118.21752548217773]], [[34.080815382118054, -118.2224178314209], [34.078895954750585, -118.22001457214355]], [[34.078895954750585, -118.22001457214355], [34.07718976057057, -118.21924209594727]], [[34.07718976057057, -118.21924209594727], [34.07285302899903, -118.21941375732422]], [[34.07285302899903, -118.21941375732422], [34.067449577393454, -118.21640968322754]], [[34.067449577393454, -118.21640968322754], [34.06602755916641, -118.21632385253906]], [[34.08607581189449, -118.18370819091797], [34.08536496210261, -118.18053245544434]], [[34.08536496210261, -118.18053245544434], [34.0865734031979, -118.1770133972168]], [[34.0865734031979, -118.1770133972168], [34.08920348007902, -118.17091941833496]], [[34.08920348007902, -118.17091941833496], [34.09005646044008, -118.1660270690918]], [[34.09005646044008, -118.1660270690918], [34.09339721743675, -118.16079139709473]]]

	for gang_id in tty_polys:
		for i in range(0, len(tty_polys[gang_id])-1):
			border_lines.append([tty_polys[gang_id][i], tty_polys[gang_id][i+1]])
	border_lines.extend(EXTRA_LINES)
	print 'Total number of lines = %s' % (len(border_lines))

	if not os.path.exists('data/' + my.DATA_FOLDER + 'json/'):
		os.makedirs('data/' + my.DATA_FOLDER + 'json/')
	with open('data/' + my.DATA_FOLDER  + 'json/' + 'border_lines.json', 'wb') as fp1:
		fp1.write(anyjson.dumps(border_lines))



