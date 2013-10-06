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
	parser.add_argument('-s', '--sets', nargs='*')
	parser.add_argument('-d', '--data', nargs='*')
	parser.add_argument('-f', '--freq', nargs='*')
	parser.add_argument('-e', '--entropy', nargs='*')
	parser.add_argument('-c', '--clean', nargs='*')
	parser.add_argument('-p', '--prepick', nargs='*')
	args = parser.parse_args()
	
	if args.sets:
		import src.sets as s
		if 'teams' in args.sets:
			s.make_team_sets()
		if 'player' in args.sets:
			s.make_player_sets()
		if 'picks' in args.sets:
			s.make_picks_sets()

	if args.data:
		import src.data as d
		if 'get' in args.data:
			d.get_data()
		if 'all' in args.data:
			d.get_all_data()
		if 'picks' in args.data:
			d.make_pick_data()
		if 'influ' in args.data:
			d.plot_influential()

	if args.freq:
		import src.freq as f
		if 'phrase' in args.freq:
			f.find_freq_phrases()
		if 'timeline' in args.freq:
			f.plot_timelines()
		if 'top' in args.freq:
			f.plot_freq_bar()

	if args.entropy:
		import src.entropy as e
		if 'vol-mat' in args.entropy:
			e.make_volume_mat()
		if 'plot' in args.entropy:
			e.plot_volume_entropy()
		if 'rng-ent' in args.entropy:
			e.find_entropy_range()

	if args.clean:
		import src.clean as c
		if 'peak' in args.clean:
			c.plot_smooth_peak()

	if args.prepick:
		import src.prepick as p
		if 'top' in args.prepick:
			p.plot_top_players()
	

	print '\n\nCOMPLETED IN', round(time.time() - start_time, 3), 'SECONDS.\n'

