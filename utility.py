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


def postprocess(input, output):
    """
    Transform the output of MiniZinc in a format suitable with project specs
    :param input: The text contained in the original input file
    :param output: the text returned by MiniZinc
    :return: string containing the result formatted as project specs require
    """
    input = input.split('\n')
    output = output.split('\n')
    makespan = int(output[3][len("makespan = "):])
    starts = list(map(int, output[0][len("Start times = ["):-1].split(',')))
    ends = map(int, output[1][len("End times = ["):-1].split(','))
    reqs = map(int, output[2][len("Reqs = ["):-1].split(','))
    h = [0 for _ in range(makespan)]
    y = []
    for s, e, r in zip(starts, ends, reqs):
        y.append(h[s])
        h[s:e] = (x + y for (x, y) in zip(h[s:e], [r for _ in range(s, e)]))
    print(y)
    print(h)
    input[0] += " {0}".format(makespan)
    for j in range(2, len(input)-1):
        input[j] += " {0} {1}".format(y[j-2], starts[j-2])
    return '\n'.join(input)
