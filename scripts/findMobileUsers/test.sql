SELECT user_id, count(id) as c
FROM t_tweet
GROUP BY user_id
ORDER BY c DESC
LIMIT 1001