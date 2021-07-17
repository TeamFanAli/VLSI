'''
Script that is used to generate solutions from the copy-paste of a MiniZinc solution.
Used when the MiniZinc IDE is required to generate a solution, as copying the data one-by-one was never an option.
'''

import argparse
from utility import preprocess, postprocess, split_output


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
    return parser.parse_args()


def read_input(file):
    with file as input:
        input_lines = input.read().split('\n')
    return input_lines


if __name__ == '__main__':
    args = register_args()
    w, n, widths, heights = preprocess(read_input(args.file))
    with args.solution as solution:
        solution_text = solution.read()
    makespan, y, x, durations, reqs, rotations = split_output(
        str(solution_text))
    solution = postprocess(
        w, makespan, n, y, x, reqs, durations)
    with args.output as file:
        file.write(solution)
