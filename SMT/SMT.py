from utility import preprocess, postprocess, print_rectangles_from_string
from no_rotations import solve as non_rotating_solver
from rotations import solve as rotating_solver
import argparse
from time import time


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
                        help="0: execution time, 1: spinners and other fancy things",
                        type=int, default=1, choices=[0, 1])
    return parser.parse_args()


def read_input(file):
    with file as input:
        input_lines = input.read().split('\n')
    return input_lines


if __name__ == "__main__":
    args = register_args()
    width, n, durations, req = preprocess(read_input(args.file))
    if args.verbosity == 0:
        start = time()
    if args.rotation:
        height, req, durations, x, y = rotating_solver(
            width, n, durations, req, args.verbosity)
    else:
        height, req, durations, x, y = non_rotating_solver(
            width, n, durations, req, args.verbosity)
    if args.verbosity == 0:
        print("Total time: %s seconds" % round((time()-start), 4))
    result = postprocess(
        width, height, n, req, durations, x, y)
    if not args.text_only:
        print_rectangles_from_string(result)
    if args.output is not None:
        with args.output as file:
            file.write(result)
