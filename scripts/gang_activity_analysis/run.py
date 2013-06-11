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
	parser.add_argument('-g', '--get', nargs='*')
	parser.add_argument('-p', '--prep', nargs='*')
	parser.add_argument('-c', '--calc', nargs='*')
	parser.add_argument('-o', '--out', nargs='*')
	parser.add_argument('-s', '--see', nargs='*')
	args = parser.parse_args()

	if args.calc:
		import src.calc_rnr_visits as calc
		if 'rnr' in args.calc:
			print '\n*** Calculate rival non-rival visit sets ***\n'
			calc.calc_rnr_visits()

	if args.out:
		import src.out as out
		if 'rivalry' in args.out:
			print '\n*** Save rivalry matrix in json format ***\n'
			out.out_rivalry_mat()