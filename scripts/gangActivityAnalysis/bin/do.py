# Gambit scripts
#
# Copyright (C) USC Information Sciences Institute
# Author: Nibir Bora <nbora@usc.edu>
# URL: <http://cbg.isi.edu/>
# For license information, see LICENSE


import sys
import os
sys.path.insert(0, os.path.abspath('..'))
import settings as my

import csv
import anyjson
import lib.geo as geo
import lib.PiP_Edge as pip


def calc_tweet_freq_in_rival_home():
# 
# 
# 
	import sys
	sys.path.append("/home/gambit/collector/gambit2/")
	from django.core.management import setup_environ
	from gambit import settings
	setup_environ(settings)

	from scraper.models import Location, Tweet


	counts = {}

	tty_counts = {}
	tty_polys = {}

	# Read location polygons for gang territories
	with open(my.DATA_FOLDER + '/' + my.LOCATION_DATA_FILE, 'rb') as fp1:
		location_data = anyjson.deserialize(fp1.read())
		for loc in location_data:
			if loc['id'] >= 23 and loc['id'] <= 54:
				tty_polys[loc['id']] = loc['polygon']

	# Count tweets
	for gang_id in my.HBK_GANG_AND_RIVAL_IDS:
		gang_data = {}
		with open(my.DATA_FOLDER + '/' + my.GANG_DATA_FOLDER + '/' + str(gang_id) + '.json', 'rb') as fp1:
			gang_data = anyjson.deserialize(fp1.read())
		gang_center = calc_center(gang_data['location_polygon'])
		bounds = get_bounding_box(gang_center, my.BOUND_RADIUS_MILES)
		bbox = arr_to_str(bounds)

		counts[gang_id] = {
			'gang' : {
				'total' : 0,
				'home' : 0,
				'rival' : {}
			},
			'la' : {
				'total' : 0,
				'home' : 0,
				'rival' : {}
			}
		}

		# Count tweets for all gang members
		counts[gang_id]['gang']['total'] = 0
		counts[gang_id]['gang']['home'] = 0
		for rival_id in my.HBK_GANG_AND_RIVAL_IDS[gang_id]:
			counts[gang_id]['gang']['rival'][rival_id] = 0

		for user_id in gang_data['users']:
			counts[gang_id]['gang']['total'] += len(gang_data['users'][user_id]['points_inside']) + len(gang_data['users'][user_id]['points_outside'])	# Universe

			counts[gang_id]['gang']['home'] += len(gang_data['users'][user_id]['points_inside'])		# Home tty

			for latlng in gang_data['users'][user_id]['points_outside']:
				for rival_id in my.HBK_GANG_AND_RIVAL_IDS[gang_id]:
					if pip.point_in_poly(latlng[0], latlng[1], tty_polys[rival_id]):
						counts[gang_id]['gang']['rival'][rival_id] += 1									# Rival tty

		# Count tweets for all LA users
		print 'Django query... gang-id ' + str(gang_id) + '... universe.'
		tweets = Tweet.objects.all()
		loc = Location.parse_bbox(my.HBK_BIG_BOUNDS_string)
		tweets = tweets.filter(geo__within=loc)
		bbox = Location.parse_bbox(bbox)
		tweets = tweets.filter(geo__within=bbox)
		counts[gang_id]['la']['total'] = tweets.count()				# Universe

		if gang_id in tty_counts:
			counts[gang_id]['la']['home'] = tty_counts[gang_id]
		else:
			print 'Django query... gang-id ' + str(gang_id) + '... home tty.'
			tweets = Tweet.objects.all()
			loc = Location.parse_bbox(my.HBK_BIG_BOUNDS_string)
			tweets = tweets.filter(geo__within=loc)
			polygon = Location.parse_polygon(arr_to_str(tty_polys[gang_id]))
			tweets = tweets.filter(geo__within=polygon)
			tty_counts[gang_id] = tweets.count()								# Home tty
			counts[gang_id]['la']['home'] = tty_counts[gang_id]

		for rival_id in my.HBK_GANG_AND_RIVAL_IDS[gang_id]:
			if rival_id in tty_counts:
				counts[gang_id]['la']['rival'][rival_id] = tty_counts[rival_id]
			else:
				print 'Django query... rival-id ' + str(rival_id) + '... rival tty.'
				tweets = Tweet.objects.all()
				loc = Location.parse_bbox(my.HBK_BIG_BOUNDS_string)
				tweets = tweets.filter(geo__within=loc)
				polygon = Location.parse_polygon(arr_to_str(tty_polys[rival_id]))
				tweets = tweets.filter(geo__within=polygon)
				tty_counts[rival_id] = tweets.count()							# Rival tty
				counts[gang_id]['la']['rival'][rival_id] = tty_counts[rival_id]

	with open(my.DATA_FOLDER + '/' + my.OUTPUT_COUNT_FILE, 'wb') as fp2:
		fp2.write(anyjson.serialize(counts))
	print counts


def calc_center(loc_arr):
	center = [0.0,0.0]
	points = 0
	for latlng in loc_arr:
		center[0] += latlng[0]
		center[1] += latlng[1]
		points += 1

	center[0] /= points
	center[1] /= points
	return center

def get_bounding_box(center, miles):
	this_point = [center[0], center[1]]
	while geo.distance(geo.xyz(center[0], center[1]), geo.xyz(this_point[0], this_point[1])) <= (miles*my.CONST_MILE_TO_METER):
		this_point[0] += 0.0001	# lat
	lat_hi = this_point[0]
	this_point = [center[0], center[1]]
	while geo.distance(geo.xyz(center[0], center[1]), geo.xyz(this_point[0], this_point[1])) <= (miles*my.CONST_MILE_TO_METER):
		this_point[0] -= 0.0001	# lat
	lat_lo = this_point[0]
	if lat_lo > lat_hi:
		lat_hi, lat_lo = lat_lo, lat_hi

	this_point = [center[0], center[1]]		
	while geo.distance(geo.xyz(center[0], center[1]), geo.xyz(this_point[0], this_point[1])) <= (miles*my.CONST_MILE_TO_METER):
		this_point[1] += 0.0001	# lng
	lng_hi = this_point[1]
	this_point = [center[0], center[1]]		
	while geo.distance(geo.xyz(center[0], center[1]), geo.xyz(this_point[0], this_point[1])) <= (miles*my.CONST_MILE_TO_METER):
		this_point[1] -= 0.0001	# lng
	lng_lo = this_point[1]
	if lng_lo > lng_hi:
		lng_hi, lng_lo = lng_lo, lng_hi

	#return [[lat_lo, lng_lo], [lat_hi, lng_lo], [lat_hi, lng_hi], [lat_lo, lng_hi]]	#polygon
	return [[lat_lo, lng_lo], [lat_hi, lng_hi]]		#bbox

def arr_to_str(arr):
	arr_str = ''
	for sub in arr:
		for val in sub:
			arr_str += str(round(val, 5)) + ','
	return arr_str[:-1]


def generate_frac_csv():
	counts = {}
	fractions = {}

	with open(my.DATA_FOLDER + '/' + my.OUTPUT_COUNT_FILE, 'rb') as fp1:
		counts = anyjson.deserialize(fp1.read())
	
	for gang_id in counts:
		fractions[gang_id] = {
			'gang' : {
				'home' : 0,
				'rival' : {}
			},
			'la' : {
				'home' : 0,
				'rival' : {}
			}
		}

		fractions[gang_id]['gang']['home'] = round(float(counts[gang_id]['gang']['home']) / float(counts[gang_id]['gang']['total']), 4)
		for rival_id in counts[gang_id]['gang']['rival']:
			fractions[gang_id]['gang']['rival'][rival_id] = round(float(counts[gang_id]['gang']['rival'][rival_id]) / float(counts[gang_id]['gang']['total']), 4)

		fractions[gang_id]['la']['home'] = round(float(counts[gang_id]['la']['home']) / float(counts[gang_id]['la']['total']), 4)
		for rival_id in counts[gang_id]['la']['rival']:
			fractions[gang_id]['la']['rival'][rival_id] = round(float(counts[gang_id]['la']['rival'][rival_id]) / float(counts[gang_id]['la']['total']), 4)

	with open(my.DATA_FOLDER + '/' + my.OUTPUT_FRACTION_FILE, 'wb') as fp2:
		csv_writer = csv.writer(fp2, delimiter=',')
		for gang_id in fractions:
			csv_writer.writerow([gang_id, fractions[gang_id]['gang']['home'], fractions[gang_id]['la']['home']])
			for rival_id in fractions[gang_id]['gang']['rival']:
				csv_writer.writerow([rival_id, fractions[gang_id]['gang']['rival'][rival_id], fractions[gang_id]['la']['rival'][rival_id]])
			csv_writer.writerow(['-', '-', '-'])
