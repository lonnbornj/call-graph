import networkx as nx
import matplotlib.pyplot as plt


def plot(G, title, pos=None):
    if pos is None:
        pos = nx.spring_layout(G)
    plt.figure(figsize=(12, 8))
    nx.draw_networkx_nodes(G, pos, node_size=200)
    nx.draw_networkx_edges(G, pos, connectionstyle="arc3,rad=0.2")

    labels, label_pos, graph_size = _get_figure_label_positions(G, pos)
    nx.draw_networkx_labels(
        G, label_pos, labels, font_color="r", font_weight="bold", font_size=10
    )
    plt.draw()
    plt.ylim([-1, plt.ylim()[1]])
    plt.title(title)
    plt.show()


def _get_figure_label_positions(G, pos, max_label_length=50):
    labels = {}
    for node in G.nodes():
        label = (
            node if len(node) < max_label_length else node[0:max_label_length] + "..."
        )
        labels[node] = label
    size_layer_0 = sum(1 for (x, y) in pos.values() if y == 0)
    ymax = max(y for (x, y) in pos.values())
    xmax = max(x for (x, y) in pos.values())
    label_pos = {}
    offset = size_layer_0 > 7
    for k, (x, y) in pos.items():
        offset_fac = x if offset else 1
        label_pos[k] = (
            (x, y + 0.5 / size_layer_0)
            if y == ymax
            # offset labels in bottom row if they are numerous
            else (x, y - 0.5 * offset_fac / size_layer_0)
        )
    return labels, label_pos, (xmax, ymax)
