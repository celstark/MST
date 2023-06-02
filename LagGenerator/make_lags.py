#!/usr/bin/env python

"""
Compute stimulus orderings for the mnemonic similarity task, described in:
Stark SM, Stevenson R, Wu C, Rutledge S, & Stark CEL (2015). Stability of
age-related deficits in the mnemonic similarity task across task variations.
Behavioral Neuroscience 129(3), 257-268.
Written by Nate Vack <njvack@wisc.edu> at the Center for Healthy Minds,
University of Wisconsin-Madison, for the mp2 study conducted by Dan Grupe
<grupe@wisc.edu>
Copyright 2018 Board of Regents of the University of Wisconsin System
Licensed under the MIT license.
"""

from __future__ import print_function, unicode_literals

import sys
import random
from itertools import count

import pandas as pd

import logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger()


# Change these constants to vary the generated data.
# We choose a lag by turning the ranges into
# lists, picking a random element from the list, and if we can't choose a lag
# of that length, removing it from the list.
# If a list is exhausted, we can't place any more lags of that length.
ZERO_LAGS = range(0, 1)
SHORT_LAGS = range(1, 10)
MED_LAGS = range(20, 81)
LONG_LAGS = range(120, 181)

LAG_COUNTS = [
    (8, ZERO_LAGS),
    (28, SHORT_LAGS),
    (14, MED_LAGS),
    (14, LONG_LAGS)
]

FOIL_TRIALS = 64

PAIR_TYPES = ['repeat', 'lure']
PAIR_COUNTS = [e[0] for e in LAG_COUNTS]
TOTAL_PAIR_TRIALS = sum(PAIR_COUNTS) * len(PAIR_TYPES) * 2  # two trials/pair

TOTAL_TRIALS = FOIL_TRIALS + TOTAL_PAIR_TRIALS


def main(task_filename, debug_filename=None):
    trial_list = make_trial_list()
    for_task = format_trial_list_for_task(trial_list)
    for_task.to_csv(task_filename, index=False, header=False)
    logger.info('Saved task data to {}'.format(task_filename))
    if debug_filename:
        trial_list.to_csv(debug_filename, index=False)
        logger.debug('Saved debug data to {}'.format(debug_filename))


def make_trial_list():
    logger.info('Generating {} total trials'.format(TOTAL_TRIALS))
    pd.set_option('display.max_rows', TOTAL_TRIALS)
    trial_list = pd.DataFrame(
        index=range(TOTAL_TRIALS),
        columns=['stim_number', 'trial_type', 'repetition', 'lag'])
    pair_type_counters = {pair_type: count(1) for pair_type in PAIR_TYPES}
    for c, lag_range in LAG_COUNTS:
        populate_lags(trial_list, c, lag_range, pair_type_counters)
    fill_foils(trial_list)
    return trial_list


def populate_lags(trial_list, lag_count, lag_range, pair_type_counters):
    """
    Adds lag_count * pair_types * 2 elements to trial_list.
    WARNING: Actively modifies trial_list.
    raises a RuntimeError if it can't place a lag in the specified range.
    """
    possible_lags = list(lag_range)
    for i in range(lag_count):
        for pair_type, counter in pair_type_counters.items():
            stim_number = next(counter)
            logger.debug('Trying to place {} #{}'.format(
                pair_type, stim_number))
            place_lagged_trials(
                trial_list, possible_lags, pair_type, stim_number)


def fill_foils(trial_list):
    foil_stim_numbers = list(range(1, FOIL_TRIALS + 1))
    random.shuffle(foil_stim_numbers)
    ix = trial_list[trial_list.stim_number.isnull()].index
    trial_list.loc[ix, 'stim_number'] = foil_stim_numbers
    trial_list.loc[ix, 'trial_type'] = 'foil'
    trial_list.loc[ix, 'repetition'] = 'x'


def place_lagged_trials(trial_list, possible_lags, pair_type, stim_number):
    """
    Puts both parts of a pair of trials into trial_list. Raises a RuntimeError
    if no possible_lags can fit in trial_list.
    """
    while len(possible_lags) > 0:
        lag = random.sample(possible_lags, 1)[0]
        starts = potential_start_indexes(trial_list, lag)
        if len(starts) == 0:
            logger.debug('No room for pair with lag {}'.format(lag))
            possible_lags.remove(lag)
            continue
        start_index = random.sample(starts, 1)[0]
        end_index = start_index + lag + 1
        logger.debug('Placed at {} and {}, lag {}'.format(
            start_index, end_index, lag))
        trial_list.loc[start_index].stim_number = stim_number
        trial_list.loc[start_index].trial_type = pair_type
        trial_list.loc[start_index].repetition = 'a'
        trial_list.loc[start_index].lag = lag
        trial_list.loc[end_index].stim_number = stim_number
        trial_list.loc[end_index].trial_type = pair_type
        trial_list.loc[end_index].repetition = 'b'
        trial_list.loc[end_index].lag = lag

        return

    else:
        logger.error(trial_list)
        free_count = trial_list.stim_number.isnull().sum()
        raise RuntimeError(
            'Out of possible lags: {} slots remain'.format(free_count))


def potential_start_indexes(trial_list, lag):
    """
    Find all the indexes (i) of trial_list where trial_list[i] and
    trial_list[i+lag+1] are blank. Returns an empty index if there are no
    candidate indexes.
    We can find this out by looking at the blank spaces in trial_list and
    a copy of the trial list shifted up by lag+1 slots, and seeing where
    both lists are blank.
    """
    start_blanks = trial_list.stim_number.isnull()
    end_blanks = start_blanks.shift(-1 * (lag + 1))
    matches = start_blanks & end_blanks
    return list(trial_list.index[matches])


def format_trial_list_for_task(trial_list):
    output = pd.DataFrame(index=trial_list.index, columns=['stype', 'lag'])
    output.stype = trial_list.apply(output_stim_type, axis=1)
    output.lag = trial_list.apply(output_lag, axis=1)
    return output


STYPE_CODE_MAP = {
    ('repeat', 'a'): 0,
    ('repeat', 'b'): 100,
    ('lure', 'a'): 200,
    ('lure', 'b'): 300,
    ('foil', 'x'): 400
}


def output_stim_type(row):
    stype_code_addend = STYPE_CODE_MAP.get(
        (row.trial_type, row.repetition), 9000)
    return stype_code_addend + row.stim_number


def output_lag(trial_row):
    if trial_row.repetition == 'b':
        return 500 + trial_row.lag
    return -1


if __name__ == '__main__':
    out_filename = sys.argv[1]
    debug_filename = None
    if len(sys.argv) > 2:
        debug_filename = sys.argv[2]
        logger.setLevel(logging.DEBUG)
    main(out_filename, debug_filename)