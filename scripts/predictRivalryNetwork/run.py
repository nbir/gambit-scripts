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
	parser.add_argument('-p', '--prep', nargs='*', help='\
		[trim-visit-mat - Trim visit matrix for min tweet bound] \n\
		[make-feat-mat - Build feature matrix] ')
	parser.add_argument('-c', '--calc', nargs='*', help='\
		[cluster - Apply Cluster analysis] ')
	parser.add_argument('-o', '--out', nargs='*', help='\
		')

	parser.add_argument('-s', '--see', nargs='*', help='\
		test - Call test function')
	args = parser.parse_args()

	if args.prep:
		import src.prep_fun as do
		if 'trim-visit-mat' in args.prep:
			print '\n*** Trim visit matrix for min tweet bound ***\n'
			do.trim_visit_mat()
		if 'make-feat-mat' in args.prep:
			print '\n*** Build feature matrix ***\n'
			do.make_feature_mat()
	
	if args.calc:
		import src.clust_fun as clust
		if 'cluster' in args.calc:
			print '\n*** Apply Cluster analysis ***\n'
			clust.cluster_all()

	if args.see:
		import src.see_fun as do
		if 'test' in args.see:
			print '\n*** Test, Test. Test! ***\n'
			do.test()
