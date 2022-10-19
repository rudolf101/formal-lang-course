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
    nfa_bool_mtx = boolean_matrix.BooleanMatrix.from_nfa(
        automata_utils.graph_to_epsilon_nfa(
            graph=graph,
            start_states=start_nodes,
            final_states=final_nodes,
        )
    )
    query_bool_mtx = boolean_matrix.BooleanMatrix.from_nfa(
        automata_utils.generate_min_dfa_by_regex(regex=query),
    )
    intersection_bool_mtx = nfa_bool_mtx & query_bool_mtx
    idx_to_state = {
        idx: state for state, idx in intersection_bool_mtx.state_to_index.items()
    }
    transitive_closure = intersection_bool_mtx.get_transitive_closure()
    result = set()
    for state_from_idx, state_to_idx in zip(*transitive_closure.nonzero()):
        state_from, state_to = idx_to_state[state_from_idx], idx_to_state[state_to_idx]
        if (
                state_from in intersection_bool_mtx.start_states
                and state_to in intersection_bool_mtx.final_states
        ):
            state_from_graph_value, _ = state_from.value
            state_to_graph_value, _ = state_to.value
            result.add(
                (state_from_graph_value, state_to_graph_value),
            )
    return result


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
