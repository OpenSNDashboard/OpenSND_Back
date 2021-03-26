from typing import List

import twitter
from twitter import TwitterError
from twitter.models import TwitterModel

from datetime import datetime
import json


# Create twitter API object
def getApi():
    with open("./settings.json", "r") as settingsFile:
        settings = json.load(settingsFile)

        api = twitter.Api(consumer_key=settings["twitter"]["consumer_key"],
                          consumer_secret=settings["twitter"]["consumer_secret"],
                          access_token_key=settings["twitter"]["access_token_key"],
                          access_token_secret=settings["twitter"]["access_token_secret"],
                          tweet_mode='extended')
        return api


# Convert twitter datetime format into a easily comparable format
def convertDatetime(created_at):
    twitter_format = '%a %b %d %H:%M:%S +0000 %Y'
    return_format = '%Y-%m-%d %H:%M:%S'
    return datetime.strftime(datetime.strptime(created_at, twitter_format), return_format)


def extractVideoLink(media):
    bestUrl = ""
    bestBitrate = 0
    for variant in media.video_info['variants']:
        if variant['content_type'] == 'video/mp4':
            if variant['bitrate'] > bestBitrate:
                bestBitrate = variant['bitrate']
                bestUrl = variant['url']
    return bestUrl


# Create a light dictionnary describing an user
def lightUser(user):
    light = {
        "id": user.id_str,
        "name": user.name,
        "screen_name": user.screen_name,
    }

    if user.verified is not None:
        light["verified"] = user.verified
    if user.profile_image_url is not None:
        light["profile_image_url"] = user.profile_image_url_https

    return light


# Create a light dictionnary describing a tweet
# Doc des modèles: https://python-twitter.readthedocs.io/en/latest/_modules/twitter/models.html
def lightTweet(tweet):
    light = {
        "type": "twitter",
        "id": tweet.id_str,
        # Infos sur l'utilisateur
        "user": lightUser(tweet.user),
        # Infos sur le tweet
        "created_at": convertDatetime(tweet.created_at),
        "favorite_count": tweet.favorite_count,
        "retweet_count": tweet.retweet_count,
        "text": tweet.full_text,
        # Contenu du retweet/réponse
        "retweeted_status": lightTweet(tweet.retweeted_status) if tweet.retweeted_status else {},
        "quoted_status": lightTweet(tweet.quoted_status) if tweet.quoted_status else {},
        # Liste des mentions
        "user_mentions": [lightUser(u) for u in tweet.user_mentions],
        # URLs et Hashtags
        "urls": [link.url for link in tweet.urls],
        "hashtags": [hashtag.text for hashtag in tweet.hashtags],
        # Medias
        "medias": []
    }

    if tweet.media is not None:
        for media in tweet.media:
            if media.type == 'photo':
                light["medias"].append({'type': 'photo', 'url': media.media_url_https})
            elif media.type == 'video':
                light["medias"].append({'type': 'video', 'url': extractVideoLink(media)})

    return light


# Get lasts tweets of an user specifier by its username
# LIMIT = 900/15mn
def getUserTimeline(username, since_id=None, include_rts=True, exclude_replies=False, count=20):
    api = getApi()

    # Recovers lasts tweets
    try:
        tweets: List[TwitterModel] = api.GetUserTimeline(screen_name=username,
                                                         since_id=since_id,
                                                         include_rts=include_rts,
                                                         exclude_replies=exclude_replies,
                                                         count=count)
    except TwitterError as e:
        print(e.message)
        return False

    posts = [lightTweet(t) for t in tweets]

    # for t in tweets:
    #    print(t)

    return posts


# ===== TEST MAIN =====
import os
os.chdir("../")
TWEETS = getUserTimeline(username='_IDVL')

for TWEET in TWEETS:
    print(TWEET)
