import urllib2
import random
from collections import deque
import itertools


def make_complete_graph(num_nodes):
    """
    Receives number of nodes and returns dictionary representation of complete graph
    """

    graph_representation = {}
    if num_nodes > 0:
        for node in range(0, num_nodes):
            graph_representation[node] = set(_ for _ in range(0, num_nodes) if _ != node)
    return graph_representation


def compute_in_degrees(digraph):
    """
    Receives a directed graph (represented as a dictionary) and
    returns the in-degrees for the nodes in the graph
    """
    graph_distribution = {}
    for tail, heads in digraph.iteritems():
        graph_distribution[tail] = graph_distribution.get(tail, 0)
        for head in heads:
            graph_distribution[head] = graph_distribution.get(head, 0) + 1
    return graph_distribution


def in_degree_distribution(digraph):
    """
    Receives a directed graph (represented as a dictionary) and
    returns the unnormalized distribution of the in-degrees of the graph.
    """
    degree_distribution = {}
    graph_distribution = compute_in_degrees(digraph)
    for distribution in graph_distribution.values():
        degree_distribution[distribution] = degree_distribution.get(distribution, 0) + 1
    return degree_distribution


def normalize_distribution(distribution):
    """
    returns normalized distribution
    """
    normalized_distribution = {}
    total = 0
    for distr_value in distribution.values():
        total += distr_value
    for key, val in distribution.items():
        normalized_distribution[key] = float(val) / total
    return normalized_distribution


def graph_er_creation(num_nodes, p):
    """ creates random directed graph"""
    graph = {}
    for node in range(0, num_nodes):
        graph[node] = set([])
    for edge in itertools.permutations(range(0, num_nodes), 2):
        if float(random.randint(0, 10)) / 10 < p:
            graph[edge[0]].add(edge[1])
    return graph


def copy_graph(graph):
    """
    Make a copy of a graph
    """
    new_graph = {}
    for node in graph:
        new_graph[node] = set(graph[node])
    return new_graph


def delete_node(ugraph, node):
    """
    Delete a node from an undirected graph
    """
    neighbors = ugraph[node]
    ugraph.pop(node)
    for neighbor in neighbors:
        ugraph[neighbor].remove(node)


def targeted_order(ugraph):
    """
    Compute a targeted attack order consisting
    of nodes of maximal degree
    Returns:
    A list of nodes
    """
    new_graph = copy_graph(ugraph)
    order = []
    while len(new_graph) > 0:
        max_degree = -1
        for node in new_graph:
            if len(new_graph[node]) > max_degree:
                max_degree = len(new_graph[node])
                max_degree_node = node
        delete_node(new_graph, max_degree_node)
        order.append(max_degree_node)
    return order


def fast_targeted_order(ugraph):
    """
    Compute a targeted attack order consisting
    of nodes of maximal degree
    Returns:
    A list of nodes
    """
    new_graph = copy_graph(ugraph)
    order_list = []
    degree_dict = {}
    degree_sets = [set() for _ in new_graph.keys()]
    num_nodes = len(new_graph.keys())

    for node, edge in new_graph.items():
        if len(edge) not in degree_dict:
            degree_dict[len(edge)].add(node)
        else:
            degree_dict[len(edge)] = {node}

    for degree in range(0, num_nodes):
        if degree in degree_dict:
            degree_sets[degree] = degree_dict[degree]

    for degree in range(num_nodes-1, -1, -1):
        while degree_sets[degree] != set():
            if degree_sets[degree]:
                node = degree_sets[degree].pop()
            else:
                continue
            for neighbor in new_graph[node]:
                neighbor_deegre = len(new_graph[neighbor])
                degree_sets[neighbor_deegre].remove(neighbor)
                degree_sets[neighbor_deegre-1].add(neighbor)
            order_list.append(node)
            delete_node(new_graph, node)
    return order_list



def bfs_visited(upgraph, start_node):
    """
    Returns the set consisting of all nodes that are visited
    by a breadth-first search that starts at start node
    """
    queue = deque([])
    visited = {start_node}
    queue.appendleft(start_node)
    while queue:
        node = queue.pop()
        for neighbor in upgraph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.appendleft(neighbor)
    return visited


def cc_visited(upgraph):
    """
    Takes the undirected graph and returns a list of sets,
    where each set consists of all the nodes (and nothing else)
    in a connected component, and there is exactly one set in the
    list for each connected component in graph and nothing else
    """
    nodes_ramained = upgraph.keys()
    cc_list = []
    while nodes_ramained:
        node = nodes_ramained.pop()
        cc_set = bfs_visited(upgraph, node)
        if cc_set not in cc_list:
            cc_list.append(cc_set)
    return cc_list


def largest_cc_size(ugraph):
    """
    Takes the undirected graph and returns the size (an integer)
    of the largest connected component in graph.
    """
    cc_visited_set = cc_visited(ugraph)
    max_cc_size = 0
    for cc_set in cc_visited_set:
        if len(cc_set) > max_cc_size:
            max_cc_size = len(cc_set)
    return max_cc_size


def delete_node_and_edges(ugraph, node):
    """
    Takes the undirected graph removes node
    and all correspondent edges. return modified graph
    """
    neighbors = ugraph[node]
    ugraph.pop(node)
    for neighbor in neighbors:
        ugraph[neighbor].remove(node)


def compute_resilience(ugraph, attack_order):
    """
    Takes ugraph measure the "resilience" of the graph at each removal from attack_order list
    by computing the size of its largest remaining connected component.
    """
    list_cc_sizes = [largest_cc_size(ugraph)]
    for node in attack_order:
        print "Attack {0}".format(node)
        delete_node_and_edges(ugraph, node)
        list_cc_sizes.append(largest_cc_size(ugraph))
        print list_cc_sizes
    return list_cc_sizes


def load_graph(graph_url):
    """
    Function that loads a graph given the URL
    for a text representation of the graph

    Returns a dictionary that models a graph
    """
    graph_file = urllib2.urlopen(graph_url)
    graph_text = graph_file.read()
    graph_lines = graph_text.split('\n')
    graph_lines = graph_lines[:-1]

    print "Loaded graph with", len(graph_lines), "nodes"

    answer_graph = {}
    for line in graph_lines:
        neighbors = line.split(' ')
        node = int(neighbors[0])
        answer_graph[node] = set([])
        for neighbor in neighbors[1 : -1]:
            answer_graph[node].add(int(neighbor))

    return answer_graph


def undirected_graph_er_creation(num_nodes, p):
    """ creates random undirected graph"""
    graph = {}
    for node in range(0, num_nodes):
        graph[node] = set([])
    for edge in itertools.permutations(range(0, num_nodes), 2):
        if float(random.randint(0, 1000)) / 1000 < p:
            graph[edge[0]].add(edge[1])
            graph[edge[1]].add(edge[0])
    return graph


def random_order(graph):
    """
    takes a graph and returns a list of the nodes in the graph in some random order
    """
    node_list = graph.keys()
    random.shuffle(node_list)
    return node_list

def main():
    NETWORK_URL = "http://storage.googleapis.com/codeskulptor-alg/alg_rf7.txt"
    g = load_graph(NETWORK_URL)
    print fast_targeted_order(g)

if __name__ == '__main__':
    main()
