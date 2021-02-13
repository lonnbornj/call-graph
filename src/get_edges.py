import re
import os
from pathlib import Path
import glob


def process_dir(root_dir, force=False):
    """Process a directory (`root_dir`/code) of .m functions, saving data about their relationships for post-processing"""
    src_files = glob.glob(os.path.join(root_dir, "code", "*.m"))
    fn_names = [os.path.basename(f).split(".")[0] for f in src_files]
    out_dir = _out_dir(root_dir)
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)
    if force:
        _reset_output_files(out_dir)
    for node in fn_names:
        _write_edges_data(node, (src_files, fn_names), force, out_dir)


def _write_edges_data(cur_node, fns, force, out_dir):
    """Write edges into and out of a node to text files"""
    edges_in_outfile = os.path.join(out_dir, cur_node + "_in.txt")
    edges_out_outfile = os.path.join(out_dir, cur_node + "_out.txt")
    if not force and os.path.isfile(edges_in_outfile):
        return
    Path(edges_out_outfile).touch(
        exist_ok=True
    )  # create empty edges-out file in case child is a leaf
    print("Finding edges into node {}".format(cur_node))
    node_edges_in = _find_edges_in(cur_node, fns)
    with open(edges_in_outfile, "w") as f:
        f.writelines([fn + "\n" for fn in node_edges_in])
    for other_edges_out_outfile in [
        os.path.join(out_dir, fn + "_out.txt") for fn in node_edges_in
    ]:
        with open(other_edges_out_outfile, "a") as f:
            f.write(cur_node + "\n")


def _find_edges_in(child, fns):
    """Find the edges into a node"""
    child_edges_in = list()
    for filen, fn in zip(*fns):
        if _file_mentions_child(filen, child):
            child_edges_in.append(fn)
    return child_edges_in


def _file_mentions_child(filen, child):
    """Returns True if a .m function mentions (calls) a specified child function, else returns False"""
    child_rexp = child + "( |\t)*(\\(|;|$)"
    child_anon_call = (
        "@( |\t)*" + child + "( |\t)*,"
    )  # anonymous function calls or form: @<fn>,
    if os.stat(filen).st_size == 0:
        return False
    with open(filen, "r") as f:
        next(f)  # skip the first line, containing the function call signature
        for line in f:
            if line.lstrip()[0] == "%":
                continue
            if re.search(child_rexp, line) or re.search(child_anon_call, line):
                return True
    return False


def read_edges_file(root_dir, node, graph_type):
    """Read in data of edges into/out of a node"""
    fname_suffix = "_in" if graph_type == "leaf" else "_out"
    with open(os.path.join(_out_dir(root_dir), node + fname_suffix + ".txt")) as f:
        edge_fns = f.readlines()
        edge_fns = [fn.strip() for fn in edge_fns if fn != node]
    return edge_fns


def _out_dir(root_dir):
    """Returns the output directory path"""
    return os.path.join(root_dir, "data")


def _reset_output_files(directory):
    """Remove previously computed edge data from the output directory"""
    for f in glob.glob(directory + "*.txt"):
        if os.path.isfile(f):
            os.remove(f)
