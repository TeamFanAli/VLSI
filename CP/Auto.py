import os

if __name__ == '__main__':
    n = 5
    for i in range(31,41):
        values1 = []
        values2 = []
        for j in range(n):
            output = os.popen(
                f"python CP.py ../instances/ins-{i}.txt -v 0 -to -o 1 -s chuffed").read().split(" ")
            v1 = float(output[0])
            v2 = float(output[1])
            values1.append(v1)
            values2.append(v2)
            print(f"{j+1}/{n} ", end='')
            if v1 >= 239:
                print("reached time cape, skipping to next instance ", end='')
                break
        print(f'instance {i}:')
        print("{0} {1}".format(round(sum(values1)/len(values1), 2), round(sum(values2)/len(values2), 2)))