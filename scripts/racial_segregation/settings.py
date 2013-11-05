# Gambit scripts
#
# Copyright (C) USC Information Sciences Institute
# Author: Nibir Bora <nbora@usc.edu>
# URL: <http://cbg.isi.edu/>
# For license information, see LICENSE



# Folders
#DATA_FOLDER = 'hand-drawn/'
DATA_FOLDER = 'tracts/'


# Relations
REL_TWEET 	= 't3_tweet_6'


# Multi processing
PROCESSES 	= 12



# DB
DB_CONN_STRING = "host='brain.isi.edu' dbname='twitter' user='twitter' password='flat2#tw1tter'"



# Params
TIMEZONE 	= 'America/Los_Angeles'
MIN_DIST = 2500
MAX_DIST = 80000
BBOX = [33.500, -118.700, 34.400, -117.200]
POLY_WKT = 'POLYGON ((-118.700 33.500, -118.700 34.400, -117.200 34.400, -117.200 33.500, -118.700 33.500))'

STATE_ID = 6

MIN_POPULATION = 500
MAX_AREA = 0.005
MIN_USERS = 2

COLOR = {
	'w': '#73B2FF', 
	'b': '#9fd400', 
	'a': '#ff0000', 
	'h': '#FF7F00', 
	'o': '#ffaa00'}



# Artificial data
LAT_RANGE = (-80000, 80000)	# in meters
LNG_RANGE = (-80000, 80000)

DELTA_METERS = 100

LAT_DELTA = 0.0009
LNG_DELTA = 0.001

GRID_LAT_DELTA = 0.005; GRID_LNG_DELTA = 0.005

