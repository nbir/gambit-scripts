# Gambit scripts
#
# Copyright (C) USC Information Sciences Institute
# Author: Nibir Bora <nbora@usc.edu>
# URL: <http://cbg.isi.edu/>
# For license information, see LICENSE

import os
import sys
import csv
import math
import anyjson
import psycopg2
import shapefile
import matplotlib
import matplotlib.pyplot as plt

from pylab import *
from PIL import Image
from pprint import pprint
from matplotlib import cm
from datetime import datetime, timedelta
from mpl_toolkits.basemap import Basemap
from matplotlib.collections import LineCollection
from matplotlib.collections import PolyCollection

import settings as my
sys.path.insert(0, os.path.abspath('..'))


#
# TWEET ACTIVITY ON MAP
#
def plot_on_map():
	'''Plot all geo-tagged tweets on map'''
	if not os.path.exists('data/' + my.DATA_FOLDER + 'plots/'):
		os.makedirs('data/' + my.DATA_FOLDER + 'plots/')
	SQL = 'SELECT ST_X(geo), ST_Y(geo)\
			FROM {rel_tweet} \
			WHERE geo IS NOT NULL'.format(rel_tweet=my.REL_TWEET)

	con = psycopg2.connect(my.DB_CONN_STRING)
	cur = con.cursor()
	cur.execute(SQL)
	recs = cur.fetchall()
	con.close()
	lats = [rec[0] for rec in recs]
	lons = [rec[1] for rec in recs]

	# World
	fig=plt.figure(figsize=(16,10))
	m = Basemap(llcrnrlon=-180, llcrnrlat=-75, urcrnrlon=180, urcrnrlat=85,
				projection='mill')
	m.drawcoastlines(linewidth=0.25)
	m.drawcountries(linewidth=0.1)
	m.fillcontinents(color='#FF7F00', alpha=0.1)
	x, y = m(lons,lats)
	m.plot(x, y, '+', color='#377EB8', alpha=0.1)
	plt.tight_layout()
	plt.savefig('data/' + my.DATA_FOLDER + 'plots/' + 'all_geo_world' + '.png')


	# USA
	fig=plt.figure(figsize=(16,10))
	m = Basemap(llcrnrlon=-130, llcrnrlat=15, urcrnrlon=-60, urcrnrlat=55,
				projection='mill')
	#m.shadedrelief()
	m.drawcoastlines(linewidth=0.25)
	m.drawcountries(linewidth=0.1)
	m.drawstates(linewidth=0.1)
	m.fillcontinents(color='#FF7F00', alpha=0.1)
	x, y = m(lons,lats)
	m.plot(x, y, '+', color='#377EB8', alpha=0.1)
	plt.tight_layout()
	plt.savefig('data/' + my.DATA_FOLDER + 'plots/' + 'all_geo_usa' + '.png')
	

	# New York
	fig=plt.figure(figsize=(16,10))
	ax=fig.add_subplot(111)
	m = Basemap(llcrnrlon=-74.65, llcrnrlat=40.25, 
				urcrnrlon=-73.25, urcrnrlat=41.0,
				projection='mill')

	r = shapefile.Reader('data/' + my.DATA_FOLDER + 'shp/' + 'USA_adm2')
	shapes = r.shapes()
	records = r.records()
	for record, shape in zip(records,shapes):
	    lons_,lats_ = zip(*shape.points)
	    data = np.array(m(lons_, lats_)).T
	 
	    if len(shape.parts) == 1:
	        segs = [data,]
	    else:
	        segs = []
	        for i in range(1,len(shape.parts)):
	            index = shape.parts[i-1]
	            index2 = shape.parts[i]
	            segs.append(data[index:index2])
	        segs.append(data[index2:])
	 
	    lines = LineCollection(segs,antialiaseds=(1,))
	    lines.set_facecolors((1, 0.5, 0, 0.1))
	    lines.set_edgecolors('k')
	    lines.set_linewidth(0.15)
	    ax.add_collection(lines)

	x, y = m(lons,lats)
	m.plot(x, y, '+', color='#377EB8', alpha=0.95)
	plt.tight_layout()
	plt.savefig('data/' + my.DATA_FOLDER + 'plots/' + 'all_geo_ny' + '.png')


	# Los Angeles
	fig=plt.figure(figsize=(16,10))
	ax=fig.add_subplot(111)
	#-118.7267991797,33.6002128689,-117.3109129492,34.3385056333
	m = Basemap(llcrnrlon=-118.75, llcrnrlat=33.6, 
				urcrnrlon=-117.30, urcrnrlat=34.35,
				projection='mill')

	r = shapefile.Reader('data/' + my.DATA_FOLDER + 'shp/' + 'USA_adm2')
	shapes = r.shapes()
	records = r.records()
	for record, shape in zip(records,shapes):
	    lons_,lats_ = zip(*shape.points)
	    data = np.array(m(lons_, lats_)).T
	 
	    if len(shape.parts) == 1:
	        segs = [data,]
	    else:
	        segs = []
	        for i in range(1,len(shape.parts)):
	            index = shape.parts[i-1]
	            index2 = shape.parts[i]
	            segs.append(data[index:index2])
	        segs.append(data[index2:])
	 
	    lines = LineCollection(segs,antialiaseds=(1,))
	    lines.set_facecolors((1, 0.5, 0, 0.1))
	    lines.set_edgecolors('k')
	    lines.set_linewidth(0.15)
	    ax.add_collection(lines)

	x, y = m(lons,lats)
	m.plot(x, y, '+', color='#377EB8', alpha=0.95)
	plt.tight_layout()
	plt.savefig('data/' + my.DATA_FOLDER + 'plots/' + 'all_geo_la' + '.png')



