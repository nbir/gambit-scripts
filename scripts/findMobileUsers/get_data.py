from datetime import datetime
from django.utils.timezone import utc
from grabber.models import Tweet
import csv

API_TS_FORMAT = "%Y-%m-%dT%H:%M:%S"
# Query parameters
_LOCATION_ID = 6
_TS_START = datetime.strptime("2012-09-30T16:00:00", API_TS_FORMAT).replace(tzinfo=utc) # Use UTC time
_TS_END = datetime.strptime("2012-10-10T15:59:59", API_TS_FORMAT).replace(tzinfo=utc)

# Counting number of tweets by each user
tweets = Tweet.objects

tweets = tweets.filter(location=_LOCATION_ID)
tweets = tweets.filter(timestamp__gte=_TS_START)
tweets = tweets.filter(timestamp__lte=_TS_END)

user_list = {}
for tweet in tweets:
	if tweet.user_id in user_list:
		user_list[tweet.user_id] += 1
	else:
		user_list[tweet.user_id] = 1

sorted_user_id = sorted(user_list.keys(), key=lambda y: user_list[y], reverse=True)

with open('research/user_tweet_count.csv', 'wb') as fp:
	csv_writer = csv.writer(fp, delimiter=',')
	for user_id in sorted_user_id:
		csv_writer.writerow([user_id, user_list[user_id]])

# Finding home locations of each user
user_list = {}
with open('research/user_tweet_count.csv', 'rb') as fp:
	csv_reader = csv.reader(fp, delimiter = ',')
	for row in csv_reader:
		user_list[int(row[0].strip())] = int(row[1].strip())

sorted_user_id = sorted(user_list.keys(), key=lambda y: user_list[y], reverse=True)

for user_id in sorted_user_id:
	tweets = Tweet.objects
	tweets = tweets.filter(location=_LOCATION_ID)
	tweets = tweets.filter(user_id=user_id)
	tweets = tweets.filter(timestamp__gte=_TS_START)
	tweets = tweets.filter(timestamp__lte=_TS_END)

	with open('research/user_tweet_locations_night/' + str(user_id) + '.csv', 'wb') as fp:
		csv_writer = csv.writer(fp, delimiter=',')
		for tweet in tweets:
			csv_writer.writerow([tweet.latitude, tweet.longitude])




SELECT user_id, count(id) as c FROM t_tweet GROUP BY user_id ORDER BY c DESC LIMIT 1001

