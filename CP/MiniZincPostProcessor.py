'''
Script that is used to generate solutions from the copy-paste of a MiniZinc solution.
Used when the MiniZinc IDE is required to generate a solution, as copying the data one-by-one was never an option.
'''

import argparse
from utility import preprocess, postprocess, split_output, print_rectangles_from_string


def register_args():
    parser = argparse.ArgumentParser(
        description='Process filename for the input.')
    parser.add_argument('file',
                        help="the file containing the instance",
                        type=argparse.FileType('r'))
    parser.add_argument('--solution',
                        help="the file containing the minizn solution",
                        type=argparse.FileType('r'))
    parser.add_argument("--output",
                        help="the file in which store the output, "
                             "if not specified it will be printed on the console",
                        type=argparse.FileType('w'), default=None)
    parser.add_argument("--print-only", "-p",
                        help="Only prints the data so that you can feed it to MiniZinc",
                        default=False, action='store_true')
    return parser.parse_args()


def read_input(file):
    with file as input:
        input_lines = input.read().split('\n')
    return input_lines


if __name__ == '__main__':
    args = register_args()
    w, n, heights, widths = preprocess(read_input(args.file))
    if args.print_only:
        print("Here's the data for MiniZinc:")
        print(w, n, widths, heights)
    else:
        with args.solution as solution:
            solution_text = solution.read()
        makespan, y, x, durations, reqs, rotations = split_output(
            str(solution_text))
        solution = postprocess(
            w, makespan, n, y, x, reqs, durations)
        print_rectangles_from_string(solution)
        with args.output as file:
            file.write(solution)
