import pytest
from pyformlang.finite_automaton import DeterministicFiniteAutomaton
from pyformlang.finite_automaton import State
from pyformlang.finite_automaton import Symbol
from pyformlang.regular_expression import Regex

from project import generate_min_dfa_by_regex


@pytest.fixture()
def min_dfa():
    return generate_min_dfa_by_regex("a*b*c*")


def test_generated_dfa_is_deterministic(min_dfa):
    assert min_dfa.is_deterministic()


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
