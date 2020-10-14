import os
import time
import datetime
import tweepy
import firebase_admin
from firebase_admin import credentials, db

from dotenv import load_dotenv

load_dotenv()

# Constants for twitter connection
API_KEY = os.environ['API_KEY']
API_KEY_SECRET = os.environ['API_KEY_SECRET']
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
ACCESS_TOKEN_SECRET = os.environ['ACCESS_TOKEN_SECRET']

# Firebase connection
GOOGLE_APPLICATION_CREDENTIALS = os.environ['GOOGLE_APPLICATION_CREDENTIALS']
FIREBASE_DATABASE_URL = os.environ['FIREBASE_DATABASE_URL']
firebase_credentials = credentials.Certificate(GOOGLE_APPLICATION_CREDENTIALS)
firebase_admin.initialize_app(firebase_credentials, {
    'databaseURL': FIREBASE_DATABASE_URL
})
db_root_ref = db.reference('/')
db_boards_ref = db.reference('Boards')


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


def check_mentions(api, keywords, last_mention):
    print('Checking mentions...')
    new_last_mention = None
    # api.mentions_timeline --> Returns the 20 most recent mentions, including retweets
    # 4 - CHECK MENTIONS
    for tweet in tweepy.Cursor(api.mentions_timeline, since_id=last_mention).items():
        new_last_mention = tweet.id
        if tweet.in_reply_to_status_id is not None:
            continue
        # 5 - CHECK IF TEXT CONTAIN ANY OF THE KEYWORDS 
        if any(keyword in tweet.text.lower() for keyword in keywords):
            # 6 - CHECK IF EXISTS A PREVIOUS GAME
            game_exists = check_existing_game(tweet.user.name)
            if not game_exists:
                # 7 - IF NOT EXISTS A PREVIOUS GAME, START A NEW ONE IF KEYWORD IS "START"
                if keyword == 'start':
                    start_game(tweet.user.name, tweet.id, api)
                else:
                    print('You didn\'t start any game')
            else:
                print('TODO - Move')
        else:
            print('Command not recognized')
    return new_last_mention


def start_game(username, id, api):
    # 8 - SAVE NEW GAME DATA
    data = {
        'id': id,
        'date': datetime.datetime.now(),
        'status': 'playing'
    }
    set_db(db_boards_ref, username, data)
    # 9 - REPLY WITH INSTRUCTIONS
    api.update_status(status='Ok, challenge accepted. To start playing reply with row (a,b,c) and col (1,2,3) like b1, a2, c0...', in_reply_to_status_id=id, auto_populate_reply_metadata=True)
    print('Reply done')



def check_existing_game(username):
    return db_boards_ref.child(username).order_by_child('status').equal_to('playing').get()


def get_last_mention():
    last_mention = get_db(db_root_ref, 'last_mention_id')
    return last_mention[0]['last_mention_id'] or 1


def update_last_mention(id):
    return set_db(db_root_ref, 'last_mention_id', id)


def get_db(ref, key):
    return ref.get(key)


def set_db(ref, key, data):
    return ref.set({
        key: data
    })
    # ref.set({
    #     'Employee': {
    #         'emp1': {
    #             'name': 'Parwiz',
    #             'lname': 'Forogh',
    #             'age': 24
    #         },
    #         'emp2': {
    #             'name': 'Orgoth',
    #             'lname': 'Margh',
    #             'age': 30
    #         }
    #     }
    # })


def main():
    last_mention = None
    keywords = ['start','a1','a2','a3','b1','b2','b3','c1','c2','c3']
    api = authenticate()
    while True:
        # 1 - CHECK LAST MENTION
        if not last_mention:
            last_mention = get_last_mention()
            print('Last Mention:', last_mention)
        # 2 - CHECK NEW MENTIONS
        new_last_mention = check_mentions(api, keywords, last_mention)
        # 3 - UPDATE LAST MENTION IF THERE ARE NEW MENTIONS
        if new_last_mention != last_mention and new_last_mention is not None:
            update_last_mention(new_last_mention)
            last_mention = new_last_mention

        time.sleep(60)


if __name__ == "__main__":
    main()