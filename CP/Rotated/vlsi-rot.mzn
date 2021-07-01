include "globals.mzn";

int: n;
set of int: Chips = 1..n;
set of int: Rotations = 1..2; % Two possible rotations for a chip
set of int: Dimensions = 1..2; % Working with 2D chips

int: available_width;
%array[Chips] of int: heights;

%int: t = sum(duration) - min(duration);

%int: total_area = sum(c in Chips)(req[c]*duration[c]);
%int: lower_bound = (total_area div w) +
%    if (total_area mod w == 0) then 0 else 1 endif; % I'm not so sure about this

% We need two arrays for both the widths and heights: 
% one will contain the optional values (which will be a (Chips,2) matrix),
% the other one the "decided"

array[Chips,Rotations, Dimensions] of int: sizes;

array[Chips,Dimensions] of int: decided_sizes;

int: upper_bound = sum(sizes[..,1,..]);
array[Chips] of var 0..upper_bound: x;
array[Chips, Rotations] of var opt 0..upper_bound: x_rotations;

constraint forall(c in Chips) (alternative(x, decided_sizes[c,..], 
                                [x_rotations[c, r] | r in Rotations], 
                                sizes[c, .. ,..]));

constraint cumulative(x, decided_sizes[..,1], decided_sizes[..,2], available_width);