import networkx as nx
import copy
from collections import defaultdict
import sys
import argparse

import get_edges
import plotting


def add_all_nodes(G, cur_node, graph_type, root_dir, processed=[]):
    """Populate the graph, by recursively finding nodes connected by a directed path the the current node"""
    G = add_relatives_to_graph(G, cur_node, graph_type, root_dir)
    processed.append(cur_node)
    cur_nodes = copy.deepcopy(G.nodes)
    for node in cur_nodes:
        if node not in processed:
            G = add_all_nodes(G, node, graph_type, root_dir, processed)
    return G


def add_relatives_to_graph(G, cur_node, graph_type, root_dir):
    """Add immediate ancestors/progeny to the graph; i.e. parents and children of the given node"""
    relatives = get_edges.read_edges_file(root_dir, cur_node, graph_type)
    for relative in relatives:
        if graph_type == "leaf":
            G.add_edges_from([(relative, cur_node)])
        elif graph_type == "root":
            G.add_edges_from([(cur_node, relative)])
    G.remove_edges_from(nx.selfloop_edges(G))
    return G


def calc_node_positions(G, graph_type, max_depth):
    """Calculate the node positions"""
    layers = calc_graph_hierarchy(copy.deepcopy(G), graph_type)
    num_layers = max(1, max([l for l in layers.values()]))
    cur_counts = defaultdict(lambda: 0)
    pos = nx.spring_layout(G)
    for node, layer in layers.items():
        cur_counts[layer] += 1
        offset = layer if layer % 2 else 0
        pos[node] = (cur_counts[layer] + offset / num_layers, layer)
    return pos


def calc_graph_hierarchy(H, graph_type, layers={}):
    """Assign nodes a y-coordinate, according to their distance to the principal"""
    if graph_type == "root":
        # build the hierarchy from the shortest path to the root
        root_node_paths = [
            x for x in nx.all_pairs_shortest_path(H) if not H.in_edges(x[0])
        ]
        layers = {k: len(root_node_paths[0][1][k]) - 1 for k in H.nodes}
    elif graph_type == "leaf":
        # build the hierarchy by recursively removing layers of root nodes until we get to the leaf
        cur_layer = max([l + 1 for l in layers.values()] if layers else [0])
        root_nodes = find_terminating_nodes(H, graph_type)
        for node in root_nodes:
            layers[node] = cur_layer
        H = remove_nodes_from_graph(H, root_nodes)
        if H.nodes:
            _ = calc_graph_hierarchy(H, graph_type, layers)
    return layers


def find_terminating_nodes(H, graph_type):
    """Find either the root of leaf nodes of a graph H"""
    term_nodes = []
    for node in H.nodes:
        edges = H.in_edges(node) if graph_type == "leaf" else H.out_edges(node)
        if not edges:
            term_nodes.append(node)
    return term_nodes


def remove_nodes_from_graph(H, nodes):
    """Remove a list of nodes and any edges in or out from the graph"""
    for node in nodes:
        H.remove_edges_from([(node, c) for c in [n[1] for n in H.out_edges(node)]])
        H.remove_edges_from([(c, node) for c in [n[1] for n in H.in_edges(node)]])
        H.remove_node(node)
    return H


def enforce_max_depth(G, node, graph_type, max_depth):
    """Prune the graph, by removing nodes > max_depth distance from the principal"""
    H = G.reverse(copy=True) if graph_type == "leaf" else G
    cur_node_paths = [x for x in nx.all_pairs_shortest_path(H) if x[0] == node][0][1]
    for node, path in cur_node_paths.items():
        if len(path) > max_depth + 1:
            remove_nodes_from_graph(G, [node])
    return G


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--dir",
        nargs=1,
        type=str,
        help="root directory, containing the functions in a subdirectory called `code`",
    )
    parser.add_argument(
        "-n", "--node", nargs=1, type=str, help="the leaf or root princpal node"
    )
    parser.add_argument(
        "-t",
        "--type",
        nargs=1,
        type=str,
        help="relationship of the node to the graph: `leaf` or `root`",
    )
    parser.add_argument(
        "-m",
        "--max_depth",
        nargs="?",
        default=-1,
        type=int,
        help="maximum number of edges between the principal node and other nodes",
    )
    args = parser.parse_args()
    root_dir, node, graph_type, max_depth = (
        args.dir[0],
        args.node[0],
        args.type[0],
        args.max_depth,
    )
    depth_string = {True: "maximum graph depth", False: "depth {}".format(max_depth)}
    print(
        "Creating graph of function `{}` as {}, to {}".format(
            node, graph_type, depth_string[max_depth == -1]
        )
    )

    # process data about the functional relationships
    get_edges.process_dir(root_dir, force=False)
    # construct the graph
    G = nx.DiGraph()
    G = add_all_nodes(G, node, graph_type, root_dir)

    if max_depth > -1:
        G = enforce_max_depth(G, node, graph_type, args.max_depth)
    # graph only has a well-defined heirarchy if root (leaf) is in fact a root (leaf)
    if graph_type == "root":
        G.remove_edges_from([(c, node) for c in G.nodes])
    else:
        G.remove_edges_from([(node, c) for c in G.nodes])
    # calculate the hierarchy of nodes, and their locations for plotting
    pos = calc_node_positions(G, graph_type, max_depth)
    plotting.plot(G, node, pos)


if __name__ == "__main__":
    main()
