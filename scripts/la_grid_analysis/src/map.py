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
import jsbeautifier as jsb
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
def plot_grid():
	'''Plot all geo-tagged tweets on map'''
	lat1, lng1, lat2, lng2 = my.BBOX
	xticks = np.arange(lng1, lng2, my.LNG_DELTA).tolist()
	xticks.append(lng2)
	print xticks
	yticks = np.arange(lat1, lat2 + my.LAT_DELTA, my.LAT_DELTA).tolist()

	fig=plt.figure(figsize=(18,13))
	fig.set_tight_layout(True)
	ax=fig.add_subplot(111)
	m = Basemap(llcrnrlon=lng1, llcrnrlat=lat1, 
				urcrnrlon=lng2, urcrnrlat=lat2,
				projection='mill')
	ax.set_xlim(lng1, lng2)
	ax.set_ylim(lat1, lat2)
	ax.set_xticks(xticks)
	ax.set_yticks(yticks)
	#ax.grid(ls='-')
	ax.grid(ls='--', lw=1.25)
	plt.setp(plt.xticks()[1], rotation=90)

	bg = matplotlib.image.imread('data/' + my.DATA_FOLDER + 'map.png')
	ax.imshow(bg, aspect='auto', extent=(lng1, lng2, lat1, lat2), alpha=0.9)

	plt.savefig('data/' + my.DATA_FOLDER + 'grid' + '.png')

	yticks.reverse()

	grid = {
		'bbox' : my.BBOX,
		'lat_delta' : my.LAT_DELTA,
		'lng_delta' : my.LNG_DELTA,
		'xticks' : [round(i, 3) for i in xticks],
		'yticks' : [round(i, 3) for i in yticks],
		'rows' : len(yticks) - 1,
		'columns' : len(xticks) - 1,
		'cells' : (len(yticks) - 1) * (len(xticks) - 1),
		'grid' : {},
		#'grid_lookup' : {}
	}

	i = 0
	for r in range(len(yticks) - 1):
		#grid['grid_lookup'][round(yticks[r+1], 3)] = {}
		for c in range(len(xticks) - 1):
			grid['grid'][i] = (	round(yticks[r+1], 3), 
								round(xticks[c], 3), 
								round(yticks[r], 3), 
								round(xticks[c+1], 3))
			#grid['grid_lookup'][round(yticks[r+1], 3)][round(xticks[c], 3)] = i
			i += 1	

	with open('data/' + my.DATA_FOLDER + 'grid.json', 'wb') as fp:
		fp.write(jsb.beautify(anyjson.dumps(grid)))

