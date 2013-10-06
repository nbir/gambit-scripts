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
import numpy
import anyjson
import psycopg2
import matplotlib
import matplotlib.pyplot as plt

from pylab import *
from PIL import Image
from pprint import pprint
from datetime import datetime
from scipy.optimize import leastsq
from matplotlib.ticker import FuncFormatter
from matplotlib.collections import PolyCollection
from matplotlib.font_manager import FontProperties
from matplotlib.backends.backend_pdf import PdfPages

import settings as my
sys.path.insert(0, os.path.abspath('..'))


#
# TWEET ACTIVITY ON MAP
#
def plot_activity_on_map():
	'''Plot displacement for all users in region on map'''
	if not os.path.exists('data/' + my.DATA_FOLDER + '_plots/'):
		os.makedirs('data/' + my.DATA_FOLDER + '_plots/')
	if not os.path.exists('data/' + my.DATA_FOLDER + '_plots_map/'):
		os.makedirs('data/' + my.DATA_FOLDER + '_plots_map/')

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
	#_plot_disp_map(['hbk', 'south-la', 'west-la', 'south-bay', 'pomona', 'bernardino', 'riverside'], file_name='_high_res')

def _plot_disp_map(folders, file_name='disp-map'):
	'''Generate multi colored plot for all specified folders'''
	#colors = ['#4DAF4A','#3B3B3B','#984EA3','#E41A1C','#A65628','#FA71AF','#FF7F00','#377EB8']
	colors = {'hbk'		: '#377EB8',
			'south-la' 	: '#FF71AF',
			'west-la' 	: '#4DAF4A',
			'south-bay' : '#A65628',
			'pomona' 	: '#3B3B3B',
			'bernardino': '#984EA3',
			'riverside' : '#FF7F00'}

	text = {'hbk'		: 'Eastside',
			'south-la' 	: 'South LA',
			'west-la' 	: 'West LA',
			'south-bay' : 'South Bay',
			'pomona' 	: 'Pomona',
			'bernardino': 'Bernardino',
			'riverside' : 'Riverside'}
	
	fig = plt.figure(figsize=(9,6))
	#fig = plt.figure(figsize=(6,4))
	fig.set_tight_layout(True)
	fig.set_facecolor('w')
	ax = fig.add_subplot(111)
	ax.set_autoscaley_on(False)
	ax.set_ylim([33.5, 34.29])
	ax.set_xlim([-118.64, -117.09])
	ax.set_yticklabels([])
	ax.set_xticklabels([])
	leg_markers, leg_labels = [], []
		
	for folder in folders:
		with open('data/' + my.DATA_FOLDER + folder + '/' + 'points.json', 'rb') as fpr:
			points = anyjson.loads(fpr.read())
		x, y = [], []
		for pt in points:
			x.append(pt[1])
			y.append(pt[0])
		ax.plot(x, y, ',', color=colors[folder], alpha=0.75, label=folder.upper())
		#ax.text(0.5, 0.05, text[folder], ha='center', va='bottom', 
		#		transform = ax.transAxes, family='monospace', fontsize=35)
		leg_markers.append(Rectangle((0, 0), 1, 1, ec=colors[folder], fc=colors[folder]))
		leg_labels.append(folder.replace('hbk', 'eastside').upper())
		
	leg = ax.legend(leg_markers, leg_labels, loc=4, fontsize=10)
	leg.get_frame().set_linewidth(0)
	#ax.set_title(', '.join(folders).upper())
	plt.savefig('data/' + my.DATA_FOLDER + '_plots/' + file_name + '.png')

	ax.get_frame().set_alpha(0)
	background = matplotlib.image.imread('data/' + my.DATA_FOLDER + 'map.png')
	ax.imshow(background, aspect='auto', extent=(-118.64, -117.09, 33.5, 34.29), alpha=0.5)
	plt.savefig('data/' + my.DATA_FOLDER + '_plots_map/' + file_name + '.png')



#
# PLOT MAP OF LA
#
def plot_la_map():

	hood_info = _load_hood_data()

	hb = [2699, 2738, 2744, 2804]
	sl = [2673,2684,2689,2702,2710,2716,2749,2751,2752,2757,2759,2768,2775,2780,2784,2801,2812,2881,2911,2912,2913,2914,2917,2921,2922,2935,2939]
	wl = [2727,2728,2743,2772,2813,2814,2815,2846,2847,2855,2870,2871,2910,2932]
	sb = [2706,2765,2766,2806,2839,2853,2858,2859,2867,2897,2923,2940]
	br = [99991]
	po = [99992]
	ri = [99993]
	
	pols = []
	pols_hb = []
	pols_sl = []
	pols_wl = []
	pols_sb = []
	pols_br = []
	pols_po = []
	pols_ri = []
	
	for h_id in hood_info:
		pol = hood_info[h_id]['polygon'][:-1]
		pol = [[ll[1], ll[0]] for ll in pol]

		if h_id in hb:
			pols_hb.append(pol)
		elif h_id in sl:
			pols_sl.append(pol)
		elif h_id in wl:
			pols_wl.append(pol)
		elif h_id in sb:
			pols_sb.append(pol)
		elif h_id in br:
			pols_br.append(pol)
		elif h_id in po:
			pols_po.append(pol)
		elif h_id in ri:
			pols_ri.append(pol)
		else:
			pols.append(pol)
	print len(pols), len(pols_hb), len(pols_sl), len(pols_wl), len(pols_sb), len(pols_br), len(pols_po), len(pols_ri)

	fig = plt.figure(figsize=(9,6))
	#fig.set_tight_layout(True)
	fig.set_facecolor('w')
	plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)

	ax = fig.add_subplot(111)
	ax.set_autoscaley_on(False)
	ax.set_ylim([33.5, 34.29])
	ax.set_xlim([-118.64, -117.09])
	ax.set_yticklabels([])
	ax.set_xticklabels([])

	"""
	m = Basemap(llcrnrlon=-118.75, llcrnrlat=33.6, 
				urcrnrlon=-117.30, urcrnrlat=34.35,
				projection='mill')
	r = shapefile.Reader('data/' + my.DATA_FOLDER + 'shp/' + 'USA_adm2')
	shapes = r.shapes()
	records = r.records()
	"""

	leg_markers, leg_labels = [], []
		
	edge_color = '#000000'
	#ax.add_collection(PolyCollection(pols, facecolors='#ffffff', edgecolors=edge_color, alpha=0.35))
	ax.add_collection(PolyCollection(pols_hb, facecolors=my.COLORS['hbk'], edgecolors=edge_color, alpha=0.5))
	ax.add_collection(PolyCollection(pols_sl, facecolors=my.COLORS['south-la'], edgecolors=edge_color, alpha=0.5))
	ax.add_collection(PolyCollection(pols_wl, facecolors=my.COLORS['west-la'], edgecolors=edge_color, alpha=0.5))
	ax.add_collection(PolyCollection(pols_sb, facecolors=my.COLORS['south-bay'], edgecolors=edge_color, alpha=0.5))
	ax.add_collection(PolyCollection(pols_br, facecolors=my.COLORS['bernardino'], edgecolors=edge_color, alpha=0.5))
	ax.add_collection(PolyCollection(pols_po, facecolors=my.COLORS['pomona'], edgecolors=edge_color, alpha=0.5))
	ax.add_collection(PolyCollection(pols_ri, facecolors=my.COLORS['riverside'], edgecolors=edge_color, alpha=0.5))

	ax.text(-118.19503784179688, 34.04697021261827, 'EASTSIDE', ha='center', va='center', fontsize=12, fontproperties=FontProperties(weight='bold'))
	ax.text(-118.29391479492188, 33.99802726234877, 'SOUTH LA', ha='center', va='center', fontsize=12, fontproperties=FontProperties(weight='bold'))
	ax.text(-118.3941650390625, 33.89207743274474, 'WEST LA', ha='center', va='center', fontsize=12, fontproperties=FontProperties(weight='bold'))
	ax.text(-118.32000732421875, 33.799691173251105, 'SOUTH BAY', ha='center', va='center', fontsize=12, fontproperties=FontProperties(weight='bold'))
	ax.text(-117.366943359375, 34.099296530126665, 'SAN BERNARDINO', ha='center', va='center', fontsize=12, fontproperties=FontProperties(weight='bold'))
	ax.text(-117.66494750976562, 34.08451193447477, 'POMONA', ha='center', va='center', fontsize=12, fontproperties=FontProperties(weight='bold'))
	ax.text(-117.5152587890625, 33.94222067051576, 'RIVERSIDE', ha='center', va='center', fontsize=12, fontproperties=FontProperties(weight='bold'))
		

	#leg = ax.legend(leg_markers, leg_labels, loc=4, fontsize=10)
	#leg.get_frame().set_linewidth(0)
	#ax.set_title(', '.join(folders).upper())
	plt.savefig('data/' + my.DATA_FOLDER + 'map_la' + '.png')

	ax.get_frame().set_alpha(0)
	background = matplotlib.image.imread('data/' + my.DATA_FOLDER + 'map.png')
	ax.imshow(background, aspect='auto', extent=(-118.64, -117.09, 33.5, 34.29), alpha=0.95)
	plt.savefig('data/' + my.DATA_FOLDER + 'map_la2' + '.pdf')

	background = matplotlib.image.imread('data/' + my.DATA_FOLDER + 'map2.png')
	ax.imshow(background, aspect='auto', extent=(-118.64, -117.09, 33.5, 34.29), alpha=0.15)
	plt.savefig('data/' + my.DATA_FOLDER + 'map_la3' + '.pdf')




_load_hood_data = lambda: dict([(int(loc['id']), loc) for loc in anyjson.loads(open('data/' + my.DATA_FOLDER + 'all_hoods_data.json', 'rb').read())])