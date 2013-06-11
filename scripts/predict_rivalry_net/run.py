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
	parser.add_argument('-c', '--calc', nargs='*')
	parser.add_argument('-p', '--plot', nargs='*')
	parser.add_argument('-t', '--test', nargs='*')
	args = parser.parse_args()
	
	if args.calc:
		import src.predict_rivalry as predict
		if 'predict' in args.calc:
			print '\n*** Predict rivalry network ***\n'
			predict.predict_rivalry('activity/', 'activity_mat')

	if args.plot:
		import src.predict_rivalry as plot
		if 'net' in args.plot:
			print '\n*** Plot rivalry network ***\n'
			plot.plot_rivalry('activity/', 'activity_mat')
