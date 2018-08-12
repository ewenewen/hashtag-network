# hashtag-network
Collection of Python script that retreive tweets about a particular hashtag and builds a network

There are two scripts:

- `download_tweets.py` is used to download tweets that contain a specific hashtag/user. It is also possible to select a time range; however the Twitter API limits the free usage to [only 7 days](https://developer.twitter.com/en/docs/tweets/search/overview/standard).
- `networkify.py` is used to convert the downloaded tweets into a network (several formats are planned, mainly Cytoscape and Gephi formats). It is possible to make:
	- a **hashtag network**: the edges between two hashtags represent the number of tweets that contain both hashtags
	- a **user/mention network**: the edges between two users/mentions represent the number of tweets that contain or that are written by both users/mentions
	- a **bipartite network**: hashtags and users are connected, the edges between them represent the number of tweets that contain both

This program is case isensitive.

## Usage
### Download tweets
`python download_tweets.py --hashtag "JOBIM2018" "darkjobim" --json jobim_tweets.json --log jobim_tweets.log --since 2018-07-03 --until 2018-07-06`

This will create a JSON file with all the tweets, along with a quick log file containing some statistics.

### Generate the network and attributes
- Cytoscape format:
	- **Hashtag network**: `python networkify.py --json jobim_tweets.json --format cytoscape --output jobim_tweets_hashtags.net --type hashtags`
	- **Users/mentions network**: `python networkify.py --json jobim_tweets.json --format cytoscape --output jobim_tweets_users.net --type mentions`
	- **Bipartite network**: `python networkify.py --json jobim_tweets.json --format cytoscape --output jobim_tweets_bipartite.net --type bipartite`
	- **Node attributes**: `python networkify.py --json jobim_tweets.json --format cytoscape --output jobim_tweets.attr --type attributes`
- Gephi format (network file contains the attributes already):
	- **Hashtag network**: `python networkify.py --json jobim_tweets.json --format cytoscape --output jobim_tweets_hashtags.gdf --type hashtags --format gephi`
	- **Users/mentions network**: `python networkify.py --json jobim_tweets.json --format cytoscape --output jobim_tweets_users.gdf --type mentions --format gephi`
	- **Bipartite network**: `python networkify.py --json jobim_tweets.json --format cytoscape --output jobim_tweets_bipartite.gdf --type bipartite --format gephi`
