include "globals.mzn";

int: n;   % Number of tasks
set of int: CHIPS = 1..n;  
array[CHIPS] of int: duration; % Task durations

int: w; % Resource capacities
array[CHIPS] of int: req; %Resource requirements of tasks


int: t = sum(duration) - min(duration);
array[CHIPS] of var 0..t: start; %Variables for task start times


int: total_area = sum(c in CHIPS)(req[c] * duration[c]);
int: lower_bound = (total_area div w) +
    if (total_area mod w == 0) then 0 else 1 endif; % I'm not so sure about this


%resource constraints
constraint cumulative(start, duration, req, w);






%makespan as objective function
var lower_bound..sum(duration): makespan = max(c in CHIPS)(start[c] + duration[c]);







solve minimize makespan;

output [
    "Start times = ", show(start), "\n",
    "Durations = ", show(duration), "\n",
    "Reqs = ", show(req), "\n",
    "makespan = ", show(makespan), "\n",
];