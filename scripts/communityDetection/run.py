# Gambit scripts
#
# Copyright (C) USC Information Sciences Institute
# Author: Nibir Bora <nbora@usc.edu>
# URL: <http://cbg.isi.edu/>
# For license information, see LICENSE


import os
import sys
import argparse


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('fname', nargs='?', default='settings.py')
	parser.add_argument('-p', '--prep', nargs='*')
	parser.add_argument('-c', '--calc', nargs='*')
	parser.add_argument('-o', '--out', nargs='*')
	parser.add_argument('-s', '--see', nargs='*', help='\
		test - Call test function')
	args = parser.parse_args()

	print args.fname
	if args.prep:
		import src.prep as prep
		if 'read-tw' in args.prep:
			print '\n*** Reading tweet and making pickle ***\n'
			prep.read_tweets_pickle()
		if 'tw-count' in args.prep:
			print '\n*** Showing tweet count in pickle ***\n'
			prep.show_tweet_count()

	if args.calc:
		import src.calc as calc
		if 'interact' in args.calc:
			print '\n*** Calculating interactions ***\n'
			calc.calc_interactions()
		
	if args.see:
		import src.see_fun as do
		if 'test' in args.see:
			print '\n*** Test, Test. Test! ***\n'
			do.test()
