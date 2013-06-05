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

# Log screen output
class Logger(object):
  def __init__(self, filename="Default.log"):
      self.terminal = sys.stdout
      self.log = open(filename, "a")
  def write(self, message):
      self.terminal.write(message)
      self.log.write(message)
if not os.path.exists('data/' + my.DATA_FOLDER):
		os.makedirs('data/' + my.DATA_FOLDER)
sys.stdout = Logger('data/' + my.DATA_FOLDER + 'log.txt')


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-g', '--get', nargs='*', help='\
		users - Get user_id for users with min_tweet tweets\n\
		night - Get night latlng for users with min_tweet tweets\n\
		all - Get all latlng for users who\'s homes were found \n\
		all-no-dj - Get all latlng for users, NO DJANGO')
	parser.add_argument('-f', '--find', nargs='*', help='\
		home - Finding homes for users (scikit-learn.cluster.DBSCAN)\n\
		trim - Trim list of user home latlng inside polygon\n\
		disp - Find daily max displacement for users\n\
		charts - Plot charts for daily max displacement')
	args = parser.parse_args()
	#print args

	if args.get:
		import bin.get_fun as do
		if 'users' in args.get:
			print '\n*** Get user_id for users with min_tweet tweets ***\n'
			do.get_min_tweet_users()
		if 'night' in args.get:
			print '\n*** Get night latlng for users with min_tweet tweets ***\n'
			do.get_user_latlng(my.FILE_MIN_TWEET_USERS, my.FOLDER_USER_NIGHT_DATA, True)
			#	Too many open file pointers error:
			#		sudo su
			#		ulimit -n 2048
		if 'all' in args.get:
			print '\n*** Get all latlng for users who\'s homes were found ***\n'
			do.get_user_latlng(my.FILE_USER_HOMES_TRIMMED, my.FOLDER_USER_DATA, None, True, True)
		if 'all-no-dj' in args.get:
			print '\n*** Get all latlng for users, NO DJANGO ***\n'
			do.get_user_latlng_no_dj(my.FILE_USER_HOMES_TRIMMED, my.FOLDER_USER_DATA, None, True, True)

	if args.find:
		import bin.find_fun as do
		if 'home' in args.find:
			print '\n*** Finding homes for users (scikit-learn.cluster.DBSCAN) ***\n'
			do.find_user_homes()
		if 'trim' in args.find:
			print '\n*** Trim list of user home latlng inside polygon ***\n'
			do.trim_user_homes(my.LOC_POL)
		if 'disp' in args.find:
			print '\n*** Find daily max displacement for users ***\n'
			do.find_daily_disp()
		if 'charts' in args.find:
			print '\n*** Plot charts for daily max displacement ***\n'
			do.generate_disp_plots()


