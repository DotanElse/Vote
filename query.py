import json
import sqlite3
import time
import logging
from flask import Flask, render_template
from utils import (
    get_random_poll_id, get_random_user_id, get_random_perm_link, get_random_group_id,
    USER_FIELD, POLL_FIELD, DISCUSSION_FIELD, GROUP_FIELD,
    str_to_list, list_to_str,
    check_password, remove_password_field,
)

logging.basicConfig(level=logging.INFO, format='%(lineno)d:%(funcName)s:%(message)s')

def authorize_user(email, password):
    logging.info("start")

    user = get_user_by_email(email)
    if not user:
        return False

    hashed = user[USER_FIELD['password']]
    if check_password(password, hashed):
        return user
    return False

def get_user_by_email(email):
    logging.info("start")
    try:
        usersConn = sqlite3.connect('users.db')
        with usersConn:
            c = usersConn.cursor()
            c.execute("SELECT * FROM users WHERE email=?", (email,))
            return c.fetchone()
    except BaseException as e:
        logging.warning(f"{e} raised")
        return None

def get_user_by_id(id):
    try:
        usersConn = sqlite3.connect('users.db')
        with usersConn:
            c = usersConn.cursor()
            c.execute("SELECT * FROM users WHERE id=?", (id,))
            return c.fetchone()
    except BaseException as e:
        logging.info("exception in this shit")
        logging.warning(f"{e} raised")
        return None

def get_group(id):
    try:
        groupConn = sqlite3.connect('groups.db')
        with groupConn:
            c = groupConn.cursor()
            c.execute("SELECT * FROM groups WHERE id=?", (id,))
            return c.fetchone()
    except BaseException as e:
        logging.warning(f"{e} raised")
        return None

def get_group_id(name):
    try:
        groupConn = sqlite3.connect('groups.db')
        with groupConn:
            c = groupConn.cursor()
            c.execute("SELECT * FROM groups WHERE name=?", (name,))
            return c.fetchone()[GROUP_FIELD['id']]
    except BaseException as e:
        logging.warning(f"{e} raised")
        return None

def get_poll(id):
    try:
        pollsConn = sqlite3.connect('polls.db')
        with pollsConn:
            c = pollsConn.cursor()
            c.execute("SELECT * FROM polls WHERE id=?", (id,))
            return c.fetchone()
    except BaseException as e:
        logging.warning(f"{e} raised")
        return None

def get_discussion(id):
    try:
        discussionsConn = sqlite3.connect('discussions.db')
        with discussionsConn:
            c = discussionsConn.cursor()
            c.execute("SELECT * FROM discussions WHERE id=?", (id,))
            return c.fetchone()
    except BaseException as e:
        logging.warning(f"{e} raised")
        return None

def submit_user(email, password, name, date):
    id = get_random_user_id()
    if id_exists(id, "users"):
        logging.warning(f"existing user id submittion")
        return submit_user(email, password, name, date)
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
        logging.warning(f"{e} raised")
        return False

def id_exists(id, db_type):
    logging.info("start")
    try:
        conn = sqlite3.connect(f'{db_type}.db')
        with conn:
            c = conn.cursor()
            c.execute(f"SELECT * FROM {db_type} WHERE id=?", (id,))
            if c.fetchone() == None:
                return False
            return True
    except BaseException as e:
        logging.warning(f"{e} raised")
        return True

def submit_group(creator, name, description, public):
    logging.info("start")
    id = get_random_group_id()
    if id_exists(id, "polls"):
        logging.warning(f"existing group id submittion")
        return submit_group(creator, name, description, public)
    permLink = get_random_perm_link()
    try:
        groupConn = sqlite3.connect('groups.db')
        with groupConn:
            c = groupConn.cursor()
            # add the poll
            c.execute(
            "INSERT INTO groups VALUES (:id, :name, :description, :creator, :users, :usersNum, :permLink, :tempLink, :public)",
            {'id': id, 'name': name, 'description': description, 'creator': creator, 'users': creator, 'usersNum': 1,
            'permLink': permLink, 'tempLink': '', 'public': public}
            )
    except BaseException as e:
        logging.warning(f"{e} raised, 1")
        return False

    user = get_user_by_id(creator)
    userGroups = str_to_list(user[USER_FIELD['groups']])
    userGroups.append(id)
    userGroups = list_to_str(userGroups)
    try: 
        usersConn = sqlite3.connect('users.db')
        with usersConn:
            c = usersConn.cursor()
            # add the poll
            c.execute("UPDATE users SET groups = ? WHERE id = ?", (userGroups, creator))
            return True
    except BaseException as e:
        logging.warning(f"{e} raised, 2")
        return False
    

def submit_poll(creator, title, group, description, optionNames, duration):
    id = get_random_poll_id()
    if id_exists(id, "polls"):
        logging.warning(f"existing poll id submittion")
        return submit_poll(creator, title, group, description, optionNames, duration)
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
            "INSERT INTO polls VALUES (:id, :startTime, :creator, :title, :group, :description, :optionNames, :optionValues, :idVoted, :duration)",
            {'id': id, 'startTime': startTime, 'creator': creator, 'title': title, 'group': group, 
            'description': description, 'optionNames': optionNames, 'optionValues': optionValues, 
            'idVoted': idVoted, 'duration': duration}
            )
    except BaseException as e:
        logging.warning(f"{e} raised, 1")
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
        logging.warning(f"{e} raised, 2")
        return False
    return True

def init_db():
    logging.info("start")
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
        logging.warning(f"{e} raised, 1")
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
                duration TEXT NOT NULL
            )
            """) #group variable refactored into "group_" as group is a keyword in db
    except BaseException as e:
        logging.warning(f"{e} raised, 2")
        return False

    try:
        groupsConn = sqlite3.connect('groups.db')
        with groupsConn:
            c = groupsConn.cursor()
            c.execute("""
            CREATE TABLE IF NOT EXISTS groups
            (
                id TEXT UNIQUE NOT NULL,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                creator TEXT,
                users TEXT,
                usersNum INTEGER,
                permLink TEXT NOT NULL,
                tempLink TEXT,
                public TEXT
            )
            """)
            c.execute(
            "INSERT OR IGNORE INTO groups VALUES (:id, :name, :description, :creator, :users, :usersNum, :permLink, :tempLink, :public)",
            {'id': 0, 'name': "Public", 'description': "", 'creator': "0", 'users': "-", 'usersNum': "0",
            'permLink': "-", 'tempLink': '', 'public': "-"}
            )
    except BaseException as e:
        logging.warning(f"{e} raised, 3")
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
        logging.warning(f"{e} raised, 4")
        return False
    return True

def find_vote(id, discussion):
    logging.info("start")
    for i in range(1, 11):
        if id in str_to_list(discussion[DISCUSSION_FIELD[f"u{i}"]]):
            return i-1

def get_voted(id, polls):
    logging.info("start")
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
            c.execute(query, poll_id)
            discussions = c.fetchall() # all discussions that the user have voted
        for discussion in discussions:
            choice = find_vote(id, discussion)
            voted[f"{discussion[DISCUSSION_FIELD['id']]}"] = choice
    except BaseException as e:
        logging.warning(f"{e} raised")
        return False  
    return voted

def get_user_and_polls(email):
    logging.info("start")
    user = get_user_by_email(email)
    if not user:
        return None, None
    nameField = user[USER_FIELD["name"]]
    groupField = str_to_list(user[USER_FIELD["groups"]])
    # Build the query string for getting all polls related to specific user
    placeholders = ', '.join(['?'] * len(groupField))
    query = f"SELECT * FROM polls WHERE group_ IN ({placeholders});"
    polls = []
    try:
        pollsConn = sqlite3.connect('polls.db')
        with pollsConn:
            c = pollsConn.cursor()
            c.execute(query, groupField)
            polls = c.fetchall()
        return user, polls
    except BaseException as e:
        logging.warning(f"{e} raised")
        return None, None

def update_poll_votes(poll_id, optionValues, voters):
    logging.info("start")
    try:
        pollsConn = sqlite3.connect('polls.db')
        with pollsConn:
            c = pollsConn.cursor()
            c.execute("UPDATE polls SET optionValues = ?, idVoted = ? WHERE id = ?", (optionValues, voters, poll_id))
    except BaseException as e:
        logging.warning(f"{e} raised")
        return False
    #add user record of voting to the discussion db


def update_discussion_users(id, poll_id, optionNumber):
    logging.info("start")
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
    except BaseException as e:
        logging.warning(f"{e} raised")
        return False

def pick_poll_option(id, poll_id, optionNumber):
    logging.info("start")
    optionNumber = int(optionNumber)
    user = get_user_by_id(id)
    poll = get_poll(poll_id)
    if not user or not poll:
        logging.error("critical db error") #shouldnt get here

    voted = str_to_list(poll[POLL_FIELD['idVoted']])
    if user[USER_FIELD['id']] in voted:
        return render_template("error.html") # user already voted
    voted.append(id)
    voted = list_to_str(voted)

    options = poll[POLL_FIELD['optionNames']]
    optionAmount = len(str_to_list(options))
    if optionNumber > optionAmount-1:
        return render_template("error.html") # user voted to unknown option

    optionValues = str_to_list(poll[POLL_FIELD['optionValues']])
    chosenOption = optionValues[optionNumber]
    chosenOption = str(int(chosenOption) + 1)
    optionValues[optionNumber] = chosenOption
    optionValues = list_to_str(optionValues)
    update_poll_votes(poll_id, optionValues, voted)
    update_discussion_users(id, poll_id, optionNumber)

def poll_view(poll_id, user_id):
    poll = get_poll(poll_id)
    user = get_user_by_id(user_id)

    if poll is None or user is None:
        return render_template("error.html")
    pollGroup = poll[POLL_FIELD['group_']]
    userGroups = user[USER_FIELD['groups']]
    if pollGroup in userGroups: # user can access this poll
        voteOption = get_voted(user_id, [poll])
        return render_template("poll.html", id=user_id, poll=poll, voted=voteOption)
    return render_template("error.html")

def user_view(page_id, user_id):
    user_requested = get_user_by_id(page_id)
    logging.info(f"user requested is {user_requested}")
    if user_requested is None:
        return render_template("error.html")
    user_requested = remove_password_field(user_requested)
            
    user = get_user_by_id(user_id)
    if user is None:
        return render_template("user.html", user=tuple(user_requested), is_owner=False)
    for field in user_requested:
        logging.info(type(field))
    if user_requested is None:
        return render_template("error.html")
    if user[USER_FIELD['id']] == user_requested[USER_FIELD['id']]: #same user
        return render_template("user.html", user=tuple(user_requested), is_owner=True)
    return render_template("user.html", user=tuple(user_requested), is_owner=False)
    # TODO - check the user being printed is one requested and check viewing without token

def group_view(group_id, user_id):
    group = get_group(group_id)
    if group is None:
        return render_template("error.html")
    user = get_user_by_id(user_id)

    if user is None:
        return render_template("group.html", group=group, user=None, admin=False, extended=False)
    userGroups = user[USER_FIELD['groups']]
    logging.info(f"requested group id is: {group[GROUP_FIELD['id']]}, user groups are {userGroups}")
    if group[GROUP_FIELD['id']] in userGroups: # user is part of this group
        if user[USER_FIELD['id']] in group[GROUP_FIELD['creator']]: # user is an admin
            return render_template("group.html", group=group, user=remove_password_field(user), admin=True, extended=True)
        return render_template("group.html", group=group, user=remove_password_field(user), admin=False, extended=True)
    return render_template("group.html", group=group, user=remove_password_field(user), admin=False, extended=False)