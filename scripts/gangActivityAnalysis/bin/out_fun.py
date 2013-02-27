# Gambit scripts
#
# Copyright (C) USC Information Sciences Institute
# Author: Nibir Bora <nbora@usc.edu>
# URL: <http://cbg.isi.edu/>
# For license information, see LICENSE


import sys
import os
sys.path.insert(0, os.path.abspath('..'))
import settings as my

import csv
import anyjson
import lib.geo as geo
import lib.PiP_Edge as pip

import bin.load_fun as load
import bin.prep_fun as prep



def generate_output(metrics_folder='metrics/'):
	measure1 = {}
	measure2 = {}
	tty_names = load.loadLocNames()

	visitation_sum = ''
	visitation_sum_norm = ''
	visitation_avg = ''
	visitation_avg_norm = ''

	each_gang = ''
	each_gang_norm = ''

	series_rival = []
	series_nonrival = []
	series_rival_norm = []
	series_nonrival_norm = []

	with open('data/' + my.DATA_FOLDER + metrics_folder + 'measure1.json', 'rb') as fp1:
		measure1 = anyjson.deserialize(fp1.read())
	with open('data/' + my.DATA_FOLDER + metrics_folder + 'measure2.json', 'rb') as fp1:
		measure2 = anyjson.deserialize(fp1.read())

	for gang_id in measure1:
		if not (len(measure1[gang_id]['rival']) == 0 and len(measure1[gang_id]['nonrival']) == 0):
			visitation_sum += tty_names[int(gang_id)] + ',' + str(sum(measure1[gang_id]['rival'])) + ', ' + str(sum(measure1[gang_id]['nonrival'])) + '\n'
			visitation_avg += tty_names[int(gang_id)] + ',' + str(0 if len(measure1[gang_id]['rival']) == 0 else round(sum(measure1[gang_id]['rival'])/float(len(measure1[gang_id]['rival'])), 5)) + ', ' + str(0 if len(measure1[gang_id]['nonrival']) == 0 else round(sum(measure1[gang_id]['nonrival'])/float(len(measure1[gang_id]['nonrival'])), 5) ) + '\n'

			each_gang += "name = '" + tty_names[int(gang_id)] + "'\n"
			each_gang += 'rival = ' + arr_to_str(measure1[gang_id]['rival']) + '\n'
			each_gang += 'nonrival = ' + arr_to_str(measure1[gang_id]['nonrival']) + '\n\n'

			series_rival += measure1[gang_id]['rival']
			series_nonrival += measure1[gang_id]['nonrival']
	visit_series = 'rival = ' + arr_to_str(series_rival) + '\n' + 'nonrival = ' + arr_to_str(series_nonrival)
	
	if not os.path.exists('data/' + my.DATA_FOLDER + metrics_folder + 'out/'):
		os.makedirs('data/' + my.DATA_FOLDER + metrics_folder + 'out/')
	with open('data/' + my.DATA_FOLDER + metrics_folder + 'out/' + 'visitation_sum' + '.csv', 'wb') as fp:
		fp.write(visitation_sum)
	with open('data/' + my.DATA_FOLDER + metrics_folder + 'out/' + 'visitation_avg' + '.csv', 'wb') as fp:
		fp.write(visitation_avg)
	with open('data/' + my.DATA_FOLDER + metrics_folder + 'out/' + 'each_gang' + '.txt', 'wb') as fp:
		fp.write(each_gang)
	with open('data/' + my.DATA_FOLDER + metrics_folder + 'out/' + 'visit_series' + '.txt', 'wb') as fp:
		fp.write(visit_series)

	for gang_id in measure2:
		if not (len(measure2[gang_id]['rival']) == 0 and len(measure2[gang_id]['nonrival']) == 0):
			visitation_sum_norm += tty_names[int(gang_id)] + ',' + str(sum(measure2[gang_id]['rival'])) + ', ' + str(sum(measure2[gang_id]['nonrival'])) + '\n'
			visitation_avg_norm += tty_names[int(gang_id)] + ',' + str(0 if len(measure2[gang_id]['rival']) == 0 else round(sum(measure2[gang_id]['rival'])/float(len(measure2[gang_id]['rival'])), 5)) + ', ' + str(0 if len(measure2[gang_id]['nonrival']) == 0 else round(sum(measure2[gang_id]['nonrival'])/float(len(measure2[gang_id]['nonrival'])), 5) ) + '\n'

			each_gang_norm += "name = '" + tty_names[int(gang_id)] + "'\n"
			each_gang_norm += 'rival = ' + arr_to_str(measure2[gang_id]['rival']) + '\n'
			each_gang_norm += 'nonrival = ' + arr_to_str(measure2[gang_id]['nonrival']) + '\n\n'

			series_rival_norm += measure2[gang_id]['rival']
			series_nonrival_norm += measure2[gang_id]['nonrival']
	visit_series_norm = 'rival = ' + arr_to_str(series_rival_norm) + '\n' + 'nonrival = ' + arr_to_str(series_nonrival_norm)

	with open('data/' + my.DATA_FOLDER + metrics_folder + 'out/' + 'visitation_sum_norm' + '.csv', 'wb') as fp:
		fp.write(visitation_sum_norm)
	with open('data/' + my.DATA_FOLDER + metrics_folder + 'out/' + 'visitation_avg_norm' + '.csv', 'wb') as fp:
		fp.write(visitation_avg_norm)
	with open('data/' + my.DATA_FOLDER + metrics_folder + 'out/' + 'each_gang_norm' + '.txt', 'wb') as fp:
		fp.write(each_gang_norm)
	with open('data/' + my.DATA_FOLDER + metrics_folder + 'out/' + 'visit_series_norm' + '.txt', 'wb') as fp:
		fp.write(visit_series_norm)

	#-CH
	try:
		measure3 = {}
		with open('data/' + my.DATA_FOLDER + metrics_folder + 'measure3.json', 'rb') as fp1:
			measure3 = anyjson.deserialize(fp1.read())
		m3_visitation_sum = ''
		m3_visitation_avg = ''
		for gang_id in measure3:
			if not (len(measure3[gang_id]['rival']) == 0 and len(measure3[gang_id]['nonrival']) == 0):
				m3_visitation_sum += tty_names[int(gang_id)] + ',' \
					+ str(sum([(x[0]*(x[0]/x[1])) for x in measure3[gang_id]['rival']])) + ', ' \
					+ str(sum([(x[0]*(x[0]/x[1])) for x in measure3[gang_id]['nonrival']])) + '\n'
				m3_visitation_avg += tty_names[int(gang_id)] + ',' \
					+ str(0 if len(measure3[gang_id]['rival']) == 0 else round(sum([(x[0]*(x[0]/x[1])) for x in measure3[gang_id]['rival']])/float(len(measure3[gang_id]['rival'])), 5)) + ', ' \
					+ str(0 if len(measure3[gang_id]['nonrival']) == 0 else round(sum([(x[0]*(x[0]/x[1])) for x in measure3[gang_id]['nonrival']])/float(len(measure3[gang_id]['nonrival'])), 5) ) + '\n'
		
		with open('data/' + my.DATA_FOLDER + metrics_folder + 'out/' + 'm3_visitation_sum' + '.csv', 'wb') as fp:
			fp.write(m3_visitation_sum)
		with open('data/' + my.DATA_FOLDER + metrics_folder + 'out/' + 'm3_visitation_avg' + '.csv', 'wb') as fp:
			fp.write(m3_visitation_avg)
	except Exception:
		print 'Error in generating output for measure3.'


def arr_to_str(arr):
	arr_str = ''
	for val in arr:
		arr_str += str(val) + ','
	return '[' + arr_str[:-1] + ']'
