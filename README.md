# fdd: Failure-driven Decision Making

This module, `fdd`, was inspired by Jacob Steinhardt's [Research as an SDP](https://cs.stanford.edu/~jsteinhardt/ResearchasaStochasticDecisionProcess.html) post. The setting is as follows.

> You have tasks A, B, C, D, ..., all of which might fail and require differing completion times. You'd like to get them all done successfully to reach your goal, but would like to fail fast otherwise. What order should you complete tasks in?

This comes up often when dealing with problems that require multiple creative, high-failure-rate steps to achieve. This module slightly generalizes the first approach Jacob lays out, providing a simple interface to finding the approach with the "maximum expected time saved".

Even at 12 tasks, considering all `12!` permutations of task orders slows even computers down to non-interactive speeds.

As inputs, we require task names (no commas allowed), completion times, and success rates, as percentages.

As outputs, we provide the order to execute the tasks in, to maximize expected time saved.

As a slight generalization, we provide the ability to add task dependencies. A dependent task's success rate should be given conditioned on the success of all of its parents. We assume we get to find out about a task's success at the end of the task.

## Setup

```
conda env create -f environment.yaml
source activate fdd-env
```

## Usage

Stdin format is expected to be a list of task names, completion time (hours or days), and success rate. After, we expect a new line and then a blocking graph over the tasks, specified in my custom DAG format. Yes, every input line must begin with a number and a period.

```
echo '
1. chop onions, 4 days, 95
2. prepare spices, 2 hours, 80
3. preheat oven, 1 hour, 90
4. bake chicken, 6 hours, 30
5. marinate chicken, 2 days, 80

3, 5 -> 4' | python -m fdd.main.schedule
# generates
# 
```

The above has one dependency, from preheating the oven to baking the chicken.

Blocking graph format is any number of lines of the form `x0, ..., xn -> y0, ..., ym -> z0, ..., zl`,
which imply directed edges from each `x*` to each `y*` and from each `y*` to each `z*`.

## Ballparks

## Not Available

#. Sometimes, multiple different tasks are redundant, in that completing any single one is enough to achieve this goal. This doesn't handle that case.
#. There might be uncertainty in your estimates for time and success rate. This isn't handled.
#. Some tasks may not be atomic, but rather have multiple possible failure points, or failure can happen according to a Poisson process. This isn't handled, but can be approximated with a long chain of dependent tasks.

## Dev info

All scripts are available in `scripts/`, and should be run from the repo root in the `fdd-env`.

| script | purpose |
| ------ | ------- |
| `lint.sh` | invokes `pylint` with the appropriate flags for this repo |
| `format.sh` | auto-format the entire `fdd` directory |

Use `conda env export > environment.yaml` to save new dependencies.
