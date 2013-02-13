# Gambit scripts
#
# Copyright (C) USC Information Sciences Institute
# Author: Nibir Bora <nbora@usc.edu>
# URL: <http://cbg.isi.edu/>
# For license information, see LICENSE


import sys
#import bin.gangVsLA as do
import bin.rivalNonrival as do
import settings as my

if '-get' in sys.argv:
	print '----- GETTING TWEETS INSIDE BOUNDS -----\n'
	do.get_tweets_in()

if '-trim' in sys.argv:
	print '----- TRIMMING HOME CLUSTERS IN DATA -----\n'
	do.trim_home_clusters()

if '-calc' in sys.argv:
	print '----- CALCULATING METRICS -----\n'
	do.calc_matrics()

if '-out' in sys.argv:
	print '----- GENERATE OUTPUT FILES -----\n'
	do.generate_output()



if '-test' in sys.argv:
	print '----- TEST, TEST, TEST! -----\n'
	do.test()