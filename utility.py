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
    chips = 'chips=[|'
    for i in range(2, len(data)):
        line = data[i].replace('\n', '').split(' ')
        chips += line[1] + ',' + line[0]  # flip
        if not i == len(data) - 1:
            chips += ',\n|'
        else:
            chips += '|];\n'
    return data[0] + data[1] + chips
