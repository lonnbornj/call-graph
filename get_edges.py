import re
import os
import glob


def process_dir(directory, force=False):
    src_files = glob.glob(os.path.join(directory, "*.m"))
    fn_names = [os.path.basename(f).split(".")[0] for f in src_files]
    for child_node in fn_names:
        write_child_edges_data(child_node, (src_files, fn_names), force)


def write_child_edges_data(child, fns, force):
    outfile = os.path.join("example", "data", child + ".txt")
    if os.path.isfile(outfile) and not force:
        return
    with open(outfile, "w") as outf:
        for filen, fn in zip(*fns):
            if file_mentions_child(filen, child):
                outf.write(fn + "\n")

def read_edges_file(data_dir, child):
    with open(os.path.join(data_dir, child + ".txt")) as f:
        parents = [fname.strip() for fname in f.readlines() if fname != child]
    return parents

def file_mentions_child(filen, child):
    with open(filen, "r") as f:
        for line in f:
            if re.search(child, line):
                return True
    return False


if __name__ == "__main__":
    process_dir(os.path.join("example", "code"))
