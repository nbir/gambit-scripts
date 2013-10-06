# Gambit scripts
#
# Copyright (C) USC Information Sciences Institute
# Author: Nibir Bora <nbora@usc.edu>
# URL: <http://cbg.isi.edu/>
# For license information, see LICENSE

import os
import sys
import argparse

import settings as my

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-d', '--db', nargs='*')
	parser.add_argument('-f', '--find', nargs='*')
	parser.add_argument('-c', '--calc', nargs='*')
	parser.add_argument('-p', '--prep', nargs='*')
	parser.add_argument('-t', '--test', nargs='*')
	args = parser.parse_args()

	if args.prep:
		import src.prep as prep
		if 'parse' in args.prep:
			prep.parse_kml()
		if 'names' in args.prep:
			prep.show_names()
		if 'riv' in args.prep:
			prep.in_rivalries()
		if 'riv-mat' in args.prep:
			prep.out_rivalry_mat()

		if 'create-hood' in args.prep:
			print '\n*** Creating nhood relation in database ***\n'
			prep.create_hood_db()
		if 'store-hood' in args.prep:
			print '\n*** Pushing all nhood data to database ***\n'
			prep.store_hoods_db()
		
		if 'base-riv' in args.prep:
			prep.calc_baseline_riv()		




