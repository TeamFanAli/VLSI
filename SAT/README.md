# SAT solving

Let's consider we have $n$ tasks $T_0,...,T_n$, each having a duration $d_i$ and requirement $r_i$.

We'll have to encode what follows: 

- We create a boolean variable for each timestep, for each variable:
  - If task $i$ is **active** at time $t$, $A_{i,t}$ is true
- We have to impose that the constraint of resources is respected:
  - to do so, we'll have to calculate all the permutations of tasks that are $\le$ than the requirement
    - For example, if we had three tasks $R={2,3,4}$ and available resources $=5$, the sets should be $\{2,3\},\{2\},\{4\}, \{3\}$, which we'll encode as $(A_0 \wedge A_1)\vee(A_0)\vee(A_2)\vee(A_1)$ for each timestep: $\bigwedge_{t=0}^{t=max_t} ((A_{0,t} \wedge A_{1,t})\vee(A_{0,t})\vee(A_{2,t})\vee(A_{1,t}))$
- When we find a solution, we can just lower $max_t$ at $max_t-1$ and check if solutions exist.



To find the Ys, then, we'll have a different encoding:

- We create a boolean variable for each x,y,task being $A_{x,y,t}$ meaning that task $t$ is active at the height $y$. 
- We'll have to find all the permutations of tasks for a given x: if we had task 1 and 3 ($req_1=2, req_3=3$) true at X=2 with $max_{req}=3$ we'll have all the possible permutations (being 1 before 3 and 3 before 1) encoded as $(A_{2,0,1}\wedge A_{2,1,1} \wedge A_{2,2,2}\wedge A_{2,3,2}\wedge A_{2,4,2}) \vee (A_{2,0,2}\wedge A_{2,1,2} \wedge A_{2,2,2}\wedge A_{2,3,1}\wedge A_{2,4,1})$
- Then, we have to impose that if $A_{x,y,t}$ is true and $A_{x+1}$ is true in the input data, $A_{x+1,y,t}$ has to be true.