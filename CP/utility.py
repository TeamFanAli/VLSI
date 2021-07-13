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


def postprocess(width, height, n, starts, x, req, durations):
    """Generates a solution string as per the requirements

    Args:

        width (int): width of the chip board
        height (int): height of the chip board
        n (int): number of circuits
        starts ([int]): list of circuits' Ys
        x ([int]): list of circuits' Xs
        req ([int]): list of circuits heights
        durations ([int]): list of circuits widths

    Returns:
        string: solution text to be output to a file
    """
    solution = ""
    solution += f"{width} {height}\n"
    solution += f"{n}\n"
    for i in range(len(starts)):
        solution += f"{req[i]} {durations[i]} {x[i]} {starts[i]}\n"
    return solution


def split_output(output):
    """Splits the output from a minizinc solution

    Args:
        output (string): MiniZinc output

    Returns:
        tuple: The minizinc variables
    """
    output = output.split('\n')
    makespan = int(output[4][len("makespan = "):])
    y = list(map(int, output[0][len("y = ["):-1].split(',')))
    x = list(map(int, output[1][len("x = ["):-1].split(',')))
    durations = list(map(int, output[2][len("Durations = ["):-1].split(',')))
    reqs = list(map(int, output[3][len("Reqs = ["):-1].split(',')))
    if len(output) >= 7:
        rotated = list(map(lambda xx: xx.strip() == "true",
                           output[5][len("rotation = ["):-1].split(',')))
    else:
        rotated = None
    return makespan, y, x, durations, reqs, rotated


def split_x_finder(output):
    """Splits the output from the second MiniZinc script

    Args:
        output (string): output of the x-finder.mzn script

    Returns:
        [int]: list of the circuits' Xs
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


def get_pretty_ticks(width, height):
    """Generates a list of pretty, well-spaced ticks for matplotlib

    Args:
        width (int): width of the motherboard
        height (int): height of the motherboard

    Returns:
        tuple: lists of x and y ticks
    """
    no_ticks = 10
    x_ticks = [int(float(x) / (no_ticks - 1) * width) for x in range(no_ticks)]
    y_ticks = [int(float(x) / (no_ticks - 1) * height) for x in range(no_ticks)]
    return x_ticks, y_ticks


def print_rectangles_from_string(result):
    """Prints the rectangles found in the solution
    """
    width, height, n, rectangles = split_results_from_string(result)
    fig = plt.figure()
    ax = fig.gca()
    # Had to do this append because range doesn't include the last one
    x_ticks, y_ticks = get_pretty_ticks(width, height)
    ax.set_xticks(x_ticks)
    ax.set_yticks(y_ticks)
    plt.xlim(0, width)
    plt.ylim(0, height)
    for rectangle in rectangles:
        ax.add_patch(Rectangle((rectangle[2], rectangle[3]), rectangle[0], rectangle[1], fill=True,
                               color=random_color(), hatch=random_hatch(), alpha=0.5, zorder=100, figure=fig))
    plt.show()


def random_hatch():
    return random.choice(['', '/', '//', 'x', 'xx', '\\', '\\\\', 'O', 'o', '.'])


def random_color():
    """Generates a random RGBA color
    Returns:
        tuple: Tuple of RGB channels in [0,1]
    """
    return random.random(), random.random(), random.random()
