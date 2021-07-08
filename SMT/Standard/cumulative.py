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
    upper_bound = np.sum(durations)
    tasks = [i for i in range(len(starts))
             if requirements[i] > 0 and durations[i] > 0]
    solver.add(And([starts[i] >= 0 for i in range(len(starts))]))
    for t in range(0, upper_bound + 1):
        solver.add(Sum([(If(starts[i] <= t, 1, 0) * If(t < starts[i] + durations[i], 1, 0))*requirements[i]
                        for i in tasks]) <= resource_limit)


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
