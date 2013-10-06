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
	parser.add_argument('-m', '--map', nargs='*')
	parser.add_argument('-t', '--time', nargs='*')
	parser.add_argument('-g', '--gram', nargs='*')
	parser.add_argument('-v', '--vw', nargs='*')
	parser.add_argument('-l', '--lda', nargs='*')
	parser.add_argument('-w', '--waj', nargs='*')
	parser.add_argument('-p', '--player', nargs='*')
	args = parser.parse_args()
	
	if args.map:
		import src.map as m
		if 'all' in args.map:
			m.plot_on_map()
	
	if args.time:
		import src.time as t
		if 'get' in args.time:
			t.get_timeline()
		if 'plot' in args.time:
			t.plot_timeline()
		if 'filler' in args.time:
			t.get_filler_ids()

	if args.gram:
		import src.n_grams as gram
		if 'vocab' in args.gram:
			gram.get_vocab()
		if 'vocab-nba' in args.gram:
			gram.add_nba_vocab()
		"""if 'combi' in args.gram:
			gram.make_combinations()"""
		if 'freq' in args.gram:
			gram.find_freq_sets()
		if 'trim' in args.gram:
			gram.trim_freq_sets()
		if 'group' in args.gram:
			gram.group_by_len()
		if 'tex' in args.gram:
			gram.group_to_tex()
		if 'time' in args.gram:
			gram.find_timestamps()

		if 'phrase' in args.gram:
			gram.plot_phrases()
		if 'len' in args.gram:
			gram.plot_phrase_lengths()
		
	if args.vw:
		import src.vw as vw
		if 'prep' in args.vw:
			vw.prep_input()
		if 'prep-from' in args.vw:
			vw.prep_input_from_lda()
		if 'lda' in args.vw:
			vw.run_lda()
		if 'vocab' in args.vw:
			vw.text_vocab()

	if args.lda:
		import src.lda as lda
		if 'prep' in args.lda:
			lda.prep_input()
		if 'lda' in args.lda:
			lda.run_lda()
		if 'topics' in args.lda:
			lda.print_topics()
		if 'cloud' in args.lda:
			lda.make_topics()

	if args.waj:
		import src.wajyahoonba as waj
		if 'get' in args.waj:
			waj.get_tweets()
		if 'show' in args.waj:
			waj.show_ts()
		if 'plot' in args.waj:
			waj.plot_time()

	if args.player:
		import src.player as pl
		if 'top' in args.player:
			pl.get_top_players()
		if 'top-plot' in args.player:
			pl.plot_top_players()
		if 'players' in args.player:
			pl.get_player_times()
		if 'picks' in args.player:
			pl.get_pick_times()
		if 'pplot' in args.player:
			pl.plot_players()
		if 'non-picks' in args.player:
			pl.plot_non_picks()
		if 'entropy' in args.player:
			pl.plot_entropies()
		if 'range' in args.player:
			pl.plot_ranges()
		if 'tex' in args.player:
			pl.make_img_tex()

	print '\n\nCOMPLETED IN', round(time.time() - start_time, 3), 'SECONDS.\n'

