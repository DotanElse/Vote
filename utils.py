"""manage utility functions and structures for organizing the project"""
import random
import time
import string
import logging
import sqlite3
import query

from flask import render_template

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

def show_main_page(email):
    user = query.get_user(email)
    logging.info(f"user is {user}")
    name_field = user[USER_FIELD["name"]]
    logging.info(f"user '{name_field}' selected for main page")
    group_field = str_to_list(user[USER_FIELD["groups"]])
    logging.info(f"user '{name_field}' has '{group_field}' groups")
    # Build the query string for getting all polls related to specific user
    placeholders = ', '.join(['?'] * len(group_field))
    query = f"SELECT * FROM polls WHERE group_ IN ({placeholders});"
    logging.info(f"query is '{query}'")
    polls_conn = sqlite3.connect('polls.db')
    polls = []
    with polls_conn:
        c = polls_conn.cursor()
        logging.info(f"query to run is '{query}' and groups are {group_field}")
        c.execute(query, group_field) # TODO start here, not working cause i think pool db dont have tables yet
        polls = c.fetchall()
    #TODO return list of tuples, enum with the utils POLL_FIELD
    return render_template("main_page.html", email, polls)
    #TODO - create that database and function to add votes to it
