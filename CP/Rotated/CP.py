"""
    Script that runs the preprocessing step, the MiniZinc optimizer, then the output graph
    """
import argparse
from utility import preprocess, postprocess, print_rectangles_from_string, split_output, split_x_finder
from minizinc import Instance, Model, Solver
from datetime import timedelta
from halo import Halo
from time import time

Y_TIMEOUT_MINS = 4
X_TIMEOUT_MINS = 1


class CPRunner:
    def __init__(self, rotation_allowed=False):
        self.rotation_allowed = rotation_allowed
        self.register_args()
        self.read_file()
        self.preprocess_and_run()

    def read_file(self):
        with self.args.file as txt_file:
            self.input_lines = txt_file.read().split('\n')

    def register_args(self):
        parser = argparse.ArgumentParser(
            description='Process filename for the input.')
        parser.add_argument('file', type=argparse.FileType('r'))
        self.args = parser.parse_args()

    def preprocess_and_run(self):
        width, n, durations, req = preprocess(self.input_lines)
        spinner = Halo(
            text='Instantiating the first MiniZinc solver to find Ys', spinner='monkey')
        spinner.start()
        # Load n-Queens model from file
        vlsi = Model("vlsi-rot.mzn") if self.rotation_allowed else Model("vlsi.mzn")
        # Find the MiniZinc solver configuration for Gecode
        gecode = Solver.lookup("gecode")
        # Create an Instance of the n-Queens model for Gecode
        instance = Instance(gecode, vlsi)
        instance["n"] = n
        instance["duration"] = durations
        instance["req"] = req
        instance["w"] = width
        spinner.stop()
        spinner = Halo(
            text=f'Solving the first MiniZinc instance, timeout={Y_TIMEOUT_MINS} minutes', spinner='monkey')
        spinner.start()
        first_instance_start = time()
        result = instance.solve(timeout=timedelta(minutes=Y_TIMEOUT_MINS))
        # Output the array q
        print("\n\nFirst instance solved in %s seconds" %
              round((time()-first_instance_start), 4))
        spinner.stop()
        print(str(result))
        makespan, starts, durations, reqs, rotations = split_output(str(result))
        spinner = Halo(
            text=f'Solving the second MiniZinc instance to find Xs, timeout={X_TIMEOUT_MINS} minutes', spinner='monkey')
        spinner.start()
        x_finder = Model("./x-finder.mzn")
        x_instance = Instance(gecode, x_finder)
        x_instance["n"] = n
        x_instance["y"] = starts
        x_instance["widths"] = reqs
        x_instance["heights"] = durations
        x_instance["w"] = width
        x_instance["makespan"] = makespan
        second_instance_start = time()
        final = x_instance.solve(timeout=timedelta(minutes=1))
        if final.solution is not None:
            x = split_x_finder(str(final))
            spinner.stop()
            print("Second instance (X solver) solved in %s seconds, now generating the graph" %
                  round(time()-second_instance_start, 4))
            solution = postprocess(
                width, makespan, n, starts, x, reqs, durations)
            print_rectangles_from_string(solution)
        else:
            print("Sorry, no solution was found 😟 Try raising the timeouts.")


if __name__ == "__main__":
    rotation = input("Allow rotation? Y/n\n") in ["y", "Y", "yes", "Yes"]
    CPRunner(rotation)
