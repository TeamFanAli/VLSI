import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import random


def preprocess(path):
    """
    Transform txt files in a string containing data readable from Minizinc.
    Also flip the chips in order to transform the problem from vertical to horizontal
    :param path: string containing the path of the .txt file (or any text file)
    :return: string containing preprocessed data
    """
    with open(path, "r") as txt_file:
        data = txt_file.readlines()
    data[0] = "w=" + data[0].replace("\n", ";\n")
    data[1] = "n=" + data[1].replace("\n", ";\n")
    duration = 'duration=['
    req = 'req=['
    for i in range(2, len(data)):
        line = data[i].replace('\n', '').split(' ')
        duration += line[1]
        req += line[0]
        if not i == len(data) - 1:
            duration += ','
            req += ','
        else:
            duration += '];\n'
            req += '];\n'
    return data[0] + data[1] + duration + req


def preprocess_for_py(input):
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


def postprocess(input, output):
    """
    Transform the output of MiniZinc in a format suitable with project specs
    :param input: The text contained in the original input file
    :param output: the text returned by MiniZinc
    :return: string containing the result formatted as project specs require
    """
    output = output.split('\n')
    makespan = int(output[3][len("makespan = "):])
    starts = list(map(int, output[0][len("Start times = ["):-1].split(',')))
    ends = map(int, output[1][len("End times = ["):-1].split(','))
    reqs = map(int, output[2][len("Reqs = ["):-1].split(','))
    h = [0 for _ in range(makespan)]
    y = []
    for s, e, r in zip(starts, ends, reqs):
        y.append(h[s])
        h[s] = h[s] + r
        h[s+1:e] = [h[s] for _ in range(s+1, e)]
    print(y)
    print(h)
    input[0] += " {0}".format(makespan)
    for j in range(2, len(input)-1):
        input[j] += " {0} {1}".format(y[j-2], starts[j-2])
    return '\n'.join(input)


def print_rectangles_from_string(result):
    """Prints the rectangles found in the solution
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

    # define Matplotlib figure and axis
    fig = plt.figure()
    ax = fig.gca()
    ax.set_xticks(range(width))
    ax.set_yticks(range(height))
    plt.xlim(0, width)
    plt.ylim(0, height)
    for rectangle in rectangles:
        ax.add_patch(Rectangle((rectangle[2], rectangle[3]), rectangle[0], rectangle[1], fill=True,
                               color=random_color(), alpha=0.5, zorder=100, figure=fig))
    plt.grid()
    plt.show()


def random_color():
    """Generates a random RGBA color

    Returns:
        tuple: Tuple of RGB channels in [0,1]
    """
    return (random.random(), random.random(), random.random())