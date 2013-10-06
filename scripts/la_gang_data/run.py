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
		import src.prep_crips_bloods as bc
		if 'kml' in args.prep:
			prep.shp_to_kml()
		if 'geoJSON' in args.prep or 'geojson' in args.prep:
			prep.kml_to_geoJSON()
		if 'combine' in args.prep:
			prep.combine_json()

		if 'parse' in args.prep:
			bc.parse_kml()
		




