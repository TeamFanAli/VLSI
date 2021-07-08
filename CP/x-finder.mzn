include "globals.mzn";

int: n;   % Number of circuits
set of int: CIRCUITS = 1..n;
array[CIRCUITS] of int: y;
array[CIRCUITS] of int: widths;
array[CIRCUITS] of int: heights;

int: w;
int: makespan;


int: max_x = w - min(widths);
array[CIRCUITS] of var 0..max_x: x;

%Rect.Left = x[i]
%Rect.Top = y[i]+heights[i]
%Rect.Right = x[i]+widths[i]
%Rect.Bottom = y[i]

constraint forall(i in CIRCUITS, j in CIRCUITS where i != j) ((x[i]+widths[i] <= x[j]) \/
                                            (x[j]+widths[j] <= x[i]) \/
                                            (y[i] >= y[j]+heights[j]) \/
                                            (y[j] >= y[i]+heights[i]));

constraint forall(i in CIRCUITS) (x[i] + widths[i] <= w);

solve satisfy;

output ["x = ", show(x)];