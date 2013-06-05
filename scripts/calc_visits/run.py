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
	parser.add_argument('-c', '--calc', nargs='*')
	args = parser.parse_args()

	if args.calc:
		import src.calc_visits as calc
		if 'activity' in args.calc:
			print '\n*** Calculating activity between nhoods ***\n'
			calc.calc_activity()
		if 'visits' in args.calc:
			print '\n*** Calculating visits between nhoods ***\n'
			calc.calc_visits()
		if 'visitors' in args.calc:
			print '\n*** Calculating visitors between nhoods ***\n'
			calc.calc_visitors()


