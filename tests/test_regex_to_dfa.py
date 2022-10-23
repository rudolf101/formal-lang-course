import pytest
from pyformlang.finite_automaton import DeterministicFiniteAutomaton
from pyformlang.finite_automaton import State
from pyformlang.finite_automaton import Symbol
from pyformlang.regular_expression import Regex

from project import generate_min_dfa_by_regex
from tests.utils import check_automatons_equivalent


@pytest.fixture()
def min_dfa():
    return generate_min_dfa_by_regex("a*b*c*")


def test_generated_dfa_is_deterministic(min_dfa):
    assert min_dfa.is_deterministic()


def test_generate_min_dfa(min_dfa):
    exp_dfa = DeterministicFiniteAutomaton()

    exp_dfa.add_start_state(State(0))
    exp_dfa.add_final_state(State(0))
    exp_dfa.add_final_state(State(1))
    exp_dfa.add_final_state(State(2))

    exp_dfa.add_transition(State(0), Symbol("a"), State(0))
    exp_dfa.add_transition(State(0), Symbol("b"), State(1))
    exp_dfa.add_transition(State(0), Symbol("c"), State(2))
    exp_dfa.add_transition(State(1), Symbol("b"), State(1))
    exp_dfa.add_transition(State(1), Symbol("c"), State(2))
    exp_dfa.add_transition(State(2), Symbol("c"), State(2))

    assert check_automatons_equivalent(exp_dfa, min_dfa)


@pytest.mark.parametrize(
    "regex, accepted, declined",
    [
        ("", [], [[Symbol("a")], [Symbol("b"), [Symbol("abba")]]]),
        (
            "a*b*c*",
            [
                [],
                [Symbol("a")],
                [Symbol("a"), Symbol("b")],
                [Symbol("a"), Symbol("b"), Symbol("c")],
                [Symbol("a"), Symbol("b"), Symbol("b"), Symbol("b"), Symbol("c")],
                [
                    Symbol("a"),
                    Symbol("a"),
                    Symbol("a"),
                    Symbol("b"),
                    Symbol("b"),
                    Symbol("b"),
                    Symbol("c"),
                ],
                [
                    Symbol("a"),
                    Symbol("a"),
                    Symbol("a"),
                    Symbol("b"),
                    Symbol("b"),
                    Symbol("c"),
                    Symbol("c"),
                ],
            ],
            [
                [Symbol("F")],
                [Symbol("c"), Symbol("b"), Symbol("a")],
            ],
        ),
    ],
)
def test_regex_to_dfa(regex, accepted, declined) -> None:
    dfa = generate_min_dfa_by_regex(Regex(regex))

    assert all(dfa.accepts(word) for word in accepted)
    assert all(not dfa.accepts(word) for word in declined)
