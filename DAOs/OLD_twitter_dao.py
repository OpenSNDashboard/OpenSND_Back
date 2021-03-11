from typing import List

import twitter
from twitter import TwitterError
from twitter.models import TwitterModel

import json
import argparse

# RATE LIMITING : https://developer.twitter.com/en/docs/twitter-api/v1/rate-limits


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


# ================ TWEETS FORMATTING FUNCTIONS ===========================

output_file = '../output_bis.json'
config_file = '../config_bis'

def update_last_seen(status_id):
    with open(config_file, 'w') as file:
        file.write(str(status_id))

def get_last_seen():
    with open(config_file, 'r') as file:
        status_id = int(file.readline())
        return status_id

def write(data):
    if data is None:
        pass
    else:
        if isinstance(data[0], twitter.models.Status):
            writeTweets(data, light=True)
        elif isinstance(data[0], twitter.models.User):
            writeUsers(data, light=True)
        elif isinstance(data[0], twitter.models.Trend):
            writeTrends(data)

def writeTweets(tweets, light=True):
    with open(output_file, 'w') as file:
        if tweets:
            if light:
                data = {'tweets': [lightTweet(t) for t in tweets]}
            else:
                data = {'tweets': [t.AsDict() for t in tweets]}
        else:
            data = {}
        print(f'{len(tweets)} nouveaux tweets!')
        json.dump(data, file, indent=4, ensure_ascii=False)

def writeUsers(users, light=True):
    with open(output_file, 'w') as file:
        if users:
            if light:
                data = {'users': [lightUser(u) for u in users]}
            else:
                data = {'users': [u.AsDict() for u in users]}
        else:
            data = {}
        json.dump(data, file, indent=4, ensure_ascii=False)

def writeTrends(trends):
    with open(output_file, 'w') as file:
        if trends:
            data = {'trends': [t.AsDict() for t in trends]}
        else:
            data = {}
        json.dump(data, file, indent=4, ensure_ascii=False)

# Write 'result' dictionnary on output file
def writeResult(result):
    with open(output_file, 'w') as file:
        data = {'result': result}
        json.dump(data, file, indent=4, ensure_ascii=False)

# Create a light dictionnary describing an user
def lightUser(user):
    light = {
        "id": user.id_str,
        "name": user.name,
        "screen_name": user.screen_name,
        "profile_image_url": user.profile_image_url,  # TODO: use https url?
        "verified": user.verified,
        "url": user.url
    }
    return light


# Create a light dictionnary describing a tweet
# Doc des modèles: https://python-twitter.readthedocs.io/en/latest/_modules/twitter/models.html
def lightTweet(tweet):
    light = {
        "id": tweet.id_str,
        # Infos sur l'utilisateur
        "user": lightUser(tweet.user),
        # Infos sur le tweet
        "created_at": tweet.created_at,
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
        "medias": [{'url': med.url, 'type': med.type} for med in tweet.media] if tweet.media else []
    }
    return light


# ================== TWEETS QUERIES FUNCTIONS ============================

# Get ID of an user, or False if user don't exists or isn't followed
# username = 'screen_name' in JSON = @pseudo
def getUserId(username):
    friends = api.GetFriends()
    for friend in friends:
        if friend.screen_name == username:
            return friend.id
    return False


# Get lasts tweets of an user specifier by its username
# TODO: remove 'user_id' or 'username' field depending of the API use
# LIMIT = 900/15mn
def getUserTimeline(args):

    username = args.username
    since_id = args.sinceid
    include_rts = args.includerts
    exclude_replies = args.excluderpl
    count = args.count
    user_id = None

    # Recovers user_id from username if not specified
    # TODO: remove this part if user_id is not used in the final API
    if user_id is None:
        if username is not None:
            id = getUserId(username)
    else:
        id = user_id

    # Recovers lasts tweets
    if id:
        tweets: List[TwitterModel] = api.GetUserTimeline(user_id=id,
                                                         since_id=since_id,
                                                         include_rts=include_rts,
                                                         exclude_replies=exclude_replies,
                                                         count=count)
        return tweets
    else:
        print("Error : user not found")
        return False


# Get lasts tweets of the home timeline
def getHomeTimeline(since_id=None, include_rts=False, exclude_replies=True, count=20, new=False):

    if new:
        since_id = get_last_seen()

    tweets: List[TwitterModel] = api.GetHomeTimeline(since_id=since_id,
                                                     exclude_replies=exclude_replies,
                                                     count=count)
    if not include_rts:
        for tweet in tweets:
            if hasattr(tweet.AsDict(), 'retweeted_status'):
                tweets.remove(tweet)

    if tweets:
        update_last_seen(tweets[0].id)

    return tweets


# TODO: refactoriser la gestion d'erreurs et le return des fonctions suivantes

# LIMIT = 1000/j
def createFavorite(status_id=None):
    try:
        status = api.CreateFavorite(status_id=status_id, include_entities=False)
        return True if status else False    # TODO: pas nécessaire? car CreateFavorite renvoie une erreur si status_id ne pointe pas vers un tweet
    except TwitterError as e:
        print(f'TwitterError  : {e.message}')
        return False


# LIMIT : 400/j
def createFriendship(user_id=None, retweets=True):
    try:
        user = api.CreateFriendship(user_id=user_id, retweets=retweets)
        return True if user else False
    except TwitterError as e:
        print(f'TwitterError  : {e.message}')
        return False


def destroyFavorite(status_id=None):
    try:
        status = api.DestroyFavorite(status_id=status_id, include_entities=False)
        return True if status else False
    except TwitterError as e:
        print(f'TwitterError  : {e.message}')
        return False


def destroyFriendship(user_id=None):
    try:
        user = api.DestroyFriendship(user_id=user_id)
        return True if user else False
    except TwitterError as e:
        print(f'TwitterError  : {e.message}')
        return False


# where = city/region/country
def getTrends(args):
    woeid = args.woeid

    if woeid:
        try:
            return api.GetTrendsWoeid(woeid=woeid)
        except TwitterError as e:
            print(f'TwitterError  : {e.message}')
            return False
    else:
        return api.GetTrendsCurrent()


# LIMIT = 300/3h
def postRetweet(status_id=None):
    try:
        status = api.PostRetweet(status_id=status_id)
        return True if status else False
    except TwitterError as e:
        print(f'TwitterError  : {e.message}')
        return False


# ======================= ARGUMENT PARSER ==============================
parser = argparse.ArgumentParser(description="Surcouche de l'API Twitter bien crados. "
                                             "Ecrit les résultats des requêtes dans 'output.json'")

parser.add_argument("--stdout", action="store_true", help="Print output in stdout")

subparsers = parser.add_subparsers(dest="action")

parser_gut = subparsers.add_parser("getUserTimeline", help='Get lasts tweets of the user specified by @username')
parser_gut.add_argument("username", help="Screen name of the user (@xyz) without the @")
parser_gut.add_argument("-s", "--sinceid", type=int, help="Display only tweets posted after the tweet of this ID")
parser_gut.add_argument("-r", "--includerts", type=bool, help="Include retweets")
parser_gut.add_argument("-a", "--excluderpl", type=bool, help="Exclude replies")
parser_gut.add_argument("-c", "--count", type=int, help="Number of tweets to get (max 200)")
parser_gut.set_defaults(action=getUserTimeline)

parser_ght = subparsers.add_parser("getHomeTimeline", help='Get lasts tweets of the home timeline')
parser_ght.add_argument("-s", "--sinceid", type=int, help="Display only tweets posted after the tweet of this ID")
parser_ght.add_argument("-a", "--excluderpl", type=bool, help="Exclude replies")
parser_ght.add_argument("-c", "--count", type=int, help="Number of tweets to get (max 200)")
parser_ght.set_defaults(action=getHomeTimeline)

parser_gtr = subparsers.add_parser("getTrends", help="Get the currents world trends")
parser_gtr.add_argument("-w", '--woeid', type=int, help="Yahoo 'Where On Earth ID")
parser_gtr.set_defaults(action=getTrends)

parser_prt = subparsers.add_parser("postRetweet", help="Retweet a tweet")
parser_prt.add_argument("status_id", type=int, help="ID of the tweet")
parser_prt.set_defaults(action=postRetweet)

parser_cfav = subparsers.add_parser("createFavorite", help="Favorite a tweet")
parser_cfav.add_argument("status_id", type=int, help="ID of the tweet")
parser_cfav.set_defaults(action=createFavorite)

parser_cfri = subparsers.add_parser("createFriendShip", help="Follow an user")
parser_cfri.add_argument("user_id", type=int, help="ID of the user")
parser_cfri.add_argument("-r", "--retweets", type=bool, help="Include retweets of this user in timeline")
parser_cfri.set_defaults(action=createFriendship)

parser_dfav = subparsers.add_parser("destroyFavorite", help="Unfavorite a tweet")
parser_dfav.add_argument("status_id", type=int, help="ID of the tweet")
parser_dfav.set_defaults(action=destroyFavorite)

parser_dfri = subparsers.add_parser("destroyFriendship", help="Unfriend an user")
parser_dfri.add_argument("user_id", type=int, help="ID of the user")
parser_dfri.set_defaults(action=destroyFriendship)

args = parser.parse_args()
action = args.action

write(action(args))

'''
if action == 'getUserTimeline':
    writeTweets(getUserTimeline(username=args.username,
                                since_id=args.sinceid,
                                include_rts=args.includerts,
                                exclude_replies=args.excluderpl,
                                count=args.count))
elif action == 'getHomeTimeline':
    writeTweets(getHomeTimeline(since_id=args.sinceid,
                                exclude_replies=args.excluderpl,
                                count=args.count))
elif action == 'getTrends':
    writeTrends(getTrends(woeid=args.woeid))
elif action == 'postRetweet':
    writeResult(postRetweet(status_id=args.status_id))
elif action == 'createFavorite':
    writeResult(createFavorite(status_id=args.status_id))
elif action == 'createFriendship':
    writeResult(createFriendship(user_id=args.user_id,
                                 retweets=args.retweets))
elif action == 'destroyFavorite':
    writeResult(destroyFavorite(status_id=args.status_id))
elif action == 'destroyFriendship':
    writeResult(destroyFriendship(user_id=args.user_id))
'''

# TODO : fonctions à tester?
# GetDirectMessages / GetSentDirectMessages
# GetFavorites
# GetFriendIDs / GetFriends
# GetMentions
# GetReplies
# GetSearch
# GetStatus / GetStatusOembed
# GetTrendsCurrent / GetTrendsWoeid / Get
# Gestion de listes (GetLists, GetListTimeline...)
# TODO :
# - pouvoir voir un thread
# - pouvoir voir les réponses d'un tweet
