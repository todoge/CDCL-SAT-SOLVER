# SAT Solver Program
This project contains a CDCL solver, an encoding of the Einstein problem as well as a study of the bahaviour of Random K-CNF formulas for k = 3 to k = 5.

The report, instructions to run the programs and the respective scripts can be found in the `sat solver` folder and the `k-cnf` folders respectively.

Run `python3 cdcl.py test.cnf --heuristic=[heuristic id]` to run the CDCL SAT solver in Dimacs form.
Run with `-h` or `--help` option to view options.
The id of the heuristics are listed below:
1. 2-Clause Heuristic
2. Variable State Independent Decaying Sum (VSIDS)
3. Unassigned Maximal Occurrence
4. Random Pick Heuristic
5. Jeroslow-Wang Heuristic
