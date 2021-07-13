"""
    Script that runs the preprocessing step, the MiniZinc optimizer, then the output graph
    """
import argparse
from utility import preprocess, postprocess, print_rectangles_from_string, split_output, split_x_finder
from minizinc import Instance, Model, Solver
from datetime import timedelta
from halo import Halo
from time import time

TIMEOUT_MINS = 5


def register_args():
    parser = argparse.ArgumentParser(
        description='Process filename for the input.')
    parser.add_argument('file',
                        help="the file containing the instance",
                        type=argparse.FileType('r'))
    parser.add_argument("-r", "--rotation",
                        help="allows to rotate circuits",
                        action="store_true")
    parser.add_argument("-s", "--solver",
                        help="CP solver of the mzn model, default is chuffed",
                        type=str, default="chuffed", choices=["chuffed", "gecode"])
    parser.add_argument("-o", "--optimization",
                        help="set the MiniZinc compiler optimisation level, "
                             "default is 1: single pass optimization",
                        type=int, default=1, choices=[0, 1, 2, 3, 4, 5])
    parser.add_argument("-p", "--processes",
                        help="set the number of processes the solver can use, "
                             "default is 1",
                        type=int, default=1)
    parser.add_argument("--output",
                        help="the file in which store the output, "
                             "if not specified it will be printed on the console",
                        type=argparse.FileType('w'), default=None)
    parser.add_argument("-to", "--text_only",
                        help="do not show the graphic visualization of the solution",
                        action="store_true"
                        )
    parser.add_argument("-v", "--verbosity",
                        help="0: execution times, 1: solution (default), 2: statistics",
                        type=int, default=1, choices=[0, 1, 2])
    return parser.parse_args()


class CPRunner:
    def __init__(self):
        self.args = register_args()
        self.read_file()
        self.preprocess_and_run()

    def read_file(self):
        with self.args.file as txt_file:
            self.input_lines = txt_file.read().split('\n')

    def preprocess_and_run(self):
        width, n, durations, req = preprocess(self.input_lines)
        spinner = Halo(
            text='Instantiating the MiniZinc solver', spinner='monkey')
        if self.args.verbosity > 0:
            spinner.start()
        vlsi = Model("vlsi-rot.mzn") if self.args.rotation else Model("vlsi.mzn")
        solver = Solver.lookup(self.args.solver)
        instance = Instance(solver, vlsi)
        instance["n"] = n
        instance["duration"] = durations
        instance["req"] = req
        instance["w"] = width
        if self.args.verbosity > 0:
            spinner.stop()
            spinner = Halo(
                text=f'Solving the MiniZinc instance, timeout={TIMEOUT_MINS} minutes', spinner='monkey')
            spinner.start()
        start = time()
        if self.args.solver == "chuffed":
            result = instance.solve(
                timeout=timedelta(minutes=TIMEOUT_MINS),
                optimisation_level=self.args.optimization,
                free_search=True)
        else:
            result = instance.solve(
                timeout=timedelta(minutes=TIMEOUT_MINS),
                optimisation_level=self.args.optimization,
                processes=self.args.processes)
        end = time()
        ex_time = round(end - start, 4)
        if self.args.verbosity > 0:
            print("\n\nInstance solved in %s seconds" % ex_time)
            spinner.stop()

        if result.solution is not None:
            makespan, y, x, durations, reqs, rotations = split_output(str(result))
            solution = postprocess(
                width, makespan, n, y, x, reqs, durations)
            if self.args.verbosity == 0:
                output = "{0} ".format(ex_time)
            elif self.args.verbosity == 1:
                output = solution
            else:
                output = "{0}\n\n{1}".format(solution, str(result.statistics))
            if self.args.output is None:
                print(output)
            else:
                with self.args.output as file:
                    file.write(output)
            if not self.args.text_only:
                print_rectangles_from_string(solution)
        else:
            if self.args.verbosity > 0:
                spinner.stop()
                print("The problem is unsat")
            else:
                print("-1 ")


if __name__ == "__main__":
    CPRunner()
