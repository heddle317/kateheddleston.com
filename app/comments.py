import datetime
import facebook
import requests
import tweepy

from app import config
from app.db import get
from app.db.comments import Comment
from app.db.galleries import Gallery
from app.db.talks import Talk
from app.db.user import User
from app.utils.datetime_tools import relative_time

from jinja2.utils import urlize


def update_facebook_comments(url, entity_uuid):
    access_token = get(User, email='kate.heddleston@gmail.com').code
    graph = facebook.GraphAPI(access_token)
    post_response = graph.get_object('me/posts')
    comments = []
    counter = 0
    while post_response.get('paging', {}).get('next') is not None:
        for post in post_response['data']:
            if url in post.get('message', ''):
                comment_response = graph.request('{}/comments'.format(post.get('id')))
                comments = comments + comment_response.get('data')
                while comment_response.get('paging', {}).get('next') is not None:
                    after = comment_response.get('paging', {}).get('cursors', {}).get('after')
                    comment_response = graph.request('{}/comments'.format(post.get('id')), {'after': after})
                    comments = comments + comment_response.get('data')
                link = "https://www.facebook.com/photo.php?fbid={}".format(post.get('id').split('_')[0])
                comments = [process_fb_comment(comment, link, graph) for comment in comments]
                for comment in comments:
                    Comment.add_or_update(comment.get('id'), entity_uuid, comment)
                return comments
        if counter > 10:
            return []
        post_response = requests.get(post_response.get('paging', {}).get('next')).json()


def process_fb_comment(comment, post_link, graph):
    fb_dict = {}
    fb_dict['id'] = comment.get('id')
    fb_dict['name'] = comment.get('from').get('name')
    fb_dict['screen_name'] = comment.get('from').get('name')
    fb_dict['user'] = comment.get('from')
    fb_dict['author'] = comment.get('from')
    fb_dict['user_url'] = 'https://www.facebook.com/{}'.format(comment.get('from').get('id'))
    fb_dict['entities'] = []
    fb_dict['created_time'] = comment.get('created_time')
    created_time = datetime.datetime.strptime(comment.get('created_time').split('+')[0], '%Y-%m-%dT%H:%M:%S')
    fb_dict['created_at'] = relative_time(created_time)
    fb_dict['link'] = post_link
    fb_dict['text'] = add_target_blank(urlize(comment.get('message')))
    fb_dict['source'] = 'facebook'

    user = graph.request('{}/picture'.format(comment.get('from').get('id')))
    fb_dict['profile_image'] = user.get('url')
    return fb_dict


def add_target_blank(text):
    '''
    This is pretty awful, but the jinja filter will have a keyword for target blank pretty soon and this can
    be removed.
    '''
    text = text.replace('<a href', '<a target="_blank" href')
    return text


def update_tweet_comments(url, entity_uuid):
    auth = tweepy.OAuthHandler(config.TWITTER_CONSUMER_KEY, config.TWITTER_CONSUMER_SECRET)
    api = tweepy.API(auth)
    tweets = search_twitter(url, api, entity_uuid)
    return tweets


def get_mentions(screen_name, tweet_id, api, entity_uuid):
    tweets = []
    for mention in tweepy.Cursor(api.search, q=screen_name, rpp=50).items():
        if mention.in_reply_to_status_id == tweet_id:
            Comment.add_or_update(mention.id, entity_uuid, process_tweet(mention))
            tweets.append(mention)
    return tweets


def search_twitter(url, api, entity_uuid):
    tweets = []
    for tweet in tweepy.Cursor(api.search,
                               q=url,
                               rpp=100,
                               include_entities=True,).items():
        tweet.entity_uuid = get_entity_uuid(tweet.entities.get('urls'))
        Comment.add_or_update(tweet.id, entity_uuid, process_tweet(tweet))
        tweets.append(tweet)
        tweets = tweets + get_mentions(tweet.author.screen_name, tweet.id, api, entity_uuid)
    return tweets


def get_entity_uuid(urls):
    entity_uuid = None
    for u in urls:
        if 'kateheddleston.com' in u.get('expanded_url'):
            url = u.get('expanded_url').replace('https://www.kateheddleston.com/', '')
            url_units = url.split('/')
            if len(url_units) > 1:
                return url_units[1]
    return entity_uuid


def search_user_timeline(user_name, url, api):
    tweets = []
    for tweet in tweepy.Cursor(api.user_timeline, screen_name='heddle317', q=url, count=100).item():
        tweet.entity_uuid = get_entity_uuid(tweet.entities.get('urls'))
        tweets.append(tweet)
        tweets = tweets + get_mentions(tweet.author.screen_name, tweet.id, api)


def get_comments_for_item(uuid):
    url = "{}/blog/{}".format(config.APP_BASE_LINK, uuid)
    tweets = update_facebook_comments(url, uuid)
    tweets = tweets + update_tweet_comments(url, uuid)
    return tweets


def get_comments_for_galleries():
    galleries = Gallery.get_list(published=True)
    tweets = []
    for gallery in galleries:
        gallery_uuid = gallery.uuid
        url = 'https://www.kateheddleston.com/blog/{}'.format(gallery_uuid)
        update_facebook_comments(url, gallery_uuid)
        tweets = tweets + update_tweet_comments(url, gallery_uuid)
    return tweets


def get_comments_for_talks():
    talks = Talk.get_list(published=True)
    tweets = []
    for talk in talks:
        talk_uuid = talk.uuid
        url = 'https://www.kateheddleston.com/talks/{}'.format(talk_uuid)
        update_facebook_comments(url, talk_uuid)
        tweets = tweets + update_tweet_comments(url, talk_uuid)


def find_all_comments():
    auth = tweepy.OAuthHandler(config.TWITTER_CONSUMER_KEY, config.TWITTER_CONSUMER_SECRET)
    api = tweepy.API(auth)
    tweets = search_twitter('kateheddleston.com', api)
    tweets = tweets + search_user_timeline('heddle317', 'kateheddleston.com', api)

    tweets = [process_tweet(tweet) for tweet in tweets]
    for tweet in tweets:
        Comment.add_or_update(tweet.get('id'), tweet.get('entity_uuid'), tweet)
    return tweets


def check_tweet(tweet, gallery_uuid, api, tweets):
    if tweet in tweets:
        return tweets
    tweets.append(tweet)
    screen_name = tweet.author.screen_name
    for mention in tweepy.Cursor(api.search, q=screen_name, rpp=50).items():
        if mention.in_reply_to_status_id == tweet.id:
            tweets = check_tweet(mention, gallery_uuid, api, tweets)
    return tweets


def process_tweet(tweet):
    '''
    Return dict of items we actually need from the tweet.
    '''
    tweet_dict = {}
    tweet_dict['id'] = tweet.id
    tweet_dict['entity_uuid'] = tweet.entity_uuid
    tweet_dict['profile_image'] = tweet.user._json.get('profile_image_url_https')
    tweet_dict['name'] = tweet.author._json.get('name')
    tweet_dict['screen_name'] = tweet.author._json.get('screen_name')
    tweet_dict['user_url'] = 'https://www.twitter.com/{}'.format(tweet.author.screen_name)
    tweet_dict['entities'] = tweet.entities
    tweet_dict['created_time'] = datetime.datetime.strftime(tweet.created_at, '%Y-%m-%dT%H:%M:%S')
    tweet_dict['created_at'] = relative_time(tweet.created_at)
    link = "https://www.twitter.com/{}/status/{}".format(tweet.author._json.get('screen_name'), tweet.id)
    tweet_dict['link'] = link
    tweet_dict['text'] = tweet.text
    tweet_dict['in_reply_to_status_id'] = tweet.in_reply_to_status_id
    tweet_dict['source'] = 'twitter'
    return tweet_dict
