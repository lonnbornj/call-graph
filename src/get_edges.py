import re
import os
from pathlib import Path
import glob


def process_dir(root_dir, force=False):
    src_files = glob.glob(os.path.join(root_dir, "code", "*.m"))
    fn_names = [os.path.basename(f).split(".")[0] for f in src_files]
    out_dir = _out_dir(root_dir)
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)
    for node in fn_names:
        _write_edges_data(node, (src_files, fn_names), force, out_dir)


def read_edges_file(root_dir, node, graph_type):
    fname_suffix = "_in" if graph_type == "leaf" else "_out"
    with open(os.path.join(_out_dir(root_dir), node + fname_suffix + ".txt")) as f:
        edge_fns = f.readlines()
        edge_fns = [fn.strip() for fn in edge_fns if fn != node]
    print(node, edge_fns)
    return edge_fns


def _write_edges_data(child, fns, force, out_dir):
    edges_in_outfile = os.path.join(out_dir, child + "_in.txt")
    edges_out_outfile = os.path.join(out_dir, child + "_out.txt")
    if not force and os.path.isfile(edges_in_outfile):
        return
    # create empty edges-out file in case child is a leaf:
    Path(edges_out_outfile).touch(exist_ok=True)
    print("Finding edges into node {}".format(child))
    node_edges_in = _find_edges_in(child, fns)
    with open(edges_in_outfile, "w") as f:
        f.writelines([fn + "\n" for fn in node_edges_in])
    for other_edges_out_outfile in [
        os.path.join(out_dir, fn + "_out.txt") for fn in node_edges_in
    ]:
        with open(other_edges_out_outfile, "a") as f:
            f.write(child + "\n")


def _find_edges_in(child, fns):
    child_edges_in = list()
    for filen, fn in zip(*fns):
        if _file_mentions_child(filen, child):
            child_edges_in.append(fn)
    return child_edges_in


def _file_mentions_child(filen, child):
    with open(filen, "r") as f:
        for line in f:
            if re.search(child, line):
                return True
    return False


def _out_dir(root_dir):
    return os.path.join(root_dir, "data")
