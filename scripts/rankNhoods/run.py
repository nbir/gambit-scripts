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
	parser.add_argument('-d', '--do', nargs='*')
	args = parser.parse_args()

	# Append forward slash
	#folder = folder+'/' if folder[-1:] != '/' else folder
	
	if args.do:
		import src.rankNhoods as do

		if 'rank' in args.do:
			print '\n*** Calc & Plot ***\n'
			do.calc_featAndPlot(folder='visits', file_name='visit_mat')
			do.calc_featAndPlot(folder='visitors', file_name='visitor_mat')




