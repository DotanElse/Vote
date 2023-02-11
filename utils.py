"""manage utility functions and structures for organizing the project"""
import random
import string
import logging
import bcrypt

logging.basicConfig(level=logging.INFO, format='%(lineno)d:%(funcName)s:%(message)s')

_POLL_ID_LEN = 11
_USER_ID_LEN = 6
_LINK_LEN = 12
_GROUP_ID_LEN = 5

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
    "startTime": 1,
    "creator": 2,
    "title": 3,
    "group_": 4,
    "description": 5,
    "optionNames": 6,
    "optionValues": 7,
    "idVoted": 8,
    "duration": 9,
}
GROUP_FIELD = {
    "id": 0,
    "name": 1,
    "description": 2,
    "creator": 3,
    "users": 4,
    "usersNum": 5,
    "permLink": 6,
    "invited": 7,
    "public": 8,
}
DISCUSSION_FIELD = {
    "id": 0,
    "o1": 1,
    "o2": 2,
    "o3": 3,
    "o4": 4,
    "o5": 5,
    "o6": 6,
    "o7": 7,
    "o8": 8,
    "o9": 9,
    "o10": 10,
    "v1": 11,
    "v2": 12,
    "v3": 13,
    "v4": 14,
    "v5": 15,
    "v6": 16,
    "v7": 17,
    "v8": 18,
    "v9": 19,
    "v10": 20,
    "u1": 21,
    "u2": 22,
    "u3": 23,
    "u4": 24,
    "u5": 25,
    "u6": 26,
    "u7": 27,
    "u8": 28,
    "u9": 29,
    "u10": 30,
}

def get_random_poll_id():
    characters = string.ascii_lowercase + string.digits
    return "".join(random.choices(characters, k=_POLL_ID_LEN))

def get_random_user_id():
    characters = string.ascii_lowercase + string.digits
    return "".join(random.choices(characters, k=_USER_ID_LEN))

def get_random_group_id():
    characters = string.ascii_lowercase + string.digits
    return "".join(random.choices(characters, k=_GROUP_ID_LEN))

def get_random_perm_link():
    characters = string.ascii_lowercase + string.digits
    return "".join(random.choices(characters, k=_LINK_LEN))
    
def str_to_list(input):
    # Split the input string on commas
    if not input:
        return []
    items = input.split(',')
    # Strip leading and trailing whitespace from each item
    return [item.strip() for item in items]

def list_to_str(input):
    return ', '.join(input)

def encrypt(input : str):
    logging.info("start")
    return bcrypt.hashpw(str.encode(input), bcrypt.gensalt())

def check_password(password, hashed):
    logging.info("start")
    return bcrypt.checkpw(str.encode(password), hashed)

def remove_password_field(user):
    # only password is in byte form, sending it over to frontend
    return tuple(field for field in user if isinstance(field, str))