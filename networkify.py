import json
import argparse
import time
import datetime
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
                       required=False, choices=['hashtags', 'mentions', 'bipartite'],
                       help='choose between hashtags or mentions for the network building.')
    parse.add_argument("--output", "-o", nargs=1, default=['tweets.net'], type=str,
                       required=False, help='output filename.')
    return(parse)


def tweets_to_hashtags(tweets):
    """ Read tweets and returns hashtag metrics """
    net = {}
    for id in tweets.keys():
        # Lowercase hashtags
        h = list(map(lambda x:x.lower(), tweets[id]['hashtags']))

        # Compute all combinations in the hashtags of each tweet
        comb_h = list(combinations(h,2))

        # Order nodes (avoid duplicates)
        for pair in comb_h:
            if (pair[1] < pair[0]):
                entry = pair[1] + "\t" + pair[0]
            else:
                entry = pair[0] + "\t" + pair[1]

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

def tweets_to_mentions(tweets):
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
            if (pair[1] < pair[0]):
                entry = pair[1] + "\t" + pair[0]
            else:
                entry = pair[0] + "\t" + pair[1]

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

def tweets_to_bipartite(tweets):
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
            for h2 in h:
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

def export_cytoscape(dico, outputfilename):
    """ Export a dico with hashtags or mentions to a file in the cytoscape format """
    f = open(outputfilename, 'w')
    f.write("source\ttarget\tn\trt\tfav\tscore\n")
    for sourcetarget in dico.keys():
        f.write(sourcetarget + '\t' + str(dico[sourcetarget]['n']) + '\t' + str(dico[sourcetarget]['rt']) + '\t' + str(dico[sourcetarget]['fav']) + '\t' + str(dico[sourcetarget]['score']) + '\n')
    f.close()


def main(jsonfilename, outputformat, outputfilename, exporttype):
    """ Main program """
    ## Input ===================================================================
    tweets = json.load(open(jsonfilename, 'r'))

    ## Read tweets and compute hashtags metrics ================================
    hashtags = tweets_to_hashtags(tweets)

    ## Read tweets and compute hashtags metrics ================================
    mentions = tweets_to_mentions(tweets)

    ## Read tweets and compute hashtags+users/mentions metrics =================
    bipartite = tweets_to_bipartite(tweets)

    ## Write output file, depending on the selected format
    if outputformat == 'cytoscape':
        if exporttype == 'hashtags':
            export_cytoscape(hashtags, outputfilename)
        elif exporttype == 'mentions':
            export_cytoscape(mentions, outputfilename)
        elif exporttype == 'bipartite':
            export_cytoscape(bipartite, outputfilename)
    elif outputformat == 'gephi':
        raise(Exception('gephi format not yet available.'))


if __name__ == '__main__':
    parse = process_args()
    args = parse.parse_args()

    main(jsonfilename=args.json[0], outputformat=args.format[0], outputfilename=args.output[0],
         exporttype=args.type[0])



#net = {}
#for tweet in tweets:
#    # Lowercase hashtags
#    h = list(map(lambda x:x.lower(), tweet['hashtags']))
#
#    # Compute all combinations in the hashtags of each tweet
#    comb_h = list(combinations(h,2))
#
#    # Order nodes (avoid duplicates)
#    for pair in comb_h:
#        if (pair[1] < pair[0]):
#            entry = pair[1] + "\t" + pair[0]
#        else:
#            entry = pair[0] + "\t" + pair[1]
#
#        # Retreive metrics: retweets and favorites
#        rt = tweet['rt']
#        fav = tweet['fav']
#
#
#        # Save everything in a dico of dico
#        if entry not in net.keys():
#            net[entry] = {'n': 1, 'fav': fav, 'rt': rt, 'score': 1*(fav+rt)}
#        else:
#            net[entry]['n'] += 1
#            net[entry]['fav'] += fav
#            net[entry]['rt'] += rt
#            net[entry]['score'] = net[entry]['n'] * (net[entry]['fav'] + net[entry]['rt'])
#
#out = open("tweets_jobim2018_scores.net", "w")
#out.write("node1\tnode2\tn\tfav\trt\tscore\n")
#for entry in net.keys():
#    out.write(entry + "\t" + str(net[entry]['n']) + "\t" + str(net[entry]['fav']) + "\t" + str(net[entry]['rt']) + "\t" + str(net[entry]['score']) + "\n")
#out.close()
