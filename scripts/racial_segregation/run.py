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
	parser.add_argument('-c', '--calc', nargs='*')
	parser.add_argument('-d', '--data', nargs='*')
	parser.add_argument('-v', '--visits', nargs='*')
	parser.add_argument('-m', '--map', nargs='*')
	parser.add_argument('-a', '--artificial', nargs='*')
	args = parser.parse_args()

	if args.calc:
		import src.calc_visits as calc
		if 'test' in args.calc:
			calc.test()

		if 'user-race' in args.calc:
			calc.find_user_race()
		if 'visits' in args.calc:
			calc.calc_user_visits()
		if 'get-pt' in args.calc:
			calc.get_race_points()

		if 'plot-visits' in args.calc:
			calc.plot_visits_map()
		if 'plot-gen' in args.calc:
			calc.plot_general_map()
		if 'plot-pie' in args.calc:
			calc.plot_race_pies()

		if 'get-dist' in args.calc:
			calc.get_distance()
		if 'plot-disp' in args.calc:
			calc.plot_disp()
		if 'visits-dn' in args.calc:
			calc.calc_user_visits_dist_norm()
		if 'plot-pie-dn' in args.calc:
			calc.plot_race_pies_dn()

	if args.data:
		import src.data as d
		if 'pop' in args.data:
			d.get_tract_population()
		if 'race' in args.data:
			d.find_tract_race()
		if 'pol' in args.data:
			d.get_tract_polygon()
		if 'city' in args.data:
			d.get_city_tracts()
		if 'area' in args.data:
			d.find_tract_areas()
		if 'center' in args.data:
			d.find_tract_centers()

		if 'users' in args.data:
			d.find_tracts_with_users()
		if 'stat' in args.data:
			d.data_stat()
		if 'check' in args.data:
			d.check_data()

		if 'tweet' in args.data:
			d.get_tweets()
		if 'all-tweet' in args.data:
			d.make_all_tweets()
		if 'split' in args.data:
			d.split_tweet_file()
		if 'tweet-count' in args.data:
			d.make_tweet_count()
		if 'check-count' in args.data:
			d.check_tweet_counts()

		if 'plot-user' in args.data:
			d.plot_each_user()
		if 'plot-video' in args.data:
			d.make_disp_video()

	if args.visits:
		import src.visits as v
		if 'grid' in args.visits:
			v.make_grid()
		if 'lookup' in args.visits:
			v.make_grid_lookup()
		if 'plot-lookup' in args.visits:
			v.plot_grid_lookup()
		if 'visits' in args.visits:
			v.calc_visit_mat()

		if 'race' in args.visits:
			v.find_race_visits()

	if args.map:
		import src.map as m
		if 'plot' in args.map:
			m.plot_map()
		if 'homes' in args.map:
			m.plot_map_with_homes()
		if 'tweets' in args.map:
			m.plot_map_with_tweets()
		if 'race' in args.map:
			m.plot_race_map()

	if args.artificial:
		import src.artificial as a
		if 'grid' in args.artificial:
			a.make_grid()
		if 'plot' in args.artificial:
			a.plot_sample_space()
		if 'points' in args.artificial:
			a.plot_sample_points()
		
		if 'index' in args.artificial:
			a.make_artificial_index()
		if 'tweet' in args.artificial:
			a.make_artificial_tweets()
		if 'split' in args.artificial:
			a.split_tweet_file()
