"""
SMT solver for the VLSI problem, allowing rotations

This is the rotating VLSI solver, allowing 
rotations in the chips. It exploits the Z3 SMT solver.
Needs the cumulative.py and utility.py scripts.

Authors: TeamFanAli (github.com/teamfanali)
Version: 1.0
"""
from numpy.core.defchararray import lower, upper
from z3 import *
from utility import *
from halo import Halo
from time import time


def declare_ends(solver, rotations, starts, ends, durations, req):
    """Declares the end coordinates for each circuit, checking whether it has been rotated or not

    Args:
        solver (Solver): The Z3 solver object
        rotations (BoolVector): contains True if the circuit is rotated, False if not
        starts (IntVector): The starts of tasks, basically the Ys of chips
        ends (IntVector): The ends of tasks, basically Y+height
        durations (List): List of heights of circuits
        req (List): List of widths of circuits
    """
    for i in range(len(durations)):
        solver.add(ends[i] == starts[i]+If(rotations[i], req[i], durations[i]))


def declare_max(solver, array, max):
    """This is needed to get the makespan, which is the maximum Y.
    We can exploit some constraints to declare a maximum: we specify that it has to be >= than all the elements,
    but still equal to one of them.

    Args:
        solver (Solver): The Z3 solver object
        array (IntVector): The array we want to find the maximum of.
        max (Int): The constant that will contain the maximum.
    """
    # We specify that max has to be greater\equal then all the elements
    for i in range(len(array)):
        solver.add(max >= array[i])
    # and that it has to be equal to at least one element
    solver.add(Or([max == array[i] for i in range(len(array))]))


def declare_makespan_bounds(solver, width, makespan, req, durations):
    """This is needed to constrain our search a little bit by limiting makespan

    Args:
        solver ([type]): [description]
        width (Int): The width of the chip
        makespan (Int): The height of the chip
        req (List): The list of requirements, i.e. our circuits' widths
        durations (List): The list of durations, i.e. our circuits' heights
    """
    total_area = np.sum([req[i]*durations[i]
                         for i in range(len(req))])
    lower_bound = int(total_area / width) + \
        (0 if (total_area % width == 0) else 1)
    # We can use the minimum among the sums of durations and reqs: in the worst case we can rotate them all
    upper_bound = np.sum([max([durations[i], req[i]])
                          for i in range(len(durations))])
    solver.add(makespan <= int(upper_bound))
    solver.add(makespan >= lower_bound)


def solve(width, n, durations, req, verbosity):
    if verbosity > 0:
        spinner = Halo(
            text=f'Solving the cumulative constraint to find the Ys', spinner='monkey')
        spinner.start()
    solver = Optimize()
    starts = IntVector('starts', n)
    ends = IntVector('ends', n)
    rotations = BoolVector('rotations', n)
    declare_ends(solver, rotations, starts, ends, durations, req)
    makespan = Int('makespan')
    declare_max(solver, ends, makespan)
    cumulative(solver, starts, durations, rotations, req, width)
    declare_makespan_bounds(solver, width, makespan, req, durations)
    starting_time = time()
    solver.minimize(makespan)
    is_sat = solver.check()
    model = solver.model()
    height = model[makespan]
    if verbosity > 0:
        spinner.stop()
        print(f"Solved the cumulative optimization in %s seconds" %
              round((time()-starting_time), 4))
    assert is_sat
    if verbosity > 0:
        spinner = Halo(
            text=f'Now satisfying the X constraints', spinner='monkey')
        spinner.start()
    y = [model[starts[i]] for i in range(len(starts))]
    rotations = [model[rotations[i]] for i in range(len(rotations))]
    # We can swap width and height for rotated circuits and act like nothing happened
    for i in range(len(rotations)):
        if rotations[i]:
            req[i], durations[i] = durations[i], req[i]
    x_solver = Solver()
    x = IntVector('x', n)
    x_finder(x_solver, x, y, durations, req, width)
    x_solver.check()
    model = x_solver.model()
    x = [model[x[i]] for i in range(len(x))]
    if verbosity > 0:
        spinner.stop()
        print("???? Optimization done in a total of %s seconds!" %
              round((time()-starting_time), 4))
    return height, req, durations, x, y


def cumulative(solver, starts, durations, rotations, requirements, resource_limit):
    """Cumulative constraint decomposition for Z3. Considers the possible rotations.

    Args:
        solver ([type]): [description]
        starts (IntVector): The starts of tasks, basically the Ys of chips
        durations (List): List of heights of circuits
        rotations (BoolVector): contains True if the circuit is rotated, False if not
        requirements (List): List of widths of circuits
        resource_limit (Int): width of the chip
    """
    # We'll have to change durations and requirement to support rotations:
    # durations[i] -> If(rotations[i], requirements[i], durations[i])
    # requirements[i] -> If(rotations[i], durations[i], requirements[i])
    solver.add(And([starts[i] >= 0 for i in range(len(starts))]))
    for task in range(len(starts)):
        sum = []
        for other_task in range(len(starts)):
            if task != other_task:
                sum.append(If(And([starts[other_task] <= starts[task], starts[task] < (
                    starts[other_task] + If(rotations[other_task], requirements[other_task], durations[other_task]))]), 1, 0)*If(rotations[other_task], durations[other_task], requirements[other_task]))
        solver.add(resource_limit >= (
            If(rotations[task], durations[task], requirements[task]) + Sum(sum)))
    # Then, we can add the helper constraints
    for i in range(len(starts)):
        for j in range(i):
            solver.add(
                Or([starts[j] >= starts[i], starts[j] < (starts[i]+If(rotations[i], requirements[i], durations[i]))]))
            solver.add(
                Or([starts[i] >= starts[j], starts[i] < (starts[j]+If(rotations[j], requirements[j], durations[j]))]))
            solver.add(Or([starts[j] >= starts[i], starts[i] >= starts[j]]))
            solver.add(Implies(starts[j] >= starts[i],
                               starts[i] < (starts[j]+If(rotations[j], requirements[j], durations[j]))))
            solver.add(Implies(starts[i] >= starts[j],
                               starts[j] < (starts[i]+If(rotations[i], requirements[i], durations[i]))))


def x_finder(solver, x, y, heights, widths, width_limit):
    """Finds the missing coordinate after the cumulative solution is found

    Args:
        solver (Solver): The Z3 solver object
        x (IntVector): Vector of the Xs we're looking for
        y (List): List of the Ys found by cumulative
        heights (List): The heights of circuits
        widths (List): The widths of circuits
        width_limit (Int): The maximum width of the chip
    """
    for i in range(len(y)):
        for j in range(len(y)):
            if i != j:
                solver.add(Or(
                    [x[i]+widths[i] <= x[j],
                     x[j] + widths[j] <= x[i],
                     y[i] >= y[j]+heights[j],
                     y[j] >= y[i]+heights[i]]
                ))
        solver.add(x[i] + widths[i] <= width_limit)
        solver.add(x[i] >= 0)
