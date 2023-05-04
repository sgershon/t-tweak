""" Fake module to fake fcntl in Windows OS. Opens a very small risk of concomitant file access. """

LOCK_EX = "lock exclusively"
LOCK_UN = "lock unlock"


def flock(*argv):
    """ Get the command. Ignore it. In the linux driver this locks the file until edit ends."""
    return True
