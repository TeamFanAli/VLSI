from z3 import *
import numpy as np


def cumulative(solver, starts, durations, requirements, resource_limit):
    """Cumulative constraint decomposition for Z3. 

    Args:
        solver ([type]): [description]
        starts (IntVector): The starts of tasks, basically the Ys of chips
        durations (List): List of heights of circuits
        requirements (List): List of widths of circuits
        resource_limit (Int): width of the chip
    """
    solver.add(And([starts[i] >= 0 for i in range(len(starts))]))
    for task in range(len(starts)):
        sum = []
        for other_task in range(len(starts)):
            if task != other_task:
                sum.append(If(And([starts[other_task] <= starts[task], starts[task] < (
                    starts[other_task] + durations[other_task])]), 1, 0)*requirements[other_task])
        solver.add(resource_limit >= (requirements[task] + Sum(sum)))
    # Then, we can add the helper constraints
    # B_{ij}^1 = starts[j] >= starts[i]
    # B_{ij}^2 = starts[j] < (starts[i]+durations[i])
    for i in range(len(starts)):
        for j in range(i):
            solver.add(
                Or([starts[j] >= starts[i], starts[j] < (starts[i]+durations[i])]))
            solver.add(
                Or([starts[i] >= starts[j], starts[i] < (starts[j]+durations[j])]))
            solver.add(Or([starts[j] >= starts[i], starts[i] >= starts[j]]))
            solver.add(Implies(starts[j] >= starts[i],
                               starts[i] < (starts[j]+durations[j])))
            solver.add(Implies(starts[i] >= starts[j],
                               starts[j] < (starts[i]+durations[i])))


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
