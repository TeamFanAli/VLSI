include "globals.mzn";

int: n;   % Number of tasks
set of int: CIRCUITS = 1..n;
array[CIRCUITS] of int: duration; % Task durations

int: w; % Resource capacities
array[CIRCUITS] of int: req; %Resource requirements of tasks

int: t = sum(duration) - min(duration);
array[CIRCUITS] of var 0..t: start; %Variables for task start times
int: max_x = w - min(req);
array[CIRCUITS] of var 0..max_x: x;


int: total_area = sum(c in CIRCUITS)(req[c] * duration[c]);
int: lower_bound = (total_area div w) +
    if (total_area mod w == 0) then 0 else 1 endif; % I'm not so sure about this


%resource constraints
constraint cumulative(
    start,
    duration,
    req,
    w);

constraint forall(i in CIRCUITS, j in CIRCUITS where i != j) ((x[i]+req[i] <= x[j]) \/
                                            (x[j]+req[j] <= x[i]) \/
                                            (start[i] >= start[j]+duration[j]) \/
                                            (start[j] >= start[i]+duration[i]));

constraint forall(i in CIRCUITS) (x[i] + req[i] <= w);

%makespan as objective function
var lower_bound..sum(duration): makespan = max(c in CIRCUITS)(start[c] + duration[c]);







solve :: seq_search([
    int_search(start, smallest, indomain_min),
    int_search([makespan], input_order, indomain_min),
    int_search(x, input_order, indomain_min)])
    minimize makespan;

output [
    "y = ", show(start), "\n",
    "x = ", show(x), "\n",
    "Durations = ", show(duration), "\n",
    "Reqs = ", show(req), "\n",
    "makespan = ", show(makespan), "\n",
];



