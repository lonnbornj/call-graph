import networkx as nx
import copy
from collections import defaultdict

import get_edges
import plotting

root_dir = "example"
fn = "a"


def add_all_ancestors(G, child, processed=[]):
    G = add_parents_to_graph(G, child)
    processed.append(child)
    cur_nodes = copy.deepcopy(G.nodes)
    for node in cur_nodes:
        if node not in processed:
            G = add_all_ancestors(G, node, processed)
    return G


def add_parents_to_graph(G, child):
    parents = get_edges.read_edges_file(root_dir, child)
    for node in parents:
        G.add_node(node)
        G.add_edges_from([(node, child)])
    G.remove_edges_from(nx.selfloop_edges(G))
    return G


def calc_node_positions(G):
    layers = calc_graph_hierarchy(copy.deepcopy(G))
    num_layers = max([l for l in layers.values()])
    cur_counts = defaultdict(lambda: 0)
    pos = nx.spring_layout(G)
    for node, layer in layers.items():
        cur_counts[layer] += 1
        offset = layer if layer % 2 else 0
        pos[node] = (cur_counts[layer] + offset / num_layers, layer)
    return pos


def calc_graph_hierarchy(H, layers={}):
    cur_layer = max([l + 1 for l in layers.values()] if layers else [0])
    root_nodes = find_root_nodes(H)
    for node in root_nodes:
        layers[node] = cur_layer
    H = remove_from_graph(H, root_nodes)
    if H.nodes:
        calc_graph_hierarchy(H, layers)
    return layers


def find_root_nodes(H):
    root_nodes = []
    for node in H.nodes:
        if not H.in_edges(node):
            root_nodes.append(node)
    return root_nodes


def remove_from_graph(H, nodes):
    for node in nodes:
        child_nodes = [n[1] for n in H.out_edges(node)]
        H.remove_edges_from([(node, c) for c in child_nodes])
        H.remove_node(node)
    return H


def main(leaf_node):

    get_edges.process_dir(root_dir, force=True)
    G = nx.DiGraph()
    G.add_node(leaf_node)
    G = add_all_ancestors(G, leaf_node)
    # assert len(G.nodes) > 1, "{} has no calling functions".format(leaf_node)
    pos = calc_node_positions(G)
    plotting.plot(G, pos)


if __name__ == "__main__":
    main(fn)
