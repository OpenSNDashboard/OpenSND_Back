import praw
import json

import urllib.request

def getApi():
    with open("../settings.json", "r") as settingsFile:
        settings = json.load(settingsFile)

        api = praw.Reddit(client_id=settings["reddit"]["client_id"],
                          client_secret=settings["reddit"]["client_secret"],
                          user_agent="my_user_agent")
        return api




def printPost(post):
    print("\n########## NEW POST ##########")
    print(f'title={post.title}')
    print(f'selftext={post.selftext}')
    print(f'url={post.url}')
    print(f'permalink={post.permalink}')
    jsonUrl = 'https://www.reddit.com' + post.permalink[:-1] + ".json"
    print(f'JSON={jsonUrl}')


def getMedia(permalink):
    jsonUrl = 'https://www.reddit.com' + permalink[:-1] + ".json"
    try:
        urllib.request.urlretrieve(jsonUrl, './data.json')
        with open('./data.json', 'r') as jsonFile:
            data = json.load(jsonFile)
            secureMedia = data[0]["data"]["children"][0]["data"]["secure_media"]
            if secureMedia:
                if 'reddit_video' in secureMedia.keys():
                    return "video", secureMedia["reddit_video"]["fallback_url"]
                elif 'oembed' in secureMedia.keys():
                    return "oembed", secureMedia["oembed"]["html"]
                else:
                    return "unknow", secureMedia
            else:
                return "text", "..."
    except UnicodeEncodeError:
        return "error", "UnicodeEncodeError"


api = getApi()

posts = api.subreddit("minecraft").hot(limit=100)

# for post in posts:
#     type, url = getMedia(post.permalink)
#     print(f'- {type} ({url})')

import pprint

vids = []

for p in posts:
    try:
        url = p.secure_media['reddit_video']['fallback_url']
        print(f'for post "{p.title[:30]}", vid={url}')
    except Exception as e:
        print("no video for ", p.title[:30])