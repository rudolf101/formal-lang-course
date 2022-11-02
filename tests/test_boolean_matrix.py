import pytest
from pyformlang.finite_automaton import (
    DeterministicFiniteAutomaton,
    State,
    EpsilonNFA,
    Symbol,
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


def test_transitive_closure_empty():
    bm = BooleanMatrix.from_nfa(EpsilonNFA())
    tc = bm.get_transitive_closure()
    assert not tc.toarray().tolist()


def test_transitive_closure(nfa):
    bm = BooleanMatrix.from_nfa(nfa)
    tc = bm.get_transitive_closure()
    assert [
        [33.0, 84.0, 60.0, 44.0],
        [44.0, 117.0, 84.0, 60.0],
        [16.0, 44.0, 33.0, 24.0],
        [24.0, 60.0, 44.0, 33.0],
    ] == tc.toarray().tolist()


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
    intersection = first_boolean_matrix & second_boolean_matrix
    assert all(
        (
            intersection.start_states == {(1, 0), (2, 0), (3, 0), (0, 0)},
            intersection.final_states
            == {(0, 1), (2, 1), (1, 1), (0, 3), (2, 3), (1, 3)},
            intersection.state_to_index
            == {
                (0, 0): 0,
                (0, 1): 1,
                (0, 2): 2,
                (0, 3): 3,
                (1, 0): 4,
                (1, 1): 5,
                (1, 2): 6,
                (1, 3): 7,
                (2, 0): 8,
                (2, 1): 9,
                (2, 2): 10,
                (2, 3): 11,
                (3, 0): 12,
                (3, 1): 13,
                (3, 2): 14,
                (3, 3): 15,
            },
        )
    )


@pytest.fixture
def non_empty_nfa():
    nfa = EpsilonNFA()
    nfa.add_transition(State(0), Symbol("a"), State(0))
    nfa.add_transition(State(0), Symbol("b"), State(1))
    nfa.add_transition(State(1), Symbol("c"), State(1))
    nfa.add_start_state(State(0))
    nfa.add_final_state(State(1))
    return nfa


def test_intersection_with_non_empty_automaton_matrix(non_empty_nfa):
    intersection = BooleanMatrix.from_nfa(non_empty_nfa) & BooleanMatrix.from_nfa(
        non_empty_nfa
    )
    for label, values in intersection.bool_matrices.items():
        print(label, values.toarray().tolist())
    assert all(
        (
            [
                [True, False, False, False],
                [False, False, False, False],
                [False, False, False, False],
                [False, False, False, False],
            ]
            == intersection.bool_matrices["a"].toarray().tolist(),
            [
                [False, False, False, True],
                [False, False, False, False],
                [False, False, False, False],
                [False, False, False, False],
            ]
            == intersection.bool_matrices["b"].toarray().tolist(),
            [
                [False, False, False, False],
                [False, False, False, False],
                [False, False, False, False],
                [False, False, False, True],
            ]
            == intersection.bool_matrices["c"].toarray().tolist(),
        )
    )
