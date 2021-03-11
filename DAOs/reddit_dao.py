import praw
from datetime import datetime


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
def getApi(client_id, client_secret, user_agent="my_user_agent"):
    api = praw.Reddit(client_id=client_id,
                      client_secret=client_secret,
                      user_agent=user_agent)
    return api


# Crée un dictionnaire simplifié contenant les infos essentielles d'un post
# Submission : https://praw.readthedocs.io/en/latest/code_overview/models/submission.html
# Subreddit  : https://praw.readthedocs.io/en/latest/code_overview/models/subreddit.html
# Redditor   : https://praw.readthedocs.io/en/latest/code_overview/models/redditor.html
# TODO:
# - trouver un moyen de récupérer l'url des vidéos (si vidéo ou gif)
# - comment sont gérées les galeries (plusieurs photos) ?
def simplified(post):
    simp = {
        "id": post.id,
        # Infos sur l'auteur
        "author": post.author.name,
        "author_id": post.author.id,
        # Infos sur le subreddit
        "sub_id": post.subreddit.id,
        "sub_display_name": post.subreddit.display_name,
        # Infos sur le post
        "title": post.title,
        "created_utc": post.created_utc,
        "selftext": post.selftext,
        "permalink": post.permalink,  # r/<sub_display_name>/comments/<id>/<title>/
        "url": post.url,  # https://i.reddit.it/<random_string>(extension)
        # Propriétés du post
        "is_self": post.is_self,
        "is_oc": post.is_original_content,
        "is_nsfw": post.over_18,
        "is_spoiler": post.spoiler,
        # Stats du post
        "upvotes": post.score,
        "ratio": post.upvote_ratio,
        "comments": post.num_comments
    }
    return simp


# Renvoie des posts reddits au format JSON
# TODO: utiliser des exceptions plutôt que des 'return False'
def getSubmissions(subreddits=None, filter='hot', timeFilter='hour', limit=20):
    api = getApi(ci, cs)

    if timeFilter not in ['hour', 'day', 'week', 'month', 'year', 'all']:
        print("Reddit API Error: invalid time filter")
        return False

    # Crée un string contenant la liste des subreddits sous la forme "sub1+sub2+sub3"
    # TODO:
    # Dans une version future, récupérer le contenu de chaque sub 1 par 1 et
    # les mélanger manuellement? pour éviter le phénomène du 'top' d'un gros sub qui
    # masque les posts des plus petits subs.
    subsChain = ""
    for i in range(len(subreddits)):
        if i == len(subreddits) - 1:
            subsChain += subreddits[i]
        else:
            subsChain += subreddits[i] + '+'

    if filter == 'hot':
        submissions = api.subreddit(subsChain).hot(limit=limit)
    elif filter == 'new':
        submissions = api.subreddit(subsChain).new(limit=limit)
    elif filter == 'top':
        submissions = api.subreddit(subsChain).top(timeFilter, limit=limit)
    elif filter == 'controversial':
        submissions = api.subreddit(subsChain).controversial(timeFilter, limit=limit)
    elif filter == 'rising':
        submissions = api.subreddit(subsChain).rising(limit=limit)
    # elif filter == 'random':
    #    submissions = api.subreddit(subsChain).random()
    else:
        print("Reddit API Error: invalid filter")
        return False

    posts = [simplified(s) for s in submissions]

    return posts


# ===== TEST MAIN =====

# filter = hot | new | top | controversial | rising
# timeFilter (if top or controversial) = hour | day | week | month | year | all
# subs = getSubmissions(subreddits=['Minecraft',
#                                   'MinecraftCommands',
#                                   'technicalminecraft',
#                                   'SciCraft'],
#                       filter='top',
#                       timeFilter='month',
#                       limit=1)
#
# for sub in subs:
#     print(sub)
# print('')
#
# with open("redditPost.json", "w") as file:
#     for sub in subs:
#         # dico = simplified(sub)
#         # json.dump(dico, file)
#         print(f'{datetime.fromtimestamp(sub.created_utc)} | '
#               f'{sub.subreddit.display_name:^20} | '
#               f'{sub.score:<5d} / {sub.upvote_ratio:.2f} | '
#               f'{sub.title}')

# for sub in subs:
# printSubmission(sub)


# NOTES
# random() renvoie que un seul post, l'implémenter quand même ou balec?
