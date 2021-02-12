import praw
import datetime
import json

# ============= TEMP : GET AUTHENTIFICATION TOKENS FROM FILE =============
def getAuth():
    with open("/home/tom/Documents/OpenSND/auth_reddit", 'r') as file:
        lines = file.readlines()
        client_id = lines[0].split(':')[1][:-1]
        client_secret = lines[1].split(':')[1][:-1]
        return client_id, client_secret

ci, cs = getAuth()
# ========================================================================

# Create a new reddit API object
api = praw.Reddit(
    client_id=ci,
    client_secret=cs,
    user_agent="my_user_agent"
)

# TODO: impossible d'utiliser la subsChain avec plusieurs subreddits
def getSubmissions(subreddits=None, filter='hot', timeFilter='hour'):

    if timeFilter not in ['hour', 'day', 'week', 'month', 'year', 'all']:
        print("Reddit API Error: invalid time filter")
        return False

    subsChain = ""
    for i in range(len(subreddits)):
        if i == len(subreddits)-1:
            subsChain += subreddits[i]
        else:
            subsChain += subreddits[i] + '+'

    print(f'subsChains = {subsChain}')

    if filter == 'hot':
        submissions = api.subreddit(subsChain).hot(limit=1)
    elif filter == 'new':
        submissions = api.subreddit(subsChain).new()
    elif filter == 'top':
        submissions = api.subreddit(subsChain).top(timeFilter)
    elif filter == 'controversial':
        submissions = api.subreddit(subsChain).controversial(timeFilter)
    elif filter == 'rising':
        submissions = api.subreddit(subsChain).rising()
    elif filter == 'random':
        submissions = api.subreddit(subsChain).random()
    else:
        print("Reddit API Error: invalid filter")
        return False

    return submissions

def printSubmission(sub):
    print("--------------------------")
    print(f'{sub.title}')
    print(f'Posted by {sub.author.name} on {datetime.datetime.fromtimestamp(sub.created_utc)}')
    print(f'OC:{sub.is_original_content} | SPOILER:{sub.spoiler} | NSFW:{sub.over_18}')
    print(f'{sub.score} upvotes | {sub.num_comments} comments | {sub.upvote_ratio} ratio')
    if sub.is_self:
        print(f'CONTENT : {sub.selftext[:10]} [...] {sub.selftext[-10:]}')
    else:
        print(f'URL : {sub.url}')

def simplified(post):
    simp = {
        "author": post.author.name,
        "sub_name": post.subreddit.name,
        "sub_display_name": post.subreddit.display_name,
        "name": post.name,
        "title": post.title,
        "created_utc": post.created_utc,
        "selftext": post.selftext,
        "permalink": post.permalink,
        "url": post.url,

        "is_self": post.is_self,
        "is_oc": post.is_original_content,
        "is_nsfw": post.over_18,
        "is_spoiler": post.spoiler,

        "upvotes": post.score,
        "ratio": post.upvote_ratio,
        "comments": post.num_comments
    }
    return simp


# ===== TEST MAIN =====

# filter = hot | new | top | controversial | rising | random
# timeFilter (if top or controversial) = hour | day | week | month | year | all
subs = getSubmissions(subreddits=['dmt'], filter='hot')


with open("redditPost.json", "w") as file:
    for sub in subs:
        dico = simplified(sub)
        json.dump(dico, file)

#for sub in subs:
    #printSubmission(sub)

