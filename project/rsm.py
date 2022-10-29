from pyformlang.cfg import Variable
from pyformlang.finite_automaton import DeterministicFiniteAutomaton
from typing import NamedTuple, Dict

__all__ = [
    "RSM",
    "minimize_rsm",
]


class RSM(NamedTuple):
    """Class represents Recursive State Machine

    Attributes:
        start_symbol(Variable): Start symbol of automaton
        boxes(Dict[Variable, DeterministicFiniteAutomaton]): Mapping from variables to deterministic finite automatons
    """

    start_symbol: Variable
    boxes: Dict[Variable, DeterministicFiniteAutomaton]


def minimize_rsm(rsm: RSM) -> RSM:
    """Minimizes RSM by minimizing internal automatons

    Args:
        rsm(RSM): Recursive state machine
    Returns:
        Minimized recursive state machine
    """
    return RSM(
        start_symbol=rsm.start_symbol,
        boxes={v: a.minimize() for v, a in rsm.boxes.items()},
    )
