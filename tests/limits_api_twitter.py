from typing import List

import twitter
from twitter import TwitterError
from twitter.models import TwitterModel

import json
import argparse

# ============= TEMP : GET AUTHENTIFICATION TOKENS FROM FILE =============
def getAuth():
    with open("/home/tom/Documents/OpenSND/auth_twitter", 'r') as file:
        lines = file.readlines()
        consummer_key = lines[0].split(':')[1][:-1]
        consumer_secret = lines[1].split(':')[1][:-1]
        access_token_key = lines[2].split(':')[1][:-1]
        access_token_secret = lines[3].split(':')[1][:-1]
        return consummer_key, consumer_secret, access_token_key, access_token_secret


ck, cs, atk, ats = getAuth()
# ========================================================================

# Create twitter API object
api = twitter.Api(consumer_key=ck,
                  consumer_secret=cs,
                  access_token_key=atk,
                  access_token_secret=ats,
                  tweet_mode='extended')


# Create a light dictionnary describing an user
def lightUser(user):
    light = {
        'id': user.id_str,
        'name': user.name,
        'screen_name': user.screen_name,
        'profile_image_url': user.profile_image_url,  # TODO: use https url?
        'verified': user.verified,
        'url': user.url
    }
    return light


# Create a light dictionnary describing a tweet
# Doc des modèles: https://python-twitter.readthedocs.io/en/latest/_modules/twitter/models.html
def lightTweet(tweet):
    light = {
        'id': tweet.id_str,
        # Infos sur l'utilisateur
        'user': lightUser(tweet.user),
        # Infos sur le tweet
        'created_at': tweet.created_at,
        'favorite_count': tweet.favorite_count,
        'retweet_count': tweet.retweet_count,
        'text': tweet.full_text,
        # Contenu du retweet/réponse
        'retweeted_status': lightTweet(tweet.retweeted_status) if tweet.retweeted_status else {},
        'quoted_status': lightTweet(tweet.quoted_status) if tweet.quoted_status else {},
        # Liste des mentions
        'user_mentions': [lightUser(u) for u in tweet.user_mentions],
        # URLs et Hashtags
        'urls': [link.url for link in tweet.urls],
        'hashtags': [hashtag.text for hashtag in tweet.hashtags],
        # Medias
        'medias': [{'url': med.url, 'type': med.type} for med in tweet.media] if tweet.media else []
    }
    return light


def getUserTimeline(username):

    since_id = None
    include_rts = True
    exclude_replies = True
    count = 20

    # Recovers lasts tweets
    if id:
        tweets: List[TwitterModel] = api.GetUserTimeline(screen_name=username,
                                                         since_id=since_id,
                                                         include_rts=include_rts,
                                                         exclude_replies=exclude_replies,
                                                         count=count)
        return tweets
    else:
        print("Error : user not found")
        return False

users = ['PoorlyAgedStuff',
         '_IDVL',
         'depressedgraph',
         'MaxencePacoret',
         'dinoman_j',
         'Polybot5',
         'BioGridGame',
         'CodysLab',
         'SamChsg',
         'tuxedolabs',
         'cursedimages',
         'archillect',
         'LaMeutePhoto',
         'gnomesbottles',
         'thisislux',
         'shenanigansen',
         'biolojical',
         'year_progress',
         'nanofictions',
         '3emeDroite',
         'BassExpression',
         'ClickerSummon',
         'DrNozman',
         'akraland',
         'NnoMan1',
         'shiffman',
         'TaranisNews',
         'Newearz',
         'SAPEUH',
         'humilityfr',
         'MsieurLeProf']

# for i in range(len(users)):
#     print(f'i={i} - user={users[i]}')
#     tweets = getUserTimeline(users[i])

tweets = getUserTimeline("archillect")

for tweet in tweets:
    light = lightTweet(tweet)
    print(light)
