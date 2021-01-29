import os
import glob
import copy
from collections import defaultdict
import random

import networkx as nx
import matplotlib.pyplot as plt

DATA_DIR = os.path.join("real_example", "function_tree_data")
fn = "save_object_data3"


def add_all_ancestors(G, child, processed=[]):
    G = add_parents_to_graph(G, child)
    processed.append(child)
    cur_nodes = copy.deepcopy(G.nodes)
    for node in cur_nodes:
        if node not in processed:
            G = add_all_ancestors(G, node, processed)
    return G


def add_parents_to_graph(G, child):
    parents = get_parents(child)
    for node in parents:
        G.add_node(node)
        G.add_edges_from([(node, child)])
    G.remove_edges_from(nx.selfloop_edges(G))
    return G


def get_parents(child):
    with open(os.path.join(DATA_DIR, child + ".txt")) as f:
        parents = [
            os.path.basename(fname).strip()[:-2]
            for fname in f.readlines()
            if fname != child
        ]
    return parents


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


def plot(G, pos=None):
    if pos is None:
        pos = nx.spring_layout(G)
    plt.figure(figsize=(30, 15))  # todo make figsize a function of graph size
    nx.draw_networkx_nodes(G, pos, node_size=200)
    nx.draw_networkx_edges(G, pos, connectionstyle="arc3,rad=0.2")
    labels, label_pos = get_figure_label_positions(G, pos)
    nx.draw_networkx_labels(
        G, label_pos, labels, font_color="r", font_weight="bold", font_size=10
    )
    plt.draw()
    plt.ylim([-1, plt.ylim()[1]])
    plt.show()


def get_figure_label_positions(G, pos, max_label_length=50):
    labels = {}
    for node in G.nodes():
        label = (
            node if len(node) < max_label_length else node[0:max_label_length] + "..."
        )
        labels[node] = label
    size_layer_0 = sum(1 for (x, y) in pos.values() if y == 0)
    num_layers = max(y for (x, y) in pos.values())
    label_pos = {}
    for k, (x, y) in pos.items():
        label_pos[k] = (
            (x, y + 0.5 * x / size_layer_0)
            if y == num_layers
            else (x, y - 0.5 * x / size_layer_0)
        )
    return labels, label_pos


def main(leaf_node):

    G = nx.DiGraph()
    G.add_node(leaf_node)
    G = add_all_ancestors(G, leaf_node)
    pos = calc_node_positions(G)
    plot(G, pos)


if __name__ == "__main__":
    main(fn)
