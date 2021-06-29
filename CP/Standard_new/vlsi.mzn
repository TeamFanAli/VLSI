include "globals.mzn";

int: n;   % Number of chips
set of int: CHIPS = 1..n;

array[CHIPS] of int: dx;
array[CHIPS] of int: dy;

int: w; % Resource capacities

int: max_h = sum(dy);
int: max_y = max_h - min(dy);
int: max_x = w - min(dx);

array[CHIPS] of var 0..max_x: x;
array[CHIPS] of var 0..max_y: y;


int: total_area = sum(c in CHIPS)(dx[c]*dy[c]);
int: min_h = (total_area div w) +
    if (total_area mod w == 0) then 0 else 1 endif; % I'm not so sure about this

var min_h..max_h: h = max(c in CHIPS)(y[c] + dy[c]);

constraint diffn(x, y, dx, dy);

constraint forall(c in CHIPS)(x[c] + dx[c] <= w);

solve minimize h;

output [
    "w = ", show(w), "\n",
    "h = ", show(h), "\n",
    "x = ", show(x), "\n",
    "y = ", show(y), "\n",
    "dx = ", show(dx), "\n",
    "dy = ", show(dy), "\n"
];