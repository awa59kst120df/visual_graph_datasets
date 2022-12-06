import typing as t

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

import visual_graph_datasets.typing as tc


def visualize_grayscale_graph(ax: plt.Axes,
                              g: tc.GraphDict,
                              node_positions: np.ndarray,
                              color_map: t.Union[str, mpl.colors.Colormap] = 'gist_yarg',
                              node_border_width: float = 1.0,
                              node_size: float = 100.0) -> None:
    """
    Creates a grayscale color graph visualization for the given graph ``g`` drawn on the canvas of ``ax``
    using the node positions ``node_positions``. The node positions have to be in the figure coordinate
    system!

    :param plt.Axes ax: The axes onto which the visualization should be drawn
    :param tc.GraphDict g: The graph which is to be drawn
    :param node_positions: An array with the shape (V, 2) where V is the number of nodes in the graph. The
        values of this array represent the x, y coordinates of the corresponding nodes in the figure
    :param color_map: A color map to determine the color of each node visualization based on the node
        attribute. Currently grayscale, but could be any matplotlib color map
    :param node_border_width:
    :param node_size:
    :return: None
    """

    if isinstance(color_map, str):
        color_map = mpl.colormaps[color_map]

    # ~ drawing nodes
    for i in g['node_indices']:
        x, y = node_positions[i]

        value = g['node_attributes'][i][0]
        color = color_map(value)
        ax.scatter(
            x,
            y,
            color=color,
            edgecolors='black',
            linewidths=node_border_width,
            s=node_size,
            zorder=2,
        )

    # ~ drawing edges
    for e, (i, j) in enumerate(g['edge_indices']):
        x_i, y_i = node_positions[i]
        x_j, y_j = node_positions[j]

        ax.plot(
            (x_i, x_j),
            (y_i, y_j),
            color='black',
            zorder=1,
        )


def visualize_color_graph(ax: plt.Axes,
                          g: tc.GraphDict,
                          node_positions: np.ndarray,
                          node_border_width: float = 1.0,
                          edge_width: float = 1.0,
                          alpha: float = 1.0,
                          node_size: float = 100.0) -> None:
    """

    :param ax:
    :param g:
    :param node_positions:
    :param color_map:
    :param node_border_width:
    :param edge_width:
    :param alpha:
    :param node_size:

    :return: None
    """
    # ~ drawing nodes
    for i in g['node_indices']:
        x, y = node_positions[i]

        color = g['node_attributes'][i][:3]
        ax.scatter(
            x,
            y,
            color=(*color, alpha),
            edgecolors='black',
            linewidths=node_border_width,
            s=node_size,
            zorder=2,
        )

    # ~ drawing edges
    # The edges are simple: They are just black lines between the nodes.
    for e, (i, j) in enumerate(g['edge_indices']):
        x_i, y_i = node_positions[i]
        x_j, y_j = node_positions[j]

        ax.plot(
            (x_i, x_j),
            (y_i, y_j),
            color='black',
            lw=edge_width,
            zorder=1,
        )
