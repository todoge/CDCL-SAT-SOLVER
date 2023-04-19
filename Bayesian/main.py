import itertools
from uai_parser import parse_uai_file

def encode_bn_to_cnf(bn):
    """
    Encodes a Bayesian network into CNF in DIMACS form.

    Parameters:
        bn (dict): A dictionary representing the Bayesian network.

    Returns:
        A string representing the CNF in DIMACS form.
    """
    cnf = []
    num_vars = sum(len(node['parents']) for node in bn.values()) + len(bn.keys())
    for node in bn.values():
        for values in itertools.product([0, 1], repeat=len(node['parents'])):
            prob = node['cpd'][values]
            if prob == 0:
                # If the probability is zero, then we add the clause that
                # negates the variables associated with this node and its parents.
                clause = [-var(node['name'], i, num_vars) for i in range(len(values)+1)]
                cnf.append(clause)
            elif prob == 1:
                # If the probability is one, then we add the clause that
                # asserts the variables associated with this node and its parents.
                clause = [var(node['name'], i, num_vars) for i in range(len(values)+1)]
                cnf.append(clause)
            else:
                # If the probability is neither zero nor one, then we add the
                # corresponding clause according to the definition of the CNF.
                clause = [-var(node['name'], len(values), num_vars)]
                for i, value in enumerate(values):
                    if value == 1:
                        clause.append(var(node['parents'][i], 1, num_vars))
                    else:
                        clause.append(-var(node['parents'][i], 1, num_vars))
                clause.append(var(node['name'], i, num_vars))
                cnf.append(clause)
                clause = [-var(node['name'], i, num_vars) for i in range(len(values)+1)]
                for i, value in enumerate(values):
                    if value == 1:
                        clause.append(-var(node['parents'][i], 1, num_vars))
                    else:
                        clause.append(var(node['parents'][i], 1, num_vars))
                cnf.append(clause)
    header = f'p cnf {num_vars} {len(cnf)}\n'
    body = '\n'.join([' '.join([str(x) for x in clause]) + ' 0' for clause in cnf])
    return header + body

def var(name, value, num_vars):
    """
    Returns the integer corresponding to the variable name with a given value.

    Parameters:
        name (str): The name of the variable.
        value (int): The value of the variable.
        num_vars (int): The total number of variables.

    Returns:
        An integer representing the variable name with a given value.
    """
    return (ord(name[0]) - 97) * (num_vars // 26) + value * (num_vars // (len(bn.keys()) + len(bn.values()))) + (int(name[1:]) - 1)

# Example usage
bn = {
    'A': {'name': 'A', 'parents': [], 'cpd': {(): 0.3}},
    'B': {'name': 'B', 'parents': [], 'cpd': {(): 0.7}},
}

from pgmpy.readwrite import UAIReader
if __name__ == "__main__":
    reader = UAIReader('TestUAI.uai')
    reader.get_domain()
    # bn = parse_uai_file('sample.txt')
    # print(bn)