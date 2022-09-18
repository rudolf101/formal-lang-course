from pyformlang.finite_automaton import DeterministicFiniteAutomaton
from pyformlang.regular_expression import Regex

__all__ = ["generate_min_dfa_by_regex"]


def generate_min_dfa_by_regex(regex_str: str) -> DeterministicFiniteAutomaton:
    """Generate deterministic automata by regular expression

    Args:
        regex_str(str): String representation of regex

    Returns:
        Generated deterministic automata

    Raises:
        MisformedRegexError: If the regular expression is misformed.
    """
    regex = Regex(regex_str)
    dfa = regex.to_epsilon_nfa().to_deterministic()
    return dfa.minimize()
