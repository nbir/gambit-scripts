# Gambit scripts
#
# Copyright (C) USC Information Sciences Institute
# Author: Nibir Bora <nbora@usc.edu>
# URL: <http://cbg.isi.edu/>
# For license information, see LICENSE


import os
import sys
#import bin.gangVsLA as do
#import bin.rivalNonrival as do
import argparse


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-g', '--get', nargs='*', help='\
		[all - Get all tweets inside bounds]')
	parser.add_argument('-p', '--prep', nargs='*', help='\
		[trim-home - Trim home clusters in data] \n\
		[trim-ngang - Trim all non gang users in data] \n\
		[trim-low-tw - Trim tweets by low tweeting gangs] \n\
		[trim-low-user - Trim tweets by gangs with low users] \n\
		[trim-lines - Trim tweets near border lines] \n\
		[trim-pols - Trim tweets inside polygons] ')
	parser.add_argument('-c', '--calc', nargs='*', help='\
		[rnr|rivalnonrival - Calculate rival-nonrival visit metrics] \n\
		[rnr-dist|rivalnonrival-dist - Calculate rival-nonrival visit metrics using distance norm] ')
	parser.add_argument('-o', '--out', nargs='*', help='\
		[rnr|rivalnonrival - Generate output for rival-nonrival metrics] \n\
		[rnr-dist|rivalnonrival-dist - Generate output for rival-nonrival metrics using distance norm] \n\
		\
		[visit-mat - Generate visit matrix json] \n\
		[gang-tw - Generate each gang\'s tweet count] \n\
		[rival-mat - Generate rivalry matrix json] \n\
		[gang-loc - Generate each gang\'s tweet locations] \n\
		[border - Generate all lines from polygon borders] ')

	parser.add_argument('-s', '--see', nargs='*', help='\
		gang-tw - See each gang\'s tweet count\n\
		test - Call test function')
	args = parser.parse_args()

	if args.get:
		import bin.get_fun as do
		if 'all' in args.get:
			print '\n*** Get all tweets inside bounds ***\n'
			do.get_tweets_in()

	if args.prep:
		import bin.prep_fun as do
		if 'trim-home' in args.prep:
			print '\n*** Trim home clusters in data ***\n'
			do.trim_home_clusters()
		if 'trim-ngang' in args.prep:
			print '\n*** Trim all non gang users in data ***\n'
			do.trim_non_gang_users()
		if 'trim-low-tw' in args.prep:
			print '\n*** Trim tweets by low tweeting gangs ***\n'
			do.trim_low_tweet_gangs()
		if 'trim-low-user' in args.prep:
			print '\n*** Trim tweets by gangs with low users ***\n'
			do.trim_low_user_gangs()
		if 'trim-lines' in args.prep:
			print '\n*** Trim tweets near border lines ***\n'
			do.trim_near_lines()
		if 'trim-pols' in args.prep:
			print '\n*** Trim tweets inside polygons ***\n'
			do.trim_inside_pols()

	if args.calc:
		import bin.calc_fun as do
		if 'rnr' in args.calc or 'rivalnonrival' in args.calc:
			print '\n*** Calculate rival-nonrival visit metrics ***\n'
			do.calc_rival_nonrival_matrics()
		if 'rnr-dist' in args.calc or 'rivalnonrival-dist' in args.calc:
			print '\n*** Calculate rival-nonrival visit metrics using distance norm ***\n'
			do.calc_rival_nonrival_matrics_dist_norm()

	if args.out:
		import bin.out_fun as do
		if 'rnr' in args.out or 'rivalnonrival' in args.out:
			print '\n*** Generate output for rival-nonrival metrics ***\n'
			do.generate_output()
		if 'rnr-dist' in args.out or 'rivalnonrival-dist' in args.out:
			print '\n*** Generate output for rival-nonrival metrics using distance norm ***\n'
			do.generate_output('metrics_dist-norm/')
		# JSON outputs
		if 'visit-mat' in args.out:
			print '\n*** Generate visit matrix json ***\n'
			do.generate_visit_mat()
		if 'gang-tw' in args.out:
			print '\n*** Generate each gang\'s tweet count ***\n'
			do.generate_gang_tweet_counts()
		if 'rival-mat' in args.out:
			print '\n*** Generate rivalry matrix json ***\n'
			do.generate_rivalry_mat()
		if 'gang-loc' in args.out:
			print '\n*** Generate each gang\'s tweet locations ***\n'
			do.generate_gang_locs_json()
		if 'border' in args.out:
			print '\n*** Generate all lines from polygon borders ***\n'
			do.generate_border_lines()

	if args.see:
		import bin.see_fun as do
		if 'gang-tw' in args.see:
			print '\n*** See each gang\'s tweet count ***\n'
			do.see_gang_tweet_counts()
		if 'test' in args.see:
			print '\n*** Test, Test. Test! ***\n'
			do.test()
