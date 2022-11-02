from networkx import MultiDiGraph
from pyformlang.finite_automaton import EpsilonNFA, Symbol, Epsilon, State

from project.automata_utils import *
from tests.utils import check_automatons_equivalent


def test_empty_graph_to_epsilon_nfa():
    empty_graph = MultiDiGraph()
    epsilon_nfa = graph_to_epsilon_nfa(empty_graph)
    assert not epsilon_nfa.states


def test_graph_to_epsilon_nfa():
    graph = MultiDiGraph()
    edges = [
        (0, 3, None),
        (0, 1, None),
        (1, 2, "a"),
        (2, 1, None),
        (2, 3, None),
        (3, 4, "b"),
    ]

    for node_from, node_to, label in edges:
        graph.add_edge(node_from, node_to, label=label)
    epsilon_nfa = graph_to_epsilon_nfa(graph, {0}, {4})

    expected_epsilon_nfa = EpsilonNFA()
    transitions = [
        (State(0), Epsilon(), State(3)),
        (State(0), Epsilon(), State(1)),
        (State(1), Symbol("a"), State(2)),
        (State(2), Epsilon(), State(1)),
        (State(2), Epsilon(), State(3)),
        (State(3), Symbol("b"), State(4)),
    ]
    for state_from, symbol, state_to in transitions:
        expected_epsilon_nfa.add_transition(state_from, symbol, state_to)
    expected_epsilon_nfa.add_start_state(State(0))
    expected_epsilon_nfa.add_final_state(State(4))

    assert check_automatons_equivalent(epsilon_nfa, expected_epsilon_nfa)
