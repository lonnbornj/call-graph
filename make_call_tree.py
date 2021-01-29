import os
import glob
import copy
from collections import defaultdict
import random

import networkx as nx
import matplotlib.pyplot as plt

DATA_DIR = os.path.join("real_example", "function_tree_data")
fn = "save_object_data3"


def get_all_ancestors(child, processed=[]):
    processed.append(child)
    ancestors = get_parents(child)
    for node in ancestors:
        if node not in processed:
            ancestors += get_all_ancestors(node, processed)
    return set(ancestors)


def get_parents(child):
    with open(os.path.join(DATA_DIR, child + ".txt")) as f:
        parents = [
            os.path.basename(fname).strip()[:-2]
            for fname in f.readlines()
            if fname != child
        ]
    return parents


def add_parent_nodes_to_graph(G, child):
    parents = get_parents(child)
    for node in parents:
        G.add_node(node)
        G.add_edges_from([(node, child)])
    G.remove_edges_from(nx.selfloop_edges(G))


def calc_graph_layers(H, layers={}):
    cur_layer = max([l + 1 for l in layers.values()] if layers else [0])
    root_nodes = find_root_nodes(H)
    for node in root_nodes:
        layers[node] = cur_layer
    H = remove_from_graph(H, root_nodes)
    if H.nodes:
        calc_graph_layers(H, layers)
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
    layers = calc_graph_layers(copy.deepcopy(G))
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
    plt.figure(figsize=(30, 15))
    nx.draw_networkx_nodes(G, pos, node_size=200)
    nx.draw_networkx_edges(G, pos, connectionstyle="arc3,rad=0.2")
    labels = {}
    max_label_length = 50
    # todo refactor into: get_figure_label_positions(G)
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

    nx.draw_networkx_labels(
        G, label_pos, labels, font_color="r", font_weight="bold", font_size=10
    )
    plt.draw()
    plt.ylim([-1, plt.ylim()[1]])
    plt.savefig("test.png")


def main(function):

    G = nx.DiGraph()
    G.add_node(function)
    nodes = [function]
    nodes.extend(get_all_ancestors(function))
    for a in nodes:
        # todo: this results in a second (unecessary) call to get_parents
        # for every node. Might as well construct the graph as we get the ancestors
        add_parent_nodes_to_graph(G, a)
    print("calculating layers")
    pos = calc_node_positions(G)
    print("plotting")
    plot(G, pos)


if __name__ == "__main__":
    main(fn)
