# Gambit scripts
#
# Copyright (C) USC Information Sciences Institute
# Author: Nibir Bora <nbora@usc.edu>
# URL: <http://cbg.isi.edu/>
# For license information, see LICENSE


import sys
import os
sys.path.insert(0, os.path.abspath('..'))
from settings import CURRENT_SETTINGS as my

import csv
import anyjson as json
import lib.geo as geo
import lib.PiP_Edge as pip


def find_user_homes():
#	Run DBSCAN on night latlng to find home loc
	
	import numpy as np
	from scipy.spatial import distance
	from sklearn.cluster import DBSCAN

	user_home_loc = []
	in_users = 0
	
	with open('data/' + my['sub_folder'] + my['files']['users_min_tweet'], 'rb') as fp1:
		csv_reader = csv.reader(fp1, delimiter=',')
		for row in csv_reader:
			user_id = int(row[0])
			in_users += 1
			# Get user latlng
			try:
				points = []
				with open('data/' + my['sub_folder'] + my['folders']['user_night_data'] + str(user_id) + '.csv', 'rb') as fp2:
					csv_reader2 = csv.reader(fp2, delimiter=',')
					for row2 in csv_reader2:
						points.append([float(row2[0]), float(row2[1])])
				print 'user_id: %s,\tlatlng: %s / %s' % (user_id, int(row[1]), len(points))

				# Run DBSCAN
				D = distance.squareform(distance.pdist(points))
				S = 1 - (D / np.max(D))
				db = DBSCAN(eps=my['dbscan']['eps'], min_samples=my['dbscan']['min_samples']).fit(S)
				core_samples = db.core_sample_indices_
				labels = db.labels_
				_labels = list(labels)
				print 'predictions : %s' % dict([(i, _labels.count(i)) for i in set(_labels)])
				label_counts = dict([(i, _labels.count(i)) for i in set(_labels) if i != -1 and i != -1.0])
				if len(label_counts) > 0:
					label_max = max(label_counts, key=label_counts.get)
					home_point_index = [i for i in core_samples if labels[i] == label_max]
					home_points = [points[i] for i in home_point_index]
					home = calc_center(home_points)
					print 'Home cluster label: %s,\tcount: %s / %s' % (label_max, len(home_point_index), len(home_points))
					print 'Home latlng : %s\n' % (home)

					user_home_loc.append([user_id, home[0], home[1]])
				else:
					print '\tHome cluster was not found.\n'
			except Exception as e:
				print '\tError opening file or calc error. user_id: %s\n' % (user_id)

	print 'Found home latlng for %s out of %s users.' % (len(user_home_loc), in_users)

	# Write user home list
	with open('data/' + my['sub_folder'] + my['files']['user_home_loc'], 'wb') as fp3:
		csv_writer = csv.writer(fp3, delimiter=',')
		for item in user_home_loc:
			csv_writer.writerow(item)
	
	user_home_loc_json = dict([(item[0], [item[1], item[2]]) for item in user_home_loc])
	with open('data/' + my['sub_folder'] + my['files']['user_home_loc_json'], 'wb') as fp3:
		fp3.write(json.dumps(user_home_loc_json))

def calc_center(loc_arr):
    center = [0,0]
    points = 0
    for latlng in loc_arr:
        center[0] += latlng[0]
        center[1] += latlng[1]
        points += 1

    center[0] /= points
    center[1] /= points
    return center

def trim_user_homes(polygon):
#	Trim list of user home latlng inside polygon
#	@param
#			polygon		trim latlng outside polygon

	user_home_loc = []
	count=0
	with open('data/' + my['sub_folder'] + my['files']['user_home_loc'], 'rb') as fp1:
		csv_reader = csv.reader(fp1, delimiter=',')
		for row in csv_reader:
			user_id = int(row[0])
			lat = float(row[1])
			lng = float(row[2])
			count += 1
			if pip.point_in_poly(lat, lng, polygon):
				user_home_loc.append([user_id, lat, lng])
	print '%s user homes read.' % (count)

	# Write user home list
	with open('data/' + my['sub_folder'] + my['files']['user_home_loc_trimmed'], 'wb') as fp3:
		csv_writer = csv.writer(fp3, delimiter=',')
		for item in user_home_loc:
			csv_writer.writerow(item)
	user_home_loc_json = dict([(item[0], [item[1], item[2]]) for item in user_home_loc])
	with open('data/' + my['sub_folder'] + my['files']['user_home_loc_trimmed_json'], 'wb') as fp3:
		fp3.write(json.dumps(user_home_loc_json))
	print '%s user homes inside polygon.' % (len(user_home_loc))
