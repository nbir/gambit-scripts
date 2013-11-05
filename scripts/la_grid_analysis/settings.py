# Gambit scripts
#
# Copyright (C) USC Information Sciences Institute
# Author: Nibir Bora <nbora@usc.edu>
# URL: <http://cbg.isi.edu/>
# For license information, see LICENSE

#
# Folders
#
#DATA_FOLDER = 'lat.05_lng.05/'
#DATA_FOLDER = 'lat.025_lng.025/'
#DATA_FOLDER = 'lat.01_lng.01/'
#DATA_FOLDER = 'spatial-norm/'
DATA_FOLDER = 'deviation-norm/'


##################################################
#
# DB
#
DB_CONN_STRING = "host='brain.isi.edu' dbname='twitter' user='twitter' password='flat2#tw1tter'"

# Relations
REL_TWEET = 't3_tweet_6'


#
# Params
#
TIMEZONE = 'America/Los_Angeles'
TS_FORMAT = '%Y-%m-%d %H:%M:%S'
TS_ISO_FORMAT = '%Y-%m-%dT%H:%M:%S'


PROCESSES = 12 		# threads


##################################################
#
# Bbox Settings
#
BBOX = [33.500, -118.700, 34.400, -117.200]

#LAT_DELTA = 0.05; LNG_DELTA = 0.05
LAT_DELTA = 0.025; LNG_DELTA = 0.025
#LAT_DELTA = 0.01; LNG_DELTA = 0.01


##################################################
#
# Time Settings
#
DATE_FORMAT = '%Y-%m-%d'

DATE_FROM = '2012-10-01'
DATE_TO = '2013-10-06'

MIN_TWEETS = 35000
#MIN_TWEETS = 0