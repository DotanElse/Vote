import json
import sqlite3
import time
import logging
from flask import Flask, render_template
from utils import (
    get_random_poll_id, get_random_userId, 
    USER_FIELD, POLL_FIELD, DISCUSSION_FIELD, 
    str_to_list, list_to_str,
    check_password)

logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(module)s:%(message)s')

def authorize_user(email, password):
    user = get_user(email)
    if not user:
        return False
    hashed = user[USER_FIELD['password']]
    if check_password(password, hashed):
        return user
    return False

def get_user(email):
    try:
        usersConn = sqlite3.connect('users.db')
        with usersConn:
            c = usersConn.cursor()
            c.execute("SELECT * FROM users WHERE email=?", (email,))
            return c.fetchone()
    except BaseException as e:
        logging.warning(f"{e} raised on get_user")
        return None

def get_user_by_id(id):
    try:
        usersConn = sqlite3.connect('users.db')
        with usersConn:
            c = usersConn.cursor()
            c.execute("SELECT * FROM users WHERE id=?", (id,))
            return c.fetchone()
    except BaseException as e:
        logging.warning(f"{e} raised on get_user_by_id")
        return None

def get_poll(id):
    try:
        pollsConn = sqlite3.connect('polls.db')
        with pollsConn:
            c = pollsConn.cursor()
            c.execute("SELECT * FROM polls WHERE id=?", (id,))
            return c.fetchone()
    except BaseException as e:
        logging.warning(f"{e} raised on get_poll")
        return None

def get_discussion(id):
    try:
        discussionsConn = sqlite3.connect('discussions.db')
        with discussionsConn:
            c = discussionsConn.cursor()
            c.execute("SELECT * FROM discussions WHERE id=?", (id,))
            return c.fetchone()
    except BaseException as e:
        logging.warning(f"{e} raised on get_discussion")
        return None

def submit_user(email, password, name, date):
    id = get_random_userId()
    try:
        usersConn = sqlite3.connect('users.db')
        with usersConn:
            c = usersConn.cursor()
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
            # add the user, all users are in the "0" group, which is THE WORLD
            c.execute("INSERT INTO users VALUES (:id, :email, :password, :name, :birthday, :groups)",
            {'id': id, 'email': email, 'password': password, 'name': name, 'birthday': date, 'groups': "0"})
            return True
    except BaseException as e:
        logging.warning(f"{e} raised on get_discussion")
        return False

def submit_poll(creator, title, group, description, optionNames, duration, public):
    id = get_random_poll_id() # stretch - check if same id exists already
    startTime = int(time.time())
    optionAmount = len(str_to_list(optionNames))
    optionValues = ','.join(['0'] * optionAmount)
    idVoted = ''
    try:
        pollsConn = sqlite3.connect('polls.db')
        with pollsConn:
            c = pollsConn.cursor()
            # add the poll
            c.execute(
            "INSERT INTO polls VALUES (:id, :startTime, :creator, :title, :group, :description, :optionNames, :optionValues, :idVoted, :duration, :public)",
            {'id': id, 'startTime': startTime, 'creator': creator, 'title': title, 'group': group, 
            'description': description, 'optionNames': optionNames, 'optionValues': optionValues, 
            'idVoted': idVoted, 'duration': duration, 'public': public}
            )
    except BaseException as e:
        logging.warning(f"{e} raised on submit_poll, 1")
        return False

    try:
        discussionsConn = sqlite3.connect('discussions.db')
        with discussionsConn:
            c = discussionsConn.cursor()
            c.execute(
            "INSERT INTO discussions VALUES (:id, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL)",
            {'id': id}
            )
    except BaseException as e:
        logging.warning(f"{e} raised on submit_poll, 2")
        return False
    return True

def init_db():
    try:
        usersConn = sqlite3.connect('users.db')
        with usersConn:
            c = usersConn.cursor()
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
    except BaseException as e:
        logging.warning(f"{e} raised on init_db, 1")
        return False

    try:
        pollsConn = sqlite3.connect('polls.db')
        with pollsConn:
            c = pollsConn.cursor()
            c.execute("""
            CREATE TABLE IF NOT EXISTS polls
            (
                id TEXT UNIQUE NOT NULL,
                startTime INTEGER NOT NULL,
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
    except BaseException as e:
        logging.warning(f"{e} raised on init_db, 2")
        return False

    try:
        groupsConn = sqlite3.connect('groups.db')
        with groupsConn:
            c = groupsConn.cursor()
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
    except BaseException as e:
        logging.warning(f"{e} raised on init_db, 3")
        return False

    try:
        discussionsConn = sqlite3.connect('discussions.db')
        with discussionsConn:
            c = discussionsConn.cursor()
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
                v10 TEXT,
                u1 TEXT,
                u2 TEXT,
                u3 TEXT,
                u4 TEXT,
                u5 TEXT,
                u6 TEXT,
                u7 TEXT,
                u8 TEXT,
                u9 TEXT,
                u10 TEXT
            )
            """)
    except BaseException as e:
        logging.warning(f"{e} raised on init_db, 4")
        return False
    logging.info("DB initialized")
    return True

def find_vote(id, discussion):
    for i in range(1, 11):
        if id in str_to_list(discussion[DISCUSSION_FIELD[f"u{i}"]]):
            return i-1
    logging.info("Error finding voted")

def get_voted(id, polls):
    voted = {}
    poll_id = []
    for poll in polls:
        if id in str_to_list(poll[POLL_FIELD['idVoted']]):
            poll_id.append(poll[POLL_FIELD['id']])
    placeholders = ', '.join(['?'] * len(poll_id))
    query = f"SELECT * FROM discussions WHERE id IN ({placeholders});"
    try:
        discussionsConn = sqlite3.connect('discussions.db')
        with discussionsConn:
            c = discussionsConn.cursor()
            logging.info(f"query to run is '{query}' and pool id is {poll_id}")
            c.execute(query, poll_id)
            discussions = c.fetchall() # all discussions that the user have voted
        for discussion in discussions:
            choice = find_vote(id, discussion)
            voted[f"{discussion[DISCUSSION_FIELD['id']]}"] = choice
    except BaseException as e:
        logging.warning(f"{e} raised on get_voted")
        return False  
    return voted

def get_user_and_polls(email):
    user = get_user(email)
    if not user:
        return None, None
    nameField = user[USER_FIELD["name"]]
    logging.info(f"user '{nameField}' selected for main page")
    groupField = str_to_list(user[USER_FIELD["groups"]])
    # Build the query string for getting all polls related to specific user
    placeholders = ', '.join(['?'] * len(groupField))
    query = f"SELECT * FROM polls WHERE group_ IN ({placeholders});"
    logging.info(f"query for main page is '{query}'")
    polls = []
    try:
        pollsConn = sqlite3.connect('polls.db')
        with pollsConn:
            c = pollsConn.cursor()
            logging.info(f"query to run is '{query}' and groups are {groupField}")
            c.execute(query, groupField)
            polls = c.fetchall()
            logging.info(f"queries selected '{polls}'")
        return user, polls
    except BaseException as e:
        logging.warning(f"{e} raised on get_user_and_polls")
        return None, None

def update_poll_votes(poll_id, optionValues, voters):
    try:
        pollsConn = sqlite3.connect('polls.db')
        with pollsConn:
            c = pollsConn.cursor()
            c.execute("UPDATE polls SET optionValues = ?, idVoted = ? WHERE id = ?", (optionValues, voters, poll_id))
            logging.info(f"poll {poll_id} updated his option values")
    except BaseException as e:
        logging.warning(f"{e} raised on update_poll_votes")
        return False
    #add user record of voting to the discussion db


def update_discussion_users(id, poll_id, optionNumber):
    discussion = get_discussion(poll_id)
    idVoted = str_to_list(discussion[DISCUSSION_FIELD[f"u{optionNumber+1}"]])
    if id in idVoted:
        return render_template("error.html") # should never reach here
    idVoted.append(id)
    idVoted = list_to_str(idVoted)
    try:
        discussionsConn = sqlite3.connect('discussions.db')
        with discussionsConn:
            c = discussionsConn.cursor()
            c.execute(f"UPDATE discussions SET u{optionNumber+1} = ? WHERE id = ?", (idVoted, poll_id))
            logging.info(f"poll {poll_id} updated his users voting values")
    except BaseException as e:
        logging.warning(f"{e} raised on update_discussion_users")
        return False

def pick_poll_option(id, poll_id, optionNumber):
    optionNumber = int(optionNumber)
    user = get_user_by_id(id)
    poll = get_poll(poll_id)
    if not user or not poll:
        logging.error("pick_poll_option db error")
    voted = str_to_list(poll[POLL_FIELD['idVoted']])
    if user[USER_FIELD['id']] in voted:
        return render_template("error.html") # add more logic and response here
    voted.append(id)
    voted = list_to_str(voted)
    options = poll[POLL_FIELD['optionNames']]
    optionAmount = len(str_to_list(options))
    if optionNumber > optionAmount-1:
        return render_template("error.html") # add more logic and response here
    optionValues = str_to_list(poll[POLL_FIELD['optionValues']])
    chosenOption = optionValues[optionNumber]
    chosenOption = str(int(chosenOption) + 1)
    optionValues[optionNumber] = chosenOption
    optionValues = list_to_str(optionValues)
    update_poll_votes(poll_id, optionValues, voted)
    update_discussion_users(id, poll_id, optionNumber)
    logging.info(f"user {id} voted for poll {poll_id} with option number {optionNumber}")