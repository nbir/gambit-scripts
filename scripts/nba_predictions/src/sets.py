# Gambit scripts
#
# Copyright (C) USC Information Sciences Institute
# Author: Nibir Bora <nbora@usc.edu>
# URL: <http://cbg.isi.edu/>
# For license information, see LICENSE

import os
import sys
import csv
import nltk
import time
import anyjson
import itertools
import lxml.html

from pprint import pprint
from nltk.corpus import stopwords

import settings as my
sys.path.insert(0, os.path.abspath('..'))


#
# TEAM SETS
#
def make_team_sets():
	''' '''
	vocab = []
	legend = {}
	sets = {} 
	with open('data/' + my.DATA_FOLDER + 'teams.txt', 'rb') as fp:
		cr = csv.reader(fp, delimiter=',')
		id = 0
		for row in cr:
			id += 1
			name = row.pop(0).strip().replace('.','')
			tw_id = row.pop().strip().replace('@','')
			htags = [h.strip().replace('#','') for h in row]
			print id, name, '\t', tw_id, htags
			legend[id] = name

			words = []
			words.append(tuple(n.lower() for n in name.split()))
			words.append(tw_id.lower())
			words.extend([h.lower() for h in htags])
			words = tuple(set(words))
			words = [[w] if type(w) != tuple else list(w) for w in words]
			print words, '\n'
			sets[id] = words

			vocab.extend(n.lower() for n in name.split())
			vocab.append(tw_id.lower())
			vocab.extend([h.lower() for h in htags])
	vocab = tuple(set(vocab))
	with open('data/' + my.DATA_FOLDER + 'vocab_teams.txt', 'wb') as fp:
		fp.write('\n'.join(vocab))
	with open('data/' + my.DATA_FOLDER + 'teams_legend.json', 'wb') as fp:
		fp.write(anyjson.dumps(legend))
	with open('data/' + my.DATA_FOLDER + 'team_sets.json', 'wb') as fp:
		fp.write(anyjson.dumps(sets))


#
# PLAYER SETS
#
def make_player_sets():
	''''''
	#_twitter_ids() # Clean step
	#_nba_players() # Clean step

	vocab = []
	legend = {}
	sets = {} 
	with open('data/' + my.DATA_FOLDER + 'nba_players.txt', 'rb') as fp:
		cr = csv.reader(fp, delimiter=',')
		players = [row[0] for row in cr]
	with open('data/' + my.DATA_FOLDER + 'nba_picks.txt', 'rb') as fp:
		cr = csv.reader(fp, delimiter=',')
		pick_players = [row[0] for row in cr]
	with open('data/' + my.DATA_FOLDER + 'twitter_players.txt', 'rb') as fp:
		cr = csv.reader(fp, delimiter=',')
		twitter_players = [row for row in cr]

	sw = stopwords.words('english')
	with open('data/' + my.DATA_FOLDER + 'stopwords.txt', 'rb') as fp:
		sw.extend(fp.read().split())
	sw.extend(my.STOPWORDS)
	sw = [w for w in sw if len(w) > 2]
	more_stopwords = ['love', 'west', 'wall', 'iii', 'len', 'ty', 'jj', \
					'jr', 'gay', 'ed', 'ish', 'j.r.', 'p.j.', 'mo']
	sw.extend(more_stopwords)
	sw = tuple(set(sw))

	vocab = tuple(itertools.chain(*[n.split() for n in players]))
	vocab = tuple([w.lower().replace('\'','') for w in vocab])
	repeats = [n for n in vocab if vocab.count(n) > 1]
	vocab = tuple(set(vocab))
	print 'Vocab:', len(vocab), ' Repeat:', len(repeats), '\n'

	'''pick_ids = []
	for n1 in players:
		#for n2 in pick_players:
		for n2, tw in twitter_players:
			if _match_names(n1, n2):
				pick_ids.append(players.index(n1))
				#pick_players.remove(n2)
				twitter_players.remove([n2, tw])
				#print n1, '\t', n2
	print len(pick_ids)
	#print pick_players
	#pprint(twitter_players)'''

	id = 0
	for name in players:
		id += 1
		legend[id] = name
		screen_name = None
		for n2, handle in twitter_players:
			if _match_names(name, n2):
				twitter_players.remove([n2, handle])
				screen_name = handle.lower()
				#print name, n2, handle
		name = [n.lower().replace('\'','') for n in name.split()]
		name = [[n] for n in name if n not in repeats \
									and n not in sw]
		if screen_name: name.append([screen_name])
		sets[id] = name
		print name


	with open('data/' + my.DATA_FOLDER + 'vocab_players.txt', 'wb') as fp:
		fp.write('\n'.join(vocab))
	with open('data/' + my.DATA_FOLDER + 'player_legend.json', 'wb') as fp:
		fp.write(anyjson.dumps(legend))
	with open('data/' + my.DATA_FOLDER + 'player_sets.json', 'wb') as fp:
		fp.write(anyjson.dumps(sets))


def _nba_players():
	'''Cleans nba_players.txt'''
	names = []
	with open('data/' + my.DATA_FOLDER + 'nba_players.txt', 'rb') as fp:
		cr = csv.reader(fp, delimiter=',')
		for row in cr:
			if len(row) > 0:
				row = [n.strip() for n in row]
				ln = row.pop(0)
				row.append(ln)
				names.append(' '.join(row))
				#print ' '.join(row)
	with open('data/' + my.DATA_FOLDER + 'nba_players.txt', 'wb') as fp:
		fp.write('\n'.join(names))

def _twitter_ids():
	'''Extracts from twitter_players.html'''
	with open('data/' + my.DATA_FOLDER + 'twitter_players.html', 'rb') as fp:
		doc = fp.read()
	tree = lxml.html.fromstring(doc)
	elements = tree.find_class('user-actions')
	print len(elements), 'NBA players on twitter.'
	players = []
	for el in elements:
		#print el.get('data-name'), el.get('data-screen-name')
		players.append([el.get('data-name'), el.get('data-screen-name')])

	with open('data/' + my.DATA_FOLDER + 'twitter_players.txt', 'wb') as fp:
		cw = csv.writer(fp, delimiter=',')
		for pl in players:
			#print pl
			cw.writerow(pl)

def _match_names(n1, n2):
	n1 = n1.lower().split()
	n2 = n2.lower().split()
	avg_len = min(len(n1), len(n2))
	thres = avg_len / 2.0
	intersect = set(n1) & set(n2)
	if len(intersect) > thres:
		return True
	else: return False



#
# PICKS SETS
#
def make_picks_sets():
	''''''
	legend = {}
	sets = {} 
	with open('data/' + my.DATA_FOLDER + 'nba_picks.txt', 'rb') as fp:
		cr = csv.reader(fp, delimiter=',')
		pick_players = [row[0] for row in cr]
	with open('data/' + my.DATA_FOLDER + 'player_legend.json', 'rb') as fp:
		player_legend = anyjson.loads(fp.read()).items()
	with open('data/' + my.DATA_FOLDER + 'player_sets.json', 'rb') as fp:
		player_sets = anyjson.loads(fp.read())

	id = 0
	for name in pick_players:
		id += 1
		screen_name = None
		pid = 0
		for id2, n2 in player_legend:
			if _match_names(name, n2):
				player_legend.remove((id2, n2))
				screen_name = n2
				pid = id2
		#print name, '\t', screen_name, pid
		legend[id] = screen_name
		sets[id] = player_sets[pid]

	with open('data/' + my.DATA_FOLDER + 'picks_legend.json', 'wb') as fp:
		fp.write(anyjson.dumps(legend))
	with open('data/' + my.DATA_FOLDER + 'picks_sets.json', 'wb') as fp:
		fp.write(anyjson.dumps(sets))