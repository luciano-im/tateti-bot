import os
import time
import logging
import tweepy

from dotenv import load_dotenv

logger = logging.getLogger()

load_dotenv()

# Constants for twitter connection
API_KEY = os.environ['API_KEY']
API_KEY_SECRET = os.environ['API_KEY_SECRET']
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
ACCESS_TOKEN_SECRET = os.environ['ACCESS_TOKEN_SECRET']

# Board matrix
board = [
    [None, None, None],
    [None, None, None],
    [None, None, None]
]
# Moves availables
board_moves = {
    'a1': [0,0],
    'a2': [0,1],
    'a3': [0,2],
    'b1': [1,0],
    'b2': [1,1],
    'b3': [1,2],
    'c1': [2,0],
    'c2': [2,1],
    'c3': [2,2]
}
# Winner combinations
winner_lines = {
    'r1': ['a1', 'a2', 'a3'],
    'r2': ['b1', 'b2', 'b3'],
    'r3': ['c1', 'c2', 'c3'],
    'c1': ['a1', 'b1', 'c1'],
    'c2': ['a2', 'b2', 'c2'],
    'c3': ['a3', 'b3', 'c3'],
    'd1': ['a1', 'b2', 'c3'],
    'd2': ['a3', 'b2', 'c1'],
}


def authenticate():
    auth = tweepy.OAuthHandler(API_KEY, API_KEY_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth, wait_on_rate_limit=True)
    try:
        api.verify_credentials()
    except Exception as e:
        logger.error("Error creating API", exc_info=True)
        raise e
    return api


def check_mentions(api, keywords, since_id):
    logger.info('Retrieving mentions')
    new_since_id = since_id
    for tweet in tweepy.Cursor(api.mentions_timeline, since_id=since_id).items():
        new_since_id = max(tweet.id, new_since_id)
        if tweet.in_reply_to_status_id is not None:
            continue
        if any(keyword in tweet.text.lower() for keyword in keywords):
            logger.info(f'Answering to {tweet.user.name}')
            api.update_status(status='Ok, challenge accepted. To start playing reply with row (a,b,c) and col (1,2,3) like b1, a2, c0...', in_reply_to_status_id=tweet.id,)
            start_game()
    return new_since_id


def main():
    api = authenticate()
    since_id = 1
    while True:
        since_id = check_mentions(api, ['start','a1','a2','a3','b1','b2','b3','c1','c2','c3'], since_id)
        logger.info('Waiting...')
        time.sleep(60)


if __name__ == "__main__":
    main()