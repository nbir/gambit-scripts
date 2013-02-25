# Gambit scripts
#
# Copyright (C) USC Information Sciences Institute
# Author: Nibir Bora <nbora@usc.edu>
# URL: <http://cbg.isi.edu/>
# For license information, see LICENSE


HBK_LOCATION_ID = 20
HBK_BOUNDS = [[34.013, -118.230], [34.113, -118.155]]
HBK_POLYGON = [[34.013, -118.230], [34.113, -118.155]]
HBK_BIG_BOUNDS = [[33.988, -118.255], [34.138, -118.105]]
HBK_BIG_BOUNDS_string = '33.988,-118.255,34.138,-118.105'


HBK_GANG_ID_LIST = range(23,55)

HBK_GANG_AND_RIVAL_IDS = {
	26: [33, 41, 39],
	27: [30, 51, 49, 39, 34],
	29: [41, 25, 31],
	32: [36, 37, 33, 47],
	33: [42, 44, 26, 32, 37, 47],
	36: [37, 32, 41, 47],
	39: [52, 48, 26, 49, 51, 30, 34, 43, 40],
	40: [39, 43],
	44: [33],
	45: [53, 23, 38, 54],
	46: [49, 28, 51, 30, 50],
	47: [33, 37, 32, 36],
	49: [28, 51, 30, 39, 46],
	50: [34, 30, 46],
	51: [49, 39, 43, 34, 30, 46],
	54: [23, 53, 45, 38, 35, 30]
}


DATA_FOLDER = 'data'
GANG_DATA_FOLDER = 'gang_data_json'

LOCATION_DATA_FILE = 'location_data_all.json'
OUTPUT_COUNT_FILE = 'gang_vs_la_count.json'
OUTPUT_FRACTION_FILE = 'gang_vs_la_count.csv'

OUT_MEASURE1_FILE = 'rival_nonrival.json'
OUT_MEASURE2_FILE = 'rival_nonrival_norm.json'

HBK_TWEET_LOC_FILE = 'hbk_all_tweet_loc.csv'
HBK_USER_HOME_LOC_FILE = 'user_home_locations_hbk.csv'
HBK_HOMES_IN_GANG_TTY_FOLDER = 'user_homes_in_gang_t'
HBK_TWEET_DIST_FILE = 'hbk_tweet_dist.csv'



#-----
BOUND_RADIUS_MILES = 5
CONST_MILE_TO_METER = 1609.34

