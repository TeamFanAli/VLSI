import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import random


def preprocess(input):
    """Takes an input txt, outputs the data we need
    Args:
        input (string): Input as defined in the project specs
    Returns:
        tuple: all the data we need for the optimization
    """
    width = int(input[0])
    n = int(input[1])
    durations = []
    req = []
    for i in range(2, len(input)):
        if input[i] != "":
            vals = [int(s)
                    for s in input[i].split()]
            durations.append(vals[1])
            req.append(vals[0])
    return width, n, durations, req


def split_output(output):
    """Splits the output from a minizinc solution
    Args:
        output (string): MiniZinc output
    Returns:
        tuple: The minizinc variables
    """
    output = output.split('\n')
    makespan = int(output[3][len("makespan = "):])
    starts = list(map(int, output[0][len("Start times = ["):-1].split(',')))
    ends = map(int, output[1][len("End times = ["):-1].split(','))
    reqs = map(int, output[2][len("Reqs = ["):-1].split(','))
    return makespan, starts, ends, reqs


def postprocess(width, height, n, starts, x, req, durations):
    """Generates a solution string as per the requirements
    Args:
        width (int): width of the chip board
        height (int): height of the chip board
        n (int): number of chips
        starts ([int]): list of chips' Ys
        x ([int]): list of chips' Xs
        req ([int]): list of chips heights
        durations ([int]): list of chips widths
    Returns:
        string: solution text to be output to a file
    """
    solution = ""
    solution += f"{width} {height}\n"
    solution += f"{n}\n"
    for i in range(len(starts)):
        solution += f"{req[i]} {durations[i]} {x[i]} {starts[i]}\n"
    return solution


def split_x_finder(output):
    """Splits the output from the second MiniZinc script
    Args:
        output (string): output of the x-finder.mzn script
    Returns:
        [int]: list of the chips' Xs
    """
    return list(map(int, output[len("x = ["):-1].split(',')))


def split_results_from_string(result):
    """Generates a tuple of results from a solution txt (as seen in the project specs)
    Args:
        result (strin): solution text
    Returns:
        tuple: The results
    """
    rectangles = []
    result = result.split('\n')
    width, height = [int(s) for s in result[0].split()]
    n = int(result[1])
    for i in range(2, len(result)):
        if result[i] != "":
            vals = [int(s)
                    for s in result[i].split()]
            rectangles.append(vals)
    return width, height, n, rectangles


def print_rectangles_from_string(result):
    """Prints the rectangles found in the solution
    """
    print("\nResult:\n{0}".format(result))
    width, height, n, rectangles = split_results_from_string(result)
    fig = plt.figure()
    ax = fig.gca()
    ax.set_xticks(range(width))
    ax.set_yticks(range(height))
    plt.xlim(0, width)
    plt.ylim(0, height)
    for rectangle in rectangles:
        ax.add_patch(Rectangle((rectangle[2], rectangle[3]), rectangle[0], rectangle[1], fill=True,
                               color=random_color(), hatch=random_hatch(), alpha=0.5, zorder=100, figure=fig))
    plt.grid()
    plt.show()


def random_hatch():
    return random.choice(['', '/', '//', 'x', 'xx', '\\', '\\\\', 'O', 'o', '.'])


def random_color():
    """Generates a random RGBA color
    Returns:
        tuple: Tuple of RGB channels in [0,1]
    """
    return (random.random(), random.random(), random.random())
