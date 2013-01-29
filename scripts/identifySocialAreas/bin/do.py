import sys
import os
sys.path.insert(0, os.path.abspath('..'))
import settings as my

import csv
import psycopg2
import anyjson
from lib.dbscan import dbscan
import lib.geo as geo

#-----  -----#

def remove_homes_outside_bounds():
	fp1 = open(my.DATA_FOLDER + '/' + my.HBK_HOME_LOC_FILE_original, 'rb')
	csv_reader = csv.reader(fp1, delimiter=',')
	fp2 = open(my.DATA_FOLDER + '/' + my.HBK_HOME_LOC_FILE, 'wb')
	csv_writer = csv.writer(fp2, delimiter=',')

	count = 0
	for row in csv_reader:
		if is_inside_bounds(my.HBK_BIG_BOUNDS, [float(row[1]), float(row[2])]):
			csv_writer.writerow(row)
			count += 1
	print str(count) + ' homes inside bounds.'

	fp1.close()
	fp2.close()

def is_inside_bounds(bounds, point):
	if bounds[0][0] < bounds[1][0]:
		lat_lo = bounds[0][0]
		lat_hi = bounds[1][0]
	else:
		lat_lo = bounds[1][0]
		lat_hi = bounds[0][0]
	if bounds[0][1] < bounds[1][1]:
		lng_lo = bounds[0][1]
		lng_hi = bounds[1][1]
	else:
		lng_lo = bounds[1][1]
		lng_hi = bounds[0][1]

	if point[0] >= lat_lo and point[0] <= lat_hi and point[1] >= lng_lo and point[1] <= lng_hi:
		return True
	return False

#-----  -----#

def get_user_tweet_locations():
	print "Connecting to DB..."
	conn = psycopg2.connect(my.DB_CONN_STRING)
	cursor = conn.cursor()
	print "Connected."

	with open(my.DATA_FOLDER + '/' + my.HBK_HOME_LOC_FILE, 'rb') as fp1:
		csv_reader = csv.reader(fp1, delimiter=',')
		for row in csv_reader:
			current_user=row[0]
			print "Querying data for user... " + str(current_user)
			SQL_STM = "select latitude, longitude	\
				from t_tweet	\
				where location_id= " + str(my.HBK_LOCATION_ID) + " and user_id=" + str(current_user)
			
			cursor.execute(SQL_STM)
			records = cursor.fetchall()

			with open(my.DATA_FOLDER + '/' + my.USER_TWEET_LOC_FOLDER + '/' + str(my.HBK_LOCATION_ID) + '/' + str(current_user) + '.csv', 'wb') as fp2:
				csv_writer = csv.writer(fp2, delimiter=',')
				for record in records:
					csv_writer.writerow([record[0], record[1]])

				print "This user had = " + str(len(records)) + " records."

#-----  -----#

def find_most_visited_loc():
	points = []
	results = []
	clusters = []

	with open(my.DATA_FOLDER + '/' + my.HBK_HOME_LOC_FILE, 'rb') as fp1:
		csv_reader = csv.reader(fp1, delimiter=',')
		for row in csv_reader:
			current_user = row[0]
			current_user_home = geo.xyz(float(row[1].strip()), float(row[2].strip()))
			try:
				with open(my.DATA_FOLDER + '/' + my.USER_TWEET_LOC_FOLDER + '/' + str(my.HBK_LOCATION_ID) + '/' + str(current_user) + '.csv', 'rb') as fp2:
					csv_reader2 = csv.reader(fp2, delimiter = ',')

					for row2 in csv_reader2:
						if row2[0].strip().__len__() != 0 and row2[1].strip().__len__() != 0:
							# if not near user's home
							this_point = geo.xyz(float(row2[0].strip()), float(row2[1].strip()))
							if int(round(geo.distance(current_user_home, this_point))) > 100:
								points.append([float(row2[0].strip()), float(row2[1].strip())])
			except IOError as e:
					print 'No file found for user... ' + str(current_user)

	print 'Total latlng pairs read: ' + str(len(points))
	if len(points) != 0:
		print 'Running DBScan... '
		results = dbscan(points, my.DBSCAN_EPSILON, my.DBSCAN_MIN_POINTS)
		print 'Run complete... Number of clusters = ' + str(len(results))

		for key in results:
			if key != -1:
				center = calc_center(results[key])
				clusters.append([center[0], center[1], len(results[key])])

		fp3 = open(my.DATA_FOLDER + '/' + my.MOST_VISITED_LOC_FILE, 'wb')
		csv_writer = csv.writer(fp3, delimiter=',')
		for row in clusters:
			csv_writer.writerow(row)
		fp3.close

		with open(my.DATA_FOLDER + '/' + my.MOST_VISITED_LOC_FILE_json, 'wb') as fp3:
			fp3.write(anyjson.serialize(clusters))

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

#-----  -----#

#def calc_entropy_for_each_cluster():
