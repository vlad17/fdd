"""
Usage: python schedule.py < input

See README.md for input format
"""

from itertools import islice
import networkx as nx
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

    log.info('read {} tasks {} edges', len(names), len(edges))

    G = nx.DiGraph()
    G.add_nodes_from(range(len(names)))
    G.add_edges_from(edges)

    if not nx.algorithms.dag.is_directed_acyclic_graph(G):
        log.info('graph is not acyclic')
        sys.exit(1)

    G = nx.algorithms.dag.transitive_reduction(G)

    best_perm = None
    max_expected_saved = -math.inf
    log.info('incremental best time saved, results printed below')

    # is this problem submodular? maybe that gives an approx solution
    # for larger problem instances
    #
    # else maybe it's possible to use dynamic programming here
    #
    # inner loop optimization:
    # for similar perms, want to save state and just compute deltas
    #
    # input optimization: for nodes who have equal ordering in the
    # DAG partial order (stricter condition than not-orderable!)
    # can simply sort them by "density": failure rate * time,
    # don't need to investigate those permutations further
    # by collapsing into a single node.
    relabels = [np.arange(len(names), dtype=int)]
    inverses = relabels[:]
    for _ in range(10):
        orig = np.arange(len(names), dtype=int)
        np.random.shuffle(orig)
        inv = np.argsort(orig)
        relabels.append(orig)
        inverses.append(inv)

    attempts_per_seed = 100 * 100

    for mapping, inverse in zip(relabels, inverses):
        mapping = {i: x for i, x in enumerate(mapping)}
        H = nx.relabel_nodes(G, mapping)
        it = nx.algorithms.dag.all_topological_sorts(H)
        it = islice(it, attempts_per_seed)
        for perm in it:
            perm = inverse[perm]

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
                print('{:8.0f} hrs {}'.format(expected_saved, perm))

    log.info('found the best perm {}', best_perm)
    log.info('expected hours saved {}', max_expected_saved)
    print()
    print('tasks, in execution order:')
    for i in best_perm:
        print('   ', names[i])


if __name__ == "__main__":
    app.run(_main)
