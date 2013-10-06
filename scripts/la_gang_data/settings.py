# Gambit scripts
#
# Copyright (C) USC Information Sciences Institute
# Author: Nibir Bora <nbora@usc.edu>
# URL: <http://cbg.isi.edu/>
# For license information, see LICENSE



# Folders
#DATA_FOLDER = 'lapd/'
DATA_FOLDER = 'bloods_crips/'

# Relations
#REL_TWEET 	= 't3_tweet_6'
REL_TWEET 	= 't2_tweet'
REL_HOME 	= 't4_home'
#REL_HOME 	= 'hbk_home'
#REL_HOME 	= 'hbk_home2'
REL_NHOOD 	= 't4_nhood'

# Multi processing
PROCESSES 	= 12

# Params
TIMEZONE 	= 'America/Los_Angeles'
TZ_OFFSET	= -8
HH_START 	= 19	# 24 hour format
HH_END 		= 4
QUERY_CONSTRAINT = "AND (timestamp < '2012-12-15 00:00:00' OR timestamp > '2013-01-10 00:00:00')"
MIN_NIGHT_TW	=	50
MAX_NIGHT_TW	=	5000
MIN_FRAC_INSIDE = 0.5

MAX_TW_TO_CLUSTER 	= 500
DBSCAN_EPS 			= 0.003
DBSCAN_MIN 			= 30

USER_IDS_FROM_DB = True
USER_IDS_FROM_DB = False if DATA_FOLDER == 'hbk/' else True

# DB
DB_CONN_STRING = "host='76.170.75.150' dbname='twitter' user='twitter' password='flat2#tw1tter'"
#DB_CONN_STRING = "host='brain.isi.edu' dbname='twitter' user='twitter' password='flat2#tw1tter'"

# Plot settings
PLOT_LABEL_ABS = True


MIN_DIR_DIST = 500

COLORS = {'hbk': '#377EB8',
		'hbk_old': '#377EB8',
		'hbk_old2': '#377EB8',
		'south-la' : '#FA71AF',
		'west-la' : '#4DAF4A',
		'south-bay' : '#A65628',
		'pomona' : '#3B3B3B',
		'bernardino' : '#984EA3',
		'riverside' : '#FF7F00'}