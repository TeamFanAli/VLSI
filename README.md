# VLSI

Very Large Scale Integration solutions using CP, SAT and SMT.

## CP

usage:

```
CP.py [-h] [-r] [-s {chuffed,gecode,gist}] [-o {0,1,2,3,4,5}] [-p PROCESSES] [--output OUTPUT] [-to] [-v {0,1,2}] file
```

positional arguments:

| arg  | explanation                      |
| ---- | -------------------------------- |
| file | the file containing the instance |

optional arguments:

| arg                                                      | explanation                                                                            |
| -------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| -h, --help                                               | show help message and exit                                                             |
| -r, --rotation                                           | allows to rotate circuits                                                              |
| -s {chuffed,gecode,gist}, --solver {chuffed,gecode,gist} | CP solver of the mzn model, default is gecode                                          |
| -o {0,1,2,3,4,5}, --optimization {0,1,2,3,4,5}           | set the MiniZinc compiler optimisation level, default is 1: single pass optimization   |
| -p PROCESSES, --processes PROCESSES                      | set the number of processes the solver can use, default is 1                           |
| --output OUTPUT                                          | the file in which store the output, if not specified it will be printed on the console |
| -to, --text_only                                         | do not show the graphic visualization of the solution                                  |
| -v {0,1,2}, --verbosity {0,1,2}                          | 0: execution times, 1: +solution (default), 2: +statistics                             |
