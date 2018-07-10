import json
import argparse
import time
import datetime
import re
from collections import defaultdict
from itertools import combinations


def process_args():
    """Parser function of main"""
    parse = argparse.ArgumentParser(description="Reads a JSON file containing tweets and export a Cytoscape or Gephi readable network file.")
    parse.add_argument("--json", "-j", nargs=1, default=['tweets.json'], type=str,
                       required=True, help='JSON filename containing the tweets.')
    parse.add_argument("--format", "-f", nargs=1, default=['cytoscape'], type=str,
                       required=False, choices=['cytoscape', 'gephi'],
                       help='format of the output file.')
    parse.add_argument("--type", "-t", nargs=1, default=['hashtags'], type=str,
                       required=False, choices=['hashtags', 'mentions', 'bipartite', 'attributes'],
                       help='choose between hashtags, mentions, bipartite for the network building, or attributes.')
    parse.add_argument("--output", "-o", nargs=1, default=['tweets.net'], type=str,
                       required=False, help='output filename.')
    return(parse)


def tweets_to_hashtags(tweets, unique_mentions):
    """ Read tweets and returns hashtag metrics """
    net = {}
    for id in tweets.keys():
        # Lowercase hashtags
        h = list(map(lambda x:x.lower(), tweets[id]['hashtags']))

        # Compute all combinations in the hashtags of each tweet
        comb_h = list(combinations(h,2))

        # Order nodes (avoid duplicates)
        for pair in comb_h:
            # Cannot change tuple values, so we use strings instead
            pair0 = pair[0]
            pair1 = pair[1]

            # Check if the hashtag is a mention as well; in such case we add a
            # tag
            if pair0 in unique_mentions:
                pair0 = pair0 + ' (hashtag)'
            if pair1 in unique_mentions:
                pair1 = pair1 + ' (hashtag)'

            if (pair1 < pair0):
                entry = pair1 + "\t" + pair0
            else:
                entry = pair1 + "\t" + pair1

            # Retreive metrics: retweets and favorites
            rt = tweets[id]['rt']
            fav = tweets[id]['fav']


            # Save everything in a dico of dico
            if entry not in net.keys():
                net[entry] = {'n': 1, 'fav': fav, 'rt': rt, 'score': 1*(fav+rt)}
            else:
                net[entry]['n'] += 1
                net[entry]['fav'] += fav
                net[entry]['rt'] += rt
                net[entry]['score'] = net[entry]['n'] * (net[entry]['fav'] + net[entry]['rt'])
    return(net)

def tweets_to_mentions(tweets, unique_hashtags):
    """ Read tweets and returns users/mentions metrics """
    net = {}
    for id in tweets.keys():
        # Lowercase mentions
        m = tweets[id]['mentions'] + [tweets[id]['user']]
        m = list(map(lambda x:x.lower(), m))

        # Compute all combinations in the mentions of each tweet
        comb_m = list(combinations(m,2))

        # Order nodes (avoid duplicates)
        for pair in comb_m:
            # Cannot change tuple values, so we use strings instead
            pair0 = pair[0]
            pair1 = pair[1]

            # Check if the mention is a hashtag as well; in such case we add a
            # tag
            if pair0 in unique_hashtags:
                pair0 = pair0 + ' (user)'
            if pair1 in unique_hashtags:
                pair1 = pair1 + ' (user)'

            if (pair1 < pair0):
                entry = pair1 + "\t" + pair0
            else:
                entry = pair0 + "\t" + pair1

            # Retreive metrics: retweets and favorites
            rt = tweets[id]['rt']
            fav = tweets[id]['fav']


            # Save everything in a dico of dico
            if entry not in net.keys():
                net[entry] = {'n': 1, 'fav': fav, 'rt': rt, 'score': 1*(fav+rt)}
            else:
                net[entry]['n'] += 1
                net[entry]['fav'] += fav
                net[entry]['rt'] += rt
                net[entry]['score'] = net[entry]['n'] * (net[entry]['fav'] + net[entry]['rt'])
    return(net)

def tweets_to_bipartite(tweets, unique_hashtags, unique_mentions):
    """ Read tweets and returns hashtags ←→ users/mentions metrics """
    net = {}
    for id in tweets.keys():
        # Lowercase mentions
        m = tweets[id]['mentions'] + [tweets[id]['user']]
        m = list(map(lambda x:x.lower(), m))

        # Lowercase hashtags
        h = list(map(lambda x:x.lower(), tweets[id]['hashtags']))

        # For each combination mention/user and hashtag, make/update an entry
        for m2 in m:
            if m2 in unique_hashtags:
                m2 = m2 + ' (user)'
            for h2 in h:
                if h2 in unique_mentions:
                    h2 = h2 + ' (hashtag)'

                entry = m2 + '\t' + h2

                rt = tweets[id]['rt']
                fav = tweets[id]['fav']

                # Save everything in a dico f dico
                if entry not in net.keys():
                    net[entry] = {'n': 1, 'fav': fav, 'rt': rt, 'score': 1*(fav+rt)}
                else:
                    net[entry]['n'] += 1
                    net[entry]['fav'] += fav
                    net[entry]['rt'] += rt
                    net[entry]['score'] = net[entry]['n'] * (net[entry]['fav'] + net[entry]['rt'])
    return(net)

def tweets_to_attributes(tweets, unique_hashtags, unique_mentions):
    """ Read tweets and return attributes for all nodes """
    attr = {}
    for id in tweets.keys():
        # Lowercase mentions
        m = list(map(lambda x:x.lower(), tweets[id]['mentions']))

        # Lowercase users
        u = [tweets[id]['user'].lower()]

        # Lowercase hashtags
        h = list(map(lambda x:x.lower(), tweets[id]['hashtags']))

        # For each combination mention/user and hashtag, make/update an entry
        for m2 in m:
            if m2 in unique_hashtags:
                m2 = m2 + ' (user)'

            rt = tweets[id]['rt']
            fav = tweets[id]['fav']

            if m2 not in attr.keys():
                attr[m2] = {'type': 'user', 'mentions': 1, 'tweets': 0, 'fav': fav, 'rt': rt, 'score': 1*(fav+rt)}
            else:
                attr[m2]['mentions'] += 1
                attr[m2]['fav'] += fav
                attr[m2]['rt'] += rt
                attr[m2]['score'] = attr[m2]['mentions'] * (attr[m2]['fav'] + attr[m2]['rt'])

        for u2 in u:
            if u2 in unique_hashtags:
                u2 = u2 + ' (user)'

            if u2 not in attr.keys():
                attr[u2] = {'type': 'user', 'mentions': 0, 'tweets': 0, 'fav': 0, 'rt': 0, 'score': 0}
            else:
                attr[u2]['tweets'] += 1

        for h2 in h:
            if h2 in unique_mentions:
                h2 = h2 + ' (hashtag)'

            rt = tweets[id]['rt']
            fav = tweets[id]['fav']

            if h2 not in attr.keys():
                attr[h2] = {'type': 'hashtag', 'mentions': 1, 'tweets': 0, 'fav': fav, 'rt': rt, 'score': 1*(fav+rt)}
            else:
                attr[h2]['mentions'] += 1
                attr[h2]['fav'] += fav
                attr[h2]['rt'] += rt
                attr[h2]['score'] = attr[h2]['mentions'] * (attr[h2]['fav'] + attr[h2]['rt'])
    return(attr)

def export_cytoscape(dico, outputfilename):
    """ Export a dico with hashtags or mentions to a file in the cytoscape format """
    f = open(outputfilename, 'w')

    col = list(dico[list(dico)[0]].keys())
    f.write('\t'.join(col))
    for val in dico.keys():
        f.write('\n' + val)
        for c in col:
            f.write('\t' + str(dico[val][c]))
    f.close()

def list_hashtags(tweets):
    """ From tweets (dico), produce a list of hashtags """
    all_hashtags = []
    for id in tweets.keys():
        # Lowercase hashtags
        h = list(map(lambda x:x.lower(), tweets[id]['hashtags']))
        all_hashtags.append(h)
    unique_hashtags = list(set([item for sublist in all_hashtags for item in sublist]))
    return(unique_hashtags)

def list_mentions(tweets):
    """ From tweets (dico), produce a list of mentions """
    all_mentions = []
    for id in tweets.keys():
        # Lowercase mentions
        m = tweets[id]['mentions'] + [tweets[id]['user']]
        m = list(map(lambda x:x.lower(), m))
        all_mentions.append(m)
    unique_mentions = list(set([item for sublist in all_mentions for item in sublist]))
    return(unique_mentions)

def main(jsonfilename, outputformat, outputfilename, exporttype):
    """ Main program """
    ## Input ===================================================================
    tweets = json.load(open(jsonfilename, 'r'))

    ## Read tweets and create a list of unique hashtags, to know whether there
    # are duplicates between hashtags and mentions. Idem for mentions.
    unique_hashtags = list_hashtags(tweets)
    unique_mentions = list_mentions(tweets)

    ## Read tweets and compute hashtags metrics ================================
    hashtags = tweets_to_hashtags(tweets, unique_mentions)

    ## Read tweets and compute hashtags metrics ================================
    mentions = tweets_to_mentions(tweets, unique_hashtags)

    ## Read tweets and compute hashtags+users/mentions metrics =================
    bipartite = tweets_to_bipartite(tweets, unique_hashtags, unique_mentions)

    ## Read tweets and compute hashtags+users/mentions attributes===============
    attributes = tweets_to_attributes(tweets, unique_hashtags, unique_mentions)


    ## Write output file, depending on the selected format =====================
    if outputformat == 'cytoscape':
        if exporttype == 'hashtags':
            export_cytoscape(hashtags, outputfilename)
        elif exporttype == 'mentions':
            export_cytoscape(mentions, outputfilename)
        elif exporttype == 'bipartite':
            export_cytoscape(bipartite, outputfilename)
        elif exporttype == 'attributes':
            export_cytoscape(attributes, outputfilename)
    elif outputformat == 'gephi':
        raise(Exception('gephi format not yet available.'))


if __name__ == '__main__':
    parse = process_args()
    args = parse.parse_args()

    main(jsonfilename=args.json[0], outputformat=args.format[0], outputfilename=args.output[0],
         exporttype=args.type[0])
