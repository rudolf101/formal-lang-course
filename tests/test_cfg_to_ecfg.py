import pytest
from pyformlang.cfg import CFG, Variable
from pyformlang.regular_expression import Regex

from project.cfg_utils import *
from project.automata_utils import *
from tests.utils import check_automatons_equivalent


@pytest.mark.parametrize(
    "text_cfg, ecfg_expected",
    [
        (
            "",
            {},
        ),
        (
            "S -> a",
            {Variable("S"): "a"},
        ),
        (
            """
                S -> a
                S -> a
                """,
            {Variable("S"): "a"},
        ),
        (
            """
                S -> c | d | e
                """,
            {Variable("S"): "((c|d)|e)"},
        ),
        (
            """
                S -> a | b
                """,
            {Variable("S"): "(a|b)"},
        ),
    ],
)
def test_cfg_to_ecfg(text_cfg, ecfg_expected):
    ecfg = cfg_to_ecfg(CFG.from_text(text_cfg))
    expected_productions = {v: Regex(r) for v, r in ecfg_expected.items()}

    assert len(ecfg.productions) == len(expected_productions)
    assert all(
        check_automatons_equivalent(
            generate_min_dfa_by_regex(ecfg.productions[v]),
            generate_min_dfa_by_regex(expected_productions[v]),
        )
        for v in ecfg.productions
    )
