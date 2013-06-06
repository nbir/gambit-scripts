# Gambit scripts
#
# Copyright (C) USC Information Sciences Institute
# Author: Nibir Bora <nbora@usc.edu>
# URL: <http://cbg.isi.edu/>
# For license information, see LICENSE



# Folders
#DATA_FOLDER = 'all-hoods/'
#DATA_FOLDER = 'regions/'
#DATA_FOLDER = 'hbk/'

DATA_FOLDER = 'south-la/'
#DATA_FOLDER = 'west-la/'
#DATA_FOLDER = 'south-bay/'

#DATA_FOLDER = 'pomona/'
#DATA_FOLDER = 'bernardino/'
#DATA_FOLDER = 'riverside/'


# Relations
REL_TWEET 	= 't3_tweet_6'
REL_HOME 	= 't4_home'
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

# Plot settings
PLOT_LABEL_ABS = True
