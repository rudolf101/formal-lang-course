import cfpq_data
from networkx import *
from typing import NamedTuple, Set, Tuple, Union, IO

__all__ = [
    "Graph",
    "load_graph",
    "save_graph_dot",
    "get_graph_info",
    "build_labeled_two_cycles_graph",
]


class Graph(NamedTuple):
    """Class that stores general information about graph.

    Attributes
    ----------
    nodes: int
        Count of nodes in graph
    edges: int
        Count of edges in graph
    labels: Set[str]
        Set of labels on edges
    """

    nodes: int
    edges: int
    labels: Set[str]


def load_graph(graph_name: str) -> MultiDiGraph:
    """Loads a graph from CFPQ_Data dataset.

    :param graph_name: name of the graph to be loaded from the dataset
    """
    path = cfpq_data.download(graph_name)
    return cfpq_data.graph_from_csv(path)


def save_graph_dot(cur_graph: MultiDiGraph, file: Union[IO, str]) -> None:
    """Saves the given graph in DOT format to file

    :param cur_graph: graph to be saved
    :param file: path or file
    """
    drawing.nx_pydot.write_dot(cur_graph, file)


def get_graph_info(cur_graph: MultiDiGraph) -> Graph:
    """Get general information about graph.

    :param cur_graph: graph to view
    :return: class with information about graph
    """
    return Graph(
        cur_graph.number_of_nodes(),
        cur_graph.number_of_edges(),
        set(label for u, v, label in cur_graph.edges(data="label") if label),
    )


def build_labeled_two_cycles_graph(
    nodes_first_cycle: int,
    nodes_second_cycle: int,
    labels: Tuple[str, str],
) -> MultiDiGraph:
    """Builds labeled graph with two cycles.

    :param nodes_first_cycle: number of nodes in first cycle
    :param nodes_second_cycle: number of nodes in second cycle
    :param labels: labels for edges"""
    return cfpq_data.labeled_two_cycles_graph(
        nodes_first_cycle, nodes_second_cycle, labels=labels
    )
