from networkx import is_isomorphic, MultiDiGraph
from networkx.algorithms.isomorphism import (
    categorical_node_match,
    categorical_multiedge_match,
)

__all__ = ["check_automatons_equivalent"]


def check_automatons_equivalent(first_automaton, second_automaton) -> bool:
    """Check if automatons are equivalent

    Args:
        first_automaton: First automaton to compare with
        second_automaton: Second automaton to compare with

    Returns:
        True if automatons are equivalent, otherwise False
    """
    return _check_graphs_isomorphic(
        _convert_automaton_to_graph(first_automaton),
        _convert_automaton_to_graph(second_automaton),
    )


def _check_graphs_isomorphic(first_graph, second_graph):
    return is_isomorphic(
        first_graph,
        second_graph,
        categorical_node_match(["label", "is_start", "is_final"], [None, None, None]),
        categorical_multiedge_match("label", None),
    )


def _convert_automaton_to_graph(automaton):
    graph = MultiDiGraph()
    for state_from, symbol, state_to in automaton:
        graph.add_edge(
            state_from,
            state_to,
            label=symbol.value,
        )
    for node, data in graph.nodes(data=True):
        data["is_start"] = node in automaton.start_states
        data["is_final"] = node in automaton.final_states
    return graph
