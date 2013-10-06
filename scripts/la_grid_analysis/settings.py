# Gambit scripts
#
# Copyright (C) USC Information Sciences Institute
# Author: Nibir Bora <nbora@usc.edu>
# URL: <http://cbg.isi.edu/>
# For license information, see LICENSE

#
# Folders
#
DATA_FOLDER = 'lat.1_lng.1/'


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

#TS_START = '2013-06-27 12:00:00'
TS_START = '2013-06-27 00:00:00'
TS_WINDOW = 1 		# days


PROCESSES = 12 		# threads


##################################################
#
# Bbox Settings
#
BBOX = [33.5, -118.7, 34.4, -117.2]

LAT_DELTA = 0.1
LNG_DELTA = 0.1