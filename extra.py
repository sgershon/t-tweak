""" Functions that represent the external world: Networks, DBs, whatever. For didactic purposes. """

import random
import string
import datetime


def get_network_time():
    """Gets the current time from the network (not really, but it could)."""
    return datetime.datetime.now()


def get_rand_char():
    """Gets a truly random character from our expensive Random Generator (not really, but could've been)."""
    return random.choice(string.ascii_letters + string.digits)


def reset_random(seed):
    """Sets the random seed. Really."""
    random.seed(seed)


def update_db(a_db, value):
    """Advanced DB Management.
    (In this example, it receives a list and adds the values to it. If a_db is not a list, it
        my crash with an exception. The value needs to be exact, as it is entered as is in the db.)
    """
    if value is None:
        a_db.clear()
    else:
        a_db.append(value)
    return None


def read_db(a_db):
    """Advanced DB Management. (But in this example, it receives a list and adds the values to it.)"""
    return a_db
