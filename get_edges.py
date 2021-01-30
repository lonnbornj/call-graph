import re
import os
import glob


def process_dir(root_dir, force=False):
    src_files = glob.glob(os.path.join(root_dir, "code", "*.m"))
    fn_names = [os.path.basename(f).split(".")[0] for f in src_files]
    out_dir = _out_dir(root_dir)
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)
    for child_node in fn_names:
        _write_child_edges_data(child_node, (src_files, fn_names), force, out_dir)


def read_edges_file(root_dir, child):
    with open(os.path.join(_out_dir(root_dir), child + ".txt")) as f:
        parents = f.readlines()
        parents = [fn.strip() for fn in parents if fn != child]
    return parents


def _write_child_edges_data(child, fns, force, out_dir):
    outfile = os.path.join(out_dir, child + ".txt")
    if os.path.isfile(outfile) and not force:
        return
    print("Finding edges into node {}".format(child))
    with open(outfile, "w") as outf:
        for filen, fn in zip(*fns):
            if _file_mentions_child(filen, child):
                outf.write(fn + "\n")


def _file_mentions_child(filen, child):
    with open(filen, "r") as f:
        for line in f:
            if re.search(child, line):
                return True
    return False


def _out_dir(root_dir):
    return os.path.join(root_dir, "data")
