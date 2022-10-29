import pytest
from pyformlang.cfg import Variable

from project.ecfg import *


@pytest.mark.parametrize(
    "text_cfg, prods_expected",
    [
        (
            "",
            {},
        ),
        (
            "S -> ",
            {Variable("S"): "Empty"},
        ),
        (
            "S -> a",
            {Variable("S"): "a"},
        ),
        (
            "S -> c | d | e",
            {Variable("S"): "((c|d)|e)"},
        ),
    ],
)
def test_ecfg_from_text(text_cfg, prods_expected):
    ecfg = ECFG.from_text(text_cfg)
    productions = {v: str(r) for v, r in ecfg.productions.items()}
    assert productions == prods_expected
