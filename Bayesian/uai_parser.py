import itertools
def parse_uai_file(file_path):
    with open(file_path, 'r') as file:
        # Read the first line to determine the network type
        network_type = file.readline().strip()
        if network_type != 'BAYES':
            raise ValueError('Invalid network type: {}'.format(network_type))

        # Read the number of variables
        num_vars = int(file.readline().strip())

        # Read the number of values for each variable
        var_sizes = [int(x) for x in file.readline().strip().split()]

        # Create a dictionary to store the network information
        network = {'type': 'BAYES',
                   'variables': [],
                   'probabilities': []}

        # Add the variables to the dictionary
        for i in range(num_vars):
            network['variables'].append({'num_states': var_sizes[i]})

        # Read the number of cliques and the cliques themselves
        num_cliques = int(file.readline().strip())
        cliques = []
        for i in range(num_cliques):
            cliques.append([int(x) for x in file.readline().strip().split()][1:])

        # Read the conditional probability table (CPT)
        cpt_size = 1
        for size in var_sizes:
            cpt_size *= size

        cpt = list(map(lambda x: float(x), file.readline().split()))
        print(cpt)
        # Construct the network structure from the cliques
        parents = {}
        for clique in cliques:
            if len(clique) == 1:
                parents[clique[0]] = []
            else:
                for i in range(len(clique) - 1):
                    parents[clique[i]] = [clique[i+1]]

        # Add the CPT to the dictionary
        for i in range(cpt_size):
            assignment = []
            for j in range(num_vars):
                num_states = var_sizes[j]
                index = (i // cpt_size) % num_states
                assignment.append(index)
                cpt_index = i % cpt_size + index * cpt_size
            probability = cpt[cpt_index]
            network['probabilities'].append({'assignment': assignment, 'probability': probability})

        # # Add the parent information to the variables
        # for i in range(num_vars):
        #     network['variables'][i]['parents'] = parents.get(i, [])

        return network


    
def encode_uai_bayesian_network_to_dimacs(bn_dict):
    num_vars = bn_dict["num_vars"]
    card_list = bn_dict["card_list"]
    cliques = bn_dict["cliques"]
    cpt = bn_dict["cpt"]

    # assign a unique index to each variable value
    var_idx = {}
    cur_idx = 1
    for var in range(num_vars):
        for val in range(card_list[var]):
            var_idx[(var, val)] = cur_idx
            cur_idx += 1

    # create a list of clauses for each clique
    clauses = []
    for clique in cliques:
        # create a dictionary to map variable assignments to their indices
        var_map = {}
        for var in clique:
            for val in range(card_list[var]):
                var_map[(var, val)] = var_idx[(var, val)]

        # create a list of variable indices for the current clique
        var_indices = [var_map[(var, val)] for var, val in var_map]

        # create a list of all possible variable assignments for the current clique
        assignments = [(var, val) for var, val in var_map]

        # create a list of clauses for the current clique
        for assignment in assignments:
            cur_var, cur_val = assignment
            cur_idx = var_idx[(cur_var, cur_val)]
            cur_prob = cpt[assignment]

            for other_assignment in assignments:
                if other_assignment == assignment:
                    continue

                other_var, other_val = other_assignment
                other_idx = var_idx[(other_var, other_val)]
                other_prob = cpt[other_assignment]

                # create a clause for each combination of assignments that violates the probability
                if cur_prob > other_prob:
                    clauses.append([-cur_idx, -other_idx])
                elif cur_prob == other_prob and cur_val > other_val:
                    clauses.append([-cur_idx, -other_idx])

    # create the header for the DIMACS file
    header = f"p cnf {cur_idx-1} {len(clauses)}\n"

    # concatenate the header and clause list into a single string
    cnf_string = header + "\n".join([" ".join(map(str, clause)) + " 0" for clause in clauses])

    return cnf_string
