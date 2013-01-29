import sys
import bin.do

if '1' in sys.argv:
	print '----- REMOVE USER HOMES OUTSIDE BIG BOUNDS -----\n'
	bin.do.remove_homes_outside_bounds()

if '2' in sys.argv:
	print '----- GET TWEET LOCATIONS FOR USERS WITH HOMES INSIDE HBK -----\n'
	bin.do.get_user_tweet_locations()

if '3' in sys.argv:
	print '----- FINDING MOST VISITED LOCATIONS -----\n'
	bin.do.find_most_visited_loc()