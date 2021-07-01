from itertools import chain, combinations
import numpy as np
from z3 import And, Or, Not, Solver, Bool


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


s = Solver()
possible_permutations = find_subsets(requirements, max_requirement)
all_conditions = []
for t in range(MAX_T):
    ors = []
    for subset in possible_permutations:
        ands = []
        for element in subset:
            ands.append(Bool(f'{t},{element}'))
            for excluded_element in set(tasks)-set(subset):
                ands.append(Not(Bool(f'{t},{excluded_element}')))
        subset_clause = And(ands)
        ors.append(subset_clause)
    all_conditions.append(Or(ors))
s.add(And(all_conditions))
print(s.check())
print(s.model())
