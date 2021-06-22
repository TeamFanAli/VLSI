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


def preprocess_for_py(file):
    with file as txt_file:
        width = int(txt_file.readline())
        n = int(txt_file.readline())
        durations = []
        req = []
        for i in range(n):
            vals = [int(s)
                    for s in txt_file.readline().split()]
            durations.append(vals[0])
            req.append(vals[1])
    return width, n, durations, req
