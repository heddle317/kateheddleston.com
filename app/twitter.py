import tweepy

from app import config
from app.db.comments import Comment
from app.utils.datetime_tools import format_date


def get_tweet_comments(gallery_uuid):
    tweets = Comment.get_comment_json(gallery_uuid)
    return tweets


def update_tweet_comments(url, gallery_uuid):
    auth = tweepy.OAuthHandler(config.CONSUMER_KEY, config.CONSUMER_SECRET)
    api = tweepy.API(auth)
    tweets = []
    for tweet in tweepy.Cursor(api.search, q=url, rpp=100).items():
        # process status here
        t = process_tweet(tweet)
        Comment.add_or_update(tweet.id, gallery_uuid, t)
        tweets.append(t)
    return tweets


def process_tweet(tweet):
    '''
    Return dict of items we actually need from the tweet.
    '''
    tweet_dict = {}
    tweet_dict['user'] = tweet.user._json
    tweet_dict['author'] = tweet.author._json
    tweet_dict['entities'] = tweet.entities
    tweet_dict['created_at'] = format_date(tweet.created_at, '%B %d, %Y')
    link = "https://www.twitter.com/{}/status/{}".format(tweet.author._json.get('screen_name'), tweet_dict.get('id'))
    tweet_dict['link'] = link
    tweet_dict['text'] = tweet.text
    tweet_dict['id'] = tweet.id
    return tweet_dict
