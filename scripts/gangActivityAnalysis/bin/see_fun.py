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



def see_gang_tweet_counts():
# See each gang's tweet count
	tty_polys, hbk_poly = load.loadLocPoly()
	tty_names = load.loadLocNames()
	hbk_all_tweets = load.loadAllTweets()
	hbk_user_home_loc = load.loadAllHomeLoc(hbk_poly)
	hbk_users_in_gang_t = load.loadUsersInGangTty(tty_polys, hbk_user_home_loc)

	# read each gang's tweet count
	hbk_tweets_by_gang = {}
	print 'Finding tweet count by each gang...'
	for gang_id in hbk_users_in_gang_t:
		hbk_tweets_by_gang[gang_id] = len(prep.keepUserIds(hbk_all_tweets, hbk_users_in_gang_t[gang_id]))
	print 'Each gang\'s tweet count: %s' % hbk_tweets_by_gang
	print '%2s %15s %5s %5s %8s %6s' % ('ID', 'NAME', '#TWs', '#USERs', '#RIVALs', 'TW/USR')
	for gang_id in hbk_tweets_by_gang:
		if hbk_tweets_by_gang[gang_id] != 0:
			print '%2s %15s %5s %5s %8s %6s' % (gang_id, tty_names[gang_id], hbk_tweets_by_gang[gang_id], len(hbk_users_in_gang_t[gang_id]), len(my.HBK_GANG_AND_RIVAL_IDS[gang_id]), int(hbk_tweets_by_gang[gang_id]/float(len(hbk_users_in_gang_t[gang_id]))))

	print 'Total number of users: %s' % sum([len(hbk_users_in_gang_t[gang_id]) for gang_id in hbk_tweets_by_gang if hbk_tweets_by_gang[gang_id] != 0])
	print 'Total tweets from all users: %s' % sum([hbk_tweets_by_gang[gang_id] for gang_id in hbk_tweets_by_gang])


def see_visit_mat():
# See Visit matrix
	tty_polys, hbk_poly = load.loadLocPoly()
	hbk_all_tweets = load.loadAllTweets()
	hbk_user_home_loc = load.loadAllHomeLoc(hbk_poly)
	hbk_users_in_gang_t = load.loadUsersInGangTty(tty_polys, hbk_user_home_loc)
	tty_names = load.loadLocNames()

	visit_mat = calc.calcVisitationMat(hbk_all_tweets, tty_polys, hbk_users_in_gang_t)

	x = ['GANG NAME', '#']
	x.extend(range(23,55))
	print '%20s - %2s: %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s' % tuple(x)
	for gang_id in visit_mat:
		x = [tty_names[gang_id], gang_id]
		y = dict([(to_id, visit_mat[gang_id][to_id]) if gang_id != to_id else (to_id, 0) for to_id in visit_mat[gang_id]])
		y = dict([(to_id, y[to_id]) if y[to_id] != 0 else (to_id, '.') for to_id in y])
		y = [str(y[to_id])+'r' if to_id in my.HBK_GANG_AND_RIVAL_IDS[gang_id] and y[to_id] !='.' else y[to_id] for to_id in y]
		x.extend(y)
		print '%20s - %2s: %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s' % tuple(x)

def see_rivalry_mat():
# See Rivalry matrix
	tty_names = load.loadLocNames()

	x = ['GANG NAME', '#']
	x.extend(range(23,55))
	print '%20s - %2s: %3s %3s %3s %3s %3s %3s %3s %3s %3s %3s %3s %3s %3s %3s %3s %3s %3s %3s %3s %3s %3s %3s %3s %3s %3s %3s %3s %3s %3s %3s %3s %3s' % tuple(x)
	for gang_id in range(23,55):
		x = [tty_names[gang_id], gang_id]
		y = ['X' if rival_id in my.HBK_GANG_AND_RIVAL_IDS[gang_id] else '.' for rival_id in range(23,55)]
		x.extend(y)
		print '%20s - %2s: %3s %3s %3s %3s %3s %3s %3s %3s %3s %3s %3s %3s %3s %3s %3s %3s %3s %3s %3s %3s %3s %3s %3s %3s %3s %3s %3s %3s %3s %3s %3s %3s' % tuple(x)

def see_rivalry_list():
# See Rivalry list
	tty_polys, hbk_poly = load.loadLocPoly()
	hbk_all_tweets = load.loadAllTweets()
	hbk_user_home_loc = load.loadAllHomeLoc(hbk_poly)
	hbk_users_in_gang_t = load.loadUsersInGangTty(tty_polys, hbk_user_home_loc)
	tty_names = load.loadLocNames()
	visit_mat_1 = calc.calcVisitationMat(hbk_all_tweets, tty_polys, hbk_users_in_gang_t)
	dist_norm = calc.calcDistNormCDF()
	visit_mat = calc.calcVisitationMat(hbk_all_tweets, tty_polys, hbk_users_in_gang_t, dist_norm, hbk_user_home_loc)

	rivalry_list = {}

	for gang_id in my.HBK_GANG_AND_RIVAL_IDS:
		for rival_id in [to_id for to_id in my.HBK_GANG_ID_LIST if to_id != gang_id]:
			if visit_mat_1[gang_id][rival_id] >= 5 and str(gang_id)+str(rival_id) not in rivalry_list and str(rival_id)+str(gang_id) not in rivalry_list:
				this_row = [gang_id, tty_names[gang_id], rival_id, tty_names[rival_id], \
					int(visit_mat[gang_id][rival_id]), \
					int(visit_mat[rival_id][gang_id])]

				this_row.append('rival') if rival_id in my.HBK_GANG_AND_RIVAL_IDS[gang_id] else this_row.append('nonrival')

				affinity = round(1.0/abs(visit_mat[gang_id][rival_id]-visit_mat[rival_id][gang_id]), 3) if visit_mat[gang_id][rival_id] != visit_mat[rival_id][gang_id] else 0
				this_row.append(affinity)
				
				this_row.append(int((visit_mat[gang_id][rival_id]+visit_mat[rival_id][gang_id])/2))

				rivalry_list[str(gang_id)+str(rival_id)] = this_row

	rivalry_list = rivalry_list.values()
	rivals = [row for row in rivalry_list if row[6] == 'rival']
	nonrivals = [row for row in rivalry_list if row[6] == 'nonrival']
	rivalry_list = rivals + nonrivals

	val = ['A#', 'GANG A', 'B#', 'GANG B', 'A>B', 'B>A', 'RnR', 'Affinity', 'AvgTw']
	print '%2s %20s => %2s %20s \t %4s \t %4s \t %8s \t %8s \t %5s' % tuple(val)
	for val in rivalry_list:
		print '%2s %20s => %2s %20s \t %4s \t %4s \t %8s \t %8s \t %5s' % tuple(val)


		
##############################################################

def test():

	'''dist_norm = calc.calcDistNormCDF()
	for k in dist_norm:
		print '%s, %s' % (k, dist_norm[k])'''
	tty_polys, hbk_poly = load.loadLocPoly()
	hbk_all_tweets = load.loadAllTweets()
	hbk_user_home_loc = load.loadAllHomeLoc(hbk_poly)
	hbk_users_in_gang_t = load.loadUsersInGangTty(tty_polys, hbk_user_home_loc)
	user_list = reduce(lambda x,y: x+y, hbk_users_in_gang_t.values())

	with open('data/' + my.DATA_FOLDER  + 'hbk_final_users.csv', 'wb') as fp1:
		csv_writer = csv.writer(fp1, delimiter=',')
		for user in user_list:
			csv_writer.writerow([user])
	# Visit matrix
	#visit_mat = calc.calcVisitationMat(hbk_all_tweets, tty_polys, hbk_users_in_gang_t)
	#print visit_mat
	#print visit_mat[24][34]
	