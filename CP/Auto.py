import os.popen

if __name__ == '__main__':
    instances = ['../instances/ins-10.txt', '../instances/ins-20.txt', '../instances/ins-30.txt']
    solvers = ["gecode", "chuffed"]
    optimizations = range(6)
    processes = range(1, 11)
    for s in solvers:
        if s == "chuffed":
            for i, o in zip(instances,optimizations):
                os.popen("CP.py {i} -s chuffed -o {o} -to -v 0")
                os.popen("CP.py {i} -s chuffed -o {o} -to -v 0 -r")
        else:
            for i, o, p in zip(instances, optimizations, processes):
                os.popen("CP.py {i} -s {s} -o {o} -p {p} -to -v 0")
                os.popen("CP.py {i} -s {s} -o {o} -p {p} -to -v 0 -r")