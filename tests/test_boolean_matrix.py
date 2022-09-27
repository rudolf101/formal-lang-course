import pytest
from pyformlang.finite_automaton import (
    DeterministicFiniteAutomaton,
    State,
    EpsilonNFA,
)

from project import BooleanMatrix


@pytest.fixture
def nfa():
    nfa = EpsilonNFA()
    nfa.add_transitions(
        [
            (0, "a", 1),
            (1, "b", 1),
            (1, "c", 2),
            (2, "c", 3),
            (3, "b", 0),
        ]
    )

    return nfa


@pytest.mark.parametrize(
    "label,edges",
    [
        ("a", [(0, 1)]),
        ("b", [(1, 1), (3, 0)]),
        ("c", [(1, 2), (2, 3)]),
    ],
)
def test_adjacency(nfa, label, edges):
    bm = BooleanMatrix.from_nfa(nfa)
    assert all(bm.bool_matrices[label][edge] for edge in edges)


def test_transitive_closure(nfa):
    bm = BooleanMatrix.from_nfa(nfa)
    tc = bm.get_transitive_closure()
    assert tc.sum() == tc.size


@pytest.mark.parametrize(
    "label,expected",
    [
        ("a", 1),
        ("b", 2),
        ("c", 2),
    ],
)
def test_nonzero(nfa, label, expected):
    bm = BooleanMatrix.from_nfa(nfa)
    actual = bm.bool_matrices[label].nnz

    assert actual == expected


def test_labels(nfa):
    bm = BooleanMatrix.from_nfa(nfa)
    actual_labels = bm.bool_matrices.keys()
    expected_labels = nfa.symbols

    assert actual_labels == expected_labels


def test_intersection(nfa):
    first_nfa = nfa
    for i in range(4):
        first_nfa.add_start_state(State(i))
    for i in range(3):
        first_nfa.add_final_state(State(i))

    first_boolean_matrix = BooleanMatrix.from_nfa(first_nfa)

    second_nfa = EpsilonNFA()
    second_nfa.add_transitions([(0, "a", 1), (1, "d", 2), (1, "b", 1), (2, "d", 3)])
    second_nfa.add_start_state(State(0))
    second_nfa.add_final_state(State(1))
    second_nfa.add_final_state(State(3))

    second_boolean_matrix = BooleanMatrix.from_nfa(second_nfa)

    expected_nfa = DeterministicFiniteAutomaton()
    expected_nfa.add_transitions([(0, "a", 1), (1, "b", 1)])
    expected_nfa.add_start_state(State(0))
    expected_nfa.add_final_state(State(1))

    assert (
        first_boolean_matrix.intersect(second_boolean_matrix)
        .to_nfa()
        .is_equivalent_to(expected_nfa)
    )
