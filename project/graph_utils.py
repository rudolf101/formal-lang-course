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
    nodes: int
    edges: int
    labels: Set[str]


def load_graph(graph_name: str) -> MultiDiGraph:
    path = cfpq_data.download(graph_name)
    return cfpq_data.graph_from_csv(path)


def save_graph_dot(cur_graph: MultiDiGraph, file: Union[IO, str]) -> None:
    drawing.nx_pydot.write_dot(cur_graph, file)


def get_graph_info(cur_graph: MultiDiGraph) -> Graph:
    return Graph(
        cur_graph.nodes(),
        cur_graph.edges(),
        set(label for u, v, label in cur_graph.edges(data="label") if label),
    )


def build_labeled_two_cycles_graph(
    nodes_first_cycle: int,
    nodes_second_cycle: int,
    labels: Tuple[str, str],
) -> MultiDiGraph:
    return cfpq_data.labeled_two_cycles_graph(
        nodes_first_cycle, nodes_second_cycle, labels=labels
    )
