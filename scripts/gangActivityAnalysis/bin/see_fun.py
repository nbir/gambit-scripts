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
# trim all non gang users in data
	tty_polys, hbk_poly = load.loadLocPoly()
	hbk_all_tweets = load.loadAllTweets()
	hbk_user_home_loc = load.loadAllHomeLoc(hbk_poly)
	hbk_users_in_gang_t = load.loadUsersInGangTty(tty_polys, hbk_user_home_loc)

	# read each gang's tweet count
	hbk_tweets_by_gang = {}
	print 'Finding tweet count by each gang...'
	for gang_id in hbk_users_in_gang_t:
		hbk_tweets_by_gang[gang_id] = len(prep.keepUserIds(hbk_all_tweets, hbk_users_in_gang_t[gang_id]))
	print 'Each gang\'s tweet count: %s' % hbk_tweets_by_gang
	for gang_id in hbk_tweets_by_gang:
		if hbk_tweets_by_gang[gang_id] != 0:
			print '%s => %s' % (gang_id, hbk_tweets_by_gang[gang_id])

	print 'Total number of users: %s' % sum([len(hbk_users_in_gang_t[gang_id]) for gang_id in hbk_tweets_by_gang if hbk_tweets_by_gang[gang_id] != 0])
	print 'Total tweets from all users: %s' % sum([hbk_tweets_by_gang[gang_id] for gang_id in hbk_tweets_by_gang])



##############################################################

def test():
	dist_norm = calc.calcDistNormCDF()
	for k in dist_norm:
		print '%s, %s' % (k, dist_norm[k])
	