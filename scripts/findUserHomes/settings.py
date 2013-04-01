# Gambit scripts
#
# Copyright (C) USC Information Sciences Institute
# Author: Nibir Bora <nbora@usc.edu>
# URL: <http://cbg.isi.edu/>
# For license information, see LICENSE


# NOTE: SCROLL TO END OF FILE


# Hollenbeck strict bounds
hbk_homes = {
	# Files & folder names
	'sub_folder'	:	'hbk_homes/',
	#'sub_folder'	:	'journeyToCrime/',
	#'sub_folder'	:	'LA/',
	'files'				: {
		'users_min_tweet'			:	'users_min_tweet.csv',
		'user_home_loc'				:	'user_home_loc.csv',
		'user_home_loc_json'	:	'user_home_loc.json',
		'user_home_loc_trimmed'				:	'hbk_user_home_loc.csv',
		'user_home_loc_trimmed_json'	:	'hbk_user_home_loc.json',
		'daily_disp' 	:	'hbk_tweet_dist.csv',
	},
	'folders'			:	{
		'user_night_data'	:	'user_night_data/',
		'user_all_data'		:	'user_all_data/',
	},

	# Universe of tweets, generally the city
	'bound_loc_id':	20,
	#'bbox'				:	None,
	#'polygon'			:	None,
	'timezone'		:	'America/Los_Angeles',

	# timestamp, timestring bounds
	#'ts_start'		:	None,
	#'ts_end'			:	None,
	#'ts_format' 	:	"%Y-%m-%dT%H:%M:%S",
	't_start'			:	'19:00:00',
	't_end'				:	'4:00:00',
	't_format'		:	"%H:%M:%S",

	# Finer constraints to consider users & home latlng
	'min_tweet'		:	25,
	'location_id'	: 6,
	'loc_pol'			:	[[34.0129, -118.23], [34.113, -118.23], [34.113, -118.155], [34.0129, -118.155], [34.0129, -118.23]],

	# DBSCAN parameters
	'dbscan'			:	{
		'eps'					:	0.003,
		'min_samples'	:	15
	}
}

# Hollenbeck extended bounds (NOT IN USE)
#	'bbox'				:	'33.988,-118.255,34.138,-118.105',
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
CURRENT_SETTINGS = hbk_homes