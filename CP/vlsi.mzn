include "globals.mzn";

int: n;   % Number of tasks
set of int: CIRCUITS = 1..n;
array[CIRCUITS] of int: duration; % Task durations

int: w; % Resource capacities
array[CIRCUITS] of int: req; %Resource requirements of tasks

int: no_of_discarded_solutions;
set of int: set_of_discarded_solutions = 1..no_of_discarded_solutions;
array [set_of_discarded_solutions,CIRCUITS] of int: discarded_solutions;

int: t = sum(duration) - min(duration);
array[CIRCUITS] of var 0..t: start; %Variables for task start times


int: total_area = sum(c in CIRCUITS)(req[c] * duration[c]);
int: lower_bound = (total_area div w) +
    if (total_area mod w == 0) then 0 else 1 endif; % I'm not so sure about this


%resource constraints
constraint cumulative(start, duration, req, w);

%impose difference from discarded solutions
constraint forall(d in set_of_discarded_solutions)(start != discarded_solutions[d,..]);



%makespan as objective function
var lower_bound..sum(duration): makespan = max(c in CIRCUITS)(start[c] + duration[c]);







solve minimize makespan;

output [
    "Start times = ", show(start), "\n",
    "Durations = ", show(duration), "\n",
    "Reqs = ", show(req), "\n",
    "makespan = ", show(makespan), "\n",
];