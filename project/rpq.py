from typing import Set, Tuple, Any, Union

import networkx as nx
from pyformlang.regular_expression import Regex

from project import matrices_utils, automata_utils


def rpq(
    graph: nx.MultiDiGraph,
    query: Union[Regex, str],
    start_nodes: set = None,
    final_nodes: set = None,
) -> Set[Tuple[Any, Any]]:
    """Regular query on graph

    Args:
        graph(MultiDiGraph): Graph on which query will be executed
        query(Regex|str): Query represented by regex
        start_nodes(Set|None): Set of start nodes be treated in NFA. If None then each graph node is start state
        final_nodes(Set|None): Set of final nodes be treated in NFA. If None then each graph node is final state

    Returns:
         The set of pairs where the node in second place is reachable from the node in first place via a given query
    """
    query_boolean_matrix = matrices_utils.BooleanMatrix.from_nfa(
        automata_utils.generate_min_dfa_by_regex(query)
    )
    intersection_bool_matrix = matrices_utils.BooleanMatrix.from_nfa(
        automata_utils.graph_to_epsilon_nfa(graph, start_nodes, final_nodes)
    ).intersect(query_boolean_matrix)
    start_states = intersection_bool_matrix.get_start_states()
    final_states = intersection_bool_matrix.get_final_states()
    transitive_closure = intersection_bool_matrix.get_transitive_closure()
    res = set()

    for state_from, state_to in zip(*transitive_closure.nonzero()):
        if state_from in start_states and state_to in final_states:
            res.add(
                (
                    state_from // query_boolean_matrix.states_count,
                    state_to // query_boolean_matrix.states_count,
                )
            )

    return res
