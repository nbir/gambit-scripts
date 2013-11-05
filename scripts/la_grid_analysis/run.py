# Gambit scripts
#
# Copyright (C) USC Information Sciences Institute
# Author: Nibir Bora <nbora@usc.edu>
# URL: <http://cbg.isi.edu/>
# For license information, see LICENSE


import os
import sys
import time
import argparse


if __name__ == '__main__':
	start_time = time.time()

	parser = argparse.ArgumentParser()
	parser.add_argument('-m', '--map', nargs='*')
	parser.add_argument('-d', '--data', nargs='*')
	parser.add_argument('-c', '--cluster', nargs='*')
	parser.add_argument('-k', '--kld', nargs='*')
	args = parser.parse_args()
	
	if args.map:
		import src.map as m
		if 'grid' in args.map:
			m.plot_grid()

	if args.data:
		import src.data as d
		if 'get' in args.data:
			d.get_data()

	if args.cluster:
		import src.cluster as c
		if 'make' in args.cluster:
			c.male_X()
		if 'cluster' in args.cluster:
			c.run_cluster()
		if 'predict' in args.cluster:
			c.predict()

		if 'snorm' in args.cluster:
			c.spatial_norm()
		if 'dnorm' in args.cluster:
			c.dev_norm()

	if args.kld:
		import src.kld as k
		if 'make' in args.cluster:
			k.male_average()
		if 'cluster' in args.cluster:
			k.run_cluster()
		if 'predict' in args.cluster:
			k.predict()
	

	print '\n\nCOMPLETED IN', round(time.time() - start_time, 3), 'SECONDS.\n'

