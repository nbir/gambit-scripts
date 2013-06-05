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
import math

import numpy
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from PIL import Image
from matplotlib.backends.backend_pdf import PdfPages

from pylab import *
from scipy.optimize import leastsq
from datetime import datetime

def out_all_homes_json():
#	Output JSON of all identified user homes
	con = psycopg2.connect(my.DB_CONN_STRING)
	cur = con.cursor()

	SQL = 'SELECT user_id, ST_X(geo), ST_Y(geo)\
				FROM {rel_home}'.format(rel_home=my.REL_HOME)
	cur.execute(SQL)
	recs = cur.fetchall()
	con.close()

	homes = {}
	for rec in recs:
		user_id, lat, lng = rec
		user_id, lat, lng = int(user_id), float(lat), float(lng)
		homes[user_id] = [lat, lng]
		

	with open('data/' + my.DATA_FOLDER + 'user_home_all.json', 'wb') as fp:
		fp.write(anyjson.dumps(homes))


def out_region_homes_latlng_json(read_pol=True):
#	Output: JSON of all homes and latlng in region
	con = psycopg2.connect(my.DB_CONN_STRING)
	cur = con.cursor()

	if read_pol:
		# REGION POL case
		with open('data/' + my.DATA_FOLDER + 'bound_pol.txt', 'rb') as fpr:
			bound_pol = fpr.read().strip()

		SQL = 'SELECT user_id, ST_X(geo), ST_Y(geo)\
					FROM {rel_home} \
					WHERE geo && ST_GeomFromGeoJSON(%s)'.format(rel_home=my.REL_HOME)
		cur.execute(SQL, (bound_pol, ))
		recs = cur.fetchall()

		user_ids = [rec[0] for rec in recs]
		homes = [[rec[1], rec[2]] for rec in recs]

	else:
		# HBK case
		if my.DATA_FOLDER == 'hbk/':
			with open('data/' + my.DATA_FOLDER + 'user_list.csv', 'rb') as fpr:
				cr = csv.reader(fpr, delimiter=',')
				user_ids = [int(row[0]) for row in cr]

			SQL = 'SELECT ST_X(geo), ST_Y(geo)\
						FROM {rel_home} \
						WHERE user_id IN %s'.format(rel_home=my.REL_HOME)

			cur.execute(SQL, (tuple(user_ids), ))
			recs = cur.fetchall()
			
			homes = [[rec[0], rec[1]] for rec in recs]

		else:
			# REGION from nhood DB case
			nhoods = tuple([int(nid) for nid in anyjson.loads(open('data/' + my.DATA_FOLDER + 'hood_ids.txt', 'rb').read())])

			SQL = 'SELECT user_id, ST_X(geo), ST_Y(geo)\
						FROM {rel_home} \
						WHERE ST_Within (geo, ST_UNION( \
							ARRAY(SELECT pol FROM {rel_nhood} \
								WHERE id IN %s)))'.format(rel_home=my.REL_HOME, rel_nhood=my.REL_NHOOD)

			cur.execute(SQL, (nhoods, ))
			recs = cur.fetchall()
			
			user_ids = [rec[0] for rec in recs]
			homes = [[rec[1], rec[2]] for rec in recs]

	#with open('data/' + my.DATA_FOLDER + 'city_bound_pol2.txt', 'rb') as fpr:
	#		bound_pol = fpr.read().strip()

	SQL = 'SELECT ST_X(geo), ST_Y(geo)\
				FROM {rel_tweet} \
				WHERE user_id IN %s'.format(rel_tweet=my.REL_TWEET)
	#			AND geo && ST_GeomFromGeoJSON(%s)'.format(rel_tweet=my.REL_TWEET)
	#cur.execute(SQL, (tuple(user_ids), bound_pol))
	cur.execute(SQL, (tuple(user_ids), ))
	recs = cur.fetchall()

	points = [[rec[0], rec[1]] for rec in recs]
	con.close()

	print 'Fetched {n_h} homes, {n_l} latlngs.'.format(n_h=len(homes), n_l=len(points))

	if not os.path.exists('data/' + my.DATA_FOLDER + 'region/'):
			os.makedirs('data/' + my.DATA_FOLDER + 'region/')
	with open('data/' + my.DATA_FOLDER + 'region/' + 'homes.json', 'wb') as fp:
		fp.write(anyjson.dumps(homes))
	with open('data/' + my.DATA_FOLDER + 'region/' + 'points.json', 'wb') as fp:
		fp.write(anyjson.dumps(points))


def out_nhood_latlng_json():
# Output: JSON of latlng by users of each nhood in region
	con = psycopg2.connect(my.DB_CONN_STRING)
	cur = con.cursor()

	nhoods = tuple([int(nid) for nid in anyjson.loads(open('data/' + my.DATA_FOLDER + 'hood_ids.txt', 'rb').read())])
	nhood_points = {}

	with open('data/' + my.DATA_FOLDER + 'bound_pol.txt', 'rb') as fpr:
		bound_pol = fpr.read().strip()

	for h_id in nhoods:
		print h_id
		SQL = 'SELECT user_id \
					FROM {rel_home} \
					WHERE ST_Within (geo, \
						(SELECT pol FROM {rel_nhood} \
							WHERE id=%s))'.format(rel_home=my.REL_HOME, rel_nhood=my.REL_NHOOD)
		
		cur.execute(SQL, (h_id, ))
		recs = cur.fetchall()
		user_ids = [rec[0] for rec in recs]

		if len(user_ids) > 0:
			SQL = 'SELECT ST_X(geo), ST_Y(geo)\
						FROM {rel_tweet} \
						WHERE user_id IN %s \
						AND geo && ST_GeomFromGeoJSON(%s)'.format(rel_tweet=my.REL_TWEET)
			cur.execute(SQL, (tuple(user_ids), bound_pol))
			recs = cur.fetchall()

			if len(recs) > 0:
				nhood_points[h_id] = [[rec[0], rec[1]] for rec in recs]
				print len(user_ids), len(nhood_points[h_id])
	con.close()

	if not os.path.exists('data/' + my.DATA_FOLDER + 'region/'):
			os.makedirs('data/' + my.DATA_FOLDER + 'region/')
	with open('data/' + my.DATA_FOLDER + 'region/' + 'nhood_points.json', 'wb') as fp:
		fp.write(anyjson.dumps(nhood_points))

################################################################################

def out_user_disp_plot():
# Plot charts for daily max displacement
	x = []
	with open('data/' + my.DATA_FOLDER + 'user_disp.csv', 'rb') as fp2:
		csv_reader = csv.reader(fp2, delimiter=',')
		for row in csv_reader:
			x.append(int(row[1]))
	print '%s daily max displacements read.' % (len(x))

	# plot
	_plot_hist(x, 99, (100,10000), '100m-10km')
	a, i = _plot_hist(x, 149, (100,15000), '100m-15km')
	print a, ',', i
	_plot_hist(x, 199,  (100,20000), '100m-20km')
	_plot_hist(x, 249,  (100,25000), '100m-25km')

def out_user_disp_plot_weekday():
# Plot charts for daily max displacement (Weekday/Weekend)
	x_wd = []
	x_we = []
	with open('data/' + my.DATA_FOLDER + 'user_disp.csv', 'rb') as fp2:
		csv_reader = csv.reader(fp2, delimiter=',')
		for row in csv_reader:
			dt = datetime.strptime(row[2], '%Y-%m-%d').date()
			if dt.weekday() in [5, 6]:
				x_we.append(int(row[1]))
			else:
				x_wd.append(int(row[1]))
	print 'Weekday: %s, Weekend: %s daily max displacements read.' % (len(x_wd), len(x_we))

	# plot
	_plot_hist(x_wd, 99, (100,10000), '100m-10km (weekday)')
	_plot_hist(x_we, 99, (100,10000), '100m-10km (weekend)')
	a, i = _plot_hist(x_wd, 149, (100,15000), '100m-15km (weekday)')
	print a, ',', i
	a, i = _plot_hist(x_we, 149, (100,15000), '100m-15km (weekend)')
	print a, ',', i
	_plot_hist(x_wd, 199,  (100,20000), '100m-20km (weekday)')
	_plot_hist(x_we, 199,  (100,20000), '100m-20km (weekend)')
	_plot_hist(x_wd, 249,  (100,25000), '100m-25km (weekday)')
	_plot_hist(x_we, 249,  (100,25000), '100m-25km (weekend)')
	

def _plot_hist(x, nbins, range, file_name):
	title = my.DATA_FOLDER[:-1].upper() + ' ' + file_name

	width = (range[1]-range[0])/nbins
	nbins_prev, nbins_after = math.ceil((range[0]-min(x))/width), math.ceil((max(x)-range[1])/width)
	h, b = numpy.histogram(x, nbins_prev+nbins+nbins_after)
	b = b[nbins_prev:-nbins_after]
	#print b, len(b)
	
	s = float(sum(h))
	h_prev = [round(val/s, 4) for val in h[:nbins_prev]]
	h_after = [round(val/s, 4) for val in h[-nbins_after:]]
	h = [round(val/s, 4) for val in h[nbins_prev:-nbins_after]]
	n_all = len(x)
	h_100_2k = round(len([val for val in x if val > 100 and val < 2000]) / float(len(x)), 4)

	#print len(x)
	#print h_100_2k
	#print len(h_prev), sum(h_prev)
	#print len(h), sum(h)
	#print len(h_after), sum(h_after)
	#print len(h_prev)+len(h)+len(h_after)
	#print sum(h_prev)*len(x) + sum(h)*len(x) + sum(h_after)*len(x)

	fig = plt.figure(figsize=(8,4))
	ax = fig.add_subplot(111)
	if my.PLOT_LABEL_ABS:
		plt.subplots_adjust(left=0.1, right=0.96, top=0.92, bottom=0.08)
	else:
		plt.subplots_adjust(left=0.075, right=0.96, top=0.92, bottom=0.08)
	#ax.set_autoscaley_on(False)
	#ax.set_ylim([0,0.1])
	ax.set_xlim(0, range[1])
	
	ax.bar(b[:-1], h, width=width, \
		color='#377EB8', alpha=0.8, edgecolor='#377EB8') 
	if my.PLOT_LABEL_ABS:
		formatter = FuncFormatter(lambda v, pos: str(int(v*n_all)) + '\n(' + str(round(v*100, 2)) + '%)')
	else:
		formatter = FuncFormatter(lambda v, pos: str(round(v*100, 2))+'%')
	plt.gca().yaxis.set_major_formatter(formatter)
	formatter = FuncFormatter(lambda v, pos: '' if v/1000 == 0 else str(int(v/1000))+'km')
	plt.gca().xaxis.set_major_formatter(formatter)
	if my.PLOT_LABEL_ABS:
		matplotlib.rc('ytick', labelsize=10)

	## Power law fit
	x = numpy.array(b[:-1])
	y = numpy.array([val if val != 0.0 else 0.0001 for val in h])
	logx = log10(x)
	logy = log10(y)
	
	fitfunc = lambda p, x: p[0] + p[1] * x
	errfunc = lambda p, x, y: (y - fitfunc(p, x))

	pinit = [1.0, -1.0]
	out = leastsq(errfunc, pinit, args=(logx, logy), full_output=1)
	pfinal = out[0]
	covar = out[1]
	index = pfinal[1]
	amp = 10.0**pfinal[0]
	
	powerlaw = lambda x, amp, index: amp * (x**index)
	ax.plot(x, powerlaw(x, amp, index), \
		label = 'fit: y = %s x ^%s' % (round(amp,3), round(index,3)), color='#E41A1C') 

	ax.text(0.95, 0.95, \
		'<{0}m = {1}%\n >{2}km = {3}%\n 100m-2km = {4}%'.format(range[0], sum(h_prev)*100, range[1]/1000, sum(h_after)*100, h_100_2k*100) + \
		'\nfit: y = {0} x^{1}'.format(round(amp,3), round(index,3)), \
		 horizontalalignment='right', verticalalignment='top', transform = ax.transAxes, fontsize=10)
	
	ax.set_title(title, fontsize=11)

	if not os.path.exists('data/' + my.DATA_FOLDER + 'disp_stat/'):
		os.makedirs('data/' + my.DATA_FOLDER + 'disp_stat/')
	plt.savefig('data/' + my.DATA_FOLDER + 'disp_stat/' + file_name + '.png')
	print 'Stored chart: %s' % file_name

	return amp, index


################################################################################
# Load lost of all nhoods in region
_load_nhoodIDs = lambda: [int(nid) for nid in anyjson.loads(open('data/' + my.DATA_FOLDER + 'hood_ids.txt', 'rb').read())]

def out_super_disp_plot():
# Plot displacement from home for all users in region
	# Read user_ids
	if my.USER_IDS_FROM_DB:
		con = psycopg2.connect(my.DB_CONN_STRING)
		cur = con.cursor()
		SQL = 'SELECT user_id \
					FROM t4_home \
					WHERE ST_Within (geo, ST_UNION( \
						ARRAY(SELECT pol FROM t4_nhood \
							WHERE id in %s)))'
		cur.execute(SQL, (tuple(_load_nhoodIDs()), ))
		records = cur.fetchall()
		con.close()
		user_ids = [int(rec[0]) for rec in records]

	else:
		with open('data/' + my.DATA_FOLDER + 'user_list.csv', 'rb') as fpr:
			cr = csv.reader(fpr, delimiter=',')
			user_ids = [int(row[0]) for row in cr]

	print 'Read {0} user_ids'.format(len(user_ids))

	# Plot super displacement plot
	x, y = [], []

	with open('data/' + my.DATA_FOLDER + 'city_bound_pol.txt', 'rb') as fpr:
		bound_pol = fpr.read().strip()

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
			#print home

			# Read all latlng pairs
			SQL = 'SELECT ST_X(geo), ST_Y(geo) \
					FROM t3_tweet_6 \
					WHERE user_id = %s \
					AND geo && ST_GeomFromGeoJSON(%s) '\
					+ my.QUERY_CONSTRAINT
			cur.execute(SQL, (user_id, bound_pol))
			records = cur.fetchall()

			# Append all latlng pairs
			for rec in records:
				lat, lng = rec
				x.append(lng-home[1])
				y.append(lat-home[0])

		else:
			print 'Missed 1 user_id!'

	con.close()
	
	## Displacement plot
	fig = plt.figure(figsize=(5,5))
	ax = fig.add_subplot(111)
	plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
	ax.set_autoscaley_on(False)
	ax.set_ylim([-0.5,0.5])
	ax.set_xlim([-0.5,0.5])
	ax.set_yticks([0.0])
	ax.set_xticks([0.0])
	ax.set_yticklabels([])
	ax.set_xticklabels([])
	ax.grid(True)
	ax.plot(x, y, 'b,', alpha=0.75)
	ax.plot([0], [0], 'r^')
	ax.text(-0.45, -0.45, my.DATA_FOLDER.replace('/', '').upper(), fontsize=10)
	
	plt.savefig('data/' + my.DATA_FOLDER + 'plot_disp__super' + '.png')


################################################################################

def out_disp_map():
# Plot displacement for all users in region on map
	#_plot_disp_map(['hbk'], file_name='hbk')
	#_plot_disp_map(['south-la'], file_name='south-la')
	#_plot_disp_map(['west-la'], file_name='west-la')
	#_plot_disp_map(['south-bay'], file_name='south-bay')

	#_plot_disp_map(['pomona'], file_name='pomona')
	#_plot_disp_map(['bernardino'], file_name='bernardino')
	#_plot_disp_map(['riverside'], file_name='riverside')
	
	#_plot_disp_map(['hbk', 'south-la', 'west-la', 'south-bay'], file_name='hbk_sla_wla_bay')
	#_plot_disp_map(['pomona', 'bernardino', 'riverside'], file_name='pom_ber_riv')

	_plot_disp_map(['hbk', 'south-la', 'west-la', 'south-bay', 'pomona', 'bernardino', 'riverside'], file_name='hswspbr')

def _plot_disp_map(folders, file_name='disp-map'):
# Generate multi colored plot for all specified folders

	#colors = ['#4DAF4A','#3B3B3B','#984EA3','#E41A1C','#A65628','#FA71AF','#FF7F00','#377EB8']
	colors = {	'hbk': '#377EB8',
							'south-la' : '#FA71AF',
							'west-la' : '#4DAF4A',
							'south-bay' : '#A65628',
							'pomona' : '#3B3B3B',
							'bernardino' : '#984EA3',
							'riverside' : '#FF7F00'
						}
	
	fig = plt.figure(figsize=(18,12))
	fig.set_facecolor('w')
	ax = fig.add_subplot(111)
	plt.subplots_adjust(left=0.02, right=0.98, top=0.95, bottom=0.02)
	ax.set_autoscaley_on(False)
	ax.set_ylim([33.5, 34.29])
	ax.set_xlim([-118.64, -117.09])
	ax.set_yticklabels([])
	ax.set_xticklabels([])
	leg_markers, leg_labels = [], []
		
	for folder in folders:
		with open('data/' + my.DATA_FOLDER + folder + '/' + 'points.json', 'rb') as fpr:
			points = anyjson.loads(fpr.read())
		#pprint(points)

		x, y = [], []
		for pt in points:
			x.append(pt[1])
			y.append(pt[0])

		ax.plot(x, y, ',', color=colors[folder], alpha=1.0, label=folder.upper())
		leg_markers.append(Rectangle((0, 0), 1, 1, ec=colors[folder], fc=colors[folder]))
		leg_labels.append(folder.upper())
		
	leg = ax.legend(leg_markers, leg_labels, loc=4, fontsize=11)
	leg.get_frame().set_linewidth(0)
	ax.set_title(', '.join(folders).upper())
	plt.savefig('data/' + my.DATA_FOLDER + '_plots/' + file_name + '.png')

	ax.get_frame().set_alpha(0)
	background = matplotlib.image.imread('data/' + my.DATA_FOLDER + 'map.png')
	ax.imshow(background, aspect='auto', extent=(-118.64, -117.09, 33.5, 34.29), alpha=0.5)
	plt.savefig('data/' + my.DATA_FOLDER + '_plots-map/' + file_name + '.png')


################################################################################

def out_disp_map_pdf():
# Plot displacement for all users in region on map (PDF)
	combinations = [['hbk'], ['south-la'], ['west-la'], ['south-bay'], ['hbk', 'south-la', 'west-la', 'south-bay'],	['pomona'], ['bernardino'], ['riverside'], ['pomona', 'bernardino', 'riverside'],	['hbk', 'south-la', 'west-la', 'south-bay', 'pomona', 'bernardino', 'riverside']]

	pdf = PdfPages('data/' + my.DATA_FOLDER + '_plots/' + 'region_activity.pdf')
	pdf_map = PdfPages('data/' + my.DATA_FOLDER + '_plots-map/' + 'region_activity__map.pdf')

	for folders in combinations:
		print folders
		colors = {	'hbk': '#377EB8',
								'south-la' : '#FA71AF',
								'west-la' : '#4DAF4A',
								'south-bay' : '#A65628',
								'pomona' : '#3B3B3B',
								'bernardino' : '#984EA3',
								'riverside' : '#FF7F00'
							}
		
		fig = plt.figure(figsize=(6,4))
		fig.set_facecolor('w')
		ax = fig.add_subplot(111)
		plt.subplots_adjust(left=0.02, right=0.98, top=0.95, bottom=0.02)
		ax.set_autoscaley_on(False)
		ax.set_ylim([33.5, 34.29])
		ax.set_xlim([-118.64, -117.09])
		ax.set_yticklabels([])
		ax.set_xticklabels([])
		leg_markers, leg_labels = [], []
			
		for folder in folders:
			with open('data/' + my.DATA_FOLDER + folder + '/' + 'points.json', 'rb') as fpr:
				points = anyjson.loads(fpr.read())
			#pprint(points)

			x, y = [], []
			for pt in points:
				x.append(pt[1])
				y.append(pt[0])

			ax.plot(x, y, ',', color=colors[folder], alpha=1.0, label=folder.upper())
			leg_markers.append(Rectangle((0, 0), 1, 1, ec=colors[folder], fc=colors[folder]))
			leg_labels.append(folder.upper())
			
		leg = ax.legend(leg_markers, leg_labels, loc=4, fontsize=10)
		leg.get_frame().set_linewidth(0)
		ax.set_title(', '.join(folders).upper())
		#plt.savefig(pdf, format='pdf')
		pdf.savefig()

		ax.get_frame().set_alpha(0)
		background = matplotlib.image.imread('data/' + my.DATA_FOLDER + 'map.png')
		ax.imshow(background, aspect='auto', extent=(-118.64, -117.09, 33.5, 34.29), alpha=0.5)
		#plt.savefig(pdf_map, format='pdf')
		pdf_map.savefig()

	pdf.close()
	pdf_map.close()


