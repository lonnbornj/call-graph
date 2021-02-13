import sys
import os
import glob
import pickle
import networkx as nx
import make_call_graph as mg


def get_graph_size(node):
    return {
        "as root": max(
            1,
            len(mg.add_all_nodes(nx.DiGraph(), node, "root", root_dir, processed=[])),
        ),
        "as leaf": max(
            1,
            len(mg.add_all_nodes(nx.DiGraph(), node, "leaf", root_dir, processed=[])),
        ),
    }


def make_sizes_dict():
    fname = "graph_sizes.pkl"
    if os.path.isfile(fname):
        with open(fname, "rb") as f:
            graph_sizes = pickle.load(f)
    else:
        graph_sizes = {}
        files = glob.glob(os.path.join(root_dir, "code_cleanup", "save", "*.m"))
        for file in files:
            function = os.path.basename(file).split(".")[0]
            graph_sizes[function] = get_graph_size(function)
        with open(fname, "wb") as f:
            pickle.dump(graph_sizes, f)
    graph_sizes, scale_factor = apply_scale_factor(graph_sizes)
    return graph_sizes, scale_factor


def apply_scale_factor(graph_sizes):
    max_calls = max(v["as root"] for v in graph_sizes.values())
    max_called = max(v["as leaf"] for v in graph_sizes.values())
    max_func_name_chars = max(len(k) for k in graph_sizes.keys())
    scale_factor = 1
    while max_calls + max_called + max_func_name_chars > 250:
        max_calls, max_called = max_calls // scale_factor, max_called // scale_factor
        scale_factor += 1
    graph_sizes_scaled = {}
    return {
        k: {
            "as root": v["as root"] // scale_factor,
            "as leaf": v["as leaf"] // scale_factor,
        }
        for k, v in graph_sizes.items()
    }, scale_factor


def save_graph_size_representation(sort_by):
    graph_sizes, scale_factor = make_sizes_dict()
    graph_sizes_sorted = [
        (k, v)
        for k, v in sorted(
            graph_sizes.items(),
            key=lambda item: item[1]["as {}".format(sort_by)],
            reverse=True,
        )
    ]
    max_calls = max(v["as root"] for v in graph_sizes.values())
    max_func_name_chars = max(len(k) for k in graph_sizes.keys())
    write_output(graph_sizes_sorted, max_calls, max_func_name_chars, scale_factor)


def write_output(graph_sizes_sorted, max_calls, max_func_name_chars, scale_factor):
    with open(output_filename, "w") as f:
        f.write("`Size root graph`: size of the graph where `function` is the root\n")
        f.write("`Size leaf graph`: size of the graph where `function` is the leaf\n\n")
        f.write(
            f"Scale factor: {scale_factor} (each dot represents {scale_factor} calls)\n"
        )
        f.write(f"Sorted by size of the {order_by} graph\n\n")
        labels = ["SIZE ROOT GRAPH", "FUNCTION", "SIZE TREE GRAPH"]
        n_spaces1 = max_calls - len(labels[0])
        n_spaces2 = max_func_name_chars - len(labels[1])
        f.write(
            labels[0]
            + "".join(n_spaces1 * [" "])
            + labels[1]
            + "".join(n_spaces2 * [" "])
            + labels[2]
            + "\n\n"
        )
        for c in graph_sizes_sorted:
            calls_string = (
                "".join((max_calls - c[1]["as root"]) * [" "])
                + "".join(c[1]["as root"] * ["."])
                + c[0]
                + "".join((max_func_name_chars - len(c[0])) * [" "])
                + "".join(c[1]["as leaf"] * ["."])
                + "\n"
            )
            f.write(calls_string)


root_dir, order_by = sys.argv[1], sys.argv[2]
output_filename = "output_" + order_by + ".txt"
if __name__ == "__main__":
    save_graph_size_representation(order_by)
