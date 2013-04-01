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

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

from pylab import *
from scipy.optimize import leastsq


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


def find_daily_disp():
#	Find daily max displacement for users
	
	all_disp = []
	user_home_loc = []
	with open('data/' + my['sub_folder'] + my['files']['user_home_loc_trimmed'], 'rb') as fp1:
		csv_reader = csv.reader(fp1, delimiter=',')
		for row in csv_reader:
			user_id, home_lat, home_lng = int(row[0]), float(row[1]), float(row[2])
			this_user_dist = {}

			with open('data/' + my['sub_folder'] + my['folders']['user_all_data'] + str(user_id) + '.csv', 'rb') as fp2:
					csv_reader2 = csv.reader(fp2, delimiter=',')
					for row2 in csv_reader2:
						lat, lng, date = float(row2[0]), float(row2[1]), row2[2]
						dist = int(round(geo.distance(geo.xyz(home_lat, home_lng), geo.xyz(lat, lng))))
						if date not in this_user_dist:
							this_user_dist[date] = []
						this_user_dist[date].append(dist)

			all_disp += [[user_id, max(this_user_dist[date])] for date in this_user_dist]
	
	with open('data/' + my['sub_folder'] + my['files']['daily_disp'], 'wb') as fp2:
		csv_writer = csv.writer(fp2, delimiter=',')
		for item in all_disp:
			csv_writer.writerow(item)
	print '%s daily max displacements stored.' % (len(all_disp))



def generate_disp_plots():
# Plot histograms
	x = []
	with open('data/' + my['sub_folder'] + my['files']['daily_disp'], 'rb') as fp2:
		csv_reader = csv.reader(fp2, delimiter=',')
		for row in csv_reader:
			x.append(int(row[1]))
	print '%s daily max displacements read.' % (len(x))

	# plot
	#plot_hist(x, 100, None, '0-inf.png')
	plot_hist(x, 99, (100,10000), '100m-10km.png')
	#plot_hist(x, 100, (x.min(),10000), '0-10km.png')
	plot_hist(x, 149, (100,15000), '100m-15km.png')
	#plot_hist(x, 150, (x.min(),15000), '0-15km.png')
	plot_hist(x, 199,  (100,20000), '100m-20km.png')
	#plot_hist(x, 200,  (x.min(),20000), '0-20km.png')
	plot_hist(x, 249,  (100,25000), '100m-25km.png')
	#plot_hist(x, 250,  (x.min(),25000), '0-25km.png')
	

def plot_hist(x, bins, range, file_name):
	count = len(x)
	fig = plt.figure(figsize=(8,4))
	plt.subplots_adjust(left=0.075, right=0.98, top=0.95, bottom=0.12)
	y, x, patches = plt.hist(x, bins=bins, range=range, normed=False, \
		color='#377EB8', alpha=0.8, edgecolor='#377EB8')
	#print n, b, p
	#formatter = FuncFormatter(lambda v, pos: str(v*10**4)+'%')
	formatter = FuncFormatter(lambda v, pos: str(round(int(v)*100/float(count)))+'%')
	plt.gca().yaxis.set_major_formatter(formatter)
	formatter = FuncFormatter(lambda v, pos: str(int(v/1000)))
	plt.gca().xaxis.set_major_formatter(formatter)
	gca().set_xlabel('Distance travelled for home (km)')
	#plt.show()	

	# Power-law fitting is best done by first converting
	# to a linear equation and then fitting to a straight line.
	#  y = a * x^b
	#  log(y) = log(a) + b*log(x)
	powerlaw = lambda x, amp, index: amp * (x**index)

	x.resize((x.size-1, ))
	ydata = powerlaw(x, 10.0, -2.0)
	yerr = y - ydata
	logx = log10(x)
	logy = log10(y)
	logyerr = yerr / y

	fitfunc = lambda p, x: p[0] + p[1] * x
	errfunc = lambda p, x, y, err: (y - fitfunc(p, x)) / err
	pinit = [1.0, -1.0]
	out = leastsq(errfunc, pinit, args=(logx, logy, logyerr), full_output=1)
	pfinal = out[0]
	covar = out[1]
	#print covar
	index = pfinal[1]
	amp = 10.0**pfinal[0]
	indexErr = sqrt( covar[0][0] )
	ampErr = sqrt( covar[1][1] ) * amp

	p, = plot(x, powerlaw(x, amp, index), \
		label = 'fit', color='#E41A1C')
	legend([patches[0], p], ['data', 'fit: y = %s x^%s' % (round(amp,3), round(index,3))])

	if not os.path.exists('data/' + my['sub_folder'] + 'charts/'):
		os.makedirs('data/' + my['sub_folder'] + 'charts/')
	plt.savefig('data/' + my['sub_folder'] + 'charts/' + file_name)
	print 'Stored chart: %s' % file_name

						

