import sqlite3
from flask import Flask, render_template
from utils import get_random_pool_id

def get_user(email, password):
    users_conn = sqlite3.connect('users.db')
    with users_conn:
        c = users_conn.cursor()
        c.execute("SELECT * FROM users WHERE email=? AND hashed_password=?", (email, password))
        return c.fetchall()

def get_user_polls(email):
    """"returns all polls"""
    pass

def submit_user(email, password, name, date):
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
            # add the user, all users are in the "0" group, which is THE WORLD
            c.execute("INSERT INTO users VALUES (:email, :hashed_password, :name, :birthday, :groups)",
            {'email': email, 'hashed_password': password, 'name': name, 'birthday': date, 'groups': "0"})
            return True
    except:
        return False

def submit_pool(creator, title, group, description, optionNames, optionValues):
    polls_conn = sqlite3.connect('polls.db')
    id = get_random_pool_id() # stretch - check if exists already
    #TODO 1 - add time param and check this function throughly again, afterwards add logging
    try:
        with polls_conn:
            c = polls_conn.cursor()
            # maybe go for init function
            c.execute("""
            CREATE TABLE IF NOT EXISTS polls 
            (
                id TEXT UNIQUE NOT NULL
                start_time TEXT NOT NULL
                creator TEXT NOT NULL,
                title TEXT NOT NULL,
                group INTEGER NOT NULL,
                description TEXT,
                optionNames TEXT NOT NULL,
                optionValues TEXT,
            )
            """)
            # add the poll
            c.execute("INSERT INTO users VALUES (:email, :hashed_password, :name, :birthday, :groups)",
            {'email': email, 'hashed_password': password, 'name': name, 'birthday': date, 'groups': "0"})
            return True
    except:
        return False
     
def show_main_page(email):
    users_conn = sqlite3.connect('users.db')
    user_groups = []
    with users_conn:
        c = users_conn.cursor()
        c.execute("SELECT * FROM groups WHERE email=?")
        user_groups = c.fetchall()

    # Build the query string for getting all polls related to specific user
    placeholders = ', '.join(['?'] * len(user_groups))
    query = f"SELECT * FROM polls WHERE group IN ({placeholders});"
    polls_conn = sqlite3.connect('polls.db')
    polls = []
    with polls_conn:
        c = polls_conn.cursor()
        c.execute(query, user_groups)
        polls = c.fetchall()
    #TODO return list of tuples, enum with the utils POLL_FIELD
    return render_template("main_page.html", email, polls)
    #TODO - create that database and function to add votes to it