"""
Usage: python schedule.py < input

See README.md for input format
"""

import numpy as np
import itertools
import math
import sys
import re

from absl import app

from .. import log

def _main(_argv):
    log.init()

    reading_tasks = False # else reading edges

    task_number = 0

    names = []
    hours = []
    failure_rates = []

    edges = []

    for line in sys.stdin.readlines():
        if not line.strip():
            continue

        ls = line.strip()
        if ls == 'tasks':
            reading_tasks = True
            continue
        elif ls == 'edges':
            reading_tasks = False
            continue

        if reading_tasks:
            m = re.fullmatch(r'(\d+)\. ([^,]*),(\s?\d*)\s*(hour|day)s?\s*,\s*(\d)*', line.strip())
            if not m:
                log.info('line {} does not match input regex', task_number)
                sys.exit(1)
            task_number_given = int(m.group(1).strip())
            assert task_number_given == task_number
            names.append(m.group(2).strip())
            is_hours = m.group(4) == 'hour'
            hours.append(float(m.group(3)) * (1 if is_hours else 24))
            failure_rates.append((100 - float(m.group(5))) / 100)
            task_number += 1
            continue

        dag_splits = line.split('->')
        # todo input validation on format, numbers
        for froms, tos in zip(dag_splits, dag_splits[1:]):
            froms = froms.split(',')
            tos = tos.split(',')
            for x, y in itertools.product(froms, tos):
                edges.append((int(x), int(y)))

    # todo dag check

    log.info('read {} tasks {} edges', len(names), len(edges))
    best_perm = None
    max_expected_saved = -math.inf

    # is this problem submodular? maybe that gives an approx solution
    # for larger problem instances
    #
    # else maybe it's possible to use dynamic programming here
    #
    # easy optimization for heavy deps: only generate valid DAG paths
    for perm in itertools.permutations(range(len(names))):
        fails = False
        for x, y in edges:
            # easy N^2 -> N: compute inverse permutation array
            # of the permutation,
            # do lookup on edge index
            if perm.index(x) > perm.index(y):
                fails = True
                break
        if fails:
            continue

        hours_remaining = np.asarray(hours)[np.asarray(perm)]
        hours_remaining = np.roll(np.cumsum(hours_remaining[::-1]), -1)
        hours_remaining[-1] = 0

        pfailure = np.asarray(failure_rates)[np.asarray(perm)]
        psuccess = np.roll(1 - pfailure, 1)
        psuccess[0] = 1

        saved_at_index = pfailure * hours_remaining
        p_get_to_index = np.cumprod(psuccess)

        expected_saved = (p_get_to_index * saved_at_index).sum()

        if expected_saved > max_expected_saved:
            max_expected_saved = expected_saved
            best_perm = perm

    log.info('found the best perm {}', best_perm)
    log.info('expected hours saved {}', max_expected_saved)
    print()
    print('tasks, in execution order:')
    for i in best_perm:
        print('   ', names[i])


if __name__ == "__main__":
    app.run(_main)
