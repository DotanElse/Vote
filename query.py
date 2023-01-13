import json
import sqlite3
import time
import logging
from flask import Flask, render_template
from utils import get_random_poll_id, get_random_user_id, USER_FIELD, POLL_FIELD, str_to_list

logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(module)s:%(message)s')

def authorize_user(email, password):
    users_conn = sqlite3.connect('users.db')
    with users_conn:
        c = users_conn.cursor()
        c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        return c.fetchone()

def get_user(email):
    users_conn = sqlite3.connect('users.db')
    with users_conn:
        c = users_conn.cursor()
        c.execute("SELECT * FROM users WHERE email=?", (email,))
        return c.fetchone()

def get_user_polls(email): # probably redundent
    """"returns all polls"""
    pass

def get_poll(id):
    polls_conn = sqlite3.connect('polls.db')
    with polls_conn:
        c = polls_conn.cursor()
        c.execute("SELECT * FROM polls WHERE id=?", (id,))
        return c.fetchone()

def submit_user(email, password, name, date):
    users_conn = sqlite3.connect('users.db')
    id = get_random_user_id()
    logging.info("a")
    try:
        with users_conn:
            c = users_conn.cursor()
            # create the db if does not exist, maybe move to different function
            c.execute("""
            CREATE TABLE IF NOT EXISTS users 
            (
                id TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                name TEXT NOT NULL,
                birthday TEXT NOT NULL,
                groups TEXT
            )
            """)
            logging.info("b")
            # add the user, all users are in the "0" group, which is THE WORLD
            c.execute("INSERT INTO users VALUES (:id, :email, :password, :name, :birthday, :groups)",
            {'id': id, 'email': email, 'password': password, 'name': name, 'birthday': date, 'groups': "0"})
            return True
    except:
        return False

def submit_poll(creator, title, group, description, optionNames, duration, public):
    polls_conn = sqlite3.connect('polls.db')
    id = get_random_poll_id() # stretch - check if same id exists already
    start_time = int(time.time())
    optionAmount = len(str_to_list(optionNames))
    optionValues = ','.join(['0'] * optionAmount)
    idVoted = ''

    try:
        with polls_conn:
            c = polls_conn.cursor()
            # add the poll
            c.execute(
            "INSERT INTO polls VALUES (:id, :start_time, :creator, :title, :group, :description, :optionNames, :optionValues, :idVoted, :duration, :public)",
            {'id': id, 'start_time': start_time, 'creator': creator, 'title': title, 'group': group, 
            'description': description, 'optionNames': optionNames, 'optionValues': optionValues, 
            'idVoted': idVoted, 'duration': duration, 'public': public}
            )
    except sqlite3.Error as error:
        logging.info(f"error of submitting poll {error}")
        return False
    
    discussions_conn = sqlite3.connect('discussions.db')
    try:
        with discussions_conn:
            c = discussions_conn.cursor()
            c.execute(
            "INSERT INTO discussions VALUES (:id, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL)",
            {'id': id}
            )
    except sqlite3.Error as error:
        print(error)
        return False
        
    return True

def get_polls_by_groups(): #currently not used
    q = """SELECT * FROM polls WHERE group_ IN (?);"""
    params = '0'
    polls_conn = sqlite3.connect('polls.db')
    polls = ""
    with polls_conn:
        c = polls_conn.cursor()
        c.execute(q, params)
        polls = c.fetchall()
    return polls

def init_db():
    users_conn = sqlite3.connect('users.db')
    try:
        with users_conn:
            c = users_conn.cursor()
            # create the db if does not exist, maybe move to different function
            c.execute("""
            CREATE TABLE IF NOT EXISTS users 
            (
                id TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
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
                optionValues TEXT NOT NULL,
                idVoted TEXT NOT NULL,
                duration TEXT NOT NULL,
                public TEXT NOT NULL
            )
            """) #group variable refactored into "group_" as group is a keyword in db
            logging.info("poll table created")
    except sqlite3.Error as error:
        print(error)
        return False

    groups_conn = sqlite3.connect('groups.db')
    try:
        with groups_conn:
            c = groups_conn.cursor()
            c.execute("""
            CREATE TABLE IF NOT EXISTS groups
            (
                id TEXT UNIQUE NOT NULL,
                creator TEXT,
                users TEXT,
                users_num TEXT,
                perm_link TEXT NOT NULL,
                temp_link TEXT,
                public TEXT  
            )
            """)
    except:
        return False

    discussions_conn = sqlite3.connect('discussions.db')
    try:
        with discussions_conn:
            c = discussions_conn.cursor()
            c.execute("""
            CREATE TABLE IF NOT EXISTS discussions
            (
                id TEXT UNIQUE NOT NULL,
                o1 TEXT,
                o2 TEXT,
                o3 TEXT,
                o4 TEXT,
                o5 TEXT,
                o6 TEXT,
                o7 TEXT,
                o8 TEXT,
                o9 TEXT,
                o10 TEXT,
                v1 TEXT,
                v2 TEXT,
                v3 TEXT,
                v4 TEXT,
                v5 TEXT,
                v6 TEXT,
                v7 TEXT,
                v8 TEXT,
                v9 TEXT,
                v10 TEXT              
            )
            """)
    except:
        return False
    logging.info("DB initialized")
    return True

def get_user_and_polls(email):
    user = get_user(email)
    name_field = user[USER_FIELD["name"]]
    logging.info(f"user '{name_field}' selected for main page")
    group_field = str_to_list(user[USER_FIELD["groups"]])
    # Build the query string for getting all polls related to specific user
    placeholders = ', '.join(['?'] * len(group_field))
    query = f"SELECT * FROM polls WHERE group_ IN ({placeholders});"
    logging.info(f"query for main page is '{query}'")
    polls_conn = sqlite3.connect('polls.db')
    polls = []
    with polls_conn:
        c = polls_conn.cursor()
        logging.info(f"query to run is '{query}' and groups are {group_field}")
        c.execute(query, group_field)
        polls = c.fetchall()
        logging.info(f"queries selected '{polls}'")
    return user, polls

def pick_poll_option(id, poll_id, optionNumber):
    logging.info("yo starting to poll vote thingie pick u know long line so i can see that")
    #get user entry
    #get poll entry
    #check if user voted to that poll
    #assert poll has no more options then optionNumber
    #get optionValues string from the poll, change it to list
    #optionValues[optionNumber]++
    #set it back to string and change the specific poll back
    #log this "user x voted y"
    pass