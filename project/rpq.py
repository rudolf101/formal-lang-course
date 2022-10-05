import enum
from networkx import MultiDiGraph
from pyformlang.regular_expression import Regex
from typing import Set, Tuple, Any, Union

import project.automata_utils as automata_utils
import project.boolean_matrix as boolean_matrix

__all__ = ["rpq_tensor", "rpq_bfs", "RpqMode"]


def rpq_tensor(
    graph: MultiDiGraph,
    query: Union[Regex, str],
    start_nodes: set = None,
    final_nodes: set = None,
) -> Set[Tuple[Any, Any]]:
    """Regular query on graph using tensor multiplication

    Args:
        graph(MultiDiGraph): Graph on which query will be executed
        query(Regex|str): Query represented by regex
        start_nodes(Set|None): Set of start nodes be treated in NFA. If None then each graph node is start state
        final_nodes(Set|None): Set of final nodes be treated in NFA. If None then each graph node is final state

    Returns:
         The set of pairs where the node in second place is reachable from the node in first place via a given query
    """
    query_boolean_matrix = boolean_matrix.BooleanMatrix.from_nfa(
        automata_utils.generate_min_dfa_by_regex(query)
    )
    intersection_bool_matrix = boolean_matrix.BooleanMatrix.from_nfa(
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


class RpqMode(enum.Enum):
    """Mode of multiple source rpq task

    Values:
        FIND_ALL_REACHABLE: Find all reachable nodes from set of start nodes
        FIND_REACHABLE_FOR_EACH_START_NODE: Find reachable nodes for each start node separately
    """

    FIND_ALL_REACHABLE = 1
    FIND_REACHABLE_FOR_EACH_START_NODE = 2


def rpq_bfs(
    graph: MultiDiGraph,
    query: Regex,
    mode: RpqMode,
    start_states: set = None,
    final_states: set = None,
) -> Set[Any]:
    """Executes regular query on graph using multiple source bfs

    Args:
        graph(MultiDiGraph): Graph on which query will be executed
        query(Regex|str): Query represented by regex
        start_states(Set|None): Set of start nodes be treated in NFA. If None then each graph node is start state
        final_states(Set|None): Set of final nodes be treated in NFA. If None then each graph node is final state
        mode(RpqMode): The mode that determines which vertices should be found

    Returns:
        If mode is FIND_ALL_REACHABLE -- set of reachable nodes, otherwise -- set of tuples (start_node, final_node)
    """
    nfa_bool_mtx = boolean_matrix.BooleanMatrix.from_nfa(
        automata_utils.graph_to_epsilon_nfa(
            graph,
            start_states,
            final_states,
        )
    )
    query_bool_mtx = boolean_matrix.BooleanMatrix.from_nfa(
        automata_utils.generate_min_dfa_by_regex(query),
    )
    return nfa_bool_mtx.sync_bfs(
        query_bool_mtx,
        mode == RpqMode.FIND_REACHABLE_FOR_EACH_START_NODE,
    )
