"""manage utility functions and structures for organizing the project"""
import random
import string
import logging
from flask_jwt_extended import create_access_token

logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(module)s:%(message)s')

_poll_ID_LEN = 11

USER_FIELD = {
    "email": 0,
    "hashed_password": 1,
    "name": 2,
    "birthday": 3,
    "groups": 4,
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
    
def str_to_list(input):
    # Split the input string on commas
    items = input.split(',')
    # Strip leading and trailing whitespace from each item
    return [item.strip() for item in items]

def list_to_str(input):
    return ', '.join(input)

def get_access_token(user):
    user_email = user[USER_FIELD['email']]
    user_name = user[USER_FIELD['name']]
    user_groups = user[USER_FIELD['groups']]
    user_birthday = user[USER_FIELD['birthday']]

    # Set the user's ID, name, and email as the identity in the JWT
    return create_access_token(identity={
        'email': user_email,
        'name': user_name,
        'groups': user_groups,
        'birthday': user_birthday
    })