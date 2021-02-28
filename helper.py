"""
Helper functions
"""

from typing import Callable
import time
import os, sys
from torch import Tensor
from pytorch_lightning import seed_everything

VERBOSITY = 3
TIMESTAMPED = False
DATA_DIR = '/Users/wouter/Documents/OneDrive/Education/KULeuven/MAI/013_THESIS/data'


# Set parameters
def set_params(verbosity: int = None, timestamped: bool = None, data_dir: str = None):
    global VERBOSITY
    global TIMESTAMPED
    global DATA_DIR

    VERBOSITY = verbosity if verbosity else VERBOSITY
    TIMESTAMPED = timestamped if timestamped else TIMESTAMPED
    DATA_DIR = data_dir if data_dir else DATA_DIR

    if data_dir:
        log("DATA_DIR is now set to {}".format(DATA_DIR), verbosity=1)
    if verbosity:
        log("VERBOSITY is set to {}".format(TIMESTAMPED),verbosity=1)


def hi(title=None):
    """
    Say hello. (It's stupid, I know.)
    If there's anything to initialize, do so here.
    """

    print("\n")
    print("     ___   _     __               __")
    print("    / _ | (_)___/ /  ___ ___ ____/ /")
    print("   / __ |/ / __/ _ \/ -_) _ `/ _  /")
    print("  /_/ |_/_/_/ /_//_/\__/\_,_/\_,_/")
    print()

    if title:
        log(title, title=True)

    print("VERBOSITY is set to {}.".format(VERBOSITY))
    print("DATA_DIR is set to {}".format(DATA_DIR))
    print()

    # Set seed
    seed_everything(616)


# Expand on what happens to input when sent through layer
def whatsgoingon(layer: Callable, input: Tensor):
    """
    Processes input through layer, and prints the effect on the dimensionality
    """

    # Generate output
    output = layer(input)

    # Log the effect
    log(f'{layer.__name__}: {input.shape} --> {output.shape}')

    return output


# Fancy print
def log(*message, verbosity=3, timestamped=TIMESTAMPED, sep="", title=False):
    """
    Print wrapper that adds timestamp, and can be used to toggle levels of logging info.

    :param message: message to print
    :param verbosity: importance of message: level 1 = top importance, level 3 = lowest importance
    :param timestamped: include timestamp at start of log
    :param sep: separator
    :param title: toggle whether this is a title or not
    :return: /
    """

    # Title always get shown
    verbosity = 1 if title else verbosity

    # Print if log level is sufficient
    if verbosity <= VERBOSITY:

        # Print title
        if title:
            n = len(*message)
            print('\n' + (n + 4) * '#')
            print('# ', *message, ' #', sep='')
            print((n + 4) * '#' + '\n')

        # Print regular
        else:
            t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            print((str(t) + (" - " if sep == "" else "-")) if timestamped else "", *message, sep=sep)

    return


def time_it(f: Callable):
    """
    Timer decorator: shows how long execution of function took.
    :param f: function to measure
    :return: /
    """

    def timed(*args, **kwargs):
        t1 = time.time()
        res = f(*args, **kwargs)
        t2 = time.time()

        log("\'", f.__name__, "\' took ", round(t2 - t1, 3), " seconds to complete.", sep="")

        return res

    return timed


def set_dir(dir) -> str:
    """
    If folder doesn't exist, make it.

    :param dir: directory to check/create
    :return: path to dir
    """

    if not os.path.exists(dir):
        os.makedirs(dir)
        log("WARNING: Data directory <{dir}> did not exist yet, and was created.".format(dir=dir), verbosity=1)
    else:
        log("\'{}\' folder accounted for.".format(dir), verbosity=3)

    return dir