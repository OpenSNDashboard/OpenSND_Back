from DAOs import twitter_dao
from DAOs import reddit_dao

import json
import os


class DAO:

    def __init__(self):
        self.dashboards = {}
        for file in os.listdir('./dashboards'):
            with open('./dashboards/' + file, 'r') as dashFile:
                id = file.split('.')[0]
                self.dashboards[id] = json.load(dashFile)
        print(f'<DAO> DAO OBJECT BUILDED, DASHBOARDS PARSED:')
        print(self.dashboards)

    def getContent(self, id, since=None, limit=200):
        twitterLimit = limit // 2
        twitterUserLimit = twitterLimit // len(self.dashboards[id]["twitter"])

        tweets = []

        for twitterUser in self.dashboards[id]["twitter"]:
            tweets.append(twitter_dao.getUserTimeline(username=twitterUser["username"],
                                                      since_id=since,
                                                      include_rts=twitterUser["include_rt"],
                                                      exclude_replies=twitterUser["include_rpl"],
                                                      count=twitterUserLimit))

        # SORT TWEETS BY DATE

        submissions = []

        for subreddit in self.dashboards[id]["reddit"]:
            submissions.append(reddit_dao.getSubmissions(subreddits=[subreddit["name"]],
                                                         filter=subreddit["filter"],
                                                         timeFilter=(subreddit["timeFilter"] if hasattr(subreddit,
                                                                                                        "timeFilter") else 'hour')))

        content = []

        # SHUFFLE TWEETS AND SUBMISSIONS
        for i in range(limit):
            if i % 4 == 0:
                if len(submissions) > 0:
                    content.append(submissions.pop(0))
            else:
                if len(tweets) > 0:
                    content.append(tweets.pop(0))

        with open("result.json", "w") as file:
            json.dump(content, file)

        return content

    def parseDashboard(self, id):
        pathToDashboard = './dashboards/' + id + '.json'

        if os.path.exists(pathToDashboard):
            with open(pathToDashboard, 'r') as dashFile:
                self.dashboards[id] = json.load(dashFile)
                print(f'<DAO> DASHBOARD {id} UPDATED (OR ADDED)')
        else:
            self.dashboards.pop(id)
            print(f'<DAO> DASHBOARD {id} REMOVED')
