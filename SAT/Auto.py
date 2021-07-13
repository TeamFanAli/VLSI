import os
import re
import signal
from subprocess import Popen, PIPE, TimeoutExpired
from time import monotonic as timer


def run_with_timeout(cmd, timeout):
    start = timer()
    with Popen(cmd, shell=True, stdout=PIPE, preexec_fn=os.setsid) as process:
        try:
            output = process.communicate(timeout=timeout)[0]
        except TimeoutExpired:
            # send signal to the process group
            os.killpg(process.pid, signal.SIGQUIT)
            output = process.communicate()[0]
    return output


if __name__ == '__main__':
    n = 1
    averages = {}
    for i in range(1, 41):
        sum = 0
        try:
            for j in range(n):
                output = run_with_timeout(
                    f"python SAT.py ../instances/ins-{i}.txt -v 0 -to", 5)
                seconds = re.search("time: (\d*\.\d*)", str(output),
                                    re.IGNORECASE).group(1)
                sum += float(seconds)
            averages[i] = sum/n
            print(f'instance {i}:{averages[i]}')
        except:
            print(f"Instance {i} failed")
            pass
    print(averages)
