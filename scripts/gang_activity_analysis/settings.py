# Gambit scripts
#
# Copyright (C) USC Information Sciences Institute
# Author: Nibir Bora <nbora@usc.edu>
# URL: <http://cbg.isi.edu/>
# For license information, see LICENSE


# Folders
#DATA_FOLDER = 'hbk/'
#DATA_FOLDER = 'hbk_old/'
DATA_FOLDER = 'hbk_old2/'


# Hollenbeck info
HBK_LOCATION_ID = 20
HBK_BOUNDS = [[34.013, -118.230], [34.113, -118.155]]
HBK_POLYGON = [[34.013, -118.230], [34.113, -118.155]]
HBK_BIG_BOUNDS = [[33.988, -118.255], [34.138, -118.105]]
HBK_BIG_BOUNDS_string = '33.988,-118.255,34.138,-118.105'

HBK_GANG_ID_LIST = range(23,55)

RIVALS = {
	23: [54, 53, 38, 45],
	24: [],
	25: [29, 41],
	26: [33, 41, 39],
	27: [30, 51, 49, 39, 34],
	28: [46, 49, 30, 35],
	29: [41, 25, 31],
	30: [50, 46, 28, 34, 27, 54],
	31: [29, 41],
	32: [36, 37, 33, 47],
	33: [42, 44, 26, 32, 37, 47],
	34: [27, 30, 50, 51, 46, 43, 39],
	35: [43, 28, 54],
	36: [37, 32, 41, 47],
	37: [32, 33, 36, 47],
	38: [53, 23, 45, 54],
	39: [27, 52, 48, 26, 49, 51, 34, 43, 40],
	40: [39, 43],
	41: [29, 25, 36, 31, 26],
	42: [33],
	43: [34, 51, 39, 40, 35],
	44: [33],
	45: [53, 23, 38, 54],
	46: [28, 30, 50, 34, 49],
	47: [33, 37, 32, 36],
	48: [52, 39],
	49: [27, 28, 51, 39, 46],
	50: [34, 30, 46],
	51: [27, 49, 39, 43, 34],
	52: [39, 48],
	53: [23, 54, 45, 38],
	54: [23, 53, 45, 38, 35, 30]
}


# Trim parameters
HOME_RADIUS = 50 		# meters
MIN_TWEETS = 20
MIN_USERS = 3
BORDER_LINE_SPAN = 50 	# meters




#----- Not used
BOUND_RADIUS_MILES = 5
CONST_MILE_TO_METER = 1609.34


GANG_DATA_FOLDER = 'gang_data_json'

OUTPUT_COUNT_FILE = 'gang_vs_la_count.json'
OUTPUT_FRACTION_FILE = 'gang_vs_la_count.csv'