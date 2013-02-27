# Gambit scripts
#
# Copyright (C) USC Information Sciences Institute
# Author: Nibir Bora <nbora@usc.edu>
# URL: <http://cbg.isi.edu/>
# For license information, see LICENSE


import os
import sys
import argparse

from settings import CURRENT_SETTINGS as my

# Log screen output
class Logger(object):
  def __init__(self, filename="Default.log"):
      self.terminal = sys.stdout
      self.log = open(filename, "a")
  def write(self, message):
      self.terminal.write(message)
      self.log.write(message)
if not os.path.exists('data/' + my['sub_folder']):
		os.makedirs('data/' + my['sub_folder'])
sys.stdout = Logger('data/' + my['sub_folder'] + 'log.txt')


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-g', '--get', nargs='*', help='\
		users - Get user_id for users with min_tweet tweets\n\
		night - Get night latlng for users with min_tweet tweets\n\
		all - Get all latlng for users who\'s homes were found')
	parser.add_argument('-f', '--find', nargs='*', help='\
		home - Finding homes for users (scikit-learn.cluster.DBSCAN)\n\
		trim - Trim list of user home latlng inside polygon')
	args = parser.parse_args()
	#print args

	if args.get:
		import bin.get_fun as do
		if 'users' in args.get:
			print '\n*** Get user_id for users with min_tweet tweets ***\n'
			do.get_min_tweet_users()
		if 'night' in args.get:
			print '\n*** Get night latlng for users with min_tweet tweets ***\n'
			do.get_user_latlng(my['files']['users_min_tweet'], my['folders']['user_night_data'], True)
			#	Too many open file pointers error:
			#		sudo su
			#		ulimit -n 2048
		if 'all' in args.get:
			print '\n*** Get all latlng for users who\'s homes were found ***\n'
			do.get_user_latlng(my['files']['user_home_loc_trimmed'], my['folders']['user_all_data'], None, True)

	if args.find:
		import bin.find_fun as do
		if 'home' in args.find:
			print '\n*** Finding homes for users (scikit-learn.cluster.DBSCAN) ***\n'
			do.find_user_homes()
		if 'trim' in args.find:
			print '\n*** Trim list of user home latlng inside polygon ***\n'
			do.trim_user_homes(my['loc_pol'])