# -*- coding: utf-8 -*-

# Find home lat-lng from a given set of points
#	using DBScan clustering algorithm
#
# Copyright (C) USC Information Sciences Institute
# Author: Nibir Bora <nbora@usc.edu>
# URL: <http://cbg.isi.edu/>
# For license information, see LICENSE
#
#
# REQUIREMENTS:
#	=============
#	numpy
#	scipy
#	sklearn
#
# FUNCTIONS:
#	==========
#		FindHome(points, eps, min_samples, verbose=False)
#		getHome()
#		getCenters()


import numpy as np
from scipy.spatial import distance
from sklearn.cluster import DBSCAN


class FindHome:
	# Class variables
	#		home = [lat, lng]
	#		centers = [[lat, lng], ...]

	def __init__(self, points, eps, min_samples, verbose=False):
		'''
		@param:
			points 			=	[[lat, lng], ...]
			eps					:	DBScan epsilon parameter
			min_samples	:	DBScan minimum points parameter
			verbose			:	True - show screen outputs

		Calls self._runDBScan() with given parameters.
		'''
		self.home = None
		self.centers = None
		self._runDBScan(points, eps, min_samples, verbose)


	def _runDBScan(self, points, eps, min_samples, verbose):
		'''
		@param:
			points 			=	[[lat, lng], ...]
			eps					:	DBScan epsilon parameter
			min_samples	:	DBScan minimum points parameter
			verbose			:	True - show screen outputs

		Sets self.home and self.centers.
		'''
		# Output string for verbose mode
		COUT = ''
		# CALC_CENTER(points=[[lat, lng], ...]) = [lat, lng]
		# 	calculates centroid of points
		CALC_CENTER = lambda points: [round(sum([ll[0] for ll in points])/float(len(points)), 6), \
																	round(sum([ll[1] for ll in points])/float(len(points)), 6)]

		try:
			# Run DBScan clustering
			D = distance.squareform(distance.pdist(points))
			S = 1 - (D / np.max(D))
			db = DBSCAN(eps=eps, min_samples=min_samples).fit(S)
			core_samples = db.core_sample_indices_
			labels = db.labels_
			_labels = list(labels)

			COUT += 'Predictions:'.rjust(20) + '\t{predict}\n'.format(predict=dict([(i, _labels.count(i)) for i in set(_labels)]))
			
			label_counts = dict([(i, _labels.count(i)) for i in set(_labels) if i != -1 and i != -1.0])
			# Compute home and centers if there are >1 valid clusters
			if len(label_counts) > 0:
				# Computer home
				label_max = max(label_counts, key=label_counts.get)
				home_point_index = [i for i in core_samples if labels[i] == label_max]
				home_points = [points[i] for i in home_point_index]
				home = CALC_CENTER(home_points)
				self.home = home

				COUT += 'Home cluster label:'.rjust(20) + '\t{label}\n'.format(label=label_max) + 'count:'.rjust(20) + '\t{count_i} / {count}\n'.format(count_i=len(home_point_index), count=len(home_points))
				COUT +=  'Home latlng :'.rjust(20) + '\t{home}\n'.format(home=home)

				# Compute other cluster centroids
				other_labels = [i for i in label_counts if i != label_max]
				if len(other_labels) > 0:
					self.centers = []
					for label in other_labels:
						label_point_index = [i for i in core_samples if labels[i] == label]
						label_points = [points[i] for i in label_point_index]
						center = CALC_CENTER(home_points)
						self.centers.append(center)

			else:
				self.home = None
				COUT += 'Home cluster was not found!\n'
		except:
			COUT += 'Error in calculation!\n'

		if verbose:
			print COUT + '\n'


	def getHome(self):
		'''
		Returns self.home
		Format 	:	[lat, lng]
		'''
		return self.home

	def getCenters(self):
		'''
		Returns self.centers
		Format 	:	[[lat, lng], ...]
		'''
		return self.centers

	
				

