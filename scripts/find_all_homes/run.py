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
	parser.add_argument('-d', '--db', nargs='*')
	parser.add_argument('-f', '--find', nargs='*')
	parser.add_argument('-o', '--out', nargs='*')
	args = parser.parse_args()

	if args.db:
		import src.find_all_homes as db
		if 'table' in args.db or 'rel' in args.db:
			print '\n*** Creating home relation in database ***\n'
			db.create_home_db()
		
	if args.find:
		import src.find_all_homes as find
		if 'users' in args.find:
			print '\n*** Get user_id for users with min_tweet tweets ***\n'
			find.get_min_tweet_users()
		if 'home' in args.find:
			print '\n*** Finding homes for users (scikit-learn.cluster.DBSCAN) ***\n'
			find.find_user_homes()

	if args.out:
		import src.find_all_homes as out
		if 'json' in args.out:
			print '\n*** Output: JSON of all identified user homes ***\n'
			out.out_all_homes_json()
