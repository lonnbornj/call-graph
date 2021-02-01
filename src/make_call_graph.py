import networkx as nx
import copy
from collections import defaultdict
import sys

import get_edges
import plotting


def add_all_nodes(G, child, graph_type, root_dir, processed=[]):
    G = add_relatives_to_graph(G, child, graph_type, root_dir)
    processed.append(child)
    cur_nodes = copy.deepcopy(G.nodes)
    for node in cur_nodes:
        if node not in processed:
            G = add_all_nodes(G, node, graph_type, root_dir, processed)
    return G


def add_relatives_to_graph(G, child, graph_type, root_dir):
    relatives = get_edges.read_edges_file(root_dir, child, graph_type)
    for relative in relatives:
        if graph_type == "leaf":
            G.add_edges_from([(relative, child)])
        elif graph_type == "root":
            G.add_edges_from([(child, relative)])
    G.remove_edges_from(nx.selfloop_edges(G))
    return G


def calc_node_positions(G, graph_type):
    layers = calc_graph_hierarchy(copy.deepcopy(G), graph_type)
    num_layers = max([l for l in layers.values()])
    if graph_type == "root":
        layers = {k: abs(v - num_layers) for (k, v) in layers.items()}
    cur_counts = defaultdict(lambda: 0)
    pos = nx.spring_layout(G)
    for node, layer in layers.items():
        cur_counts[layer] += 1
        offset = abs(layer-num_layers) if abs(layer-num_layers) % 2 else 0
        offset = layer if layer % 2 else 0
        pos[node] = (cur_counts[layer] + offset / num_layers, layer)
    return pos


def calc_graph_hierarchy(H, graph_type, layers={}):
    cur_layer = max([l + 1 for l in layers.values()] if layers else [0])
    root_nodes = find_terminating_nodes(H, graph_type)
    for node in root_nodes:
        layers[node] = cur_layer
    H = remove_from_graph(H, root_nodes)
    if H.nodes:
        _ = calc_graph_hierarchy(H, graph_type, layers)
    return layers


def find_terminating_nodes(H, graph_type):
    root_nodes = []
    for node in H.nodes:
        edges = H.in_edges(node) if graph_type == "leaf" else H.out_edges(node)
        if not edges:
            root_nodes.append(node)
    return root_nodes


def remove_from_graph(H, nodes):
    for node in nodes:
        child_nodes = [n[1] for n in H.out_edges(node)]
        H.remove_edges_from([(node, c) for c in child_nodes])
        H.remove_node(node)
    return H


def main():
    root_dir, node, graph_type = sys.argv[1], sys.argv[2], sys.argv[3]
    get_edges.process_dir(root_dir, force=True)
    G = nx.DiGraph()
    G = add_all_nodes(G, node, graph_type, root_dir)
    pos = calc_node_positions(G, graph_type)
    plotting.plot(G, node, pos)


if __name__ == "__main__":
    main()
