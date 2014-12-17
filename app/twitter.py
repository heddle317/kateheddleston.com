import facebook
import tweepy

from app import config
from app.db import get
from app.db.comments import Comment
from app.db.user import User
from app.utils.datetime_tools import format_date


def get_tweet_comments(gallery_uuid):
    tweets = Comment.get_comment_json(gallery_uuid)
    return tweets


def update_facebook_comments(url, gallery_uuid):
    # graph = facebook.GraphAPI()
    access_token = get(User, email='kate.heddleston@gmail.com').code
    graph = facebook.GraphAPI(access_token)
    posts = graph.get_object('me/posts')
    comments = []
    for post in posts['data']:
        if url in post.get('message', ''):
            comment_response = graph.request('{}/comments'.format(post.get('id')))
            comments = comments + comment_response.get('data')
            while comment_response.get('paging').get('next') is not None:
                after = comment_response.get('paging').get('cursors').get('after')
                comment_response = graph.request('{}/comments'.format(post.get('id')), {'after': after})
                comments = comments + comment_response.get('data')
    print len(comments)
    for comment in comments:
        print comment


def update_tweet_comments(url, gallery_uuid):
    auth = tweepy.OAuthHandler(config.TWITTER_CONSUMER_KEY, config.TWITTER_CONSUMER_SECRET)
    api = tweepy.API(auth)
    tweets = []
    for tweet in tweepy.Cursor(api.search, q=url, rpp=100).items():
        tweets.append(tweet)
        screen_name = tweet.author.screen_name
        for mention in tweepy.Cursor(api.search, q=screen_name, rpp=50).items():
            if mention.in_reply_to_status_id == tweet.id:
                tweets.append(mention)

    tweets = [process_tweet(tweet) for tweet in tweets]
    for tweet in tweets:
        Comment.add_or_update(tweet.get('id'), gallery_uuid, tweet)
    return tweets


def check_tweet(tweet, gallery_uuid, tweepy, api, tweets):
    if tweet in tweets:
        return tweets
    tweets.append(tweet)
    screen_name = tweet.author.screen_name
    for mention in tweepy.Cursor(api.search, q=screen_name, rpp=50).items():
        if mention.in_reply_to_status_id == tweet.id:
            tweets = check_tweet(mention, gallery_uuid, tweepy, api, tweets)
    return tweets


def process_tweet(tweet):
    '''
    Return dict of items we actually need from the tweet.
    '''
    tweet_dict = {}
    tweet_dict['id'] = tweet.id
    tweet_dict['user'] = tweet.user._json
    tweet_dict['author'] = tweet.author._json
    tweet_dict['entities'] = tweet.entities
    tweet_dict['created_at'] = format_date(tweet.created_at, '%B %d, %Y')
    link = "https://www.twitter.com/{}/status/{}".format(tweet.author._json.get('screen_name'), tweet_dict.get('id'))
    tweet_dict['link'] = link
    tweet_dict['text'] = tweet.text
    tweet_dict['in_reply_to_status_id'] = tweet.in_reply_to_status_id
    return tweet_dict
