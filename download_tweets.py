import tweepy
import json
import re
import argparse
import time
import datetime
import sys
from collections import defaultdict
from credentials import *

### See credentials_example.py for an example of credentials
# To get them, go on https://apps.twitter.com
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)


def process_args():
    """ Parser function of main """
    parse = argparse.ArgumentParser(description="Download all accessible tweets from a defined hashtag or a list of hashtags.")
    parse.add_argument("--hashtag", "-H", nargs='+', default=['JOBIM2018'], type=str,
                       required=True, help='hashtag or list of hashtags, case insensitive.')
    parse.add_argument("--json", "-j", nargs=1, default=['tweets.json'], type=str,
                       required=False, help='JSON filename in which the tweets will be exported.')
    parse.add_argument("--log", "-l", nargs=1, type=str,
                       required=False, help='optional logfile in which some statistics will be written.')
    parse.add_argument("--since", "-s", nargs=1, type=str,
                       required=False, help='optional start date (format YYYY-MM-DD).')
    parse.add_argument("--until", "-u", nargs=1, type=str,
                       required=False, help='optional end date (format YYYY-MM-DD).')
    return(parse)


def retrieve_tweets(hashtag, tweets, since, until):
    for tweet in tweepy.Cursor(api.search, q=hashtag, since=since, until=until).items():
        dic = {}

        id = tweet._json['id']
        dic['text'] = tweet._json['text']
        if not re.match('^RT ', dic['text']) and id not in tweets.keys():
            dic['user'] = tweet._json['user']['screen_name']
            dic['date'] = tweet._json['created_at']
            dic['fav'] = tweet._json['favorite_count']
            dic['rt'] = tweet._json['retweet_count']
            dic['source'] = tweet._json['source']

            hashtags = tweet._json['entities']['hashtags']
            hashtags_list = []
            for h in hashtags:
                hashtags_list.append(h['text'])
            dic['hashtags'] = hashtags_list

            mentions = tweet._json['entities']['user_mentions']
            mentions_list = []
            for m in mentions:
                mentions_list.append(m['screen_name'])
            dic['mentions'] = mentions_list

            tweets[id] = dic
    return(tweets)

def write_json(dico, filename):
    """ Converts a dictionary into a json file """
    f = open(filename, 'w')
    json.dump(dico, f)
    f.close()

def write_log(logfilename, tweets):
    """ Write log file containing statistics about the tweets """
    n_tweets = len(tweets)
    hashtag_counts = defaultdict(int)
    mention_counts = defaultdict(int)
    user_counts = defaultdict(int)
    time_range = {}

    for id in tweets.keys():
        ### Hashtag counts
        for h in tweets[id]['hashtags']:
            hashtag_counts[h] += 1

        ### Mention counts
        for m in tweets[id]['mentions']:
            mention_counts[m] += 1

        ### Number of tweets per uses
        user_counts[tweets[id]['user']] += 1

        ### Date range
        t = time.strptime(tweets[id]['date'], "%a %b %d %H:%M:%S %z %Y")
        if 'first' not in time_range.keys() or t < time_range['first']:
            time_range['first'] = t
        if 'last' not in time_range.keys() or t > time_range['last']:
            time_range['last'] = t



    text = ""

    ### Command
    text += time.strftime("Command ran on %Y-%m-%d at %H:%m") + ': \n' +  ' '.join(sys.argv) + '\n\n'

    ### Number of tweets
    text += str(n_tweets) + " tweets were retreived.\n"

    ### 5 most common users
    text += "Most common users:\n"
    for c in sorted(user_counts, key=user_counts.get, reverse=True)[0:5]:
        text += "\t" + c + ": " + str(user_counts[c]) + " tweets\n"

    ### 5 most common hashtags
    text += "Most common hashtags:\n"
    for h in sorted(hashtag_counts, key=hashtag_counts.get, reverse=True)[0:5]:
        text += "\t" + h + ": " + str(hashtag_counts[h]) + " tweets\n"

    ### 5 most common mentions
    text += "Most common mentions:\n"
    for m in sorted(mention_counts, key=mention_counts.get, reverse=True)[0:5]:
        text += "\t" + m + ": " + str(mention_counts[m]) + " tweets\n"

    ### Time range
    text += "First tweet: " + time.strftime("%a %b %d %H:%M:%S %Y", time_range['first']) + "\n"
    text += "Last tweet:  " + time.strftime("%a %b %d %H:%M:%S %Y", time_range['last']) + "\n"

    print(text)

    ## Open and write in the file ==============================================
    f = open(logfilename, 'w')
    f.write(text)
    f.close()



def main(hashtag, jsonfilename, logfilename, since, until):
    """ Main program """
    ## Check the hashtags validity =============================================
    ### TODO

    ## Check since/until option validity =======================================
    if since is None:
        since = "2000-01-01"
    else:
        since = since[0]
    if until is None:
        until = str(datetime.date.today())
    else:
        until = until[0]
    if not bool(re.match("^[0-9]{4}-[0-9]{2}-[0-9]{2}$", since)):
        raise(Exception("wrong format for --since"))
    if not bool(re.match("^[0-9]{4}-[0-9]{2}-[0-9]{2}$", until)):
        raise(Exception("wrong format for --until"))

    ## Populate the tweet dictionary, hashtag afther hashtag ===================
    tweets = {}
    for h in hashtag:
        tweets = retrieve_tweets(h, tweets, since=since, until=until)

    ## Write the json file
    outfile = open(jsonfilename, 'w')
    json.dump(tweets, outfile)

    ## Write the log file
    if logfilename is not None:
        write_log(logfilename[0], tweets)
    outfile.close()



if __name__ == '__main__':
    parse = process_args()
    args = parse.parse_args()


    main(hashtag=args.hashtag, jsonfilename=args.json[0], logfilename=args.log,
         since=args.since, until=args.until)
