include "globals.mzn";

int: n;   % Number of tasks
set of int: CHIPS = 1..n;  
array[CHIPS] of int: duration; % Task durations

int: w; % Resource capacities
array[CHIPS] of int: req; %Resource requirements of tasks


int: t = sum(duration); 
array[CHIPS] of var 0..t: start; %Variables for task start times


%resource constraints
constraint cumulative(start, duration, [req[c] | c in CHIPS], w);

%makespan as objective function
var int: makespan = max(c in CHIPS)(start[c] + duration[c]);

solve minimize makespan;

output [
    "Start times = ", show(start), "\n",
    "End times   =", show([start[i]+duration[i] | i in CHIPS]), "\n",
    "makespan = ", show(makespan), "\n"
];
