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

import numpy as np
import matplotlib.pyplot as plt

import bin.load_fun as load
import bin.prep_fun as prep
import bin.calc_fun as calc



# OUTPUT metric files
def generate_outputs_files():
# Generate output metric files for all measures
	generate_output('no_norm')
	generate_output('non_home_norm')
	generate_output('tw_freq_norm')
	generate_output('dist_norm')
	generate_output('rivals_norm')

	generate_output('dist__non_home')
	generate_output('dist__tw_freq')
	generate_output('dist__rivals')

	generate_output('dist__tw_freq__non_home')
	generate_output('dist__tw_freq__non_home__rivals')

def generate_output(folder_name):
	measure1 = {}
	tty_names = load.loadLocNames()

	visitation_sum = ''
	visitation_avg = ''
	each_gang = ''
	series_rival = []
	series_nonrival = []

	with open('data/' + my.DATA_FOLDER + 'metrics/' + folder_name + '/' + 'visit_sets.json', 'rb') as fp1:
		measure1 = anyjson.deserialize(fp1.read())

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
	
	with open('data/' + my.DATA_FOLDER + 'metrics/' + folder_name + '/' + 'visitation_sum' + '.csv', 'wb') as fp:
		fp.write(visitation_sum)
	with open('data/' + my.DATA_FOLDER + 'metrics/' + folder_name + '/' + 'visitation_avg' + '.csv', 'wb') as fp:
		fp.write(visitation_avg)
	with open('data/' + my.DATA_FOLDER + 'metrics/' + folder_name + '/' + 'each_gang' + '.txt', 'wb') as fp:
		fp.write(each_gang)
	with open('data/' + my.DATA_FOLDER + 'metrics/' + folder_name + '/' + 'visit_series' + '.txt', 'wb') as fp:
		fp.write(visit_series)

def arr_to_str(arr):
	arr_str = ''
	for val in arr:
		arr_str += str(val) + ','
	return '[' + arr_str[:-1] + ']'


# OUTPUT charts
def generate_outputs_charts():
# Generate output metric files for all measures
	generate_charts('no_norm')
	generate_charts('non_home_norm')
	generate_charts('tw_freq_norm')
	generate_charts('dist_norm')
	generate_charts('rivals_norm')

	generate_charts('dist__non_home')
	generate_charts('dist__tw_freq')
	generate_charts('dist__rivals')

	generate_charts('dist__tw_freq__non_home')
	generate_charts('dist__tw_freq__non_home__rivals')

def generate_charts(folder_name):
	measure1 = {}
	tty_names = load.loadLocNames()

	names = []
	sum_rival = []
	sum_nonrival = []
	avg_rival = []
	avg_nonrival = []

	with open('data/' + my.DATA_FOLDER + 'metrics/' + folder_name + '/' + 'visit_sets.json', 'rb') as fp1:
		measure1 = anyjson.deserialize(fp1.read())

	for gang_id in measure1:
		if not (len(measure1[gang_id]['rival']) == 0 and len(measure1[gang_id]['nonrival']) == 0):
			names.append(str(tty_names[int(gang_id)].replace('_', ' ')))
			sum_rival.append(round(sum(measure1[gang_id]['rival']), 5))
			sum_nonrival.append(round(sum(measure1[gang_id]['nonrival']),5))
			avg_rival.append(0 if len(measure1[gang_id]['rival']) == 0 else round(sum(measure1[gang_id]['rival'])/float(len(measure1[gang_id]['rival'])), 5))
			avg_nonrival.append(0 if len(measure1[gang_id]['nonrival']) == 0 else round(sum(measure1[gang_id]['nonrival'])/float(len(measure1[gang_id]['nonrival'])), 5))
	
	'''print names
	print sum_rival
	print sum_nonrival
	print avg_rival
	print avg_nonrival'''
	
	plot_visits_chart(names, sum_rival, sum_nonrival, folder_name, 'visits_sum.png')
	plot_visits_chart(names, avg_rival, avg_nonrival, folder_name, 'visits_avg.png')

def plot_visits_chart(names, rival, nonrival, folder_name, file_name):
	ind = np.arange(len(names))  # the x locations for the groups
	#width = 0.30       # the width of the bars
	width = 0.25       # the width of the bars
	#fig = plt.figure(figsize=(14,5))
	fig = plt.figure(figsize=(8,5))
	ax = fig.add_subplot(111)
	ax.set_autoscaley_on(False)
	ax.set_ylim([0,1])
	plt.subplots_adjust(left=0.045, right=0.99, top=0.98, bottom=0.28)
	rects1 = ax.bar(ind, rival, width, color='#E41A1C', alpha=0.65, edgecolor='#E41A1C')
	rects2 = ax.bar(ind+width, nonrival, width, color='#377EB8', alpha=0.8, edgecolor='#377EB8')
	ax.set_ylabel('Fraction of visits')
	ax.set_xticks(ind+width)
	#ax.set_xticklabels(names)
	xtickNames = plt.setp(ax, xticklabels=names)
	#plt.setp(xtickNames, rotation=45)
	plt.setp(xtickNames, rotation=90)
	ax.legend((rects1[0], rects2[0]), ('rival', 'nonrival'), fontsize=11, \
		title=folder_name.replace('_', ' ')+'\n'+file_name.replace('.png','').replace('visits_', ''))

	if not os.path.exists('data/' + my.DATA_FOLDER + 'metrics/' + folder_name + '/charts/'):
		os.makedirs('data/' + my.DATA_FOLDER + 'metrics/' + folder_name + '/charts/')
	plt.savefig('data/' + my.DATA_FOLDER + 'metrics/' + folder_name + '/charts/' + file_name)



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



