from itertools import chain, combinations
import numpy as np
from z3 import And, Or, Not, Solver, Bool, is_true


def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))


MAX_T = 10
n = 5
max_requirement = 10
timesteps = range(0, MAX_T)
tasks = range(0, n)
requirements = np.array([5, 4, 3, 6, 3])
durations = np.array([4, 3, 6, 3, 1])


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


def find_duration_subsets(max_t, duration):
    subsets = []
    for i in range(max_t-duration):
        subsets.append(np.arange(i, i+duration, 1))
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
        for element in subset:
            # First try to look for the bool in the saved ones
            try:
                ands.append(task_active[t][element])
            except KeyError:
                if t in task_active:  # If the timestep is already defined, just add this bool
                    task_active[t][element] = Bool(f'{t},{element}')
                else:  # Otherwise, create the timestep dict and the bool
                    task_active[t] = {element: Bool(f'{t},{element}')}
                ands.append(task_active[t][element])
            # Then negate the other ones
            for excluded_element in set(tasks)-set(subset):
                try:
                    ands.append(Not(task_active[t][excluded_element]))
                except KeyError:
                    if t in task_active:  # If the timestep is already defined, just add this bool
                        task_active[t][excluded_element] = Bool(
                            f'{t},{excluded_element}')
                    else:  # Otherwise, create the timestep dict and the bool
                        task_active[t] = {excluded_element: Bool(
                            f'{t},{excluded_element}')}
                    ands.append(Not(task_active[t][excluded_element]))
        subset_clause = And(ands)
        ors.append(subset_clause)
    all_conditions.append(Or(ors))
s.add(And(all_conditions))

"""
Then, the duration constraint: if a task becomes active at time i, it will have to stay active until time i+d
We therefore have to get the set of sequences of d timesteps between 0 and t_max
"""
task_ands = []
for task in tasks:
    ors = []
    for timestep_sequence in find_duration_subsets(MAX_T, durations[task]):
        ands = []
        for timestep in timestep_sequence:
            ands.append(task_active[timestep][task])
        # And negate the other timesteps
        for excluded_timestep in np.setdiff1d(np.arange(0, MAX_T, 1), timestep_sequence):
            ands.append(Not(task_active[excluded_timestep][task]))
        ors.append(And(ands))
    task_ands.append(Or(ors))
s.add(And(task_ands))
# The
print(s.check())
print(s.model())
m = s.model()
for t in m.decls():
    if is_true(m[t]):
        print(t)
