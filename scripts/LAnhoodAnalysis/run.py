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
	parser.add_argument('-o', '--out', nargs='*')
	parser.add_argument('-t', '--test', nargs='*')
	args = parser.parse_args()

	if args.db:
		import src.db as db
		if 'create-hood' in args.db:
			print '\n*** Creating nhood relation in database ***\n'
			db.create_hood_db()
		if 'store-hood' in args.db:
			print '\n*** Pushing all nhood data to database ***\n'
			db.store_hoods_db()
		if 'check' in args.db:
			print '\n*** Checking all nhood data in database ***\n'
			db.check_hoods_db()
		if 'create-home' in args.db:
			print '\n*** Creating home relation in database ***\n'
			db.create_home_db()

		if 'hbk-homes' in args.db:
			print '\n*** Pushing all HBK homes to database ***\n'
			db.store_hbk_homes_db()
		if 'hbk-hoods' in args.db:
			print '\n*** Pushing HBK nhood data to database ***\n'
			db.store_hbk_hoods_db()

	if args.find:
		import src.find_disp as find
		if 'disp' in args.find:
			print '\n*** Find daily max displacement for each users ***\n'
			find.find_daily_disp()
		if 'disp-super' in args.find:
			print '\n*** Plot displacement from home for all users in region ***\n'
			find.plot_super_disp_plot()
		if 'disp-join' in args.find:
			print '\n*** Join max displacement for all users into one file ***\n'
			find.join_daily_disp()

		import src.disp_stat as stat
		if 'disp-plot' in args.find:
			print '\n*** Plot charts for daily max displacement ***\n'
			stat.out_user_disp_plot()
		if 'wed-plot' in args.find:
			print '\n*** Plot charts for daily max displacement (Weekday/Weekend) ***\n'
			stat.out_user_disp_plot_weekday()
		if 'disp-plot-all' in args.find:
			import src.disp_combined as out1
			print '\n*** Plot Power Law fits for regions on single plot ***\n'
			out1.out_disp_combined()

		if 'dir-pdf' in args.find:
			import src.direction_pdf as out1
			print '\n*** Generating direction PDF for region ***\n'
			out1.out_dir_pdf()

	if args.calc:
		import src.calc as calc
		pass

	if args.out:
		import src.out as out
		if 'region' in args.out:
			print '\n*** Output: JSON of all homes and latlng in region ***\n'
			out.out_homes_and_points_json()
		if 'nhood-pts' in args.out:
			print '\n*** Output: JSON of latlng by users of each nhood in region ***\n'
			out.out_hoodwise_latlng_json()	


		if 'disp-map' in args.out:
			print '\n*** Plot displacement for all users in region on map ***\n'
			out.out_disp_map()

	if args.test:
		import src.test as test
		if 'test' in args.test:
			print '\n*** Test; Test, test! ***\n'
			test.test()
		if 'home' in args.test:
			print '\n*** Test: home. ***\n'
			test.test_home()




