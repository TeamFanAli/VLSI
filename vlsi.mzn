include "globals.mzn";

int: n;   % Number of tasks
set of int: CHIPS = 1..n;  
array[CHIPS] of int: duration; % Task durations

int: w; % Resource capacities
array[CHIPS] of int: req; %Resource requirements of tasks


int: t = sum(duration); 
array[CHIPS] of var 0..t-1: start; %Variables for task start times

array[CHIPS] of var 0..w: chip_x;

%resource constraints
constraint cumulative(start, duration, [req[c] | c in CHIPS], w);
%Rect.Left = chip_x[i]
%Rect.Top = start[i]+duration[i]
%Rect.Right = chip_x[i]+req[i]
%Rect.Bottom = start[i]
constraint forall(i in CHIPS, j in CHIPS) ((chip_x[i]+req[i] <= chip_x[j]) \/ 
                                            (chip_x[j] + req[j] <= chip_x[i]) \/ 
                                            (start[i] >= start[j]+duration[j]) \/ 
                                            (start[j] >= start[i]+duration[i]));

%makespan as objective function
var int: makespan = max(c in CHIPS)(start[c] + duration[c]);

solve minimize makespan;

output [
    "Start times = ", show(start), "\n",
    "End times = ", show([start[i]+duration[i] | i in CHIPS]), "\n",
    "Reqs = ", show(req), "\n",
    "makespan = ", show(makespan), "\n",
    "y = " ,show(chip_x)
];