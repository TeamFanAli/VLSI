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


class CPRunner():
    def __init__(self):
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
        w, n, dx, dy = preprocess(self.input_lines)
        spinner = Halo(
            text='Instantiating the MiniZinc solver', spinner='monkey')
        spinner.start()
        # Load n-Queens model from file
        vlsi = Model("./vlsi.mzn")
        # Find the MiniZinc solver configuration for Gecode
        gecode = Solver.lookup("gecode")
        # Create an Instance of the n-Queens model for Gecode
        instance = Instance(gecode, vlsi)
        instance["w"] = w
        instance["n"] = n
        instance["dx"] = dx
        instance["dy"] = dy
        spinner.stop()
        spinner = Halo(
            text=f'Solving the first MiniZinc instance, timeout={Y_TIMEOUT_MINS} minutes', spinner='monkey')
        spinner.start()
        first_instance_start = time()
        result = instance.solve(timeout=timedelta(minutes=Y_TIMEOUT_MINS))
        # Output the array q
        print("\n\nInstance solved in %s seconds" %
              round((time()-first_instance_start), 4))
        spinner.stop()
        print(str(result))


if __name__ == "__main__":
    CPRunner()
