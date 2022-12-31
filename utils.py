"""manage utility functions and structures for organizing the project"""
import random
import time
import string
import logging
import sqlite3

logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(module)s:%(message)s')

_POOL_ID_LEN = 11

USER_FIELD = {
    "email": 0,
    "hashed_password": 1,
    "name": 2,
    "birthday": 3,
    "groups": 4,
}
POOL_FIELD = {
    "id": 0,
    "start_time": 1,
    "creator": 2,
    "title": 3,
    "group_": 4,
    "description": 5,
    "optionNames": 6,
    "optionValues": 7,
}

def get_random_pool_id():
    characters = string.ascii_lowercase + string.digits
    return "".join(random.choices(characters, k=_POOL_ID_LEN))
    
def str_to_list(input):
    # Split the input string on commas
    items = input.split(',')
    # Strip leading and trailing whitespace from each item
    return [item.strip() for item in items]

def init_db():
    users_conn = sqlite3.connect('users.db')
    try:
        with users_conn:
            c = users_conn.cursor()
            # create the db if does not exist, maybe move to different function
            c.execute("""
            CREATE TABLE IF NOT EXISTS users 
            (
                email TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                name TEXT NOT NULL,
                birthday TEXT NOT NULL,
                groups TEXT
            )
            """)
    except:
        return False
    polls_conn = sqlite3.connect('polls.db')
    try:
        with polls_conn:
            c = polls_conn.cursor()
            # create the db if does not exist
            # c.execute("""
            # CREATE TABLE IF NOT EXISTS polls 
            # (
            #     id TEXT UNIQUE NOT NULL,
            #     start_time INTEGER NOT NULL,
            #     creator TEXT NOT NULL,
            #     title TEXT NOT NULL,
            #     group_ INTEGER NOT NULL,
            #     description TEXT,
            #     optionNames TEXT NOT NULL,
            #     optionValues TEXT
            # )
            # """)
            c.execute("""
            CREATE TABLE IF NOT EXISTS polls
            (
                id TEXT UNIQUE NOT NULL,
                start_time INTEGER NOT NULL,
                creator TEXT NOT NULL,
                title TEXT NOT NULL,
                group_ TEXT NOT NULL,
                description TEXT,
                optionNames TEXT NOT NULL,
                optionValues TEXT
            )
            """) #group variable refactored into "group_" as group is a keyword in db
            logging.info("pool table created")
    except sqlite3.Error as error:
        print(error)
        return False
    logging.info("DB initialized")
    return True
