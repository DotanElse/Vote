import json
import sqlite3
import time
import logging
from flask import Flask, render_template
from utils import (
    get_random_poll_id, get_random_user_id, get_random_perm_link, get_random_group_id,
    USER_FIELD, POLL_FIELD, DISCUSSION_FIELD, GROUP_FIELD, NOTIFICATIONS_FIELD,
    str_to_list, list_to_str, add_to_str, remove_from_str,
    check_password, remove_password_field,
)

logging.basicConfig(level=logging.INFO, format='%(lineno)d:%(funcName)s:%(message)s')

def update_field(db, id, field, value):
    logging.info(f"start, {db}, {field}, {value}")
    try:
        conn = sqlite3.connect(f'{db}.db')
        with conn:
            c = conn.cursor()
            c.execute(f"UPDATE {db} SET {field} = ? WHERE id = ?", (value, id))
    except BaseException as e:
        logging.warning(f"{e} raised")
        return False

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

def submit_user(email, password, name, date, picture):
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
            picture.save(f"static/img/users/{id}.jpg")
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
            "INSERT INTO groups VALUES (:id, :name, :description, :creator, :users, :usersNum, :permLink, :invited, :public)",
            {'id': id, 'name': name, 'description': description, 'creator': creator, 'users': creator, 'usersNum': 1,
            'permLink': permLink, 'invited': '', 'public': public}
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
                invited TEXT,
                public TEXT
            )
            """)
            c.execute(
            "INSERT OR IGNORE INTO groups VALUES (:id, :name, :description, :creator, :users, :usersNum, :permLink, :invited, :public)",
            {'id': 0, 'name': "World", 'description': "", 'creator': "0", 'users': "-", 'usersNum': "0",
            'permLink': "-", 'invited': '', 'public': "-"}
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
    try:
        notificationsConn = sqlite3.connect('notifications.db')
        with notificationsConn:
            c = notificationsConn.cursor()
            # create the db if does not exist, maybe move to different function
            c.execute("""
            CREATE TABLE IF NOT EXISTS notifications 
            (
                id TEXT NOT NULL,
                time TEXT NOT NULL,
                category TEXT NOT NULL,
                initiator TEXT NOT NULL,
                group_ TEXT NOT NULL
            )
            """)
    except BaseException as e:
        logging.warning(f"{e} raised, 5")
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
    except BaseException as e:
        logging.warning(f"{e} raised")
        return None, None
    active_polls = []
    for poll in polls:
        days_diff = (int(time.time()) - poll[POLL_FIELD['startTime']])/(60 * 60 * 24)
        if days_diff > int(poll[POLL_FIELD['duration']]): # too much time has passed
            continue
        active_polls.append(poll)
    sorted_active_polls = sorted(active_polls, key=lambda x: x[POLL_FIELD['startTime']], reverse=True)
    return user, sorted_active_polls


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
    if user_requested is None:
        return render_template("error.html")
    user_requested = remove_password_field(user_requested)
            
    user = get_user_by_id(user_id)
    if user is None:
        return render_template("user.html", user=tuple(user_requested), is_owner=False)
    if user_requested is None:
        return render_template("error.html")
    if user[USER_FIELD['id']] == user_requested[USER_FIELD['id']]: #same user
        return render_template("user.html", user=tuple(user_requested), is_owner=True)
    return render_template("user.html", user=tuple(user_requested), is_owner=False)
    # TODO - check the user being printed is one requested and check viewing without token

def get_uninvited_users(group_id):
    # get all users
    users = []
    try:
        usersConn = sqlite3.connect('users.db')
        with usersConn:
            c = usersConn.cursor()
            c.execute("SELECT * FROM users")
            users = c.fetchall()
    except BaseException as e:
        logging.warning(f"{e} raised")
        return None

    # remove the users that are in the group or in the invite list
    uninvited_users = []
    for user in users:
        if not user_in_group(user[USER_FIELD['id']], group_id) and not user_in_invite_list(user[USER_FIELD['id']], group_id):
            uninvited_users.append(user)
    uninvited_dict = {user[USER_FIELD['id']]: user[USER_FIELD['name']] for user in uninvited_users}
    return uninvited_dict

def get_group_users(group_id):
    # get all users
    users = []
    try:
        usersConn = sqlite3.connect('users.db')
        with usersConn:
            c = usersConn.cursor()
            c.execute("SELECT * FROM users")
            users = c.fetchall()
    except BaseException as e:
        logging.warning(f"{e} raised")
        return None

    # remove the users that are in the group or in the invite list
    group_users = []
    for user in users:
        if user_in_group(user[USER_FIELD['id']], group_id):
            group_users.append(user)
    group_dict = {user[USER_FIELD['id']]: user[USER_FIELD['name']] for user in group_users}
    logging.info(group_dict)
    return group_dict

def get_group_dict(groups_id):
    groups = {}
    for id in groups_id:
        group = get_group(id)
        if group == None:
            continue
        groups[id] = group[GROUP_FIELD['name']]
    return groups

def get_detailed_notifications(user_id):
    """returns a list of notifications which can be interperted by the frontend"""
    notifications = get_user_notifications(user_id)
    detailed_notifications = []
    for notification in notifications:
        initiator = get_user_by_id(notification[NOTIFICATIONS_FIELD['initiator']])
        initiator_name = initiator[USER_FIELD['name']]
        group = get_group(notification[NOTIFICATIONS_FIELD['group_']])
        group_name = group[GROUP_FIELD['name']]
        detailed_notification = list(notification)
        detailed_notification.append(initiator_name)
        detailed_notification.append(group_name)
        logging.info(detailed_notification)
        detailed_notifications.append(detailed_notification)
    logging.info(detailed_notifications)
    return detailed_notifications


def get_user_notifications(user_id):
    try:
        usersConn = sqlite3.connect('notifications.db')
        with usersConn:
            c = usersConn.cursor()
            c.execute("SELECT * FROM notifications WHERE id=?", (user_id,))
            return c.fetchall()
    except BaseException as e:
        logging.warning(f"{e} raised")
        return None

def group_view(group_id, user_id):
    group = get_group(group_id)
    if group is None:
        return render_template("error.html")
    user = get_user_by_id(user_id)

    if user is None:
        return render_template("group.html", group=group, user=None, admin=False, extended=False, users=None)
    userGroups = user[USER_FIELD['groups']]
    if group[GROUP_FIELD['id']] in userGroups: # user is part of this group
        if user[USER_FIELD['id']] in group[GROUP_FIELD['creator']]: # user is an admin
            return render_template("group.html", group=group, user=remove_password_field(user), admin=True, extended=True, users=get_uninvited_users(group_id), group_users=get_group_users(group[GROUP_FIELD['id']]))
        return render_template("group.html", group=group, user=remove_password_field(user), admin=False, extended=True, users=None, group_users=get_group_users(group[GROUP_FIELD['id']]))
    return render_template("group.html", group=group, user=remove_password_field(user), admin=False, extended=False, users=None, group_users=None)

def user_in_group(user_id, group_id):
    user = get_user_by_id(user_id)
    user_groups = str_to_list(user[USER_FIELD['groups']])
    if group_id in user_groups:
        return True
    return False

def user_in_invite_list(user_id, group_id):
    group = get_group(group_id)
    group_invite = str_to_list(group[GROUP_FIELD['invited']])
    if user_id in group_invite:
        return True
    return False

def add_notification(id, category, initiator, group):
    start_time = int(time.time())
    try:
        notificationsConn = sqlite3.connect('notifications.db')
        with notificationsConn:
            c = notificationsConn.cursor()
            c.execute("INSERT INTO notifications VALUES (:id, :time, :category, :initiator, :group)",
            {'id': id, 'time': start_time, 'category': category, 'initiator': initiator, 'group': group})
    except BaseException as e:
        logging.warning(f"{e} raised")
        return False

def invite_users(admin_id, group_id, user_id_list):
    logging.info("start")
    group = get_group(group_id)
    group_invited = str_to_list(group[GROUP_FIELD['invited']])
    for id in user_id_list:
        add_notification(id, 'invitation', admin_id, group_id)
        group_invited.append(id)
    group_invited = list_to_str(group_invited)
    update_field("groups", group_id, "invited", group_invited)

def remove_users(admin_id, group_id, user_id_list):
    logging.info("start")
    group = get_group(group_id)
    group_users = str_to_list(group[GROUP_FIELD['users']])
    group_user_amount = group[GROUP_FIELD['usersNum']]
    new_group_users = []
    for user in group_users:
        if user not in user_id_list:
            new_group_users.append(user)
    new_group_users = list_to_str(new_group_users)
    for user in user_id_list:
        remove_group_from_user(user, group_id)
    
    update_field("groups", group_id, "users", new_group_users)
    logging.info(f"JOJO {len(user_id_list)}")
    update_field("groups", group_id, "usersNum", group_user_amount-len(user_id_list))

def add_to_group(id, group_id):
    logging.info("start")
    user = get_user_by_id(id)
    group = get_group(group_id)
    logging.info(type(user[USER_FIELD['groups']]))
    user_groups = add_to_str(user[USER_FIELD['groups']], group_id)
    group_users = add_to_str(group[GROUP_FIELD['users']], id)

    update_field("users", id, "groups", user_groups)
    update_field("groups", group_id, "usersNum", group[GROUP_FIELD['usersNum']]+1)
    update_field("groups", group_id, "users", group_users)
    logging.info("all added")
    return True

def remove_group_from_user(id, group_id):
    logging.info("start")
    user = get_user_by_id(id)
    user_groups = remove_from_str(user[USER_FIELD['groups']], group_id)

    update_field("users", id, "groups", user_groups)
    return True

def handle_request_notification(initator, group_id, choice):
    logging.info("start")
    values = (initator, group_id)
    logging.info(values)
    query = "DELETE FROM notifications WHERE initiator=? AND group_=?"
    try:
        notificationsConn = sqlite3.connect('notifications.db')
        with notificationsConn:
            c = notificationsConn.cursor()
            c.execute(query, values)
    except BaseException as e:
        logging.warning(f"{e} raised")
        return False
    if choice:
        add_to_group(initator, group_id)

def handle_invite_notification(id, group_id, choice):
    # Remove all notifications of the specific user and group
    logging.info("start")
    values = (id, group_id)
    query = "DELETE FROM notifications WHERE id=? AND group_=?"
    try:
        notificationsConn = sqlite3.connect('notifications.db')
        with notificationsConn:
            c = notificationsConn.cursor()
            c.execute(query, values)
    except BaseException as e:
        logging.warning(f"{e} raised")
        return False
    group = get_group(group_id)
    invited = group[GROUP_FIELD['invited']]
    updated_invited = remove_from_str(group[GROUP_FIELD['invited']], id)
    logging.info(f"well, invited is {invited} and after is {updated_invited}")
    update_field("groups", group_id, "invited", updated_invited)
    if choice:
        add_to_group(id, group_id)

def setup_main_page(email):
    # after authenticating, returns a set of variables for main page
    user, polls = get_user_and_polls(email)

    id = get_user_by_email(email)[USER_FIELD['id']]
    username = get_user_by_email(email)[USER_FIELD['name']]
    groups_id = str_to_list(get_user_by_email(email)[USER_FIELD['groups']])
    groups_dict = get_group_dict(groups_id)

    voted = get_voted(id, polls)
    return user, render_template('main_page.html', id=id, username=username, groups=groups_dict, polls=polls, voted=voted, notifications=get_detailed_notifications(id))

def add_group_to_user(user_id, group_id):
    user = get_user_by_id(user_id)
    user_groups = user[USER_FIELD['groups']]
    updated_user_groups = add_to_str(user_groups, group_id)
    update_field("users", user_id, "groups", updated_user_groups)

def handle_group_request(group_id, user_id):
    group = get_group(group_id)
    if group[GROUP_FIELD['public']] == "Public":
        add_to_group(user_id, group_id)
        add_group_to_user(user_id, group_id)
        return "Added"
    add_notification(group[GROUP_FIELD['creator']], "request", user_id, group_id)
    return "Requested"
    
def check_requested_status(group_id, user_id):
    group = get_group(group_id)
    group_creator = group[GROUP_FIELD['creator']]
    try:
        notificationConn = sqlite3.connect('notifications.db')
        with notificationConn:
            c = notificationConn.cursor()
            c.execute("SELECT * FROM notifications WHERE id = ? AND initiator = ? AND group_ = ?", (group_creator, user_id, group_id))
            a = c.fetchall()
            if a:
                return True
            return False
    except BaseException as e:
        logging.warning(f"{e} raised")
        return None
    
    #invite-leave button control
    # if a user is in the group, always show remove button
    # if group is public, add the user to the group and group to user
    # (if group is private) add notification to the admin with the user and group with "request" type
    # 

    
    # if group is private, add a notification to the admin
