"""manage utility functions and structures for organizing the project"""
import random
import time
import string
import logging

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
    "group": 4,
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
