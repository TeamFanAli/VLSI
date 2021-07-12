from rotations import solve_instance as rotating_solver
from no_rotations import solve_instance as nonrotating_solver
from utility import parse_args, preprocess, postprocess, print_rectangles_from_string
from time import time
import argparse
import numpy as np


def register_args():
    parser = argparse.ArgumentParser(
        description='Process filename for the input.')
    parser.add_argument('file',
                        help="the file containing the instance",
                        type=argparse.FileType('r'))
    parser.add_argument("-r", "--rotation",
                        help="allows to rotate circuits",
                        action="store_true")
    parser.add_argument("--output",
                        help="the file in which store the output, "
                             "if not specified it will be printed on the console",
                        type=argparse.FileType('w'), default=None)
    parser.add_argument("-to", "--text_only",
                        help="do not show the graphic visualization of the solution",
                        action="store_true"
                        )
    parser.add_argument("-v", "--verbosity",
                        help="0: execution time, 1: times of iterations",
                        type=int, default=1, choices=[0, 1])
    return parser.parse_args()


def read_input(file):
    with file as input:
        input_lines = input.read().split('\n')
    return input_lines


if __name__ == "__main__":
    args = register_args()
    w, n, widths, heights = preprocess(read_input(args.file))
    # Iterate until it's sat
    total_area = np.sum([widths[i] * heights[i] for i in range(len(widths))])
    lower_bound = int(total_area / w) + \
        (0 if (total_area % w == 0) else 1)
    upper_bound = sum(heights)
    height = lower_bound  # We start checking heights at the lower bound
    found_sat = False
    decrementing = False
    last_working_solution = None
    total_start = time()
    while True:
        if args.verbosity > 0:
            print(f"Trying solution with height={height}")
        first_instance_start = time()
        if args.rotation:
            found_sat, solution, widths, heights = rotating_solver(
                w, height, n, widths, heights)
        else:
            found_sat, solution, widths, heights = nonrotating_solver(
                w, height, n, widths, heights)
        if args.verbosity > 0:
            print("which took %s seconds" %
                  round((time()-first_instance_start), 4))
            print(f"and resulted {found_sat}")
        if not found_sat and not decrementing:
            decrementing = False
            print(upper_bound)
            height = int(height*1.5) if int(height *
                                            1.5) < upper_bound else upper_bound
        elif (not found_sat) and decrementing:
            height += 1
            break
        else:
            decrementing = True
            last_working_solution = solution
            height -= 1
    print("Total time: %s seconds" % round((time()-total_start), 4))
    solution_string = postprocess(
        w, height, n, widths, heights, last_working_solution)
    if not args.text_only:
        print_rectangles_from_string(solution_string)
    if args.output is not None:
        with args.output as file:
            file.write(solution_string)
