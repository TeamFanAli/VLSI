include "globals.mzn";

int: n;   % Number of tasks
set of int: CIRCUITS = 1..n;
array[CIRCUITS] of int: duration; % Task durations

int: w; % Resource capacities
int: no_of_discarded_solutions;
set of int: set_of_discarded_solutions = 1..no_of_discarded_solutions;
array [set_of_discarded_solutions,CIRCUITS] of int: discarded_solutions;

array[CIRCUITS] of int: req; %Resource requirements of tasks


int: t = sum(c in CIRCUITS)(max(duration[c], req[c])) - min(c in CIRCUITS)(min(duration[c], req[c]));
array[CIRCUITS] of var 0..t: start; %Variables for task start times
array[CIRCUITS] of var bool: rotation;

int: total_area = sum(c in CIRCUITS)(req[c] * duration[c]);
int: lower_bound = (total_area div w) +
    if (total_area mod w == 0) then 0 else 1 endif; % I'm not so sure about this


%resource constraints
constraint cumulative(
    start,
    [if (rotation[c]) then req[c] else duration[c] endif | c in CIRCUITS],
    [if (rotation[c]) then duration[c] else req[c] endif | c in CIRCUITS],
    w);

%impose difference from discarded solutions
constraint forall(d in set_of_discarded_solutions)(start != discarded_solutions[d,..]);

%makespan as objective function
var lower_bound..sum(c in CIRCUITS)(max(duration[c], req[c])): makespan = max(c in CIRCUITS)(
    start[c] +
    if (rotation[c]) then
        req[c]
    else
        duration[c]
    endif);

solve minimize makespan;

output [
    "Start times = ", show(start), "\n",
    "Durations = ", show([
        if (rotation[i]) then
            req[i]
        else
            duration[i]
        endif | i in CIRCUITS]), "\n",
    "Reqs = ", show([
        if (rotation[i]) then
            duration[i]
        else
            req[i]
        endif | i in CIRCUITS]), "\n",
    "makespan = ", show(makespan), "\n",
    "rotation = ", show(rotation), "\n"
];