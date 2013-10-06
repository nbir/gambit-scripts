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
	parser.add_argument('-p', '--plot', nargs='*')
	args = parser.parse_args()

	if args.plot:
		import src.plot_activity_map as plot
		if 'map' in args.plot:
			print '\n*** Plot displacement for all users in region on map ***\n'
			plot.plot_activity_on_map()

		if 'la' in args.plot:
			print '\n*** Plot map of LA ***\n'
			plot.plot_la_map()


