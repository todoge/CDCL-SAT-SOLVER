import argparse
import itertools
import random
from math import ceil
import os
from pycryptosat import Solver
import matplotlib.pyplot as plt
import numpy as np
import time

class FormulaGenerator:

    def __init__(self, k, r, n) -> None:
        self.clause_types = list(itertools.product((-1, 1), repeat=k))
        self.n = n
        self.r = r
        self.k = k
        self.solver = Solver()
    
    # Generate a random clause
    def __getRandomClause(self):
        variables = random.sample(range(1, self.n+1), self.k)
        clause_type = random.choice(self.clause_types)
        clause = [a*b for a,b in zip(variables,clause_type)]
        return clause

    # Generate a random forumla and get the number of satisfying assignments
    def getModelCount(self):
        self.solver = Solver()
        for _ in range(ceil(self.r*self.n)):
            self.solver.add_clause(self.__getRandomClause())
        count = 0
        # while True:
        #     isSAT, SOL = self.solver.solve()
        #     if isSAT:
        #         count += 1
        #         self.solver.add_clause(SOL)
        #     else:
        #         break
        # Iterate over the solutions
        while True:
            # Try to find a solution
            isSAT, SOL = self.solver.solve()
            # If no more solutions exist, exit the loop
            if isSAT != True:
                break
            
            # Increment the number of solutions found
            count += 1
            # print(isSAT, self.solver.is_satisfiable())
            # print(SOL)
            # Add a blocking clause to exclude the current solution
            blocking_clause = [-lit if SOL[lit] else lit
                            for lit in range(1, len(SOL))]
            self.solver.add_clause(blocking_clause)
            # print(blocking_clause)
            # print(self.solver.nb_clauses())
            # break
            # print(self.solver.nb_clauses())
        # print(count)
        return count
    # Get average number of satisfying assignments
    def getSATCount(self, numOfFormulas):
        count = 0
        for _ in range(numOfFormulas):
            count += self.getModelCount()
        return count / numOfFormulas

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--kstart', type=int, help='k is the size of the clause', default=3)
    parser.add_argument('--kend', type=int, help='k is the size of the clause', default=3)
    parser.add_argument('--rstart', type=float, help='r size', default=0)
    parser.add_argument('--rend', type=float, help='r size', default=5)
    parser.add_argument('--n', type=int, help='n size', default=150)
    parser.add_argument('--numOfForms', type=int, help='number of formulas', default=50)
    parser.add_argument('--rinterval', type=float, help='r interval size', default=0.2)
    args = parser.parse_args()
    kstart, kend, rstart, rend, n, numOfForms, rinterval = args.kstart, args.kend, args.rstart, args.rend, args.n, args.numOfForms, args.rinterval
    # We can plot multiple k-graphs at once if needed
    if kstart > kend:
        kend = kstart
    if rstart > rend:
        rend = rstart
    print('Parameters:', 'kstart={}'.format(kstart), 'kend={}'.format(kend),\
           'r={}'.format(rend), 'r-interval={}'.format(rinterval), 'numOfForms={}'.format(numOfForms), 'n={}'.format(n))
    # Set the title of graph
    plt.suptitle("#Models vs r for k={}".format(','.join(str(x) for x in range(kstart, kend+1)), n, n),fontsize=18)
    plt.xlabel("r: Clause Density (#Clauses/#Variables)")
    plt.ylabel("#Models")
    plt.xlim([rstart, rend+rinterval])
    # plt.ylim([0, ])
    legend = []
    # Start Timer
    tic = time.perf_counter()
    # Plot the graph
    for k in range(kstart, kend+1):
        legend.append('k={}'.format(k))
        xpoints = []
        ypoints = []
        for r_val in np.arange(rstart, rend+rinterval, rinterval):
            # Get Probability for r_val, k and n
            generator = FormulaGenerator(k, r_val, n)
            count = generator.getSATCount(numOfForms)
            xpoints.append(r_val)
            ypoints.append(count)
        plt.plot(xpoints, ypoints)
    # Stop timer
    toc = time.perf_counter()
    plt.title('#FORMS={}, r-interval={}, Time-taken={:0.2f}s n={}'.format(numOfForms, rinterval, toc - tic, n),fontsize=10)
    plt.grid()
    plt.legend(legend)
    plt.savefig('{}-{}cnf-n{}-assignments.png'.format(kstart,kend, n))
    