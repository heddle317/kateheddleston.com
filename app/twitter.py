import json
import tweepy

from app import config


def get_tweet_comments(url):
    auth = tweepy.OAuthHandler(config.CONSUMER_KEY, config.CONSUMER_SECRET)
    api = tweepy.API(auth)
    tweets = []
    for tweet in tweepy.Cursor(api.search, q=url, rpp=100).items():
        # process status here
        tweets.append(process_tweet(tweet))
    return tweets


def process_tweet(tweet):
    '''
    Return dict of items we actually need from the tweet.
    '''
    tweet_dict = {}
    fields = dir(tweet)
    for field in fields:
        if '_' not in field:
            tweet_dict[field] = getattr(tweet, field)
    tweet_dict['user'] = json.dumps(tweet.user._json)
    tweet_dict['author'] = json.dumps(tweet.author._json)
    tweet_dict['retweets'] = [json.dumps(retweet._json) for retweet in tweet.retweets()]
    tweet_dict.pop('favorite')
    tweet_dict.pop('retweet')
    tweet_dict.pop('parse')
    tweet_dict.pop('destroy')
    return tweet_dict
