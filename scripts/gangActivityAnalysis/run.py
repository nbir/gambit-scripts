# Gambit scripts
#
# Copyright (C) USC Information Sciences Institute
# Author: Nibir Bora <nbora@usc.edu>
# URL: <http://cbg.isi.edu/>
# For license information, see LICENSE


import sys
import bin.do
import settings as my

if '-get' in sys.argv:
	print '----- GETTING TWEETS INSIDE BOUNDS -----\n'
	bin.do.get_tweets_in()

if '-trim' in sys.argv:
	print '----- TRIMMING HOME CLUSTERS IN DATA -----\n'
	bin.do.trim_home_clusters()

if '-count' in sys.argv:
	print '----- CALCULATING METRICS -----\n'
	bin.do.calc_gang_vs_la_tweeting_pattern()

if '-csv' in sys.argv:
	print '----- GENERATE FRACTIONS GANG vs LA CSV -----\n'
	bin.do.generate_frac_csv()