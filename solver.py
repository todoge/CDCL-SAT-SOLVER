import random
from cnf import CNF
import itertools
from bisect import bisect_left
from typing import List, Optional
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
        self.predecessors = dict() # (UnitPropNode) -> list of (UnitPropNode). Only one clause can cause a unit clause
        self.successors = dict() # (UnitPropNode) -> list of (clause, (UnitPropNode)). A unit clause can affect multiple clauses. clause assigned to edge 
        self.picked_props = set() # (UnitPropNode)
        self.props_to_node = dict() # (var, val) -> UnitPropNode

    #consider cause_clause as a
    def add_node(self, var, val, level, cause_clause = None, is_pick = False):
        '''
        var, val, level: the unitPropNode
        cause_clause: the clause that caused the unit clause
        '''
        node = UnitPropNode(var, val, level)
        literal : tuple = (var, val)
        if literal not in self.props_to_node.keys():
            # initialize
            self.props_to_node[literal] = node
            self.predecessors[node] = list()
            self.successors[node] = list()

        if not is_pick and cause_clause is not None:
            cause_clause_cp = cause_clause.copy() # tuple of (var, val)s
            if (var, val) in cause_clause_cp:
                cause_clause_cp.remove((var, val))
            causes_props = [(i,e) for (i,e) in cause_clause_cp]
            for cause_lit in causes_props:
                cause_node = self.props_to_node[cause_lit]
                self.predecessors[node].append(cause_node)
                self.successors[cause_node].append((cause_clause, node))
        elif is_pick:
            self.picked_props.add(node)
        else : # is not a pick, and no cause clause. i.e. given by the problem
            pass

    # need not add conlict node
    def get_last_UIP_cut(self, clause, level): 
        '''
        clause: a clause that led to the conflict
        return the last UIP cut clause to be learned
        '''
        clause_literals_list= [(i, -e) for (i, e) in (clause) if e != 0] # (var, val) that led to the conflict
        stack = []
        visited = set()
        new_learned_clause = tuple()

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
                new_learned_clause = new_learned_clause + ((cause_var, -cause_val),) # learn the opposite of the picked literal

            else:
                for cause_prop in self.predecessors[node]:
                    if cause_prop not in visited:
                        stack.append(cause_prop)

        return new_learned_clause
    
    def remove_nodes_by_node(self, node):
        '''
        remove all nodes that follow the node, via transitive closure
        '''
        level = node.level
        # remove nodes from predecessors and successors
        if node in self.picked_props:
            self.picked_props.pop(node, None)

        for pred_node in self.predecessors[node]:
            if pred_node in self.successors:
                self.successors[pred_node].pop(node, None)

        for succ_node in self.successors[node]:
            assert succ_node.level >= level
            self.remove_nodes_by_node(succ_node)

        # remove node from graph
        self.predecessors.pop(node, None)
        self.successors.pop(node, None)
        self.props_to_node.pop((node.var, node.val), None)


    def remove_nodes(self, pick):
        '''
        remove all nodes that have level >= level
        '''
        # remove nodes from predecessors and successors
        pick_unit_prop_node = self.props_to_node[pick]
        self.remove_nodes_by_node(pick_unit_prop_node)

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

    def __init__(self, n_var, clauses):
        self.assignment:List[int] = [0] * (n_var + 1) # idx: var, val: 1 or -1
        self.picked_literals = set() # (var, val)
        self.level_to_pick = list() # level_idx -> (var, val) # :List[(int, int)]
        self.level_to_propList= list() # level_idx -> list of (var, val) #List[List[(int,int)]]
        self.clauses = clauses # each clause: tuple of (var,val) in sorted order. clauses: set(tuple(var:int,val:int))
        self.learned_clauses = set()
        self.level = 0
        self.impl_graph = ImplicationGraph()

    def is_unit(self, clause):
        return len(clause) == 1
    
    def is_empty(self, clause):
        return len(clause) == 0
    
    def get_unit(self, clause):
        '''
        return the unit literal and its value
        '''
        assert self.is_unit(clause)
        idx = len(clause) - 1
        return clause[idx][0], clause[idx][1] 

    def all_assigned(self):
        return 0 not in self.assignment[1:]

    def preprocess(self):
        """
        preprocess the clauses
        removes unit clasues, checks consistency, assigns them.
        update level_to_pick, level_to_propList, assignment, clauses
        return False if conflict is found, otherwise return True
        """    
        proplist = list() # a list of (var, val) that are assigned at level 0, i.e. given #:List[(int, int)] 
        # for every clause, if unit clause, assign it. if conflict, return False
        units_to_remove = set()
        for clause in self.clauses:
            if self.is_unit(clause):
                var, value = self.get_unit(clause)
                if self.assignment[var] == 0:
                    self.assignment[var] = value
                    proplist.append((var, value))
                elif self.assignment[var] != value:
                    return False
                
                # remove unit clauses from clauses
                units_to_remove.add(clause)
        
        # remove unit clauses from clauses
        for clause in units_to_remove:
            self.clauses.remove(clause)

        # update and unit propagate
        self.level_to_pick.append(None)
        self.level_to_propList.append(proplist)

        for (var, val) in proplist:
            self.impl_graph.add_node(var, val, self.level)
        return True
                 
    def check_literal(self, literal):
        """
        check if a literal is consistent with assignment.
        return value of the literal if it is not assigned
        return value of the literal if it is assigned to the same value
        return 0 if it is assigned to the opposite value
        """
        var, val = literal
        if self.assignment[var] == 0:
            return var, val
        elif self.assignment[var] == val:
            return var, val
        else:
            return var, 0
        
    def remove_zero_val_literal(self, clause):
        for literal in clause:
            var, val = literal
            if val == 0:
                clause.remove(literal)
        return clause
    
    def resolve_clause(self, clause): 
        """
        resolve a clause with the current assignment
        return (derived unit clause, True) if a fresh unit clause is derived,
        return (None, False) if conflict is found.
        otherwise return (None, True)
    
        """
        mapped_clause = self.remove_zero_val_literal(tuple(map(self.check_literal, clause)))  # conlifcting = 0 is resolved. non-zero val is unassigned or consistent.
        derived_is_unit = self.is_unit(mapped_clause)
        derived_is_conflict = self.is_empty(mapped_clause) # if all literals are resolved, then it is a conflict
        if derived_is_unit:
            var, val = self.get_unit(mapped_clause)
            if self.assignment[var] == 0:
                return (mapped_clause, True)
            else:
                return (None, True)
        elif derived_is_conflict :
            return (None, False)
        else :
            return (None, True)
        
    def unit_propagate(self):
        """
        assumes level_to_pick, assignment, level, level_to_proplist are already instantiated/updated. and picked_literal added to implication graph

        picked_literal: (var, val) or None
        unit propagation. assigns unit clauses and update implication graph
        returns clause if conflict is found, otherwise returns None
        """
        # List[(int,int)] 
        while True:
            fresh_derived = False
            # for each clause, check if something can be derived.
            for clause in [x for x in self.clauses.union(self.learned_clauses)]:
                # (fresh derived unit clause, True) or (None, True) or (clause, False)
                derived_clause, is_consistent = self.resolve_clause(clause)
                if is_consistent:
                    ## fresh unit clause is derived
                    if derived_clause is not None:
                        fresh_derived = True
                        unit_var, unit_val = self.get_unit(derived_clause)
                        # assign the unit clause
                        self.assignment[unit_var] = unit_val ## => same clause will not be derived again
                        # update level_to_propList
                        self.level_to_propList[self.level].append((unit_var, unit_val))
                        # add to implication graph
                        self.impl_graph.add_node(unit_var, unit_val, self.level, clause)
                    else :
                        # no fresh unit clause is derived
                        continue
                else: # conflict is found
                    return clause
                
            # no new unit clause is derived
            if not fresh_derived: 
                return None
            else : # new unit clause is derived so run unit propagation again
                continue

    def solve(self):
        """
        preprocess the clauses
        if no conflict is found, run DPLL
        """
        # preprocess
        if not self.preprocess():
            return False
        while True:
            # unit propagate
            conflict_clause = self.unit_propagate()
            
            if conflict_clause is not None:
                if self.level == 0:
                    return False
                
                # conflict is found
                learned_clause = self.impl_graph.get_last_UIP_cut(conflict_clause, self.level)
                self.learned_clauses.add(learned_clause)

                # backtrack to the level before the learned clause is derived
                self.backtrack(self.level)

                # backtrack by one
                self.level -= 1

            else:
                # no conflict is found
                # check if all variables are assigned
                if self.all_assigned():
                    return True
                else:
                    #increase level
                    self.level += 1
                    # pick a variable
                    picked_literal = self.pick_branch_rand()
                    # add to level_to_pick
                    self.level_to_pick.append(picked_literal)
                    # add to assignment
                    self.assignment[picked_literal[0]] = picked_literal[1]
                    # add to level_to_propList
                    self.level_to_propList.append(list())
                    assert len(self.level_to_propList) == (self.level + 1)
                    self.level_to_propList[self.level].append(picked_literal)
                    # add to implication graph
                    self.impl_graph.add_node(picked_literal[0], picked_literal[1], self.level, None)
                    # run unit propagation
                    continue

    def backtrack(self, level):
        """
        backtrack to before the given level. i.e. remove up to given level incl.
        """
        # remove all levels equal to or greater than the given level
        for i in reversed(range(level, self.level+1)):
            pick = self.level_to_pick.pop()
            assert i == len(self.level_to_propList) + 1
            propList = self.level_to_propList[i]
            for var, val in propList:
                self.assignment[var] = 0
            self.level_to_propList.pop()
            self.implication_graph.remove_nodes(pick)

        assert len(self.level_to_pick) == level
        assert len(self.level_to_propList) == level

    def pick_branch_rand(self):
        """
        pick a variable to branch on
        """
        # pick a variable
        var = random.choice([x for x in range(1, len(self.assignment)) if self.assignment[x] == 0])
        val = random.sample([1, -1], 1)
        return (var, val)
    
    # def pick_branch_3SAT(self):
    #     """
    #     pick a variable to branch on
    #     """
    #     freq_pos = [0] * (self.n_var + 1) # frequency of each variable with 1. index 0 is not used.
    #     freq_neg = [0] * (self.n_var + 1) # frequency of each variable with -1. index 0 is not used. 
    #     for clause in [x for x in self.clauses.append(self.learned_clauses)]:
    #         if sum( x != 0 for x in clause) < 3:
    #             for i, e in enumerate(clause):
    #                 if e != 0:
    #                     if e == 1:
    #                         freq_pos[i+1] += 1
    #                     else:
    #                         freq_neg[i+1] += 1
        
    #     freq = [x + y for x, y in zip(freq_pos, freq_neg)]
    #     freq_copy = freq.copy()
    #     sorted(freq_copy, key = lambda x: x[0]+x[1])


    #     # pick a variable
        
    #     var = random.choice([x for x in range(1, self.n_var+1) if self.assignment[x] == 0])
    #     val = random.sample([1, -1], 1)
    #     return (var, val)
    

        



                
                

                  
                  
                   
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
