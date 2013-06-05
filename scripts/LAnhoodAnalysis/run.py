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
	parser.add_argument('-c', '--calc', nargs='*')
	parser.add_argument('-o', '--out', nargs='*')
	parser.add_argument('-t', '--test', nargs='*')
	args = parser.parse_args()

	# Append forward slash
	#folder = folder+'/' if folder[-1:] != '/' else folder
	
	if args.db:
		import src.db as db
		if 'create-hood' in args.db:
			print '\n*** Creating nhood relation in database ***\n'
			db.create_hood_db()
		if 'create-home' in args.db:
			print '\n*** Creating home relation in database ***\n'
			db.create_home_db()
		if 'store' in args.db:
			print '\n*** Pushing all nhood data to database ***\n'
			db.store_hoods_db()
		if 'check' in args.db:
			print '\n*** Checking all nhood data in database ***\n'
			db.check_hoods_db()

		if 'hbk-homes' in args.db:
			print '\n*** Pushing all HBK homes to database ***\n'
			db.store_hbk_homes_db()
		if 'hbk-hoods' in args.db:
			print '\n*** Pushing HBK nhood data to database ***\n'
			db.store_hbk_hoods_db()

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
		if 'disp' in args.find:
			print '\n*** Find daily max displacement for each users ***\n'
			find.find_daily_disp()
		if 'disp-join' in args.find:
			print '\n*** Join max displacement for all users into one file ***\n'
			find.join_daily_disp()

	if args.calc:
		import src.calc_visits as calc
		if 'activity' in args.calc:
			print '\n*** Calculating activity between nhoods ***\n'
			calc.calc_activity()
		if 'visits' in args.calc:
			print '\n*** Calculating visits between nhoods ***\n'
			calc.calc_visits()
		if 'visitors' in args.calc:
			print '\n*** Calculating visitors between nhoods ***\n'
			calc.calc_visitors()
		if 'visit-mat' in args.calc:
			print '\n*** Saving visit matrices to JSON ***\n'
			calc.save_visitMatJSONs()

	if args.out:
		import src.out as out
		if 'home' in args.out:
			print '\n*** Output: JSON of all identified user homes ***\n'
			out.out_all_homes_json()
		if 'region' in args.out:
			print '\n*** Output: JSON of all homes and latlng in region ***\n'
			out.out_region_homes_latlng_json()
		if 'region-ids' in args.out:
			print '\n*** Output: JSON of all homes and latlng in region ***\n'
			out.out_region_homes_latlng_json(False)
		if 'nhood-pts' in args.out:
			print '\n*** Output: JSON of latlng by users of each nhood in region ***\n'
			out.out_nhood_latlng_json()

		if 'disp-plot' in args.out:
			print '\n*** Plot charts for daily max displacement ***\n'
			out.out_user_disp_plot()
		if 'wed-plot' in args.out:
			print '\n*** Plot charts for daily max displacement (Weekday/Weekend) ***\n'
			out.out_user_disp_plot_weekday()
		if 'disp-super' in args.out:
			print '\n*** Plot displacement from home for all users in region ***\n'
			out.out_super_disp_plot()

		if 'disp-map' in args.out:
			print '\n*** Plot displacement for all users in region on map ***\n'
			out.out_disp_map()
		if 'disp-map-pdf' in args.out:
			print '\n*** Plot displacement for all users in region on map (PDF) ***\n'
			out.out_disp_map_pdf()

		# Misc. scripts
		if 'disp-plot-all' in args.out:
			import src.dispFromHomeAll as out1
			print '\n*** Plot Power Law fits for regions on single plot ***\n'
			out1.out_dispFromHomeAll()
		if 'dir-pdf' in args.out:
			import src.directionPDF as out1
			print '\n*** Generating direction PDF for region ***\n'
			out1.out_dirPDF()

	if args.test:
		import src.test as test
		if 'test' in args.test:
			print '\n*** Test; Test, test! ***\n'
			test.test()
		if 'home' in args.test:
			print '\n*** Test: home. ***\n'
			test.test_home()




