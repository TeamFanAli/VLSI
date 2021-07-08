from z3 import *
import numpy as np


def cumulative(solver, starts, durations, requirements, resource_limit):
    # This will become durations or requirements in the rotated case
    upper_bound = np.sum(durations)
    tasks = [i for i in range(len(starts))
             if requirements[i] > 0 and durations[i] > 0]
    solver.add(And([starts[i] >= 0 for i in range(len(starts))]))
    for t in range(0, upper_bound + 1):
        solver.add(Sum([(If(starts[i] <= t, 1, 0) * If(t < starts[i] + durations[i], 1, 0))*requirements[i]
                        for i in tasks]) <= resource_limit)


def x_finder(solver, x, y, heights, widths, width_limit):
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
