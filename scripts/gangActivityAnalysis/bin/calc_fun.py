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


def calc_rival_nonrival_matrics():
	tty_polys, hbk_poly = load.loadLocPoly()
	hbk_all_tweets = load.loadAllTweets()
	hbk_user_home_loc = load.loadAllHomeLoc(hbk_poly)
	hbk_users_in_gang_t = load.loadUsersInGangTty(tty_polys, hbk_user_home_loc)
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
	#-CH 	measure3 stores [frac, norm] instead of absolute values
	measure3 = {}
	
	for gang_id in my.HBK_GANG_AND_RIVAL_IDS:
		measure1[gang_id] = {
			'rival' : [],
			'nonrival' : []
			}
		measure2[gang_id] = {
			'rival' : [],
			'nonrival' : []
			}
		#-CH
		measure3[gang_id] = {
			'rival' : [],
			'nonrival' : []
			}

		non_home_sum = sum(visit_mat[gang_id].values()) - visit_mat[gang_id][gang_id]

		for rival_id in my.HBK_GANG_AND_RIVAL_IDS[gang_id]:
			if gang_id != rival_id and visit_mat[gang_id][rival_id] != 0:
				frac = visit_mat[gang_id][rival_id]/float(non_home_sum)
				measure1[gang_id]['rival'].append(round(frac, 5))
				measure2[gang_id]['rival'].append(round(frac/norm[rival_id], 5))
				#-CH
				measure3[gang_id]['rival'].append([frac, norm[rival_id]])

		for non_rival_id in my.HBK_GANG_ID_LIST:
			if gang_id != non_rival_id and non_rival_id not in my.HBK_GANG_AND_RIVAL_IDS[gang_id]:
				if visit_mat[gang_id][non_rival_id] != 0 and norm[non_rival_id] != 0:
					frac = visit_mat[gang_id][non_rival_id]/float(non_home_sum)
					measure1[gang_id]['nonrival'].append(round(frac, 5))
					measure2[gang_id]['nonrival'].append(round(frac/norm[non_rival_id], 5))
					#-CH
					measure3[gang_id]['nonrival'].append([frac, norm[non_rival_id]])

	# Store metrics
	if not os.path.exists('data/' + my.DATA_FOLDER + 'metrics/'):
		os.makedirs('data/' + my.DATA_FOLDER + 'metrics/')
	with open('data/' + my.DATA_FOLDER + 'metrics/' + 'measure1.json', 'wb') as fp2:
		fp2.write(anyjson.serialize(measure1))
	with open('data/' + my.DATA_FOLDER + 'metrics/' + 'measure2.json', 'wb') as fp2:
		fp2.write(anyjson.serialize(measure2))
	#-CH
	with open('data/' + my.DATA_FOLDER + 'metrics/' + 'measure3.json', 'wb') as fp2:
		fp2.write(anyjson.serialize(measure3))



def calc_rival_nonrival_matrics_dist_norm():
	tty_polys, hbk_poly = load.loadLocPoly()
	hbk_all_tweets = load.loadAllTweets()
	hbk_user_home_loc = load.loadAllHomeLoc(hbk_poly)
	hbk_users_in_gang_t = load.loadUsersInGangTty(tty_polys, hbk_user_home_loc)
	dist_norm = calcDistNorm()
	visit_mat = calcVisitationMat(hbk_all_tweets, tty_polys, hbk_users_in_gang_t, dist_norm, hbk_user_home_loc)
	#print visit_mat
	norm = calcNorm(calcVisitationMat(hbk_all_tweets, tty_polys, hbk_users_in_gang_t))

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

		non_home_sum = sum(visit_mat[gang_id].values()) - visit_mat[gang_id][gang_id]

		for rival_id in my.HBK_GANG_AND_RIVAL_IDS[gang_id]:
			if gang_id != rival_id and visit_mat[gang_id][rival_id] != 0:
				frac = visit_mat[gang_id][rival_id]/float(non_home_sum)
				measure1[gang_id]['rival'].append(round(frac, 5))
				measure2[gang_id]['rival'].append(round(frac/norm[rival_id], 5))

		for non_rival_id in my.HBK_GANG_ID_LIST:
			if gang_id != non_rival_id and non_rival_id not in my.HBK_GANG_AND_RIVAL_IDS[gang_id]:
				if visit_mat[gang_id][non_rival_id] != 0 and norm[non_rival_id] != 0:
					frac = visit_mat[gang_id][non_rival_id]/float(non_home_sum)
					measure1[gang_id]['nonrival'].append(round(frac, 5))
					measure2[gang_id]['nonrival'].append(round(frac/norm[non_rival_id], 5))

	# Store metrics
	if not os.path.exists('data/' + my.DATA_FOLDER + 'metrics_dist-norm/'):
		os.makedirs('data/' + my.DATA_FOLDER + 'metrics_dist-norm/')
	with open('data/' + my.DATA_FOLDER + 'metrics_dist-norm/' + 'measure1.json', 'wb') as fp2:
		fp2.write(anyjson.serialize(measure1))
	with open('data/' + my.DATA_FOLDER + 'metrics_dist-norm/' + 'measure2.json', 'wb') as fp2:
		fp2.write(anyjson.serialize(measure2))



def arr_to_str(arr):
	arr_str = ''
	for val in arr:
		arr_str += str(val) + ','
	return '[' + arr_str[:-1] + ']'


# CALC functions
def calcVisitationMat(hbk_all_tweets, tty_polys, hbk_users_in_gang_t, dist_norm=None, hbk_user_home_loc=None):
# visit_mat[i][j] = #tw(i) in j
	print 'Calculating visitation matrix...'

	hbk_home_list = {}
	if dist_norm:
		print '...for distance norm.'
		for user_home in hbk_user_home_loc:
			hbk_home_list[user_home[0]] = [user_home[1], user_home[2]]

	visit_mat = {}
	for gang_id in my.HBK_GANG_ID_LIST:
		visit_mat[gang_id] = {}

	for gang_id in my.HBK_GANG_ID_LIST:
		if gang_id not in hbk_users_in_gang_t:
			for to_id in my.HBK_GANG_ID_LIST:
				visit_mat[gang_id][to_id] = 0
				#visit_mat[to_id][gang_id] = 0
		else:
			this_gang_tweets = prep.keepUserIds(hbk_all_tweets, hbk_users_in_gang_t[gang_id])
			for to_id in my.HBK_GANG_ID_LIST:
				this_tty_tweets = prep.keepPolygon(this_gang_tweets, tty_polys[to_id])
				if dist_norm == None:
					visit_mat[gang_id][to_id] = len(this_tty_tweets)
				else:
					visit_val = 0
					for tweet in this_tty_tweets:
						dist = geo.distance(geo.xyz(tweet[1], tweet[2]), geo.xyz(hbk_home_list[tweet[0]][0], hbk_home_list[tweet[0]][1]))
						dist_i = int(round(dist/100 + 1))
						visit_val += 1/dist_norm[dist_i]
						#print str(dist_i) + '\t=>\t' + str(1/dist_norm[dist_i])
					visit_mat[gang_id][to_id] = round(visit_val, 5)
	print 'Done calculating visitation matrix...'
	return visit_mat
	# visit_mat[from][to] = count

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

def calcDistNorm():
	calcTweetDistances()
	print 'Calculating distance norm vector...'
	norm = {}
	for i in range(1, 101):
		norm[i] = 0
	count = 1
	with open('data/' + my.DATA_FOLDER + my.HBK_TWEET_DIST_FILE, 'rb') as fp:
		csv_reader = csv.reader(fp, delimiter=',')
		for row in csv_reader:
			dist_i = int(int(row[1])/100)+1
			if dist_i > 0 and dist_i <= 100:
				norm[dist_i] += 1
				count += 1
	for i in range(1, 101):
		norm[i] = (1/float(count) if norm[i] == 0 else norm[i]/float(count))
	return norm

def calcTweetDistances():
	print 'Calculating tweeting distances...'
	_, hbk_poly = load.loadLocPoly()
	hbk_all_tweets = load.loadAllTweets()
	hbk_user_home_loc = load.loadAllHomeLoc(hbk_poly)
	hbk_home_list = {}
	for user_home in hbk_user_home_loc:
		hbk_home_list[user_home[0]] = [user_home[1], user_home[2]]

	with open('data/' + my.DATA_FOLDER + my.HBK_TWEET_DIST_FILE, 'wb') as fp:
		csv_writer = csv.writer(fp, delimiter=',')
		for tweet in hbk_all_tweets:
			user_id = tweet[0]
			dist = int(round(geo.distance(geo.xyz(tweet[1], tweet[2]), geo.xyz(hbk_home_list[user_id][0], hbk_home_list[user_id][1]))))
			csv_writer.writerow([user_id, dist])
	print 'Done calculating tweeting distances...'




#- CALC functions


