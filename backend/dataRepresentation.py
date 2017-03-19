#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import preprocessor as p
import string
import math


def build_feature_trajectories(tweetsAsJson, firstEpochTime, lastEpochTime):
    """ Build a vector of tf-idf measures in every time points
    for all word features"""

    # The tweets are represented as a list of dictionaries
    # T is the defined period

    # convert the tweets from json to list of dictionaries
    tweets = json.loads(tweetsAsJson)

    # delta
    T = (lastEpochTime - firstEpochTime) // 86400

    # local Term-Frequency for each word feature
    # map of word feature to list, where the list is having T elements
    TFt = {}

    # global term frequency, total number of documents containing each feature
    TF = {}

    # number of documents for day t
    Nt = [0] * (T + 1)

    # total number of documents
    N = len(tweets)


    # iterate over the tweets
    for tweet in tweets:
        # clean the tweets and split only the words
        words = p.clean(tweet['text']).decode('utf-8')\
            .translate(string.punctuation).split()

        # make it a set
        word = list(set(words))

        # convert the timestamp
        t = (int(tweet['createdAtAsLong']) - firstEpochTime) // 86400


        # increase the number of documents for day t
        Nt[t] += 1

        for word in words:

            # if the word does not exist
            if word not in TFt:
                TFt[word] = [0] * (T + 1)
                TF[word] = 0

            # increase the frequency of the current word for day t
            TFt[word][t] += 1
            TF[word] += 1


    featTraj = {}

    for key in TFt:
        featTraj[key] = [0] * (T + 1)

        for idx, val in enumerate(TFt[key]):
            featTraj[key][idx] = (float(val) / Nt[idx]) * math.log(float(N) / TF[key])

    return featTraj
