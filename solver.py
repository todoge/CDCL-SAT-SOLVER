from cnf import CNF
import itertools
from bisect import bisect_left
import queue
from typing import List
from collections import deque
from dataclasses import dataclass, FrozenInstanceError


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
                # isSolvable = True
                return True
            else:
                # print(assignment, 'not solvable')
                pass
        return False

class UnitPropNode:
    var : int
    val : int
    level : int

    def __init__(self, var, val, level):
        self.var = var
        self.val = val
        self.level = level

    def __hash__(self):
        return hash((self.var, self.val, self.level))
    
    def __eq__(self, other):
        return (self.var, self.val, self.level) == (other.var, other.val, other.level)
    
class ImplicationGraph:
    def __init__(self):
        self.predecessors = {} # (UnitPropNode) -> list of (UnitPropNode). Only one clause can cause a unit clause
        self.successors = {} # (UnitPropNode) -> list of (clause, (UnitPropNode)). A unit clause can affect multiple clauses. clause assigned to edge 
        self.picked_props = set() # (UnitPropNode)
        self.props_to_node = {} # (var, val) -> UnitPropNode

    #consider cause_clause as a
    def add_node(self, var, val, level, cause_clause, is_pick):
        '''
        var, val, level: the unitPropNode
        cause_clause: the clause that caused the unit clause
        is_pick: whether the unit clause is picked

        '''
        node = UnitPropNode(var, val, level)
        # initialize
        self.predecessors[node] = []
        self.successors[node] = []

        cause_clause_cp = cause_clause.copy()
        cause_clause_cp[node.var] = 0
        causes_props = [(i,e) for i, e in enumerate(cause_clause_cp) if e != 0]
        for (var, val) in causes_props:
            cause_node = self.props_to_node[(var, val)]
            self.predecessors[node].append(cause_node)
            self.successors[cause_node].append((cause_clause, node))
        self.props_to_node[(var, val)] = node
        if is_pick:
            self.picked_props.add(node)

    # need not add conlict node
    def get_last_UIP_cut(self, clause, level): 
        '''
        clause: a clause that led to the conflict
        return the last UIP cut clause to be learned
        '''
        clause_literals_list= [(i, -e) for i, e in enumerate(clause) if e != 0] # (var, val) that led to the conflict
        stack = []
        visited = set()
        new_learned_clause = [0] * (self.var_length + 1)

        # populate stack with first causes
        for (var, val) in clause_literals_list:
            node = self.props_to_node[(var, val)]
            stack.append(node)
          
        while (len(stack) > 1):
            node = stack.pop()
            if node in visited:
                continue
            visited.add(node)
            if node in self.picked_props or node.level != level:
                if (node in self.picked_props):
                    assert node.level == level
                
                cause_var, cause_val = node.var, node.val
                new_learned_clause[cause_var] = -cause_val # learn the opposite of the picked literal

            else:
                for cause_prop in self.predecessors[node]:
                    if cause_prop not in visited:
                        stack.append(cause_prop)

        return new_learned_clause


###### Conflict analysis: 1) closest to choice point, 2) first UIP
### first UIP: first unit clause that is not a descendant of the choice point
### impl
### closest to choice point: the clause that is closest to the choice point

### multiple clauses could cause the same unit clause. So the choice of caused by saving is also affective
### <assignment, level.> + clause no. -> <assignment, level.> 
### <assignment, level.>.is_pick
## removing learnt clauses: 
    
class ComplexSatSolver:
    # all literals start from 1

    def __init__(self, n_var, clauses) -> None:
            self.assignment:List[int] = [0] * (n_var + 1) # idx: var, val: 1 or -1
            self.unit_level = {} # (var, val) -> level
            self.picked_literals = set() # (var, val)
            self.level_to_pick = list() # level_idx -> (var, val) # :List[(int, int)]
            self.level_to_propList= list() # level_idx -> list of (var, val) #List[List[(int,int)]]
            self.clauses = clauses # List[List[int]]
            # list of clauses, each clause is a list of literals in the form of an array with idx: var, val: 1 or -1 or 0
            self.learned_clauses = list() # List[List[int]]
            # list of learned clauses, each clause is a list of literals in the form of an array with idx: var, val: 1 or -1 or 0
            self.impl_graph = {} # (var, val) -> list of ((var, val), level)
            self.level = 0

    def is_unit(self, clause):
        return clause.count_non_zero() == 1
    
    def get_unit(self, clause):
        '''
        return the unit literal and its value
        '''
        for i in range (1, self.n_var + 1):
            if clause[i] != 0:
                return i, clause[i]

    # save nodes as level 0.

    def preprocess(self):
        """
        preprocess the clauses
        removes unit clasues, checks consistency, assigns them.
        unitpropagate and update level 0
        return False if conflict is found, otherwise return True
        """    
        proplist = list() # a list of (var, val) that are assigned at level 0, i.e. given #:List[(int, int)] 
        unit_clauses_idxs:List(int) = list() # a list of indexes of unit clauses in self.clauses
        # for every clause, if unit clause, assign it. if conflict, return False
        for i in range(0, len(self.clauses)):
            clause = self.clauses[i]
            if self.is_unit(clause):
                unit_clauses_idxs.append(i)
                var, value = self.get_unit(clause)
                if self.assignment[var] == 0:
                    self.assignment[var] = value
                    proplist.append((var, value))
                elif self.assignment[var] != value:
                    return False
                
        # remove unit clauses from clauses
        adjust = 0
        for i in unit_clauses_idxs[::-1]:
            self.clauses.pop(i - adjust)
            adjust += 1

        # unit propagate and update level 0
        # TODO
        
        # update level 0
        self.level_to_propList[self.level] = proplist
                 
    def check_literal(self, var, val):
        """
        check if a literal is consistent with assignment.
        return value of the literal if it is not assigned
        return value of the literal if it is assigned to the same value
        return 0 if it is assigned to the opposite value
        """
        if self.assignment[var] == 0:
            return val
        elif self.assignment[var] == val:
            return val
        else:
            return 0

    ### when checking a clause against an assignment. if any of it contains 0, nothing derived.
    ### if all of them are 1, then the clause is satisfied. nothing derived.
    ### if any of them is -1, then that literal is resolved. 0 is derived.

    
    def resolve_clause(self, clause):
        """
        resolve a clause with the current assignment
        return (derived unit clause, True) if a fresh unit clause is derived,
        return (this clause, False) if conflict is found.
        otherwise return (None, True)
    
        """
        mapped = list(map(self.check_literal, clause))  # conlifcting = 0 is resolved. non-zero val is unassigned or consistent.
        derived_is_unit = True if sum( x != 0 for x in mapped) == 1 else False # if only one literal is not resolved, then it is a unit clause
        derived_is_conflict = True if sum (x == 0 for x in mapped) == len(mapped) else False # if all literals are resolved, then it is a conflict
        if derived_is_unit:
            var, val = self.get_unit(mapped)
            if self.assignment[var] == 0:
                return (mapped, True)
            else:
                return (None, True)
        elif derived_is_conflict :
            return (clause, False)
        else :
            return (None, True)

    def unit_propagate(self, picked_literal):
         """
         picked_literal: (var, val) or None
         unit propagation. assigns unit clauses and update implication graph
         returns clause if conflict is found, otherwise returns None
         """
        if picked_literal is not None:
            self.assignment[picked_literal[0]] = picked_literal[1]
            self.level_to_propList[self.level].append(picked_literal)
        
        
        level_proplist:List[(int,int)] = self.level_to_propList[self.level] if self.level < len(self.level_to_propList) else []
         while True:
            fresh_derived = False
            # for each clause, check if something can be derived.
            for clause in [x for x in self.clauses.append(self.learned_clauses)]:
                derived_clause, is_consistent = self.resolve_clause(clause)
                if is_consistent:
                    ## fresh unit clause is derived
                    if derived_clause is not None:
                        unit_var, unit_val = self.get_unit(derived_clause)
                        self.assignment[unit_var] = unit_val ## => same clause will not be derived again
                        # TODO: add to implication graph

                        self.implication_graph[(unit_var, unit_val)] = 
                        fresh_derived = True
                        self.level_to_propList.append((unit_var, unit_val))
                    else :
                        continue
                else: # conflict is found
                    return clause
                
            # no new unit clause is derived
            if not fresh_derived: 
                self.level_to_propList[self.level] = level_proplist
                return None
            else : # new unit clause is derived so run unit propagation again
                continue


                
                

                  
                  
                   
    # def __init__(self, n_var, cnf:CNF) -> None:
    #     self.n_var = n_var
    #     self.cnf = cnf
    #     self.clauses = cnf.clauses
    #     self.assignment = [0] * (n_var + 1)
    #     self.matrix = []
    #     self.row_number_and_assigned_variable_stack = deque()
    #     self.row_number_of_pick_stack = deque()
    #     print(self.clauses)

    # def all_assigned(self):
    #     return 0 not in self.assignment[1:] # no variable is unassigned 

    # ### get the unit variable and its value (1 or -1)
    # def get_unit(self, row_number):
    #     if self.is_unit(row_number):
    #         for i in range (self.n_var + 1):
    #             if self.matrix[row_number][i] != 0:
    #                 return i, self.matrix[row_number][i]
    
    
    # def is_repeat(self, row):
    #     for i in range(len(self.matrix)):
    #         return self.are_identical_clauses(i, row)

    # ### unit propagation with unit clause of row_number over the matrix
    # def unit_prop(self, row_number):
    #     to_propagate_queue = deque()
    #     to_propagate_queue.append(row_number)

    #     while to_propagate_queue:
    #         unit_row_number = to_propagate_queue.popleft()
    #         assert unit_row_number >= row_number
    #         unit_var, unit_value = self.get_unit(unit_row_number)

    #         ## propagate unit variable
    #         for i in range(len(self.matrix)):
    #             num_of_new_clause_literals = 0
    #             # if varible is opposite to the unit variable value, derive new clause
    #             if self.matrix[i][unit_var] != 0 and self.matrix[i][unit_var] != unit_value:
    #             # derive new clause
    #                 clause = [0] * (1 + self.n_var + 1 + 1)
    #                 # derived clause does not contain the unit variable
    #                 clause[unit_var] = 0
    #                 for j in range(self.n_var + 1):
    #                     if self.matrix[i][j] != 0 and j != unit_var:
    #                         clause[j] = self.matrix[i][j]
    #                         num_of_new_clause_literals += 1
    #                 clause[-2] = num_of_new_clause_literals
    #                 clause[-1] = i # row number of the clause that caused this clause to be derived

    #                 if num_of_new_clause_literals == 0:
    #                     return "UNSAT", clause[-1] # return UNSAT status and the prev row number of the clause leading to the conflict

    #                 if not self.is_repeat(clause):
    #                     self.matrix.append(clause)
    #                     if self.is_unit(clause):
    #                         clause_row_number = len(self.matrix) - 1
    #                         clause_unit_var, clause_unit_value = self.get_unit(clause_row_number)
    #                         self.assignment[clause_unit_var] = clause_unit_value
    #                         self.row_number_and_assigned_variable_stack.append((clause_row_number, clause_unit_var))
    #                         to_propagate_queue.append(clause)
    #     return "", -1
    
    # def solve(self):
    #     unit_row_numbers = []
    #     for idx, clause in enumerate(self.clauses):
    #         if clause.isUnit():
    #             print("UNIT", clause)
    #             unit_row_numbers.append(idx)
    #             idx, val = clause.getUnit()
    #             self.assignment[idx+1] = val
        
    #     print(self.assignment)
    #     return 
    #     # for unit_row in unit_row_numbers:
    #     #     status, row_number = self.unit_prop(unit_row)
    #     #     if status == "UNSAT":
    #     #         return "UNSAT"

    #     # while not self.all_assigned():
    #     #     picked_var, picked_value = self.pick_branch()
    #     #     row = [0] * (1 + self.n_var + 1 + 1)
    #     #     row[-1] = -1 # nothing caused this row to be derived. It is a branch pick
    #     #     row[picked_var] = picked_value
    #     #     row[-2] = 1 # unit clause
    #     #     self.matrix.append(row)
    #     #     self.assignment[picked_var] = picked_value
    #     #     picked_var_row_number = len(self.matrix) - 1
    #     #     self.row_number_and_assigned_variable_stack.append((picked_var_row_number, picked_var))
    #     #     self.row_number_of_pick_stack.append(picked_var_row_number)
    #     #     self.unit_prop_analyze_backtrack(picked_var, picked_var_row_number)
    #     # return "SAT"
    
    # # returns the variable and its value (-1 or 1) to be picked
    # def pick_branch(self): # pick by occurence frequency, per length of clause
    #     # remember to check the existing assignment
    #     for i in range (1, len(self.assignment)):
    #         if self.assignment[i] == 0 :
    #             return i, 1


    # def analyze_conflict(self, cause_row_number, picked_var, picked_var_row_number):
    #     row_number = cause_row_number
    #     backward_implications = deque()
    #     backtrack_to = 0

    #     # while cause trace is a branch pick
    #     while (row_number >= self.row_number_of_pick_stack[0]):
    #         picked_cause_row_number = self.find_picked_cause_row_number(row_number)
    #         if not picked_cause_row_number in backward_implications:
    #             backward_implications.append(picked_cause_row_number)
    #             backtrack_to = picked_cause_row_number - 1
    #         row_number = self.matrix[row_number][-1] # trace the cause (row number)

    #     # picked variable is the cause of the conflict
    #     backward_implications.append(picked_var_row_number)

    #     # produce the new clause
    #     new_clause = [0] * (1 + self.n_var + 1 + 1)
    #     new_clause[-1] = -3 # conflict analysis caused this clause to be derived
    #     new_clause_literals = 0
    #     for row_number in backward_implications:
    #         assert self.matrix[row_number][-2] == 1 # unit clause
    #         var, value = self.get_unit(row_number)
    #         new_clause[var] = value
    #         new_clause_literals += 1
    #     new_clause[-2] = new_clause_literals
        
    #     return backtrack_to, new_clause
    
    # def backtrack(self, backtrack_to, new_clause):

    #     remove_n_assignments = 0
    #     remove_from_incl = len(self.row_number_of_pick_stack) - 1
    #     # remove all assigments that are after the backtrack_to
    #     for i in range(len(self.row_number_and_assigned_variable_stack)):
    #         if self.row_number_and_assigned_variable_stack[i][0] > backtrack_to:
    #             remove_from_incl = min(remove_from_incl, i)
    #             self.assignment[self.row_number_and_assigned_variable_stack[i][1]] = 0
    #             remove_n_assignments += 1
    #     assert remove_n_assignments == len(self.row_number_and_assigned_variable_stack) - remove_from_incl

    #     # remove the assignments
    #     for i in range(remove_n_assignments):
    #         self.row_number_and_assigned_variable_stack.pop()


    #     # remove all picks that are after the backtrack_to
    #     remove_n_picks = 0
    #     remove_pick_after_incl = len(self.row_number_of_pick_stack) - 1
    #     for i in range(len(self.row_number_of_pick_stack)):
    #         if self.row_number_of_pick_stack[i] > backtrack_to:
    #             remove_pick_after_incl = min(remove_pick_after_incl, i)
    #             remove_n_picks += 1
    #     assert remove_n_picks == len(self.row_number_of_pick_stack) - remove_pick_after_incl

    #     # remove the picks
    #     for i in range(remove_n_picks):
    #         self.row_number_of_pick_stack.pop()
        
    #     # remove the clauses that are after the backtrack_to
    #     self.matrix = self.matrix[:backtrack_to + 1]

        
    #     # add the new clause
    #     assert self.is_repeat(new_clause) == False
    #     self.matrix.append(new_clause)
    #     if self.is_unit(len(self.matrix) - 1):
    #         clause_unit_var, clause_unit_value = self.get_unit(len(self.matrix) - 1)
    #         self.assignment[clause_unit_var] = clause_unit_value
    #         self.row_number_and_assigned_variable_stack.append((len(self.matrix) - 1, clause_unit_var))
        

                
    # def unit_prop_analyze_backtrack(self, picked_var, picked_var_row_number):
    #     status, cause_row_number = self.unit_prop(picked_var_row_number)
    #     if status == "UNSAT":
    #         backtrack_to, new_clause = self.analyze_conflict(cause_row_number, picked_var, picked_var_row_number)
    #         self.backtrack(backtrack_to, new_clause) # backtracks and addes the new_clause to the matrix
    #         if (self.is_unit(backtrack_to + 1)) :
    #             clause_unit_var, clause_unit_value = self.get_unit(backtrack_to + 1)
    #             self.unit_prop_analyze_backtrack(clause_unit_var, backtrack_to + 1)
            
         


    # # returns the row number of the picked branch that caused the conflict
    # def find_picked_cause_row_number(self, cause_row_number):
    #     for i in range(len(self.row_number_of_pick_stack)):
    #         if self.row_number_of_pick_stack[i] == cause_row_number:
    #             assert False # should not happen
    #             return cause_row_number
    #     picked_cause_row_number = bisect_left(self.row_number_of_pick_stack, cause_row_number) - 1
    #     return self.row_number_of_pick_stack[picked_cause_row_number]
