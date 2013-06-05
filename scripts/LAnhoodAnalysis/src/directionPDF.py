# Gambit scripts
#
# Copyright (C) USC Information Sciences Institute
# Author: Nibir Bora <nbora@usc.edu>
# URL: <http://cbg.isi.edu/>
# For license information, see LICENSE

import os
import sys
sys.path.insert(0, os.path.abspath('..'))
import settings as my

import anyjson
import csv
import psycopg2
from pprint import pprint

import numpy
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import math

COLORS = {'hbk': '#377EB8',
					'south-la' : '#FA71AF',
					'west-la' : '#4DAF4A',
					'south-bay' : '#A65628',
					'pomona' : '#3B3B3B',
					'bernardino' : '#984EA3',
					'riverside' : '#FF7F00'
					}
BIN_SIZE = 5


def out_dirPDF():
	'''Calculates direction PDF for region and plots a polar diagram'''
	#_find_dirList()
	y = _get_dirPDF()
	#print y
	print len(y), min(y), max(y), sum(y)
	_plot_dirPDF([y])


def _find_dirList():
	'''Find the list of direction for all users in region. [user_directions.csv]'''
	# Read user_ids
	with open('data/' + my.DATA_FOLDER + 'user_list.json', 'rb') as fpr:
		user_ids = anyjson.loads(fpr.read())
	user_ids = [int(user_id) for user_id in user_ids]
	print 'Read {0} user_ids'.format(len(user_ids))

	user_directions = []

	con = psycopg2.connect(my.DB_CONN_STRING)
	cur = con.cursor()

	for user_id in user_ids:
		# Read home
		SQL = 'SELECT ST_X(geo), ST_Y(geo) \
				FROM t4_home \
				WHERE user_id = %s '
		cur.execute(SQL, (user_id,))
		records = cur.fetchall()

		# If home exist
		if len(records) > 0:
			home = records[0]
			hx, hy = home[1], home[0]

			# Read all latlng pairs
			SQL = 'SELECT ST_X(geo), ST_Y(geo) \
					FROM t3_tweet_6 \
					WHERE user_id = %s '\
					+ my.QUERY_CONSTRAINT
			cur.execute(SQL, (user_id,))
			records = cur.fetchall()

			# Append all latlng pairs
			for rec in records:
				lat, lng = rec
				x, y = lng-hx, lat-hy
				if x != 0 and y != 0:
					deg = int(round(_calc_angle(x, y)))
					user_directions.append([user_id, deg])
		else:
			print 'Missed 1 user_id!'

	con.close()

	# Statistics
	x = [d[1] for d in user_directions]
	print len(x), min(x), max(x), sum(x)/len(x)

	with open('data/' + my.DATA_FOLDER + 'user_directions.csv', 'wb') as fpw:
		cw = csv.writer(fpw, delimiter=',')
		for row in user_directions:
			cw.writerow(row)


def _get_dirPDF():
	'''Returns the direction PDF function as a list of fractions, 0-360'''
	y = [0] * (360/BIN_SIZE)

	with open('data/' + my.DATA_FOLDER + 'user_directions.csv', 'rb') as fpr:
		cr = csv.reader(fpr, delimiter=',')
		for row in cr:
			deg = int(row[1])/BIN_SIZE
			y[deg % (360/BIN_SIZE)] += 1

	s = float(sum(y))
	y = [val/s for val in y]		
	return y


def _plot_dirPDF(Y):
	'''Plot direction PDF function of a polar graph'''
	fig = plt.figure(figsize=(6,6))
	ax = fig.add_subplot(111, projection='polar')
	#plt.subplots_adjust(left=0.075, right=0.96, top=0.92, bottom=0.08)
	#ax.set_autoscaley_on(False)
	#ax.set_ylim([0,0.1])
	#ax.set_xlim(0, RANGE[1])

	x = range(0, 360, BIN_SIZE)
	theta = numpy.radians(x)

	for y in Y:
		y = numpy.array(y)
		label = my.DATA_FOLDER[:-1]

		ax.plot(theta, y, label=label.upper(), color=COLORS[label], alpha=0.95)
	
	ax.legend()
	plt.savefig('data/' + my.DATA_FOLDER + 'plot_disp_direction' + '.png')



# Load list of all nhoods in region
_load_nhoodIDs = lambda: [int(nid) for nid in anyjson.loads(open('data/' + my.DATA_FOLDER + 'hood_ids.txt', 'rb').read())]

def test():
	home = (34.012, -118.299)
	ne = (34.051, -118.252)
	nw = (34.046, -118.342)
	sw = (33.976, -118.338)
	se = (33.978, -118.241)


	hx, hy = home[1], home[0]
	for p in [ne, nw, sw, se]:
		x, y = p[1]-hx, p[0]-hy
		
		print _which_quad(x,y)
		print math.degrees(math.atan(y/x))
		_calc_angle(x, y)

def _which_quad(x, y):
	'''Returns the quadrant of the coordinate pair (x,y)'''
	quad = {(1, 1) : 1,
					(-1,1) : 2,
					(-1,-1): 3,
					(1,-1) : 4,
					}
	return quad[(numpy.sign(x), numpy.sign(y))]

def _calc_angle(x, y):
	'''Returns angle of point (x,y) w.r.t. +ve x-axis'''
	if x == 0:
		deg = 90 if y > 0 else 270
	elif y == 0:
		deg = 0 if x > 0 else 180
	else:
		deg = math.degrees(math.atan(y/x))
		quad = _which_quad(x, y)

		if quad == 2 or quad == 3:
			deg += 180
		elif quad == 4:
			deg += 360

	return deg