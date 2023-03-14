from cnf import CNF
import itertools
from bisect import bisect_left
import queue
from typing import List
from collections import deque
class SATSolver:
    def __init__(self, var_len:int, clause_len:int):
        self.var_length = var_len
        self.clause_len = clause_len

    def simpleSolver(self, cnf:CNF):
        print('Running SIMPLE SAT SOLVER')
        assignments = itertools.product((-1, 1), repeat=self.var_length)
        isSolvable = False
        for assignment in assignments:
            if cnf.isSAT(assignment=assignment):
                print(assignment, 'SOLVABLE!')
                isSolvable = True
                return True
            else:
                # print(assignment, 'not solvable')
                pass
        return isSolvable
    
class ComplexSatSolver:
    def __init__(self, n_var, cnf:CNF) -> None:
        self.n_var = n_var
        self.cnf = cnf
        self.clauses = cnf.clauses
        self.assignment = [0] * (n_var + 1)
        self.matrix = []
        self.row_number_and_assigned_variable_stack = deque()
        self.row_number_of_pick_stack = deque()
        print(self.clauses)

    def all_assigned(self):
        return 0 not in self.assignment[1:] # no variable is unassigned 

    ### get the unit variable and its value (1 or -1)
    def get_unit(self, row_number):
        if self.is_unit(row_number):
            for i in range (self.n_var + 1):
                if self.matrix[row_number][i] != 0:
                    return i, self.matrix[row_number][i]
    
    
    def is_repeat(self, row):
        for i in range(len(self.matrix)):
            return self.are_identical_clauses(i, row)

    ### unit propagation with unit clause of row_number over the matrix
    def unit_prop(self, row_number):
        to_propagate_queue = deque()
        to_propagate_queue.append(row_number)

        while to_propagate_queue:
            unit_row_number = to_propagate_queue.popleft()
            assert unit_row_number >= row_number
            unit_var, unit_value = self.get_unit(unit_row_number)

            ## propagate unit variable
            for i in range(len(self.matrix)):
                num_of_new_clause_literals = 0
                # if varible is opposite to the unit variable value, derive new clause
                if self.matrix[i][unit_var] != 0 and self.matrix[i][unit_var] != unit_value:
                # derive new clause
                    clause = [0] * (1 + self.n_var + 1 + 1)
                    # derived clause does not contain the unit variable
                    clause[unit_var] = 0
                    for j in range(self.n_var + 1):
                        if self.matrix[i][j] != 0 and j != unit_var:
                            clause[j] = self.matrix[i][j]
                            num_of_new_clause_literals += 1
                    clause[-2] = num_of_new_clause_literals
                    clause[-1] = i # row number of the clause that caused this clause to be derived

                    if num_of_new_clause_literals == 0:
                        return "UNSAT", clause[-1] # return UNSAT status and the prev row number of the clause leading to the conflict

                    if not self.is_repeat(clause):
                        self.matrix.append(clause)
                        if self.is_unit(clause):
                            clause_row_number = len(self.matrix) - 1
                            clause_unit_var, clause_unit_value = self.get_unit(clause_row_number)
                            self.assignment[clause_unit_var] = clause_unit_value
                            self.row_number_and_assigned_variable_stack.append((clause_row_number, clause_unit_var))
                            to_propagate_queue.append(clause)
        return "", -1
    
    def solve(self):
        unit_row_numbers = []
        for idx, clause in enumerate(self.clauses):
            if clause.isUnit():
                print("UNIT", clause)
                unit_row_numbers.append(idx)
                idx, val = clause.getUnit()
                self.assignment[idx+1] = val
        
        print(self.assignment)
        return 
        # for unit_row in unit_row_numbers:
        #     status, row_number = self.unit_prop(unit_row)
        #     if status == "UNSAT":
        #         return "UNSAT"

        # while not self.all_assigned():
        #     picked_var, picked_value = self.pick_branch()
        #     row = [0] * (1 + self.n_var + 1 + 1)
        #     row[-1] = -1 # nothing caused this row to be derived. It is a branch pick
        #     row[picked_var] = picked_value
        #     row[-2] = 1 # unit clause
        #     self.matrix.append(row)
        #     self.assignment[picked_var] = picked_value
        #     picked_var_row_number = len(self.matrix) - 1
        #     self.row_number_and_assigned_variable_stack.append((picked_var_row_number, picked_var))
        #     self.row_number_of_pick_stack.append(picked_var_row_number)
        #     self.unit_prop_analyze_backtrack(picked_var, picked_var_row_number)
        # return "SAT"
    
    # returns the variable and its value (-1 or 1) to be picked
    def pick_branch(self): # pick by occurence frequency, per length of clause
        # remember to check the existing assignment
        for i in range (1, len(self.assignment)):
            if self.assignment[i] == 0 :
                return i, 1


    def analyze_conflict(self, cause_row_number, picked_var, picked_var_row_number):
        row_number = cause_row_number
        backward_implications = deque()
        backtrack_to = 0

        # while cause trace is a branch pick
        while (row_number >= self.row_number_of_pick_stack[0]):
            picked_cause_row_number = self.find_picked_cause_row_number(row_number)
            if not picked_cause_row_number in backward_implications:
                backward_implications.append(picked_cause_row_number)
                backtrack_to = picked_cause_row_number - 1
            row_number = self.matrix[row_number][-1] # trace the cause (row number)

        # picked variable is the cause of the conflict
        backward_implications.append(picked_var_row_number)

        # produce the new clause
        new_clause = [0] * (1 + self.n_var + 1 + 1)
        new_clause[-1] = -3 # conflict analysis caused this clause to be derived
        new_clause_literals = 0
        for row_number in backward_implications:
            assert self.matrix[row_number][-2] == 1 # unit clause
            var, value = self.get_unit(row_number)
            new_clause[var] = value
            new_clause_literals += 1
        new_clause[-2] = new_clause_literals
        
        return backtrack_to, new_clause
    
    def backtrack(self, backtrack_to, new_clause):

        remove_n_assignments = 0
        remove_from_incl = len(self.row_number_of_pick_stack) - 1
        # remove all assigments that are after the backtrack_to
        for i in range(len(self.row_number_and_assigned_variable_stack)):
            if self.row_number_and_assigned_variable_stack[i][0] > backtrack_to:
                remove_from_incl = min(remove_from_incl, i)
                self.assignment[self.row_number_and_assigned_variable_stack[i][1]] = 0
                remove_n_assignments += 1
        assert remove_n_assignments == len(self.row_number_and_assigned_variable_stack) - remove_from_incl

        # remove the assignments
        for i in range(remove_n_assignments):
            self.row_number_and_assigned_variable_stack.pop()


        # remove all picks that are after the backtrack_to
        remove_n_picks = 0
        remove_pick_after_incl = len(self.row_number_of_pick_stack) - 1
        for i in range(len(self.row_number_of_pick_stack)):
            if self.row_number_of_pick_stack[i] > backtrack_to:
                remove_pick_after_incl = min(remove_pick_after_incl, i)
                remove_n_picks += 1
        assert remove_n_picks == len(self.row_number_of_pick_stack) - remove_pick_after_incl

        # remove the picks
        for i in range(remove_n_picks):
            self.row_number_of_pick_stack.pop()
        
        # remove the clauses that are after the backtrack_to
        self.matrix = self.matrix[:backtrack_to + 1]

        
        # add the new clause
        assert self.is_repeat(new_clause) == False
        self.matrix.append(new_clause)
        if self.is_unit(len(self.matrix) - 1):
            clause_unit_var, clause_unit_value = self.get_unit(len(self.matrix) - 1)
            self.assignment[clause_unit_var] = clause_unit_value
            self.row_number_and_assigned_variable_stack.append((len(self.matrix) - 1, clause_unit_var))
        

                
    def unit_prop_analyze_backtrack(self, picked_var, picked_var_row_number):
        status, cause_row_number = self.unit_prop(picked_var_row_number)
        if status == "UNSAT":
            backtrack_to, new_clause = self.analyze_conflict(cause_row_number, picked_var, picked_var_row_number)
            self.backtrack(backtrack_to, new_clause) # backtracks and addes the new_clause to the matrix
            if (self.is_unit(backtrack_to + 1)) :
                clause_unit_var, clause_unit_value = self.get_unit(backtrack_to + 1)
                self.unit_prop_analyze_backtrack(clause_unit_var, backtrack_to + 1)
            
         


    # returns the row number of the picked branch that caused the conflict
    def find_picked_cause_row_number(self, cause_row_number):
        for i in range(len(self.row_number_of_pick_stack)):
            if self.row_number_of_pick_stack[i] == cause_row_number:
                assert False # should not happen
                return cause_row_number
        picked_cause_row_number = bisect_left(self.row_number_of_pick_stack, cause_row_number) - 1
        return self.row_number_of_pick_stack[picked_cause_row_number]
