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
from scipy.stats import ks_2samp
from scipy.optimize import leastsq
from matplotlib.ticker import FuncFormatter
from matplotlib.backends.backend_pdf import PdfPages

import settings as my
sys.path.insert(0, os.path.abspath('..'))


#
# DISPLACEMENT STATISTICS
#
def out_user_disp_plot():
	'''Plot charts for daily max displacement'''
	with open('data/' + my.DATA_FOLDER + 'displacement/' + 'user_disp.csv', 'rb') as fp2:
		csv_reader = csv.reader(fp2, delimiter=',')
		x = [int(row[1]) for row in csv_reader]
	print '%s daily max displacements read.' % (len(x))

	_plot_hist(x, 99, (100,10000), '100m-10km')
	a, i = _plot_hist(x, 149, (100,15000), '100m-15km')
	print a, ',', i
	_plot_hist(x, 199,  (100,20000), '100m-20km')
	_plot_hist(x, 249,  (100,25000), '100m-25km')

def out_user_disp_plot_weekday():
	'''Plot charts for daily max displacement (Weekday/Weekend)'''
	x_wd = []
	x_we = []
	with open('data/' + my.DATA_FOLDER + 'displacement/' + 'user_disp.csv', 'rb') as fp2:
		csv_reader = csv.reader(fp2, delimiter=',')
		for row in csv_reader:
			dt = datetime.strptime(row[2], '%Y-%m-%d').date()
			if dt.weekday() in [5, 6]:
				x_we.append(int(row[1]))
			else:
				x_wd.append(int(row[1]))
	print 'Weekday: %s, Weekend: %s daily max displacements read.' % (len(x_wd), len(x_we))

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

	# Power law fit
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
	info = '<{0}m = {1}%\n >{2}km = {3}%\n 100m-2km = {4}%'.format(range[0], sum(h_prev)*100, \
															range[1]/1000, sum(h_after)*100, h_100_2k*100) + \
		   '\nfit: y = {0} x^{1}'.format(round(amp,3), round(index,3))

	#KS Statistics
	y_ = powerlaw(x, amp, index)
	d, p = ks_2samp(y, y_)
	#print 'D, p: ', d, p
	info += '\nKS statistic: {0}\np: {1}'.format(round(d,5), round(p,5))

	ax.text(0.95, 0.95, info, horizontalalignment='right', verticalalignment='top', transform = ax.transAxes, fontsize=10)
	ax.set_title(title, fontsize=11)
	if not os.path.exists('data/' + my.DATA_FOLDER + 'displacement/' + 'disp_stat/'):
		os.makedirs('data/' + my.DATA_FOLDER + 'displacement/' + 'disp_stat/')
	plt.savefig('data/' + my.DATA_FOLDER + 'displacement/' + 'disp_stat/' + file_name + '.pdf')
	print 'Stored chart: %s' % file_name

	return amp, index
