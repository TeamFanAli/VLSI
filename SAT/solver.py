from itertools import chain, combinations
import numpy as np
from numpy.core.numeric import full
from z3 import And, Or, Not, Solver, Bool, is_true


def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))


MAX_T = 2
n = 2
max_requirement = 1
timesteps = range(0, MAX_T)
tasks = range(0, n)
requirements = np.array([1, 1])
durations = np.array([1, 1])


def find_subsets(requirements, max_requirement):
    """Finds all the subsets of tasks that can be run within max_requirement.
    Exponentially bad.

    Args:
        requirements (list[int]): list of requirements
        max_requirement (int): max computational power
    """
    result = []
    for possible_set_indices in powerset(range(len(requirements))):
        if sum(requirements[list(possible_set_indices)]) <= max_requirement:
            result.append(list(possible_set_indices))
    return result


def find_subsets_to_max(max, requirement):
    subsets = []
    for i in range(max-requirement):
        subsets.append(np.arange(i, i+requirement, 1))
    return subsets


s = Solver()
possible_permutations = find_subsets(requirements, max_requirement)
all_conditions = []
task_active = {}
"""
First, we constrain the resources:
 for each timestep, we check the possible permutations that respect the resources constraint
 and specify an OR to choose between one of these for each timestep
 """
for t in range(MAX_T):
    ors = []
    for subset in possible_permutations:
        ands = []
        for task in subset:
            # First try to look for the bool in the saved ones
            try:
                ands.append(task_active[t][task])
            except KeyError:
                if t in task_active:  # If the timestep is already defined, just add this bool
                    task_active[t][task] = Bool(f'{t},{task}')
                else:  # Otherwise, create the timestep dict and the bool
                    task_active[t] = {task: Bool(f'{t},{task}')}
                ands.append(task_active[t][task])
            # Then, specify that other tasks can't be active if this is
            for other_task in tasks:
                if other_task != task:
                    try:
                        ands.append(Not(task_active[t][other_task]))
                    except KeyError:
                        if t in task_active:  # If the timestep is already defined, just add this bool
                            task_active[t][other_task] = Bool(
                                f'{t},{other_task}')
                        else:  # Otherwise, create the timestep dict and the bool
                            task_active[t] = {
                                other_task: Bool(f'{t},{other_task}')}
                        ands.append(Not(task_active[t][other_task]))
            # Then negate the other ones
            for excluded_task in set(tasks)-set(subset):
                try:
                    ands.append(Not(task_active[t][excluded_task]))
                except KeyError:
                    if t in task_active:  # If the timestep is already defined, just add this bool
                        task_active[t][excluded_task] = Bool(
                            f'{t},{excluded_task}')
                    else:  # Otherwise, create the timestep dict and the bool
                        task_active[t] = {excluded_task: Bool(
                            f'{t},{excluded_task}')}
                    ands.append(Not(task_active[t][excluded_task]))
        if len(ands) > 0:
            subset_clause = And(ands)
            if subset_clause is not None:
                ors.append(subset_clause)
    if len(ors) > 0:
        all_conditions.append(Or(ors))
if len(all_conditions) > 0:
    s.add(And(all_conditions))

"""
Then, the duration constraint: if a task becomes active at time i, it will have to stay active until time i+d
We therefore have to get the set of sequences of d timesteps between 0 and t_max
"""
task_ands = []
for task in tasks:
    ors = []
    for timestep_sequence in find_subsets_to_max(MAX_T, durations[task]):
        ands = []
        for timestep in timestep_sequence:
            ands.append(task_active[timestep][task])
        # And negate the other timesteps
        for excluded_timestep in np.setdiff1d(np.arange(0, MAX_T, 1), timestep_sequence):
            ands.append(Not(task_active[excluded_timestep][task]))
        if len(ands) > 0:
            ors.append(And(ands))
    if len(ors) > 0:
        task_ands.append(Or(ors))
if len(task_ands) > 0:
    s.add(And(task_ands))
s.check()
print(s)
m = s.model()
# Dictionary containing task:[timesteps]
cumulative_solution = {t: [] for t in tasks}
for t in m.decls():
    if is_true(m[t]):
        timestep, task = tuple(str(t).split(','))
        cumulative_solution[int(task)].append(int(timestep))
print(cumulative_solution)

task_active = {t: {} for t in tasks}
full_proposition = []
for task in tasks:
    ors = []
    for subset_of_requirement in find_subsets_to_max(max_requirement, requirements[task]):
        # We want to get all the timesteps in which the task is true
        x_ands = []
        for x_timestep in cumulative_solution[task]:
            # Then AND the Ys of that task at X
            ands = []
            for y in subset_of_requirement:
                try:
                    ands.append(task_active[task][x_timestep][y])
                except KeyError:
                    if x_timestep in task_active[task]:
                        task_active[task][x_timestep][y] = Bool(
                            f"{task},{x_timestep},{y}")
                    else:
                        task_active[task][x_timestep] = {
                            y: Bool(f"{task},{x_timestep},{y}")}
                    ands.append(task_active[task][x_timestep][y])
                for other_task in tasks:
                    if other_task != task:
                        try:
                            ands.append(
                                Not(task_active[other_task][x_timestep][y]))
                        except KeyError:
                            if x_timestep in task_active[other_task]:
                                task_active[other_task][x_timestep][y] = Bool(
                                    f"{other_task},{x_timestep},{y}")
                            else:
                                task_active[other_task][x_timestep] = {
                                    y: Bool(f"{other_task},{x_timestep},{y}")}
                            ands.append(
                                Not(task_active[other_task][x_timestep][y]))
                for y_excluded in np.setdiff1d(np.arange(0, max_requirement, 1), subset_of_requirement):
                    try:
                        ands.append(
                            Not(task_active[task][x_timestep][y_excluded]))
                    except KeyError:
                        if x_timestep in task_active[task]:
                            task_active[task][x_timestep][y_excluded] = Bool(
                                f"{task},{x_timestep},{y_excluded}")
                        else:
                            task_active[task][x_timestep] = {
                                y_excluded: Bool(f"{task},{x_timestep},{y_excluded}")}
                        ands.append(
                            Not(task_active[task][x_timestep][y_excluded]))
            if len(ands) > 0:
                x_ands.append(And(ands))
        if len(x_ands) > 0:
            ors.append(And(x_ands))
    if len(ors) > 0:
        full_proposition.append(Or(ors))
s = Solver()
if len(full_proposition) > 0:
    s.add(full_proposition)
print(s.check())
m = s.model()
# To find the starts of the chips, we just get the minimum of the Xs and Ys
starts = {t: [MAX_T, max_requirement] for t in tasks}
for t in m.decls():
    if is_true(m[t]):
        task, x, y = tuple([int(to_cast) for to_cast in str(t).split(',')])
        if starts[task][0] > x:
            starts[task][0] = x
        if starts[task][1] > y:
            starts[task][1] = y
print(starts)
