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
from matplotlib.backends.backend_pdf import PdfPages

import settings as my
sys.path.insert(0, os.path.abspath('..'))


#
# TWEET ACTIVITY ON MAP
#
def plot_activity_on_map():
	'''Plot displacement for all users in region on map'''
	#_plot_disp_map(['hbk'], file_name='hbk')
	#_plot_disp_map(['south-la'], file_name='south-la')
	#_plot_disp_map(['west-la'], file_name='west-la')
	#_plot_disp_map(['south-bay'], file_name='south-bay')

	#_plot_disp_map(['pomona'], file_name='pomona')
	_plot_disp_map(['bernardino'], file_name='bernardino')
	#_plot_disp_map(['riverside'], file_name='riverside')
	
	#_plot_disp_map(['hbk', 'south-la', 'west-la', 'south-bay'], file_name='hbk_sla_wla_bay')
	#_plot_disp_map(['pomona', 'bernardino', 'riverside'], file_name='pom_ber_riv')

	#_plot_disp_map(['hbk', 'south-la', 'west-la', 'south-bay', 'pomona', 'bernardino', 'riverside'], file_name='hswspbr')

def _plot_disp_map(folders, file_name='disp-map'):
	'''Generate multi colored plot for all specified folders'''
	#colors = ['#4DAF4A','#3B3B3B','#984EA3','#E41A1C','#A65628','#FA71AF','#FF7F00','#377EB8']
	colors = {'hbk'		: '#377EB8',
			'south-la' 	: '#FA71AF',
			'west-la' 	: '#4DAF4A',
			'south-bay' : '#A65628',
			'pomona' 	: '#3B3B3B',
			'bernardino': '#984EA3',
			'riverside' : '#FF7F00'}
	
	fig = plt.figure(figsize=(12,8))
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


