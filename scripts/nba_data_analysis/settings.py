# Gambit scripts
#
# Copyright (C) USC Information Sciences Institute
# Author: Nibir Bora <nbora@usc.edu>
# URL: <http://cbg.isi.edu/>
# For license information, see LICENSE

#
# Folders
#
#DATA_FOLDER = 'nba-geo/'
#DATA_FOLDER = 'nba-text/'
#DATA_FOLDER = 'nba-time/'
#DATA_FOLDER = 'wojyahoonba/'
#DATA_FOLDER = 'nba-picks/'
DATA_FOLDER = 'nba-non-picks/'
#DATA_FOLDER = 'nba-players/'

#DATA_FOLDER = 'twitter-time/'

#DATA_FOLDER = 'post-1/'
#DATA_FOLDER = 'post-2/'
#DATA_FOLDER = 'post-3/'
#DATA_FOLDER = 'post-4/'

#DATA_FOLDER = 'post-1_skip/'
#DATA_FOLDER = '30-post-1/'
#DATA_FOLDER = 'post-1_v+/'
#DATA_FOLDER = '30-post-1_v+/'


##################################################
#
# DB
#
#DB_CONN_STRING = "host='76.170.75.150' dbname='twitter' user='twitter' password='flat2#tw1tter'"
DB_CONN_STRING = "host='brain.isi.edu' dbname='twitter' user='twitter' password='flat2#tw1tter'"

# Relations
#REL_TWEET = 'nba_tweet'
REL_TWEET = 'nba_tweet_2'
#REL_TWEET = 'nba_tweet_filler'

#REL_TWEET = 't3_tweet_6'


#
# Params
#
TIMEZONE = 'America/Los_Angeles'
TS_FORMAT = '%Y-%m-%d %H:%M:%S'
TS_ISO_FORMAT = '%Y-%m-%dT%H:%M:%S'

TS_START = '2013-06-27 00:00:00'

#TS_START = '2013-06-27 12:00:00'
#TS_START = '2013-06-30 6:00:00'
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
