Gambit - Research scripts
=========================

Research scripts for [Gambit](http://brain.isi.edu/~gambit/v2.0/index.html)
| [CBG](http://cbg.isi.edu) ISI, University of Southern California, Los Angeles, CA

---

Gambit is a visualization tool for geotagged data from Twitter, and to understand patterns in human behavior.

### Contributors

* [Nibir Bora](http://nibir.me/) | <nbora@usc.edu>
* [Vladimir Zaytsev](http://zvm.me/) | <zaytsev@usc.edu>


Most frequently tweeting and mobile users
---

This script is a collection of algorithms to find most frequently tweeting and mobile users.


### File structure

Following the file structure research scripts.

	..
	|-	README.md
	|	



### Pseudocode.

`location_id`,
`ts_start`,
`ts_end`,

Getting list of users.
	
	tweets := all tweets in database
	
	FILTER tweets:
		location_id = ##
		timestamp >= ts_start
		timestamp <= ts_end
	
	FOR EACH tweet IN tweets:
		PUSH tweet.user_id INTO user_list
	
	WRITE TO FILE user_list

Counting number of tweets by each user.
	
	READ FROM FILE user_list
	
	FOR EACH user_id IN user_list
		tweets := all tweets in database
		
		FILTER tweets:
			location_id = ##
			user_id = user_id
			timestamp >= ts_start
			timestamp <= ts_end
	
		user_id.count := COUNT(tweets)
	
	SORT user_list BY .count
	
	WRITE TO FILE user_tweet_count


Finding home locations of each user.
	
	READ FROM FILE user_tweet_count

	FOR EACH user_id IN user_list
		tweets := all tweets in database
		
		FILTER tweets:
			location_id = ##
			user_id = user_id
			timestamp >= ts_start
			timestamp <= ts_end
			
			timestamp.hour >= 17
			timestamp.hour <= 24
		
		FOR EACH tweet IN tweets:
			STORE tweet.latitude
			STORE tweet.longitude
	
	WRITE TO FILE user_tweet_locations_night/
	
	clustering := RUN dbscan() OR optics() CLUSTERING
	ORDER clustering BY .size
	CHOOSE LARGEST cluster
	
	CALC center FOR cluster
	user_id.home_area := CIRCLE(center, _RADIUS)
	WRITE TO FILE user_homes
	
Calculating average displacement of each user from their home locations.
	
	READ FROM FILE user_homes
	
	FOR EACH user_id IN user_list
		tweets := all tweets in database
		
		FILTER tweets:
			location_id = ##
			user_id = user_id
			timestamp >= ts_start
			timestamp <= ts_end
			
		FOR EACH tweet IN tweets:
			disp := DISPLACEMENT(tweet.latitude, tweet.longitude) FROM user_home.home_area
			PUSH disp INTO user_id.disp
		
		user_id.avg_disp := CALC AVG(user_id.disp)
	
	SORT user_list BY .avg_disp
	
	WRITE TO FILE avg_user_disp

