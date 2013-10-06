# Gambit scripts
#
# Copyright (C) USC Information Sciences Institute
# Author: Nibir Bora <nbora@usc.edu>
# URL: <http://cbg.isi.edu/>
# For license information, see LICENSE

#
# Folders
#
#DATA_FOLDER = 'team-sets/'
#DATA_FOLDER = 'player-sets/'
#DATA_FOLDER = 'picks-sets/'

#DATA_FOLDER = 'teams-data3/'
#DATA_FOLDER = 'players-data/'
#DATA_FOLDER = 'all-data/'
#DATA_FOLDER = 'picks-data/'

#DATA_FOLDER = 'teams-freq-set2/'
#DATA_FOLDER = 'teams-freq-timeline/'
#DATA_FOLDER = 'players-freq-set/'
#DATA_FOLDER = 'teams-freq-timeline/'

#DATA_FOLDER = 've-teams-players/'
#DATA_FOLDER = 've-all-players/'
#DATA_FOLDER = 've-players-teams/'

#DATA_FOLDER = 'range-entropy/'

#DATA_FOLDER = 'smooth-peak/'
#DATA_FOLDER = 'pre-pick-prob/'

#DATA_FOLDER = 'influential-users/'
#DATA_FOLDER = 'teams-data-influential/'
#DATA_FOLDER = 've-teams-players-influential/'
DATA_FOLDER = 'pre-pick-prob-influential/'


##################################################
#
# DB
#
DB_CONN_STRING = "host='brain.isi.edu' dbname='twitter' user='twitter' password='flat2#tw1tter'"

# Relations
#REL_TWEET = 'nba_tweet'
REL_TWEET = 'nba_tweet_2'


#
# Params
#
TIMEZONE = 'America/Los_Angeles'
TS_FORMAT = '%Y-%m-%d %H:%M:%S'
TS_ISO_FORMAT = '%Y-%m-%dT%H:%M:%S'

#TS_START = '2013-06-27 12:00:00'
TS_START = '2013-06-27 00:00:00'
TS_WINDOW = 1 		# days


PROCESSES = 12 		# threads

VOCAB_SIZE = 1000 	# size of vocabulary (top K words)
N = 2 				# 1-gram, 2-gram, ..., n-grams
K = 1000 			# number of phrases

STOPWORDS = ['a', 'able', 'about', 'across', 'after', 'all', 'almost', 'also', 'am', 'among', 'an', 'and', 'any', 'are', 'as', 'at', 'be', 'because', 'been', 'but', 'by', 'can', 'cannot', 'could', 'dear', 'did', 'do', 'does', 'either', 'else', 'ever', 'every', 'for', 'from', 'get', 'got', 'had', 'has', 'have', 'he', 'her', 'hers', 'him', 'his', 'how', 'however', 'i', 'if', 'in', 'into', 'is', 'it', 'its', 'just', 'least', 'let', 'like', 'likely', 'may', 'me', 'might', 'most', 'must', 'my', 'neither', 'no', 'nor', 'not', 'of', 'off', 'often', 'on', 'only', 'or', 'other', 'our', 'own', 'rather', 'said', 'say', 'says', 'she', 'should', 'since', 'so', 'some', 'than', 'that', 'the', 'their', 'them', 'then', 'there', 'these', 'they', 'this', 'tis', 'to', 'too', 'twas', 'us', 'wants', 'was', 'we', 'were', 'what', 'when', 'where', 'which', 'while', 'who', 'whom', 'why', 'will', 'with', 'would', 'yet', 'you', 'your', \
	'http', 'https', 'rt']


#
# Plot settings
#
X_INTERVALS = 0


##################################################
#
# Timeline settings
#
TL__TS_START = '2013-8-1 00:00:00'
TL__N_DAYS = 18

#TL__TS_START = '2013-6-27 00:00:00'
#TL__N_DAYS = 2


##################################################
#
# Filler settings
#
FILL_TS_START = '2013-06-27 15:00:00'
FILL_TS_END = '2013-06-28 09:00:00'
FILL_MIN_COUNT = 25


##################################################
#
# Twitter API settings
#
CONSUMER_TOKEN = "OaZbaBSNn129eTSp5bjw"
CONSUMER_SECRET = "DCZvUFByhsLZGMXfu2z3mY0y87LD1ELv1pgbfFLNFIU"
ACCESS_TOKEN = "47117381-wxXeDRn5yIeJclEysQe5rXuAkaQrjZHNZoodzHaVE"
ACCESS_SECRET = "QEjepLwQKwGdj96UhsBZkLeOUNlu6urOEiAZc2athY"

SINCE_ID = 349948100913283072
MAX_ID =  350702156543819777


##################################################
#
# WojYahooNBA settings
#
WOJ__TS_START = '2013-6-27 00:00:00'
WOJ__N_DAYS = 1


##################################################
#
# Players settings
#
#TOP_N = 10
#TOP_N = 20
#TOP_N = 30
TOP_N = 41
#TOP_N = 50

PLOT_SEPERATE = False
PICK_X_LIM = (360, 720) # Optional
#PICK_X_LIM = (480, 660)


##################################################
#
# LDA settings
#
#TOPICS_START = 10;
#TOPICS_STEP = 10;
#TOPICS_END = 100
#TOPICS_START = 10; TOPICS_STEP = 10; TOPICS_END = 70
#TOPICS_START = 80; TOPICS_STEP = 10; TOPICS_END = 90
TOPICS_START = 100; TOPICS_STEP = 10; TOPICS_END = 100

BATCH_SIZE = 10000
