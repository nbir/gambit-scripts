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


def calc_visit_sets():
# Calculate all visit sets
	tty_polys, hbk_poly = load.loadLocPoly()
	hbk_all_tweets = load.loadAllTweets()
	hbk_user_home_loc = load.loadAllHomeLoc(hbk_poly)
	hbk_users_in_gang_t = load.loadUsersInGangTty(tty_polys, hbk_user_home_loc)

	# Visit matrix
	visit_mat = calcVisitationMat(hbk_all_tweets, tty_polys, hbk_users_in_gang_t)

	# Norm vectors
	non_home_norm = calcNonHomeNorm(visit_mat)
	tw_freq_norm = calcTwFreqNorm(visit_mat)
	#dist_norm = calcDistNorm()		# Different distance norm functions
	dist_norm = calcDistNormCDF()

	# Metrics- No normalization (absolute fractions)
	store_visit_set_output(calc_visit_sets_from_visit_mat(visit_mat), 'no_norm')

	# Metrics- Non-home normalized (TO-tty normalized)
	normalized_visit_mat = apply_non_home_norm(visit_mat, non_home_norm)
	store_visit_set_output(calc_visit_sets_from_visit_mat(normalized_visit_mat), 'non_home_norm')

	# Metrics- Tweet freq normalized (FROM-tty normalized)
	normalized_visit_mat = apply_tw_freq_norm(visit_mat, tw_freq_norm)
	store_visit_set_output(calc_visit_sets_from_visit_mat(normalized_visit_mat), 'tw_freq_norm')

	# Metrics- Distance normalized
	visit_mat_dist_norm = calcVisitationMat(hbk_all_tweets, tty_polys, hbk_users_in_gang_t, dist_norm, hbk_user_home_loc)
	store_visit_set_output(calc_visit_sets_from_visit_mat(visit_mat_dist_norm), 'dist_norm')

	# Metrics- Rival count normalized
	normalized_visit_mat = apply_rivals_norm(visit_mat)
	store_visit_set_output(calc_visit_sets_from_visit_mat(normalized_visit_mat), 'rivals_norm')

	# Metrics- Distance + Non-home norm
	normalized_visit_mat = apply_non_home_norm(visit_mat_dist_norm, non_home_norm)
	store_visit_set_output(calc_visit_sets_from_visit_mat(normalized_visit_mat), 'dist__non_home')

	# Metrics- Distance + Tweet freq norm
	normalized_visit_mat = apply_tw_freq_norm(visit_mat_dist_norm, tw_freq_norm)
	store_visit_set_output(calc_visit_sets_from_visit_mat(normalized_visit_mat), 'dist__tw_freq')

	# Metrics- Distance + Rivals normalized
	normalized_visit_mat = apply_rivals_norm(visit_mat_dist_norm)
	store_visit_set_output(calc_visit_sets_from_visit_mat(normalized_visit_mat), 'dist__rivals')

	# Metrics- Distance + Tweet freq + Non-home norm
	normalized_visit_mat = apply_tw_freq_norm(visit_mat_dist_norm, tw_freq_norm)
	normalized_visit_mat = apply_non_home_norm(normalized_visit_mat, non_home_norm)
	store_visit_set_output(calc_visit_sets_from_visit_mat(normalized_visit_mat), 'dist__tw_freq__non_home')
	# Metrics- Distance + Tweet freq + Non-home + Rivals norm
	normalized_visit_mat = apply_rivals_norm(normalized_visit_mat)
	store_visit_set_output(calc_visit_sets_from_visit_mat(normalized_visit_mat), 'dist__tw_freq__non_home__rivals')

def calc_visit_sets_from_visit_mat(visit_mat):
# Calculate visit set from visit matrix
	visit_sets = {}

	for gang_id in my.HBK_GANG_AND_RIVAL_IDS:
		visit_sets[gang_id] = {
			'rival' : [],
			'nonrival' : []
			}

		non_home_sum = sum(visit_mat[gang_id].values()) - visit_mat[gang_id][gang_id]

		for rival_id in my.HBK_GANG_AND_RIVAL_IDS[gang_id]:
			if gang_id != rival_id and visit_mat[gang_id][rival_id] != 0:
				frac = visit_mat[gang_id][rival_id]/float(non_home_sum)
				visit_sets[gang_id]['rival'].append(round(frac, 5))

		for non_rival_id in my.HBK_GANG_ID_LIST:
			if gang_id != non_rival_id and non_rival_id not in my.HBK_GANG_AND_RIVAL_IDS[gang_id]:
				if visit_mat[gang_id][non_rival_id] != 0:
					frac = visit_mat[gang_id][non_rival_id]/float(non_home_sum)
					visit_sets[gang_id]['nonrival'].append(round(frac, 5))
	return visit_sets


def store_visit_set_output(visit_sets, folder_name):
# Stores the calculated visit sets to output json file
	if not os.path.exists('data/' + my.DATA_FOLDER + 'metrics/' + folder_name + '/'):
		os.makedirs('data/' + my.DATA_FOLDER + 'metrics/' + folder_name + '/')
	with open('data/' + my.DATA_FOLDER + 'metrics/'  + folder_name + '/' + 'visit_sets.json', 'wb') as fp2:
		fp2.write(anyjson.serialize(visit_sets))


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
	# Different distance norm functions
	#dist_norm = calcDistNorm()
	dist_norm = calcDistNormCDF()

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




# NORMALIZING FUNCTIONS
# Calculate normalizing vectors & functions
def calcNonHomeNorm(visit_mat):
	print 'Calculating Non-Home norm vector...'
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

def calcTwFreqNorm(visit_mat):
	print 'Calculating Tweet-Freq norm vector...'
	norm = dict([(gang_id, sum(visit_mat[gang_id].values())) for gang_id in my.HBK_GANG_ID_LIST])
	norm = dict([(gang_id, norm[gang_id]/float(sum(norm.values()))) for gang_id in norm])
	return norm

## Alternate distance norm measures
def calcDistNorm():
	#calcTweetDistances()		# Get file from findUserHomes
	print 'Calculating distance norm vector (fraction)...'
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

def calcDistNormCDF():
	#calcTweetDistances()		# Get file from findUserHomes
	print 'Calculating distance norm vector (CDF)...'
	frac = {}
	for i in range(1, 101):
		frac[i] = 0
	count = 1
	with open('data/' + my.DATA_FOLDER + my.HBK_TWEET_DIST_FILE, 'rb') as fp:
		csv_reader = csv.reader(fp, delimiter=',')
		for row in csv_reader:
			dist_i = int(int(row[1])/100)+1
			if dist_i > 0 and dist_i <= 100:
				frac[dist_i] += 1
				count += 1
	
	cdf = {}
	for i in range(1, 101):
		cdf[i] = sum([frac[j] for j in range(1, i+1)])/float(count)
	#cdf[100] = 1.0
	
	norm = {}
	for i in range(1, 101):
		#norm[i] = 1/cdf[i]		# dist_norm_2
		norm[i] = 1-cdf[i]		# dist_norm_3
	
	return norm

def calcTweetDistances():
	print 'Calculating tweeting distances...'
	_, hbk_poly = load.loadLocPoly()
	hbk_all_tweets = load.loadAllTweets()
	hbk_user_home_loc = load.loadAllHomeLoc(hbk_poly)
	print [i[0] for i in hbk_user_home_loc]
	hbk_home_list = {}
	for user_home in hbk_user_home_loc:
		hbk_home_list[user_home[0]] = [user_home[1], user_home[2]]

	with open('data/' + my.DATA_FOLDER + my.HBK_TWEET_DIST_FILE, 'wb') as fp:
		csv_writer = csv.writer(fp, delimiter=',')
		for tweet in hbk_all_tweets:
			user_id = tweet[0]
			#print tweet, hbk_home_list[user_id]
			dist = int(round(geo.distance(geo.xyz(tweet[1], tweet[2]), geo.xyz(hbk_home_list[user_id][0], hbk_home_list[user_id][1]))))
			csv_writer.writerow([user_id, dist])
	print 'Done calculating tweeting distances...'


# Apply Normalizing vectors to visit matrix
def apply_non_home_norm(visit_mat, norm):
	print 'Applying Non-Home tweet count normalization to visit matrix...'
	for from_id in my.HBK_GANG_ID_LIST:
		for to_id in my.HBK_GANG_ID_LIST:
			if norm[to_id] != 0:
				visit_mat[from_id][to_id] /= norm[to_id]
			else:
				visit_mat[from_id][to_id] = 0
	return visit_mat

def apply_tw_freq_norm(visit_mat, norm):
	print 'Applying Tweet freq normalization to visit matrix...'
	for from_id in my.HBK_GANG_ID_LIST:
		for to_id in my.HBK_GANG_ID_LIST:
			if norm[from_id] != 0:
				visit_mat[from_id][to_id] /= norm[from_id]
			else:
				visit_mat[from_id][to_id] = 0
	return visit_mat

def apply_rivals_norm(visit_mat):
	norm = dict([(gang_id, len(my.HBK_GANG_AND_RIVAL_IDS[gang_id])) for gang_id in my.HBK_GANG_AND_RIVAL_IDS])
	norm = dict([(gang_id, norm[gang_id]/float(len(my.HBK_GANG_ID_LIST))) for gang_id in norm])
	print 'Applying Rival count normalization to visit matrix...'
	for from_id in my.HBK_GANG_ID_LIST:
		for to_id in my.HBK_GANG_ID_LIST:
			if norm[from_id] != 0:
				visit_mat[from_id][to_id] /= norm[from_id]
			else:
				visit_mat[from_id][to_id] = 0
	return visit_mat

#- CALC functions


