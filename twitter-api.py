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


# TODO : utiliser la fonction hasattr(dict, 'attribute') pour vérifier si retweet ou pas?


# ================ TWEETS FORMATTING FUNCTIONS ===========================

output_file = 'output.json'
config_file = 'twitter.conf'

def update_last_seen(status_id):
    with open(config_file, 'w') as file:
        file.write(str(status_id))

def get_last_seen():
    with open(config_file, 'r') as file:
        status_id = int(file.readline())
        return status_id

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

def writeResult(result):
    with open(output_file, 'w') as file:
        data = {'result': result}
        json.dump(data, file, indent=4, ensure_ascii=False)

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
# TODO: add 'urls' and 'hashtags' fields
def lightTweet(tweet):
    light = {
        'user': lightUser(tweet.user),
        'id': tweet.id_str,
        'created_at': tweet.created_at,
        'favorite_count': tweet.favorite_count,
        'retweet_count': tweet.retweet_count,
        'text': tweet.full_text,
        'retweeted_status': lightTweet(tweet.retweeted_status) if tweet.retweeted_status else {},
        'quoted_status': lightTweet(tweet.quoted_status) if tweet.quoted_status else {},
        'user_mentions': [lightUser(u) for u in tweet.user_mentions]
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
def getUserTimeline(user_id=None, username=None, since_id=None, include_rts=True, exclude_replies=True, count=50):
    # Recovers user_id from username if not specified
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
# TODO: add an option to exclude retweets
def getHomeTimeline(since_id=None, exclude_replies=True, count=20, new=True):
    if new:
        since_id = get_last_seen()
    tweets: List[TwitterModel] = api.GetHomeTimeline(since_id=since_id,
                                                     exclude_replies=exclude_replies,
                                                     count=count)
    if tweets:
        update_last_seen(tweets[0].id)
    return tweets


# TODO: refactoriser la gestion d'erreurs et le return des fonctions suivantes

def createFavorite(status_id=None):
    try:
        status = api.CreateFavorite(status_id=status_id, include_entities=False)
        return True if status else False
    except TwitterError as e:
        print(f'TwitterError  : {e.message}')
        return False


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
def getTrends(woeid=None):
    if woeid:
        try:
            return api.GetTrendsWoeid(woeid=woeid)
        except TwitterError as e:
            print(f'TwitterError  : {e.message}')
            return False
    else:
        return api.GetTrendsCurrent()


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

# TODO [URGENT]: refactoriser les appels de fonctions avec 'parser.set_defaults(func=fonction)'
# exemple:
# > parser_bar = subparsers.add_parser('bar')
# > parser_bar.add_argument('z')
# > parser_bar.set_defaults(func=bar)
# > def bar(args):
# >    print(args.z)

subparsers = parser.add_subparsers(dest="action")

parser_gut = subparsers.add_parser("getUserTimeline", help='Get lasts tweets of the user specified by @username')
parser_gut.add_argument("username", help="Screen name of the user (@xyz) without the @")
parser_gut.add_argument("-s", "--sinceid", type=int, help="Display only tweets posted after the tweet of this ID")
parser_gut.add_argument("-r", "--includerts", type=bool, help="Include retweets")
parser_gut.add_argument("-a", "--excluderpl", type=bool, help="Exclude replies")
parser_gut.add_argument("-c", "--count", type=int, help="Number of tweets to get (max 200)")

parser_ght = subparsers.add_parser("getHomeTimeline", help='Get lasts tweets of the home timeline')
parser_ght.add_argument("-s", "--sinceid", type=int, help="Display only tweets posted after the tweet of this ID")
parser_ght.add_argument("-a", "--excluderpl", type=bool, help="Exclude replies")
parser_ght.add_argument("-c", "--count", type=int, help="Number of tweets to get (max 200)")

parser_gtr = subparsers.add_parser("getTrends", help="Get the currents world trends")
parser_gtr.add_argument("-w", '--woeid', type=int, help="Yahoo 'Where On Earth ID")

parser_prt = subparsers.add_parser("postRetweet", help="Retweet a tweet")
parser_prt.add_argument("status_id", type=int, help="ID of the tweet")

parser_cfav = subparsers.add_parser("createFavorite", help="Favorite a tweet")
parser_cfav.add_argument("status_id", type=int, help="ID of the tweet")

parser_cfri = subparsers.add_parser("createFriendShip", help="Follow an user")
parser_cfri.add_argument("user_id", type=int, help="ID of the user")
parser_cfri.add_argument("-r", "--retweets", type=bool, help="Include retweets of this user in timeline")

parser_dfav = subparsers.add_parser("destroyFavorite", help="Unfavorite a tweet")
parser_dfav.add_argument("status_id", type=int, help="ID of the tweet")

parser_dfri = subparsers.add_parser("destroyFriendship", help="Unfriend an user")
parser_dfri.add_argument("user_id", type=int, help="ID of the user")

args = parser.parse_args()
action = args.action

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
