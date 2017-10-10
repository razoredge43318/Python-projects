# Objective of this code is to interface with the twitter API, tweepy using python 2.7
# to get a list of user -> friend / follower -> user tuples in a csv file

import csv
import json
import time
import tweepy


# Rate limit chart for Twitter REST API - https://dev.twitter.com/rest/public/rate-limits

def loadKeys(key_file):

    # Lading twitter API keys
    with open(key_file) as data_file:
        data = json.load(data_file)

    api_key = data['api_key']
    api_secret = data['api_secret']
    token = data['token']
    token_secret = data['token_secret']

    return api_key,api_secret,token,token_secret


def getPrimaryFriends(api, root_user, no_of_friends):

    # fetching 'no_of_friends' primary friends of 'root_user'
    primary_friends = []
    user = api.get_user(root_user)
    i=0
    for friend in user.friends():
        if i < no_of_friends:
            primary_friends.append((user.screen_name,friend.screen_name))
        i=i+1

    return primary_friends


def getNextLevelFriends(api, friends_list, no_of_friends):

    # fetching 'no_of_friends' friends for each primary friend
    next_level_friends = []
    i=0
    for x in friends_list:
        try:
            user = api.get_user(x)
        except tweepy.TweepError:
            continue
        try:
            uf = user.friends()
        except tweepy.TweepError:
            continue
        for y in uf:
            if i < no_of_friends:
                next_level_friends.append((user.screen_name,y.screen_name))
            i=i+1
        time.sleep(60)
        i=0
    return next_level_friends


def getNextLevelFollowers(api, followers_list, no_of_followers):

    # fetching 'no_of_followers' followers for each next level friend
    next_level_followers = []
    i=0
    for x in followers_list:
        try:
            user = api.get_user(x)
        except tweepy.TweepError:
            continue
        try:
            ufo = user.followers()
        except tweepy.TweepError:
            continue
        for y in ufo:
            if i < no_of_followers:
                next_level_followers.append((y.screen_name,user.screen_name))
            i=i+1
        time.sleep(60)
        i=0
    return next_level_followers


def GatherAllEdges(api, root_user, no_of_neighbours):

    # implementing this method for calling the methods getPrimaryFriends, getNextLevelFriends
    # and getNextLevelFollowers. Using no_of_neighbours to specify the no_of_friends/no_of_followers parameter.
    all_edges = []
    primarylist = []
    friendlist = []
    followerslist = []
    iterlist = []
    primarylist = getPrimaryFriends(api, root_user, no_of_neighbours)
    time.sleep(60)
    iterlist = [x[1] for x in primarylist]
    friendlist = getNextLevelFriends(api, iterlist, no_of_neighbours)
    time.sleep(2*60)
    followerslist = getNextLevelFollowers(api, iterlist, no_of_neighbours)
    all_edges = primarylist + friendlist + followerslist

    return all_edges



def writeToFile(data, output_file):

    # write data to output_file
    with open(output_file,'wb') as out:
        csv_out = csv.writer(out)
        for row in data:
            csv_out.writerow(row)
    pass


def test():
    KEY_FILE = 'keys.json'
    OUTPUT_FILE_GRAPH = 'graph.csv'
    NO_OF_NEIGHBOURS = 20
    ROOT_USER = 'thesagarbabu'

    api_key, api_secret, token, token_secret = loadKeys(KEY_FILE)

    auth = tweepy.OAuthHandler(api_key, api_secret)
    auth.set_access_token(token, token_secret)
    api = tweepy.API(auth)

    edges = GatherAllEdges(api, ROOT_USER, NO_OF_NEIGHBOURS)

    writeToFile(edges, OUTPUT_FILE_GRAPH)


if __name__ == '__main__':
    test()

