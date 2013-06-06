# Gambit scripts
#
# Copyright (C) USC Information Sciences Institute
# Author: Nibir Bora <nbora@usc.edu>
# URL: <http://cbg.isi.edu/>
# For license information, see LICENSE



# Folders
#DATA_FOLDER = 'LA/'
#DATA_FOLDER = 'LA2/'
DATA_FOLDER = 'LA3/'
#DATA_FOLDER = '/'

# Relations
#REL_HOME 	= 'la_home'
#REL_HOME 	= 'la2_home'
REL_HOME 	= 'la3_home'
REL_TWEET 	= 't3_tweet_6'
#REL_HOME 	= 't4_home'
REL_NHOOD 	= 't4_nhood'

# Multi processing
PROCESSES 	= 12

# Night time query parameters
TIMEZONE 	= 'America/Los_Angeles'
TZ_OFFSET	= -8
HH_START 	= 19	# 24 hour format
HH_END 		= 4
QUERY_CONSTRAINT = "AND (timestamp < '2012-12-15 00:00:00' OR timestamp > '2013-01-10 00:00:00')"

MIN_NIGHT_TW	=	50
MAX_NIGHT_TW	=	5000


# Clustering parameters
MAX_TW_TO_CLUSTER = 500
DBSCAN_EPS = 0.003
DBSCAN_MIN_FRAC = 0.20
DBSCAN_MIN_ABS = 15


# DB
DB_CONN_STRING = "host='76.170.75.150' dbname='twitter' user='twitter' password='flat2#tw1tter'"


