"""
Implement the find_internal_nodes_num function
    ->An internal node is any node of a tree that has at least one child
"""


def find_internal_nodes_num_using_set(parent_list):
    if not parent_list:
        return 0

    parent_set = set(parent_list)
    internal_nodes = len(parent_set) - 1
    return internal_nodes

def find_internal_nodes_num(parent_list):
    if not parent_list:
        return 0
    
    n = len(parent_list)
    children_count = [0] * n
    
    for parent in parent_list:
        if parent != -1:
            children_count[parent] += 1
    
    internal_nodes = 0
    for count in children_count:
        if count > 0:
            internal_nodes += 1
    
    return internal_nodes

# Test cases
parent_list_1 = [4, 4, 1, 5, -1, 4, 5]
internal_node_count_1 = find_internal_nodes_num(parent_list_1)
internal_node_count_set_1 = find_internal_nodes_num_using_set(parent_list_1)
print("internal_node_count_set_1", internal_node_count_set_1)
assert internal_node_count_1 == 3, f"Expected 3 internal nodes, but got {internal_node_count_1}"
assert internal_node_count_set_1 == 3, f"Expected 3 internal nodes, but got {internal_node_count_set_1}"


print("Test cases passed!")
