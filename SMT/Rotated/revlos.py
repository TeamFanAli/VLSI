from numpy.core.defchararray import lower, upper
from cumulative import cumulative, x_finder
from z3 import *
from utility import *
from halo import Halo
from time import time


def declare_ends(solver, rotations, starts, ends, durations, req):
    for i in range(len(durations)):
        solver.add(ends[i] == starts[i]+If(rotations[i], req[i], durations[i]))


def declare_max(solver, array, max):
    # We specify that max has to be greater\equal then all the elements
    for i in range(len(array)):
        solver.add(max >= array[i])
    # and that it has to be equal to at least one element
    solver.add(Or([max == array[i] for i in range(len(array))]))


def declare_makespan_bounds(solver, width, makespan, req, durations):
    total_area = np.sum([req[i]*durations[i]
                         for i in range(len(req))])
    lower_bound = int(total_area / width) + \
        (0 if (total_area % width == 0) else 1)
    # We can use the minimum among the sums of durations and reqs: in the worst case we can rotate them all
    upper_bound = np.sum([max([durations[i], req[i]])
                          for i in range(len(durations))])
    solver.add(makespan <= int(upper_bound))
    solver.add(makespan >= lower_bound)


if __name__ == "__main__":
    input = parse_args()
    width, n, durations, req = preprocess(input)
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
    spinner.stop()
    print(f"Solved the cumulative optimization in %s seconds" %
          round((time()-starting_time), 4))
    assert is_sat
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
    spinner.stop()
    print("🎉 Everything done in a total of %s seconds!" %
          round((time()-starting_time), 4))
    result = postprocess(
        width, height, n, req, durations, x, y)
    print_rectangles_from_string(result)
