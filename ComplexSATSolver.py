class Clause:
    def __init__(self, clause):
        self.clause = clause

    def isUnit(self):
        count = 0
        for lit in self.clause:
            if lit != 0:
                count += 1
        return count == 1
    
    def getUnit(self):
        for idx, lit in enumerate(self.clause):
            if lit != 0:
                return idx, lit

class Solver:
    # level to picked literal (no parity)
    level_to_pick = []
    # unit clauses (with parity and caused by)
    # (clause, caused_by)
    unit_proplist = []
    # level to unit clauses idx
    level_to_proplist_idx = []
    # non unit clauses (with parity)
    non_unit_clauses = []
    # level to non unit clauses idx
    level_to_non_unit_clauses_idx = []

    # history of picked unit clauses (literals with parity)
    pick_history = []
    # assignment of literals
    assignment = []

    unsat = False


    def __init__(self, var_len, clauses):
        self.var_len = var_len
        for clause in clauses:
            tmp_clause = [0] * (var_len + 1)
            count = 0
            for literal in clause:
                idx = abs(literal) - 1
                prop = 1 if literal > 0 else -1
                if tmp_clause[idx] != 0 and tmp_clause[idx] != prop:
                    # conflict
                    self.unsat = True
                elif tmp_clause[idx] == 0:
                    tmp_clause[idx] = prop
                else:
                    pass
            new_clause = Clause(tmp_clause)
            if new_clause.isUnit():
                # unit clause
                self.unit_proplist.append((new_clause, -1))
                idx, parity = new_clause.getUnit()
                self.assignment[idx] = parity
            else:
                # non unit clause
                self.non_unit_clauses.append(new_clause)
        # init level 0. level to last idx
        self.level_to_proplist_idx.append(len(self.unit_proplist - 1))
        self.level_to_non_unit_clauses_idx.append(len(self.non_unit_clauses - 1))
    
    def complete_assignment(self):
        for a in self.assignment:
            if a != 0:
                return False
            
    def unit_propagate(self):



    def solve(self):
        if self.unsat:
            return False
        level = 0
        # unit propagate on given clauses
        self.unit_propagate()

        while not self.complete_assignment():
            # while no satisfiable assignment
            # increment level
            # pick a literal
            # add to pick history
            # add to level to pick
            # unit propagate
            # if conflict, conflict analysis then backtrack
            # if no conflict, add to pick history
            # if no conflict, add to assignment





                                          
            
    

            
                




    



# from typing import List
# from collections import deque

# class Clause:
#     caused_by = -1
#     unsat = False
#     def __init__(self, clause, var_len, caused_by=-1):
#         tmp_clause = [0] * (var_len + 1)
#         for literal in clause:
#             idx = abs(literal) - 1
#             prop = 1 if literal > 0 else -1
#             # filled and prop is of different parity ==> conflict
#             if tmp_clause[idx] != 0 and tmp_clause[idx] != prop:
#                 self.unsat = True
#             else:
#                 tmp_clause[idx] = prop
        
#         self.clause = tmp_clause
#         self.caused_by = caused_by
#         self.size = 0
#         for lit in self.clause:
#             if lit != 0:
#                 self.size += 1

#     def isUnit(self):
#         return self.size == 1
    
#     def isUnsat(self):
#         return self.unsat

#     def getUnit(self):
#         for idx, lit in enumerate(self.clause):
#             if lit != 0:
#                 return idx, lit
            
#     def resolve(self, clause_idx, truth_assignments):
#         temp = self.clause.copy()
#         temp_size = self.size
#         for idx, lit in enumerate(truth_assignments):
#             if lit != 0:
#                 if temp[idx] == lit:
#                     temp[idx] = 0
#                     temp_size -= 1
#         if temp_size == 1:
#             new_clause = Clause(temp, len(truth_assignments), clause_idx)
#         elif temp_size == 0:
#             new_clause = Clause(temp, len(truth_assignments), clause_idx)
#             new_clause.unsat = True
#         else:
#             new_clause = Clause(temp, len(truth_assignments), clause_idx)
#         return new_clause
             
            

# class CNF:
#     def __init__(self, var_len, clauses):
#         self.var_len = var_len
#         ## only append non-unit clauses
#         self.non_unit_clauses = List[Clause]
#         ## can appendLeft unit clauses
#         self.unit_clauses = deque()

#         self.assignment = [0] * var_len
#         # caused_by nothing 
#         for clause in clauses:
#             clause = Clause(clause, var_len)
#             ## stop if unsat ##TODO
#             if clause.isUnsat():
#                 return
            
#             if clause.isUnit():
#                 self.unit_clauses.append(clause)
#                 lit, parity = clause.getUnit()
#                 self.assignment[lit] = parity
#             else:
#                 self.non_unit_clauses.append(clause)

#         ## stack of literals that are picked 
#         self.pick = deque()

#     def find_row_of_pick(self, picked_literal):
#         for i in range(len(self.unit_clauses)):
#             if self.unit_clauses[i].getUnit()[0] == picked_literal:
#                 return i

# class ComplexSATSolver:
#     def __init__(self, var_len, clauses):
#         self.cnf = CNF(var_len, clauses)

#     def solve(self):

#     def resolve(self, clause_idx, assignments):
#         clause = self.cnf.non_unit_clauses[clause_idx]
#         new_clause = clause.resolve(clause_idx, assignments)
#         if new_clause.isUnsat():
#             return False
#         if new_clause.isUnit():
#             self.cnf.unit_clauses.append(new_clause)
#             lit, parity = new_clause.getUnit()
#             self.cnf.assignment[lit] = parity
#             self.cnf.pick.append(lit)
#             self.cnf.non_unit_clauses = [c for c in self.cnf.non_unit_clauses if c.clause[lit] != parity]
#         else:
#             self.cnf.non_unit_clauses.append(new_clause)
#         return True
    
#     def unit_propagate(self):
#         for clause in enumerate(self.cnf.non_unit_clauses):
#             self.resolve(clause_idx, self.assignments)
#             while self.cnf.unit_clauses:
#             clause = self.cnf.unit_clauses.popleft()
#             lit, parity = clause.getUnit()
#             self.cnf.assignment[lit] = parity
#             self.cnf.pick.append(lit)
#             self.cnf.non_unit_clauses = [c for c in self.cnf.non_unit_clauses if c.clause[lit] != parity]
#             for clause in self.cnf.non_unit_clauses:
#                 if clause.isUnit():
#                     self.cnf.unit_clauses.append(clause)
#                     lit, parity = clause.getUnit()
#                     self.cnf.assignment[lit] = parity

        

    
        

