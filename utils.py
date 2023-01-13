"""manage utility functions and structures for organizing the project"""
import random
import string
import logging
from flask_jwt_extended import create_access_token

logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(module)s:%(message)s')

_poll_ID_LEN = 11
_user_ID_LEN = 6

USER_FIELD = {
    "id": 0,
    "email": 1,
    "password": 2,
    "name": 3,
    "birthday": 4,
    "groups": 5,
}
POLL_FIELD = {
    "id": 0,
    "start_time": 1,
    "creator": 2,
    "title": 3,
    "group_": 4,
    "description": 5,
    "optionNames": 6,
    "optionValues": 7,
    "idVoted": 8,
    "duration": 9,
    "public": 10,
}

def get_random_poll_id():
    characters = string.ascii_lowercase + string.digits
    return "".join(random.choices(characters, k=_poll_ID_LEN))

def get_random_user_id():
    characters = string.ascii_lowercase + string.digits
    return "".join(random.choices(characters, k=_user_ID_LEN))
    
def str_to_list(input):
    # Split the input string on commas
    items = input.split(',')
    # Strip leading and trailing whitespace from each item
    return [item.strip() for item in items]

def list_to_str(input):
    return ', '.join(input)
