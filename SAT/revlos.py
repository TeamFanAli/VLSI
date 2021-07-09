from itertools import chain, combinations, product
import itertools
import numpy as np
import argparse
from time import time
from utility import parse_args, preprocess, postprocess, print_rectangles_from_string
from numpy.core.numeric import full
from z3 import And, Or, Not, Solver, Bool, is_true, sat, unsat, Implies
from collections import defaultdict


def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))


def get_possible_rotations(length):
    return [list(i) for i in itertools.product([False, True], repeat=length)]


def find_subsets(widths, heights, max_width):
    """Finds all the subsets of chips that can sit in max_width, with rotations.
    Exponentially bad.

    Args:
        widths (list[int]): list of widths
        heights (list[int]): list of heights
        max_width (int): max width
    """
    result = []
    for possible_set_indices in powerset(range(len(widths))):
        for possible_rotations_array in get_possible_rotations(len(possible_set_indices)):
            sum = 0
            for i in range(len(possible_set_indices)):
                sum += widths[possible_set_indices[i]
                              ] if not possible_rotations_array[i] else heights[possible_set_indices[i]]
            if sum <= max_width:
                result.append((possible_set_indices, possible_rotations_array))
    return result


def find_subsets_to_max(max, requirement):
    subsets = []
    for i in range(max-requirement+1):
        subsets.append(np.arange(i, i+requirement, 1))
    return subsets


def solve_instance(max_width, max_height, n, widths, heights):
    tasks = range(0, n)
    s = Solver()
    possible_permutations = find_subsets(widths, heights, max_width)
    all_conditions = []
    task_active = defaultdict(lambda: defaultdict(dict))
    """
    First, we constrain the resources:
    for each timestep, we check the possible permutations that respect the resources constraint
    and specify an OR to choose between one of these for each timestep
    """
    for t in range(max_height):
        ors = []
        for indices, rotations in possible_permutations:
            ands = []
            for i in range(len(indices)):
                # First try to look for the bool in the saved ones
                try:
                    ands.append(task_active[t][indices[i]][rotations[i]])
                except KeyError:
                    task_active[t][indices[i]][rotations[i]] = Bool(
                        f'{t},{indices[i]}, {rotations[i]}')
                    ands.append(task_active[t][indices[i]][rotations[i]])
                # And the negation of its rotated sibling
                try:
                    ands.append(
                        Not(task_active[t][indices[i]][not rotations[i]]))
                except KeyError:
                    task_active[t][indices[i]][not rotations[i]] = Bool(
                        f'{t},{indices[i]}, {not rotations[i]}')
                    ands.append(
                        Not(task_active[t][indices[i]][not rotations[i]]))
                # Then negate the other ones
                for excluded_task in set(tasks)-set(indices):
                    try:
                        if not True in task_active[t][excluded_task]:
                            task_active[t][excluded_task][True] = Bool(
                                f'{t},{excluded_task}, {True}')
                    except KeyError:
                        task_active[t][excluded_task][True] = Bool(
                            f'{t},{excluded_task}, {True}')
                    try:
                        if not False in task_active[t][excluded_task]:
                            task_active[t][excluded_task][False] = Bool(
                                f'{t},{excluded_task}, {False}')
                    except KeyError:
                        task_active[t][excluded_task][False] = Bool(
                            f'{t},{excluded_task}, {False}')
                    # If the task isn't present in the set, we'll want to negate both the rotated and non-rotated versions
                    ands.append(Not(task_active[t][excluded_task][True]))
                    ands.append(Not(task_active[t][excluded_task][False]))
            if len(ands) > 0:
                subset_clause = And(ands)
                if subset_clause is not None:
                    ors.append(subset_clause)
        # Or, possibly, no task could be active in this timestep
        empty_timestep = [Not(task_active[t][task][True])
                          for task in tasks]+[Not(task_active[t][task][False])
                                              for task in tasks]
        ors.append(And(empty_timestep))
        all_conditions.append(Or(ors))
    if len(all_conditions) > 0:
        s.add(And(all_conditions))

    """
    Then, the duration constraint: if a task becomes active at time i, it will have to stay active until time i+d
    We therefore have to get the set of sequences of d timesteps between 0 and t_max
    """
    # We first do this for non-rotated circuits
    task_ands = []
    for task in tasks:
        ors = []
        # This variable is used to check that we don't pass both the rotated and non-rotated checks: it would be unsat.
        already_passed = False
        for rotation in [False, True]:
            height_subsets = find_subsets_to_max(
                max_height, widths[task]) if rotation else find_subsets_to_max(max_height, heights[task])
            if len(height_subsets) == 0:
                if not already_passed:
                    already_passed = True
                    pass
                else:
                    return False, {}
            for timestep_sequence in height_subsets:
                ands = []
                for timestep in timestep_sequence:
                    ands.append(task_active[timestep][task][rotation])
                    ands.append(Not(task_active[timestep][task][not rotation]))
                # And negate the other timesteps
                for excluded_timestep in np.setdiff1d(np.arange(0, max_height, 1), timestep_sequence):
                    ands.append(
                        Not(task_active[excluded_timestep][task][False]))
                    ands.append(
                        Not(task_active[excluded_timestep][task][True]))
                if len(ands) > 0:
                    ors.append(And(ands))
        if len(ors) > 0:
            task_ands.append(Or(ors))
    if len(task_ands) > 0:
        s.add(And(task_ands))
    if s.check() == unsat:
        return False, {}
    m = s.model()
    # Dictionary containing task:[timesteps]
    cumulative_solution = {t: [] for t in tasks}
    for t in m.decls():
        if is_true(m[t]):
            timestep, task, rotation = tuple(str(t).split(','))
            cumulative_solution[int(task)].append(
                (int(timestep), rotation.strip() == "True"))
    # We then invert height and widths for rotated circuits
    for i in range(len(cumulative_solution)):
        # To check if the circuit is rotated, we take value 1 (the rotation) at timestep 0, since it will be the same at all timesteps
        if cumulative_solution[i][0][1]:
            widths[i], heights[i] = heights[i], widths[i]
        # Then, we can get rid of the rotation infos
        for t in range(len(cumulative_solution[i])):
            cumulative_solution[i][t] = cumulative_solution[i][t][0]

    task_active = {t: {} for t in tasks}
    full_proposition = []
    for task in tasks:
        ors = []
        for subset_of_requirement in find_subsets_to_max(max_width, widths[task]):
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
                    for y_excluded in np.setdiff1d(np.arange(0, max_width, 1), subset_of_requirement):
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
    if s.check() == unsat:
        return False, {}
    m = s.model()
    # To find the starts of the chips, we just get the minimum of the Xs and Ys
    starts = {t: [max_height, max_width] for t in tasks}
    for t in m.decls():
        if is_true(m[t]):
            task, x, y = tuple([int(to_cast) for to_cast in str(t).split(',')])
            if starts[task][0] > x:
                starts[task][0] = x
            if starts[task][1] > y:
                starts[task][1] = y

    return True, starts


if __name__ == "__main__":
    w, n, widths, heights = preprocess(parse_args())
    # Iterate until it's sat
    total_area = np.sum([widths[i] * heights[i] for i in range(len(widths))])
    lower_bound = int(total_area / w) + \
        (0 if (total_area % w == 0) else 1)
    upper_bound = sum(heights)
    height = lower_bound  # We start checking heights at the lower bound
    found_sat = False
    decrementing = False
    last_working_solution = None
    while True:
        print(f"Trying solution with height={height}")
        first_instance_start = time()
        found_sat, solution = solve_instance(w, height, n, widths, heights)
        print("which took %s seconds" %
              round((time()-first_instance_start), 4))
        print(f"and resulted {found_sat}")
        if not found_sat and not decrementing:
            decrementing = False
            height = int(height*1.2) if int(height *
                                            1.2) < upper_bound else upper_bound
        elif (not found_sat) and decrementing:
            height += 1
            break
        else:
            decrementing = True
            last_working_solution = solution
            height -= 1
    solution_string = postprocess(
        w, height, n, widths, heights, last_working_solution)
    print_rectangles_from_string(solution_string)
