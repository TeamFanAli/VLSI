"""
    Script that runs the preprocessing step, the MiniZinc optimizer, then the output graph
    """
import argparse
from utility import preprocess, postprocess, print_rectangles_from_string, split_output, split_x_finder
from minizinc import Instance, Model, Solver
from datetime import timedelta
from halo import Halo
from time import time
import numpy as np

Y_TIMEOUT_MINS = 4
X_TIMEOUT_MINS = 1


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
                        help="CP solver of the mzn model, default is gecode",
                        type=str, default="gecode", choices=["chuffed", "gecode", "gist"])
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

    def preprocess_and_run(self, discarded_solutions=[]):
        width, n, durations, req = preprocess(self.input_lines)
        if discarded_solutions == []:
            discarded_solutions = np.empty((0, n)).tolist()
        spinner = Halo(
            text='Instantiating the first MiniZinc solver to find Ys', spinner='monkey')
        if self.args.verbosity > 0:
            spinner.start()
        vlsi = Model(
            "vlsi-rot.mzn") if self.args.rotation else Model("vlsi.mzn")
        solver = Solver.lookup(self.args.solver)
        instance = Instance(solver, vlsi)
        instance["n"] = n
        instance["duration"] = durations
        instance["req"] = req
        instance["w"] = width
        instance["no_of_discarded_solutions"] = len(discarded_solutions)
        instance["discarded_solutions"] = discarded_solutions
        if self.args.verbosity > 0:
            spinner.stop()
            spinner = Halo(
                text=f'Solving the first MiniZinc instance, timeout={Y_TIMEOUT_MINS} minutes', spinner='monkey')
            spinner.start()
        if self.args.processes > 1:
            result = instance.solve(
                timeout=timedelta(minutes=Y_TIMEOUT_MINS),
                optimisation_level=self.args.optimization,
                processes=self.args.processes)
        else:
            result = instance.solve(
                timeout=timedelta(minutes=Y_TIMEOUT_MINS),
                optimisation_level=self.args.optimization
            )
        makespan, starts, durations, reqs, rotations = split_output(
            str(result))
        ex_time_1 = round(result.statistics['time'].total_seconds(), 4)
        if self.args.verbosity > 0:
            print("\n\nFirst instance solved in %s seconds" % ex_time_1)
            spinner.stop()
            spinner = Halo(
                text=f'Solving the second MiniZinc instance to find Xs, timeout={X_TIMEOUT_MINS} minutes',
                spinner='monkey')
            spinner.start()
        x_finder = Model("x-finder.mzn")
        x_instance = Instance(solver, x_finder)
        x_instance["n"] = n
        x_instance["y"] = starts
        x_instance["widths"] = reqs
        x_instance["heights"] = durations
        x_instance["w"] = width
        x_instance["makespan"] = makespan
        final = x_instance.solve(timeout=timedelta(minutes=1))
        if final.solution is not None:
            x = split_x_finder(str(final))
            ex_time_2 = round(final.statistics['time'].total_seconds(), 4)
            if self.args.verbosity > 0:
                spinner.stop()
                print("Second instance (X solver) solved in %s seconds" %
                      ex_time_2)
            solution = postprocess(
                width, makespan, n, starts, x, reqs, durations)
            if self.args.verbosity == 0:
                output = "{0} {1}".format(ex_time_1, ex_time_2)
            elif self.args.verbosity == 1:
                output = solution
            else:
                output = "{0}\n\n{1}".format(solution, final.statistics)
            if self.args.output is None:
                print(output)
            else:
                with self.args.output as file:
                    file.write(output)
            if not self.args.text_only:
                print_rectangles_from_string(solution)
        else:
            spinner.stop()
            print("Sorry, no solution was found 😟 I'm gonna reset and try again")
            discarded_solutions.append(starts)
            self.preprocess_and_run(discarded_solutions)


if __name__ == "__main__":
    CPRunner()
