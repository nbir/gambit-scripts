# Gambit scripts
#
# Copyright (C) USC Information Sciences Institute
# Author: Nibir Bora <nbora@usc.edu>
# URL: <http://cbg.isi.edu/>
# For license information, see LICENSE



# Folders
#DATA_FOLDER = 'hbk/'
#DATA_FOLDER = 'south-la/'
#DATA_FOLDER = 'west-la/'
#DATA_FOLDER = 'south-bay/'
#DATA_FOLDER = 'hbk_old/'
#DATA_FOLDER = 'hbk_old2/'
#DATA_FOLDER = 'blood_crip/'


# Relations
REL_TWEET 	= 't3_tweet_6'
REL_HOME 	= 't4_home'
#REL_HOME 	= 'hbk_home'
#REL_HOME 	= 'hbk_home2'
REL_NHOOD 	= 't4_nhood'
#REL_NHOOD 	= 'nh_blood_crip'

# Multi processing
PROCESSES 	= 12

# Params
TIMEZONE 	= 'America/Los_Angeles'
TZ_OFFSET	= -8
HH_START 	= 19	# 24 hour format
HH_END 		= 4
QUERY_CONSTRAINT = "AND (timestamp < '2012-12-15 00:00:00' OR timestamp > '2013-01-10 00:00:00')"
MIN_NIGHT_TW	= 50
MAX_NIGHT_TW	= 5000
MIN_FRAC_INSIDE = 0.5

# DB
DB_CONN_STRING = "host='76.170.75.150' dbname='twitter' user='twitter' password='flat2#tw1tter'"

