# OpenSND_Back

## twitter-api.py

**Use**: python3 twitter-api.py [api-call]

**Calls**:

- getUserTimeline: get lasts tweets of the user specified by @username
    - username
    - -s / --sinceid
    - -r / --includerts
    - -a / --excluderpl
    - -c / --count
    
- getHomeTimeline: get lasts tweets of the home timeline
    - -s / --sinceid
    - -a / --exlucerpl
    - -c / --count

- postRetweet: retweet a tweet
    - status_id

- createFavorite: favorite a tweet
    - status_id

- createFriendship: follow an user
    - user_id
    - -r / --retweets

- destroyFavorite: unfavorite a tweet
    - status_id

- destroyFriendship: unfriend an user
    - user_id

**Todo**:

- Calls:
    - destroyRetweet -> need to use destroyStatus ?