import pytest
from pyformlang.finite_automaton import DeterministicFiniteAutomaton
from pyformlang.finite_automaton import State
from pyformlang.finite_automaton import Symbol

from project import generate_min_dfa_by_regex


@pytest.fixture()
def min_dfa():
    return generate_min_dfa_by_regex("a*b*c*")


def test_generated_dfa_is_deterministic(min_dfa):
    assert min_dfa.is_deterministic()


def test_generate_min_dfa(min_dfa):
    exp_dfa = DeterministicFiniteAutomaton()

    state0 = State(0)
    state1 = State(1)
    state2 = State(2)

    exp_dfa.add_start_state(state0)
    exp_dfa.add_final_state(state0)
    exp_dfa.add_final_state(state1)
    exp_dfa.add_final_state(state2)

    exp_dfa.add_transition(state0, Symbol("a"), state0)
    exp_dfa.add_transition(state0, Symbol("b"), state1)
    exp_dfa.add_transition(state0, Symbol("c"), state2)
    exp_dfa.add_transition(state1, Symbol("b"), state1)
    exp_dfa.add_transition(state1, Symbol("c"), state2)
    exp_dfa.add_transition(state2, Symbol("c"), state2)

    assert min_dfa.is_equivalent_to(exp_dfa) and len(min_dfa.states) == len(
        exp_dfa.states
    )


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
def test_regex_to_dfa_accepting_words(regex, accepted, declined) -> None:
    dfa = generate_min_dfa_by_regex(regex)

    assert all(dfa.accepts(word) for word in accepted)
    assert all(not dfa.accepts(word) for word in declined)
