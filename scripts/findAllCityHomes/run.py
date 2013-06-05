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
	#parser.add_argument('folder', nargs='?', default='all-hoods')
	parser.add_argument('-d', '--db', nargs='*')
	parser.add_argument('-g', '--get', nargs='*')
	parser.add_argument('-f', '--find', nargs='*')
	parser.add_argument('-o', '--out', nargs='*')
	parser.add_argument('-t', '--test', nargs='*')
	args = parser.parse_args()

	# Append forward slash
	#folder = folder+'/' if folder[-1:] != '/' else folder
	
	if args.db:
		import src.db as db
		if 'create-home' in args.db:
			print '\n*** Creating home relation in database ***\n'
			db.create_home_db()
		
	if args.get:
		import src.get as get
		if 'users' in args.get:
			print '\n*** Get user_id for users with min_tweet tweets ***\n'
			get.get_min_tweet_users()

	if args.find:
		import src.find as find
		if 'home' in args.find:
			print '\n*** Finding homes for users (scikit-learn.cluster.DBSCAN) ***\n'
			find.find_user_homes()

	if args.out:
		import src.out as out
		if 'home' in args.out:
			print '\n*** Output: JSON of all identified user homes ***\n'
			out.out_all_homes_json()
