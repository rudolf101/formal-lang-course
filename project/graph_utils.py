from typing import NamedTuple, Set, Tuple, Union, IO

import cfpq_data
from networkx import *

__all__ = [
    "Graph",
    "load_graph",
    "save_graph_dot",
    "get_graph_info",
    "get_graph_info_by_name",
    "build_labeled_two_cycles_graph",
    "build_then_save_labeled_two_cycles_graph",
]


class Graph(NamedTuple):
    """Class that stores general information about graph.

    Attributes:
        nodes (int): Count of nodes in graph.
        edges (int): Count of edges in graph.
        labels (Set[str]): Set of labels on edges
    """

    nodes: int
    edges: int
    labels: Set[str]


def load_graph(graph_name: str) -> MultiDiGraph:
    """Loads a graph from CFPQ_Data dataset.

    Args:
        graph_name (str): Name of the graph to be loaded from the dataset.

    Returns:
        Class loaded from csv file
    """
    path = cfpq_data.download(graph_name)
    return cfpq_data.graph_from_csv(path)


def save_graph_dot(cur_graph: MultiDiGraph, file: Union[IO, str]) -> None:
    """Saves the given graph in DOT format to file

    Args:
        cur_graph (MultiDiGraph): Graph to be saved
        file (Union[IO, str]): path or file where graph should be saved

    Returns:
        None
    """
    drawing.nx_pydot.write_dot(cur_graph, file)


def get_graph_info(cur_graph: MultiDiGraph) -> Graph:
    """Get general information about graph.

    Args:
        cur_graph (MultiDiGraph): Graph to view

    Returns:
        Class with information about graph
    """
    return Graph(
        cur_graph.number_of_nodes(),
        cur_graph.number_of_edges(),
        set(label for u, v, label in cur_graph.edges(data="label") if label),
    )


def get_graph_info_by_name(graph_name: str) -> Graph:
    """Get graph info from by name in CFPQ_Data dataset.

    Args:
        graph_name (str): Name of the graph to get info

    Returns:
        Class with information about graph
    """
    return get_graph_info(load_graph(graph_name))


def build_labeled_two_cycles_graph(
    nodes_first_cycle: int,
    nodes_second_cycle: int,
    labels: Tuple[str, str],
) -> MultiDiGraph:
    """Builds labeled graph with two cycles.

    Args:
        nodes_first_cycle (int): number of nodes in first cycle
        nodes_second_cycle (int): number of nodes in second cycle
        labels (Tuple[str, str]): labels for edges

    Returns:
        Labeled two cycles graph as MultiDiGraph
    """
    return cfpq_data.labeled_two_cycles_graph(
        nodes_first_cycle, nodes_second_cycle, labels=labels
    )


def build_then_save_labeled_two_cycles_graph(
    nodes_first_cycle: int,
    nodes_second_cycle: int,
    labels: Tuple[str, str],
    file: Union[IO, str],
) -> None:
    """Builds and save labeled graph with two cycles.

    Args:
        nodes_first_cycle (int): number of nodes in first cycle
        nodes_second_cycle (int): number of nodes in second cycle
        labels (Tuple[str, str]): labels for edges
        file (Union[IO, str]): path or file where graph should be saved

    Returns:
        None
    """
    graph_to_save = build_labeled_two_cycles_graph(
        nodes_first_cycle, nodes_second_cycle, labels
    )
    save_graph_dot(graph_to_save, file)
