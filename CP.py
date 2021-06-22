"""
    Script that runs the preprocessing step, the MiniZinc optimizer, then the output graph
    """
import argparse
from utility import preprocess_for_py, postprocess
from minizinc import Instance, Model, Solver


class CPRunner():
    def __init__(self):
        self.register_args()
        self.read_file()
        self.preprocess_and_run()

    def read_file(self):
        with self.args.file as txt_file:
            self.input_lines = txt_file.readlines()

    def register_args(self):
        parser = argparse.ArgumentParser(
            description='Process filename for the input.')
        parser.add_argument('file', type=argparse.FileType('r'))
        self.args = parser.parse_args()

    def preprocess_and_run(self):
        width, n, durations, req = preprocess_for_py(self.input_lines)
        # Load n-Queens model from file
        vlsi = Model("./vlsi.mzn")
        # Find the MiniZinc solver configuration for Gecode
        gecode = Solver.lookup("gecode")
        # Create an Instance of the n-Queens model for Gecode
        instance = Instance(gecode, vlsi)
        instance["n"] = n
        instance["duration"] = durations
        instance["req"] = req
        instance["w"] = width
        result = instance.solve()
        # Output the array q
        print((postprocess(self.input_lines, str(result))))


if __name__ == "__main__":
    CPRunner()
