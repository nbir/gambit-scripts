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
		all - Get all tweets inside bounds')
	parser.add_argument('-p', '--prep', nargs='*', help='\
		trim-home - Trim home clusters in data\n\
		trim-ngang - Trim all non gang users in data')
	parser.add_argument('-c', '--calc', nargs='*', help='\
		rnr|rivalnonrival - Calculate rival-nonrival visit metrics\n\
		rnr-dist|rivalnonrival-dist - Calculate rival-nonrival visit metrics using distance norm')
	parser.add_argument('-o', '--out', nargs='*', help='\
		rnr|rivalnonrival - Generate output for rival-nonrival metrics\n\
		rnr-dist|rivalnonrival-dist - Generate output for rival-nonrival metrics using distance norm')

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

	if args.see:
		import bin.see_fun as do
		if 'gang-tw' in args.see:
			print '\n*** See each gang\'s tweet count ***\n'
			do.see_gang_tweet_counts()
		if 'test' in args.see:
			print '\n*** Test, Test. Test! ***\n'
			do.test()
