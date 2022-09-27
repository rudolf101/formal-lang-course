from typing import Set, Union

from networkx import MultiDiGraph
from pyformlang.finite_automaton import (
    DeterministicFiniteAutomaton,
    EpsilonNFA,
    State,
    Epsilon,
    Symbol,
)
from pyformlang.regular_expression import Regex, PythonRegex

__all__ = ["generate_min_dfa_by_regex", "graph_to_epsilon_nfa"]


def generate_min_dfa_by_regex(regex: Union[Regex, str]) -> DeterministicFiniteAutomaton:
    """Generate min DFA by regex

    Args:
        regex(Union[Regex, str]): Regex or string representation of regex

    Returns:
        Generated deterministic automata
    """
    regex = PythonRegex(regex) if type(regex) is str else regex
    dfa = regex.to_epsilon_nfa().to_deterministic()
    return dfa.minimize()


def graph_to_epsilon_nfa(
    graph: MultiDiGraph,
    start_states: Set = None,
    final_states: Set = None,
) -> EpsilonNFA:
    """Converts graph to epsilon NFA

    Args:
        graph(MultiDiGraph): Graph to be converted
        start_states(Set|None): Set of start states in NFA. If None then each graph node is start state
        final_states(Set|None): Set of final states in NFA. If None then each graph node is final state

    Returns:
        Epsilon NFA
    """
    epsilon_nfa = EpsilonNFA()
    for node_from, node_to, edge_data in graph.edges(data=True):
        epsilon_nfa.add_transition(
            State(node_from),
            Epsilon() if not edge_data["label"] else Symbol(edge_data["label"]),
            State(node_to),
        )

    if start_states is None:
        start_states = set(graph.nodes)
    if final_states is None:
        final_states = set(graph.nodes)

    for state in map(State, start_states):
        epsilon_nfa.add_start_state(state)
    for state in map(State, final_states):
        epsilon_nfa.add_final_state(state)

    return epsilon_nfa
