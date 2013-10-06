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
			predict.predict_rivalry('activity/', 'activity_mat__dtf_norm')
			predict.predict_rivalry('activity/', 'activity_mat__dist_norm')

			predict.predict_rivalry('visits/', 'visit_mat')
			predict.predict_rivalry('visits/', 'visit_mat__dtf_norm')
			predict.predict_rivalry('visits/', 'visit_mat__dist_norm')

			predict.predict_rivalry('visitors/', 'visitor_mat')

		if 'plot-feat' in args.calc:
			predict.plot_features('activity/', 'activity_mat')

	if args.plot:
		import src.plot as plot
		if 'net' in args.plot:
			print '\n*** Plot rivalry network ***\n'
			plot.plot_rivalry('activity/', 'activity_mat')
			plot.plot_rivalry('activity/', 'activity_mat__dtf_norm')
			plot.plot_rivalry('activity/', 'activity_mat__dist_norm')

			plot.plot_rivalry('visits/', 'visit_mat')
			plot.plot_rivalry('visits/', 'visit_mat__dtf_norm')
			plot.plot_rivalry('visits/', 'visit_mat__dist_norm')

			plot.plot_rivalry('visitors/', 'visitor_mat')
