include "globals.mzn";

int: n;   % Number of chips
set of int: CHIPS = 1..n;
array[CHIPS] of int: y;
array[CHIPS] of int: widths;
array[CHIPS] of int: heights;

int: w;
int: makespan;


int: max_x = makespan - min(widths);
array[CHIPS] of var 0..max_x: x;

%Rect.Left = x[i]
%Rect.Top = y[i]+heights[i]
%Rect.Right = x[i]+widths[i]
%Rect.Bottom = y[i]

constraint forall(i in CHIPS, j in CHIPS where i != j) ((x[i]+widths[i] <= x[j]) \/
                                            (x[j]+widths[j] <= x[i]) \/
                                            (y[i] >= y[j]+heights[j]) \/
                                            (y[j] >= y[i]+heights[i]));

constraint forall(i in CHIPS) (x[i] + widths[i] <= w);

solve satisfy;

output ["x = ", show(x)];