# Gambit scripts
#
# Copyright (C) USC Information Sciences Institute
# Author: Nibir Bora <nbora@usc.edu>
# URL: <http://cbg.isi.edu/>
# For license information, see LICENSE


DATA_FOLDER = 'hbk_homes/'
DATA_FOLDER = 'journeyToCrime/'
DATA_FOLDER = 'LA/'

# Files & folder names
FOLDER_USER_NIGHT_DATA = 'user_night_data/'
FOLDER_USER_DATA = 'user_all_data/'

FILE_MIN_TWEET_USERS = 'users_min_tweet.csv'
FILE_USER_HOMES = 'user_home_loc.csv'
FILE_USER_HOMES_JSON = 'user_home_loc.json'
FILE_USER_HOMES_TRIMMED = 'hbk_final_users.csv'
FILE_USER_HOMES_TRIMMED_JSON = 'hbk_user_home_loc.json'
FILE_DAILY_DISP = 'hbk_tweet_dist.csv'


# Universe of tweets, generally the city
# Hollenbeck strict bounds
BOUND_LOC_ID = 20
# Hollenbeck extended bounds (NOT IN USE)
#	BBOX = '33.988,-118.255,34.138,-118.105'
#	POLYGON = '33.988,-118.255,34.138,-118.255,34.138,-118.105,33.988,-118.105'
TIMEZONE = 'America/Los_Angeles'

# timestamp, timestring bounds
#TS_START = 
#TS_END = 
TS_FORMAT = "%Y-%m-%dT%H:%M:%S"
T_START = '19:00:00'
T_END ='4:00:00'
T_FORMAT = "%H:%M:%S"

#Finer constraints to consider users & home latlng
MIN_TWEET = 25
LOCATION_ID = 6
LOC_POL = [[34.0129, -118.23], [34.113, -118.23], [34.113, -118.155], [34.0129, -118.155], [34.0129, -118.23]]

# DBSCAN parameters
DBSCAN_EPS = 0.003
DBSCAN_MIN = 15





'''hbk_homes = {
	# Files & folder names
	#'sub_folder'	:	'hbk_homes/',
	#'sub_folder'	:	'journeyToCrime/',
	#'sub_folder'	:	'LA/',
	'files'				: {
		#'users_min_tweet'			:	'users_min_tweet.csv',
		#'user_home_loc'				:	'user_home_loc.csv',
		#'user_home_loc_json'	:	'user_home_loc.json',
		#'user_home_loc_trimmed'				:	'hbk_final_users.csv',
		#'user_home_loc_trimmed'				:	'hbk_user_home_loc.csv',
		'user_home_loc_trimmed_json'	:	'hbk_user_home_loc.json',
		'daily_disp' 	:	'hbk_tweet_dist.csv',
	},
	'folders'			:	{
		#'user_night_data'	:	'user_night_data/',
		#'user_all_data'		:	'user_all_data/',
	},

	# Universe of tweets, generally the city
	#'bound_loc_id':	20,
	#'bbox'				:	None,
	#'polygon'			:	None,
	'timezone'		:	'America/Los_Angeles',

	# timestamp, timestring bounds
	#'ts_start'		:	None,
	#'ts_end'			:	None,
	#'ts_format' 	:	"%Y-%m-%dT%H:%M:%S",
	#'t_start'			:	'19:00:00',
	't_end'				:	'4:00:00',
	't_format'		:	"%H:%M:%S",

	# Finer constraints to consider users & home latlng
	'min_tweet'		:	25,
	'location_id'	: 6,
	#'loc_pol'			:	[[34.0129, -118.23], [34.113, -118.23], [34.113, -118.155], [34.0129, -118.155], [34.0129, -118.23]],

	# DBSCAN parameters
	'dbscan'			:	{
		'eps'					:	0.003,
		'min_samples'	:	15
	}
}


#	
hbk_large_homes = {
	'sub_folder'	:	'hbk_large_homes/',
	'files'				: {
		'users_min_tweet'			:	'users_min_tweet.csv',
		'user_home_loc_json'	:	'hbk_user_home_loc.json',
		'user_home_loc'				:	'hbk_user_home_loc.csv'
	},
	'folders'			:	{
		'user_night_data'	:	'user_night_data/',
		'user_all_data'		:	'user_all_data/',
	},

	#'location_id'	:	20,
	#'bbox'				:	'33.988,-118.255,34.138,-118.105',
	'polygon'			:	'33.988,-118.255,34.138,-118.255,34.138,-118.105,33.988,-118.105',
	'timezone'		:	'America/Los_Angeles',

	#'ts_start'		:	None,
	#'ts_end'			:	None,
	#'ts_format' 	:	"%Y-%m-%dT%H:%M:%S",
	't_start'			:	'19:00:00',
	't_end'				:	'4:00:00',
	't_format'		:	"%H:%M:%S",

	'min_tweet'		:	25,

	'dbscan'			:	{
		'eps'					:	0.003,
		'min_samples'	:	15
	}
}

# SET CURENT SETTING dict HERE
CURRENT_SETTINGS = hbk_homes'''