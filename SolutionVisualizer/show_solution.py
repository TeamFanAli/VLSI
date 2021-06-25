"""
    show_solution.py

    Script that prints VLSI solutions using Matplotlib

    authors: @TeamFanAli
    """

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import random
import argparse

def random_color():
    """Generates a random RGBA color

    Returns:
        tuple: Tuple of RGB channels in [0,1]
    """
    return (random.random(), random.random(), random.random())


def random_hatch():
    return random.choice(['-', '+', 'x', '\\', '*', 'o', 'O', '.'])

def print_rectangles():
    """Prints the rectangles found in the solution
    """
    parser = argparse.ArgumentParser(
        description='Process filename for the solution.')
    parser.add_argument('file', type=argparse.FileType('r'))
    args = parser.parse_args()
    rectangles = []
    with args.file as input_solution:
        width, height = [int(s) for s in input_solution.readline().split()]
        n = int(input_solution.readline())
        for i in range(n):
            rectangles.append([int(s)
                               for s in input_solution.readline().split()])

    # define Matplotlib figure and axis
    fig = plt.figure()
    ax = fig.gca()
    ax.set_xticks(range(width))
    ax.set_yticks(range(height))
    plt.xlim(0, width)
    plt.ylim(0, height)
    for rectangle in rectangles:
        ax.add_patch(Rectangle((rectangle[2], rectangle[3]), rectangle[0], rectangle[1], fill=True,
                               facecolor=random_color(), hatch="*", alpha=0.5, zorder=100, figure=fig))
    plt.grid()
    plt.show()





if __name__ == "__main__":
    print_rectangles()
