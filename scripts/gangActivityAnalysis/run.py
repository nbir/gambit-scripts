# Gambit scripts
#
# Copyright (C) USC Information Sciences Institute
# Author: Nibir Bora <nbora@usc.edu>
# URL: <http://cbg.isi.edu/>
# For license information, see LICENSE


import sys
import bin.do

if '7' in sys.argv:
	print '----- CALCULATE TWEET FREQ. IN RIVAL AND HOME TERRITORY -----\n'
	bin.do.calc_tweet_freq_in_rival_home()

if '8' in sys.argv:
	print '----- GENERATE FRACTIONS GANG vs LA CSV -----\n'
	bin.do.generate_frac_csv()